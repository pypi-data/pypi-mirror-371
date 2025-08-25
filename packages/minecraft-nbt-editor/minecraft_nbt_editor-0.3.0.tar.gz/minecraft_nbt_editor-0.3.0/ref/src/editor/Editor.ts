import type { JsonValue } from 'deepslate'
import { NbtFile, NbtRegion, NbtType } from 'deepslate'
import type { NbtPath } from '../common/NbtPath'
import type { SearchQuery } from '../common/Operations'
import { applyEdit, getEditedFile } from '../common/Operations'
import type { EditorMessage, NbtEdit, ViewMessage } from '../common/types'
import { ChunkEditor } from './ChunkEditor'
import { FileInfoEditor } from './FileInfoEditor'
import { locale } from './Locale'
import { MapEditor } from './MapEditor'
import { SnbtEditor } from './SnbtEditor'
import { StructureEditor } from './StructureEditor'
import { TreeEditor } from './TreeEditor'
import { getInt } from './Util'

export type VSCode = {
	postMessage(message: EditorMessage): void,
}

export const TYPES = Object.keys(NbtType).filter(e => isNaN(Number(e)))

declare function acquireVsCodeApi(): VSCode
const vscode = acquireVsCodeApi()

const root = document.querySelector('.nbt-editor')!

function lazy<T>(getter: () => T) {
	let value: T | null = null
	return () => {
		if (value === null) {
			value = getter()
		}
		return value
	}
}

export type SearchResult = {
	path: NbtPath,
	show(): void,
	replace(replacement: SearchQuery): NbtEdit,
}

export interface EditorPanel {
	reveal?(): void
	hide?(): void
	onInit?(file: NbtFile, prefix?: NbtPath): void
	onUpdate?(file: NbtFile, edit: NbtEdit): void
	onMessage?(message: ViewMessage): void
	onSearch?(query: SearchQuery | null): SearchResult[]
	menu?(): Element[]
}

export type EditHandler = (edit: NbtEdit) => void

class Editor {
	private readonly panels: {
		[key: string]: {
			editor: () => EditorPanel,
			updated?: boolean,
			options?: string[],
		},
	} = {
			structure: {
				editor: lazy(() => new StructureEditor(root, vscode, e => this.makeEdit(e), this.readOnly)),
				options: ['structure', 'default', 'snbt', 'info'],
			},
			map: {
				editor: lazy(() => new MapEditor(root, vscode, e => this.makeEdit(e), this.readOnly)),
				options: ['map', 'default', 'snbt', 'info'],
			},
			chunk: {
				editor: lazy(() => new ChunkEditor(root, vscode, e => this.makeEdit(e), this.readOnly)),
				options: ['chunk', 'default', 'snbt'],
			},
			default: {
				editor: lazy(() => new TreeEditor(root, vscode, e => this.makeEdit(e), this.readOnly)),
				options: ['default', 'snbt', 'info'],
			},
			snbt: {
				editor: lazy(() => new SnbtEditor(root, vscode, e => this.makeEdit(e), this.readOnly)),
			},
			info: {
				editor: lazy(() => new FileInfoEditor(root, vscode, () => {}, this.readOnly)),
			},
		}

	private type: string
	private nbtFile: NbtFile | NbtRegion.Ref
	private activePanel: string
	private readOnly: boolean

	private readonly findWidget: HTMLElement
	private searchQuery: SearchQuery = {}
	private searchResults: SearchResult[] | null = null
	private searchIndex: number = 0
	private lastReplace: NbtPath | null = null

	private inMap = false
	private selectedChunk: { x: number, z: number } = { x: 0, z: 0 }
	private readonly invalidChunks = new Set<string>()

	private readonly messageCallbacks = new Map<number, { res: (data: unknown) => void, rej: (error: string) => void }>()
	private messageId = 1

