#!/usr/bin/env python3
"""
測試修復後的 set 命令
"""

import sys
import os
import tempfile
import shutil

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.nbt_types import NbtCompound, NbtInt, NbtString, NbtByte
from core.nbt_file import NbtFile, write_nbt_file, read_nbt_file
from core.operations import NbtSetEdit, apply_edit_tag

def test_set_command():
    """測試 set 命令"""
    print("🧪 測試 set 命令...")
    
    # 創建臨時檔案
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.dat")
    
    try:
        # 創建測試檔案
        root = NbtCompound({
            'Data': NbtCompound({
                'LevelName': NbtString("Test World"),
                'GameType': NbtInt(0)
            })
        })
        
        nbt_file = NbtFile(
            root=root,
            compression='gzip',
            little_endian=True,
            bedrock_header=True
        )
        
        write_nbt_file(test_file, nbt_file)
        print(f"✅ 創建測試檔案: {test_file}")
        
        # 檢查原始結構
        print("\n📋 原始檔案結構:")
        original_file = read_nbt_file(test_file)
        print(f"   根標籤類型: {type(original_file.root).__name__}")
        print(f"   根標籤內容: {list(original_file.root.keys())}")
        if 'Data' in original_file.root:
            data = original_file.root['Data']
            print(f"   Data 內容: {list(data.keys())}")
        
        # 測試 set 命令 - 設置新標籤
        print("\n🔧 測試設置新標籤: experiments.data_driven_biomes = 1")
        
        # 創建編輯操作
        edit = NbtSetEdit("experiments.data_driven_biomes", NbtByte(1))
        apply_edit_tag(original_file.root, edit)
        
        print("✅ 編輯操作已應用")
        
        # 檢查更新後的結構
        print("\n📋 更新後結構:")
        print(f"   根標籤類型: {type(original_file.root).__name__}")
        print(f"   根標籤內容: {list(original_file.root.keys())}")
        
        if 'experiments' in original_file.root:
            experiments = original_file.root['experiments']
            print(f"   experiments 類型: {type(experiments).__name__}")
            if isinstance(experiments, NbtCompound):
                print(f"   experiments 內容: {list(experiments.keys())}")
                if 'data_driven_biomes' in experiments:
                    value = experiments['data_driven_biomes']
                    print(f"   data_driven_biomes: {value} (類型: {type(value).__name__})")
        
        # 寫入檔案
        write_nbt_file(test_file, original_file)
        print("✅ 檔案已保存")
        
        # 重新讀取檔案驗證
        print("\n🔍 重新讀取檔案驗證...")
        updated_file = read_nbt_file(test_file)
        print(f"   根標籤類型: {type(updated_file.root).__name__}")
        print(f"   根標籤內容: {list(updated_file.root.keys())}")
        
        if 'experiments' in updated_file.root:
            experiments = updated_file.root['experiments']
            print(f"   experiments 類型: {type(experiments).__name__}")
            if isinstance(experiments, NbtCompound):
                print(f"   experiments 內容: {list(experiments.keys())}")
        
        # 檢查檔案大小
        file_size = os.path.getsize(test_file)
        print(f"\n📊 檔案大小: {file_size:,} bytes")
        
        print("✅ 所有測試通過！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理臨時檔案
        try:
            shutil.rmtree(temp_dir)
            print(f"\n🧹 已清理臨時檔案: {temp_dir}")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Minecraft NBT Editor - Set Command 測試")
    print("=" * 60)
    
    test_set_command()
    
    print("\n" + "=" * 60)
    print("✨ 測試完成！")
