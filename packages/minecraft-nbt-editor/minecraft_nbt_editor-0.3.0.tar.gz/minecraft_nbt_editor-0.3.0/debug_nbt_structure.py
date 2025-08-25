#!/usr/bin/env python3
"""
調試 NBT 結構破壞問題
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

def create_test_level_dat():
    """創建測試用的 level.dat 檔案"""
    root = NbtCompound({
        'Data': NbtCompound({
            'LevelName': NbtString("Test World"),
            'GameType': NbtInt(0),
            'DataVersion': NbtInt(1),
            'Time': NbtInt(0),
            'DayTime': NbtInt(0),
            'SpawnX': NbtInt(0),
            'SpawnY': NbtInt(64),
            'SpawnZ': NbtInt(0),
            'SizeOnDisk': NbtInt(0),
            'RandomSeed': NbtInt(12345)
        })
    })

    nbt_file = NbtFile(
        root=root,
        compression='none',
        little_endian=True,
        bedrock_header=True
    )

    return nbt_file

def debug_nbt_corruption():
    """調試 NBT 結構破壞問題"""
    print("🔍 調試 NBT 結構破壞問題...")
    
    # 創建臨時檔案
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "level.dat")
    
    try:
        # 創建測試檔案
        nbt_file = create_test_level_dat()
        write_nbt_file(test_file, nbt_file)
        
        print(f"✅ 創建測試檔案: {test_file}")
        print(f"   檔案大小: {os.path.getsize(test_file)} bytes")
        
        # 檢查原始檔案結構
        print("\n📋 原始檔案結構:")
        original_file = read_nbt_file(test_file)
        print(f"   根標籤類型: {type(original_file.root).__name__}")
        print(f"   根標籤內容: {list(original_file.root.keys())}")
        print(f"   壓縮: {original_file.compression}")
        print(f"   字節序: {'little-endian' if original_file.little_endian else 'big-endian'}")
        print(f"   Bedrock 頭部: {original_file.bedrock_header}")
        
        # 測試簡單的編輯操作
        print("\n🔧 測試簡單編輯操作...")
        
        # 測試 1: 設置現有標籤
        print("\n   測試 1: 設置現有標籤 Data.LevelName = 'Modified World'")
        try:
            edit1 = NbtSetEdit("Data.LevelName", NbtString("Modified World"))
            print(f"    創建編輯操作: {edit1}")
            
            # 檢查編輯前的根標籤類型
            print(f"    編輯前根標籤類型: {type(original_file.root).__name__}")
            
            apply_edit_tag(original_file.root, edit1)
            print(f"    ✅ 編輯操作成功")
            
            # 檢查編輯後的根標籤類型
            print(f"    編輯後根標籤類型: {type(original_file.root).__name__}")
            
            # 驗證值是否被設置
            if 'Data' in original_file.root:
                data = original_file.root['Data']
                if 'LevelName' in data:
                    level_name = data['LevelName']
                    print(f"    ✅ 驗證成功: LevelName = {level_name}")
                else:
                    print(f"    ❌ 驗證失敗: LevelName 不在 Data 中")
            else:
                print(f"    ❌ 驗證失敗: Data 不在根標籤中")
                
        except Exception as e:
            print(f"    ❌ 測試 1 失敗: {e}")
            import traceback
            traceback.print_exc()
        
        # 測試 2: 添加新標籤
        print("\n   測試 2: 添加新標籤 experiments.data_driven_biomes = 1")
        try:
            edit2 = NbtSetEdit("experiments.data_driven_biomes", NbtByte(1))
            print(f"    創建編輯操作: {edit2}")
            
            # 檢查編輯前的根標籤類型
            print(f"    編輯前根標籤類型: {type(original_file.root).__name__}")
            
            apply_edit_tag(original_file.root, edit2)
            print(f"    ✅ 編輯操作成功")
            
            # 檢查編輯後的根標籤類型
            print(f"    編輯後根標籤類型: {type(original_file.root).__name__}")
            
            # 驗證值是否被設置
            if 'experiments' in original_file.root:
                experiments = original_file.root['experiments']
                if 'data_driven_biomes' in experiments:
                    value = experiments['data_driven_biomes']
                    print(f"    ✅ 驗證成功: data_driven_biomes = {value}")
                else:
                    print(f"    ❌ 驗證失敗: data_driven_biomes 不在 experiments 中")
            else:
                print(f"    ❌ 驗證失敗: experiments 不在根標籤中")
                
        except Exception as e:
            print(f"    ❌ 測試 2 失敗: {e}")
            import traceback
            traceback.print_exc()
        
        # 檢查最終結構
        print(f"\n📋 最終檔案結構:")
        print(f"   根標籤類型: {type(original_file.root).__name__}")
        print(f"   根標籤內容: {list(original_file.root.keys())}")
        
        if 'Data' in original_file.root:
            data = original_file.root['Data']
            print(f"   Data 內容: {list(data.keys())}")
        
        if 'experiments' in original_file.root:
            experiments = original_file.root['experiments']
            print(f"   experiments 內容: {list(experiments.keys())}")
        
        # 寫入檔案
        print(f"\n💾 寫入檔案...")
        write_nbt_file(test_file, original_file)
        print(f"✅ 檔案已保存")
        
        # 重新讀取檔案驗證
        print(f"\n🔍 重新讀取檔案驗證...")
        try:
            updated_file = read_nbt_file(test_file)
            print(f"   重新讀取成功")
            print(f"   根標籤類型: {type(updated_file.root).__name__}")
            print(f"   根標籤內容: {list(updated_file.root.keys())}")
            
            # 檢查是否仍然可以被 ref 讀取
            print(f"\n🔍 檢查 NBT 結構完整性...")
            if isinstance(updated_file.root, NbtCompound):
                print(f"   ✅ 根標籤是 NbtCompound 類型")
                print(f"   ✅ 結構完整，應該可以被 ref 讀取")
            else:
                print(f"   ❌ 根標籤類型錯誤: {type(updated_file.root).__name__}")
                print(f"   ❌ 這就是 'Top tag should be a compound' 錯誤的原因！")
                
        except Exception as e:
            print(f"   ❌ 重新讀取失敗: {e}")
            import traceback
            traceback.print_exc()
        
        # 檢查檔案大小變化
        new_size = os.path.getsize(test_file)
        print(f"\n📊 檔案大小: {new_size} bytes")
        
    except Exception as e:
        print(f"❌ 調試失敗: {e}")
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
    print("🚀 Minecraft NBT Editor - NBT 結構破壞調試")
    print("=" * 70)
    
    debug_nbt_corruption()
    
    print("\n" + "=" * 70)
    print("✨ 調試完成！")