	constructor() {
		window.addEventListener('message', async e => {
			this.onMessage(e.data)
		})

		this.findWidget = document.querySelector('.find-widget') as HTMLElement
		const findTypeSelect = this.findWidget.querySelector('.find-part > .type-select > select') as HTMLSelectElement
		const findNameInput = this.findWidget.querySelector('.find-part > .name-input') as HTMLInputElement
		const findValueInput = this.findWidget.querySelector('.find-part > .value-input') as HTMLInputElement
		findTypeSelect.addEventListener('change', () => {
			findTypeSelect.parentElement!.setAttribute('data-icon', findTypeSelect.value)
			this.doSearch()
		})
		this.findWidget.querySelectorAll('.type-select select').forEach(select => {
			['Any', ...TYPES].filter(e => e !== 'End').forEach(t => {
				const option = document.createElement('option')
				option.value = t
				option.textContent = t.charAt(0).toUpperCase() + t.slice(1).split(/(?=[A-Z])/).join(' ')
				select.append(option)
			})
			select.parentElement!.setAttribute('data-icon', 'Any')
		})
		this.findWidget.querySelector<HTMLElement>('.find-part')?.addEventListener('keyup', evt => {
			if (evt.key !== 'Enter') {
				this.doSearch()
			}
		})
		this.findWidget.querySelector<HTMLElement>('.find-part')?.addEventListener('keydown', evt => {
			if (evt.key === 'Enter') {
				if (evt.shiftKey) {
					this.showMatch(this.searchIndex - 1)
				} else {
					this.showMatch(this.searchIndex + 1)
				}
			}
		})
		this.findWidget.querySelector('.previous-match')?.addEventListener('click', () => {
			this.showMatch(this.searchIndex - 1)
		})
		this.findWidget.querySelector('.next-match')?.addEventListener('click', () => {
			this.showMatch(this.searchIndex + 1)
		})
		this.findWidget.querySelector('.close-widget')?.addEventListener('click', () => {
			this.findWidget.classList.remove('visible')
		})
		this.findWidget.querySelector<HTMLElement>('.replace-part')?.addEventListener('keydown', evt => {
			if (evt.key === 'Enter') {
				if (evt.altKey && evt.ctrlKey) {
					this.doReplaceAll()
				} else {
					this.doReplace()
				}
			}
		})
		const replaceExpand = this.findWidget.querySelector('.replace-expand')
		replaceExpand?.addEventListener('click', () => {
			const expanded = this.findWidget.classList.toggle('expanded')
			replaceExpand?.classList.remove('codicon-chevron-right', 'codicon-chevron-down')
			replaceExpand?.classList.add(expanded ? 'codicon-chevron-down' : 'codicon-chevron-right')
		})
		this.findWidget.querySelector('.replace')?.addEventListener('click', () => {
			this.doReplace()
		})
		this.findWidget.querySelector('.replace-all')?.addEventListener('click', () => {
			this.doReplaceAll()
		})

		document.querySelector('.region-menu .btn')?.addEventListener('click', () => {
			this.inMap = !this.inMap
			this.updateRegionMap()
		})

		document.querySelectorAll('.region-menu input').forEach(el => {
			el.addEventListener('change', () => {
				this.refreshChunk()
			})
			el.addEventListener('keydown', evt => {
				if ((evt as KeyboardEvent).key === 'Enter') {
					this.refreshChunk()
				}
			})
		})

		document.addEventListener('keydown', evt => {
			if (evt.ctrlKey && (evt.code === 'KeyF' || evt.code === 'KeyH')) {
				this.findWidget.classList.add('visible')
				if (this.searchQuery.name) {
					findNameInput.focus()
					findNameInput.setSelectionRange(0, findNameInput.value.length)
				} else {
					findValueInput.focus()
					findValueInput.setSelectionRange(0, findValueInput.value.length)
				}
				this.findWidget.classList.toggle('expanded', evt.code === 'KeyH')
				replaceExpand?.classList.remove('codicon-chevron-right', 'codicon-chevron-down')
				replaceExpand?.classList.add(evt.code === 'KeyH' ? 'codicon-chevron-down' : 'codicon-chevron-right')
				if (this.searchResults && this.searchResults.length > 0) {
					this.searchResults[this.searchIndex].show()
				}
			} else if (evt.key === 'Escape') {
				this.findWidget.classList.remove('visible')
				this.getPanel()?.onSearch?.(null)
			}
		})
		document.addEventListener('contextmenu', evt => {
			evt.preventDefault()
		})

		vscode.postMessage({ type: 'ready' })
	}

	private onMessage(m: ViewMessage) {
		switch (m.type) {
			case 'init':
				console.log(m.body)
				this.type = m.body.type
				this.nbtFile = m.body.type === 'region'
					? NbtRegion.fromJson(m.body.content, (x, z) => this.getChunkData(x, z))
					: NbtFile.fromJson(m.body.content)
				console.log(this.nbtFile)
				this.readOnly = m.body.readOnly
				if (this.nbtFile instanceof NbtRegion.Ref) {
					this.type = 'chunk'
					this.activePanel = 'default'
					this.inMap = true
					this.invalidChunks.clear()
					this.updateRegionMap()
				} else {
					this.setPanel(this.type)
				}
				return

			case 'update':
				try {
					applyEdit(this.nbtFile, m.body)
					const { file: editedFile, edit } = getEditedFile(this.nbtFile, m.body)
					if (editedFile) {
						this.refreshSearch()
						Object.values(this.panels).forEach(p => p.updated = false)
						this.getPanel()?.onUpdate?.(editedFile, edit)
						this.panels[this.activePanel].updated = true
					}
				} catch (e) {
					vscode.postMessage({ type: 'error', body: e.message })
				}
				return

			case 'response':
				const callback = this.messageCallbacks.get(m.requestId ?? 0)
				if (m.body) {
					callback?.res(m.body)
				} else {
					callback?.rej(m.error ?? 'Unknown response')
				}
				return

			default:
				this.panels[this.type].editor().onMessage?.(m)
		}
	}

