#!/usr/bin/env python3
"""
調試 enable 命令的腳本
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

def debug_enable_command():
    """調試 enable 命令"""
    print("🔍 調試 enable 命令...")
    
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
        
        # 定義所有實驗功能
        experiments = {
            "data_driven_biomes": 1,
            "experimental_creator_cameras": 1,
            "experiments_ever_used": 1,
            "gametest": 1,
            "jigsaw_structures": 1,
            "saved_with_toggled_experiments": 1,
            "upcoming_creator_features": 1,
            "villager_trades_rebalance": 1,
            "y_2025_drop_3": 1
        }
        
        print(f"\n🔧 開始設置實驗功能...")
        
        # 逐個設置實驗功能，並檢查每一步
        for i, (exp_name, exp_value) in enumerate(experiments.items(), 1):
            print(f"\n  步驟 {i}: 設置 {exp_name} = {exp_value}")
            
            # 創建編輯操作
            edit = NbtSetEdit(f"experiments.{exp_name}", NbtByte(exp_value))
            print(f"    創建編輯操作: {edit}")
            
            try:
                # 應用編輯
                apply_edit_tag(original_file.root, edit)
                print(f"    ✅ 編輯操作成功")
                
                # 檢查是否真的被設置了
                if 'experiments' in original_file.root:
                    experiments_tag = original_file.root['experiments']
                    if isinstance(experiments_tag, NbtCompound):
                        if exp_name in experiments_tag:
                            actual_value = experiments_tag[exp_name]
                            print(f"    ✅ 驗證成功: {exp_name} = {actual_value} (類型: {type(actual_value).__name__})")
                        else:
                            print(f"    ❌ 驗證失敗: {exp_name} 不在 experiments 中")
                    else:
                        print(f"    ❌ experiments 不是 compound 類型")
                else:
                    print(f"    ❌ experiments 標籤不存在")
                    
            except Exception as e:
                print(f"    ❌ 編輯操作失敗: {e}")
                import traceback
                traceback.print_exc()
        
        # 檢查最終結構
        print(f"\n📋 最終檔案結構:")
        print(f"   根標籤類型: {type(original_file.root).__name__}")
        print(f"   根標籤內容: {list(original_file.root.keys())}")
        
        if 'experiments' in original_file.root:
            experiments_tag = original_file.root['experiments']
            print(f"   experiments 類型: {type(experiments_tag).__name__}")
            if isinstance(experiments_tag, NbtCompound):
                print(f"   experiments 內容:")
                for key, value in experiments_tag.items():
                    print(f"     {key}: {value} (類型: {type(value).__name__})")
                
                # 統計成功設置的實驗功能
                successful_experiments = [
                    key for key in experiments.keys() 
                    if key in experiments_tag and 
                    isinstance(experiments_tag[key], NbtByte) and 
                    experiments_tag[key].value == 1
                ]
                
                print(f"\n📊 統計結果:")
                print(f"   總共嘗試設置: {len(experiments)} 個實驗功能")
                print(f"   成功設置: {len(successful_experiments)} 個")
                print(f"   失敗: {len(experiments) - len(successful_experiments)} 個")
                
                if successful_experiments:
                    print(f"   成功的實驗功能: {', '.join(successful_experiments)}")
                
                failed_experiments = [key for key in experiments.keys() if key not in successful_experiments]
                if failed_experiments:
                    print(f"   失敗的實驗功能: {', '.join(failed_experiments)}")
        
        # 寫入檔案
        print(f"\n💾 寫入檔案...")
        write_nbt_file(test_file, original_file)
        print(f"✅ 檔案已保存")
        
        # 重新讀取檔案驗證
        print(f"\n🔍 重新讀取檔案驗證...")
        updated_file = read_nbt_file(test_file)
        
        if 'experiments' in updated_file.root:
            experiments_tag = updated_file.root['experiments']
            if isinstance(experiments_tag, NbtCompound):
                print(f"   重新讀取後 experiments 內容:")
                for key, value in experiments_tag.items():
                    print(f"     {key}: {value} (類型: {type(value).__name__})")
        
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
    print("🚀 Minecraft NBT Editor - Enable Command 調試")
    print("=" * 70)
    
    debug_enable_command()
    
    print("\n" + "=" * 70)
    print("✨ 調試完成！")
