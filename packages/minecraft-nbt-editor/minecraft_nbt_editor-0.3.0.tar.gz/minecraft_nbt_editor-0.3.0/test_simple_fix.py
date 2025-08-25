#!/usr/bin/env python3
"""
簡單測試修復後的編輯操作
"""

import sys
import os

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.nbt_types import NbtCompound, NbtInt, NbtString, NbtByte
from core.nbt_file import NbtFile
from core.operations import NbtSetEdit, apply_edit_tag

def test_simple_edit():
    """測試簡單的編輯操作"""
    print("🧪 測試簡單的編輯操作...")
    
    # 創建一個簡單的 NBT 結構
    root = NbtCompound({
        'Data': NbtCompound({
            'LevelName': NbtString("Test World")
        })
    })
    
    print(f"原始根標籤類型: {type(root).__name__}")
    print(f"原始內容: {list(root.keys())}")
    
    # 測試添加 experiments 標籤
    print("\n🔧 添加 experiments 標籤...")
    experiments_tag = NbtCompound({})
    edit = NbtSetEdit("experiments", experiments_tag)
    
    try:
        apply_edit_tag(root, edit)
        print("✅ 成功添加 experiments 標籤")
        print(f"更新後內容: {list(root.keys())}")
        
        # 測試添加實驗功能
        print("\n🔧 添加實驗功能...")
        exp_edit = NbtSetEdit("experiments.data_driven_biomes", NbtByte(1))
        apply_edit_tag(root, edit)
        print("✅ 成功添加實驗功能")
        
        # 檢查最終結構
        print(f"\n📋 最終結構:")
        print(f"根標籤類型: {type(root).__name__}")
        print(f"根標籤內容: {list(root.keys())}")
        
        if 'experiments' in root:
            experiments = root['experiments']
            print(f"experiments 類型: {type(experiments).__name__}")
            if isinstance(experiments, NbtCompound):
                print(f"experiments 內容: {list(experiments.keys())}")
        
        print("✅ 所有測試通過！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 簡單修復測試")
    print("=" * 40)
    
    test_simple_edit()
    
    print("\n" + "=" * 40)
    print("✨ 測試完成！")