	private async sendMessageWithResponse(message: EditorMessage) {
		const requestId = this.messageId++
		const promise = new Promise((res, rej) => {
			this.messageCallbacks.set(requestId, { res, rej })
		})
		vscode.postMessage({ ...message, requestId })
		return promise
	}

	private async getChunkData(x: number, z: number) {
		const data = await this.sendMessageWithResponse({ type: 'getChunkData', body: { x, z } })
		const chunk = NbtFile.fromJson(data as JsonValue)
		return chunk
	}

	private getPanel(): EditorPanel | undefined {
		return this.panels[this.activePanel]?.editor()
	}

	private setPanel(panel: string) {
		root.innerHTML = '<div class="spinner"></div>'
		this.getPanel()?.hide?.()
		this.activePanel = panel
		const editorPanel = this.getPanel()!
		this.setPanelMenu(editorPanel)
		setTimeout(async () => {
			if (!this.panels[panel].updated) {
				try {
					if (this.nbtFile instanceof NbtRegion.Ref) {
						const chunk = this.nbtFile.findChunk(this.selectedChunk.x, this.selectedChunk.z)
						const file = chunk?.getFile()
						if (chunk && file) {
							editorPanel.onInit?.(file)
						}
					} else {
						editorPanel.onInit?.(this.nbtFile)
					}
				} catch (e) {
					if (e instanceof Error) {
						console.error(e)
						const div = document.createElement('div')
						div.classList.add('nbt-content', 'error')
						div.textContent = e.message
						root.innerHTML = ''
						root.append(div)
						return
					}
				}
				this.panels[panel].updated = true
			}
			root.innerHTML = ''
			editorPanel?.reveal?.()
		})
	}

	private setPanelMenu(panel: EditorPanel) {
		const el = document.querySelector('.panel-menu')!
		el.innerHTML = ''
		const btnGroup = document.createElement('div')
		btnGroup.classList.add('btn-group')
		el.append(btnGroup)
		this.panels[this.type].options?.forEach((p: string) => {
			const button = document.createElement('div')
			btnGroup.append(button)
			button.classList.add('btn')
			button.textContent = locale(`panel.${p}`)
			if (p === this.activePanel) {
				button.classList.add('active')
			} else {
				button.addEventListener('click', () => this.setPanel(p))
			}
		})
		const menuPanels = panel.menu?.() ?? []
		if (menuPanels.length > 0) {
			el.insertAdjacentHTML('beforeend', '<div class="menu-spacer"></div>')
			menuPanels.forEach(e => el.append(e))
		}
	}

	private updateRegionMap() {
		if (!(this.nbtFile instanceof NbtRegion.Ref)) {
			return
		}
		document.querySelector('.region-menu .btn')?.classList.toggle('active', this.inMap)
		document.querySelector('.panel-menu')?.classList.toggle('hidden', this.inMap)
		document.querySelector('.nbt-editor')?.classList.toggle('hidden', this.inMap)
		
		document.querySelector('.region-map')?.remove()
		if (this.inMap) {
			const map = document.createElement('div')
			map.classList.add('region-map')
			for (let z = 0; z < 32; z += 1) {
				for (let x = 0; x < 32; x += 1) {
					const chunk = this.nbtFile.findChunk(x, z)
					const cell = document.createElement('div')
					cell.classList.add('region-map-chunk')
					cell.textContent = `${x} ${z}`
					cell.classList.toggle('empty', chunk === undefined)
					cell.classList.toggle('loaded', chunk?.isResolved() ?? false)
					cell.classList.toggle('invalid', this.invalidChunks.has(`${x} ${z}`))
					if (chunk !== undefined) {
						cell.addEventListener('click', () => {
							this.selectChunk(x, z)
						})
					}
					cell.setAttribute('data-pos', `${x} ${z}`)
					map.append(cell)
				}
			}
			document.body.append(map)
		}
	}

	private refreshChunk() {
		if (!(this.nbtFile instanceof NbtRegion.Ref)) {
			return
		}
		const x = getInt(document.getElementById('chunk-x')) ?? 0
		const z = getInt(document.getElementById('chunk-z')) ?? 0
		this.selectChunk(x, z)
	}

	private async selectChunk(x: number, z: number) {
		if (!(this.nbtFile instanceof NbtRegion.Ref)) {
			return
		}
		x = Math.max(0, Math.min(31, Math.floor(x)))
		z = Math.max(0, Math.min(31, Math.floor(z)));
		(document.getElementById('chunk-x') as HTMLInputElement).value = `${x}`;
		(document.getElementById('chunk-z') as HTMLInputElement).value = `${z}`
		if (this.selectedChunk.x === x && this.selectedChunk.z === z) {
			this.inMap = false
			this.updateRegionMap()
			return
		}
		this.selectedChunk = { x, z }
		const chunk = this.nbtFile.findChunk(x, z)
		if (!chunk) {
			this.invalidChunks.add(`${x} ${z}`)
			document.querySelector('.region-menu')?.classList.add('invalid')
			this.updateRegionMap()
			return
		}
		Object.values(this.panels).forEach(p => p.updated = false)
		try {
			await chunk.getFileAsync()
		} catch (e) {
			this.invalidChunks.add(`${x} ${z}`)
			document.querySelector('.region-menu')?.classList.add('invalid')
			this.updateRegionMap()
			return
		}
		document.querySelector('.region-menu')?.classList.remove('invalid')
		this.setPanel(this.activePanel)
		this.inMap = false
		this.updateRegionMap()
		this.setPanel(this.activePanel)
	}

	private doSearch() {
		const query = this.getQuery(this.findWidget.querySelector('.find-part'))
		if (['type', 'name', 'value'].every(e => this.searchQuery?.[e] === query[e])) {
			return
		}
		this.searchQuery = query
		this.searchIndex = 0
		this.refreshSearch()
	}

	private refreshSearch() {
		const editorPanel = this.getPanel()
		if (editorPanel?.onSearch && (this.searchQuery.name || this.searchQuery.value || this.searchQuery.type)) {
			this.searchResults = editorPanel.onSearch(this.searchQuery)
		} else {
			this.searchResults = null
		}
		if (this.lastReplace && this.searchResults?.[this.searchIndex]?.path?.equals(this.lastReplace)) {
			this.searchIndex += 1
			this.lastReplace = null
		}
		this.showMatch(this.searchIndex)
	}

	private doReplace() {
		if (this.searchResults === null || this.searchResults.length === 0) return
		const query = this.getQuery(this.findWidget.querySelector('.replace-part'))
		if (query.name || query.value || query.type) {
			const result = this.searchResults[this.searchIndex]
			this.lastReplace = result.path
			this.makeEdit(result.replace(query))
		}
		console.log('Done replace!')
	}

	private doReplaceAll() {
		if (!this.searchResults) return
		const query = this.getQuery(this.findWidget.querySelector('.replace-part'))
		if (query.name || query.value || query.type) {
			const edits = this.searchResults.map(r => r.replace(query))
			this.makeEdit({ type: 'composite', edits })
		}
	}

	private getQuery(element: Element | null): SearchQuery {
		const typeQuery = (element?.querySelector('.type-select > select') as HTMLSelectElement).value
		const nameQuery = (element?.querySelector('.name-input') as HTMLInputElement).value
		const valueQuery = (element?.querySelector('.value-input') as HTMLInputElement).value
		return {
			type: typeQuery === 'Any' ? undefined : TYPES.indexOf(typeQuery as any),
			name: nameQuery || undefined,
			value: valueQuery || undefined,
		}
	}

	private showMatch(index: number) {
		if (this.searchResults === null || this.searchResults.length === 0) {
			this.findWidget.querySelector('.matches')!.textContent = 'No results'
			this.getPanel()?.onSearch?.(null)
		} else {
			const matches = this.searchResults.length
			this.searchIndex = (index % matches + matches) % matches
			this.findWidget.querySelector('.matches')!.textContent = `${this.searchIndex + 1} of ${matches}`
			this.searchResults[this.searchIndex].show()
		}
		this.findWidget.classList.toggle('no-results', this.searchResults !== null && this.searchResults.length === 0)
		this.findWidget.querySelectorAll('.previous-match, .next-match').forEach(e =>
			e.classList.toggle('disabled', this.searchResults === null || this.searchResults.length === 0))
	}

	private makeEdit(edit: NbtEdit) {
		if (this.readOnly) return
		if (this.nbtFile instanceof NbtRegion.Ref) {
			edit = { type: 'chunk', ...this.selectedChunk, edit }
		}
		console.warn('Edit', edit)
		vscode.postMessage({ type: 'edit', body: edit })
	}
}

new Editor()
