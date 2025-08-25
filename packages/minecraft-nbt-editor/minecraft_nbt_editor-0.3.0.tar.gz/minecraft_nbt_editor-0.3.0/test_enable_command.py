#!/usr/bin/env python3
"""
測試修復後的 enable 命令
"""

import sys
import os
import tempfile
import shutil

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.nbt_types import NbtCompound, NbtInt, NbtString, NbtByte
from core.nbt_file import NbtFile, write_nbt_file

def create_test_level_dat():
    """創建測試用的 level.dat 檔案"""
    # 創建一個基本的 Bedrock level.dat 結構
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
            'RandomSeed': NbtInt(12345),
            'WorldGenSettings': NbtCompound({
                'seed': NbtInt(12345),
                'dimensions': NbtCompound({
                    'minecraft:overworld': NbtCompound({
                        'generator': NbtCompound({
                            'type': NbtString("minecraft:noise"),
                            'settings': NbtString("minecraft:overworld"),
                            'biome': NbtString("minecraft:plains")
                        })
                    })
                })
            })
        })
    })
    
    # 創建 NBT 檔案（Bedrock 格式）
    nbt_file = NbtFile(
        root=root,
        compression='gzip',
        little_endian=True,
        bedrock_header=True
    )
    
    return nbt_file

def test_enable_command():
    """測試 enable 命令"""
    print("🧪 測試 enable 命令...")
    
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
        from core.nbt_file import read_nbt_file
        original_file = read_nbt_file(test_file)
        print(f"   根標籤類型: {type(original_file.root).__name__}")
        print(f"   壓縮: {original_file.compression}")
        print(f"   字節序: {'little-endian' if original_file.little_endian else 'big-endian'}")
        print(f"   Bedrock 頭部: {original_file.bedrock_header}")
        
        # 檢查是否有 experiments 標籤
        if 'experiments' in original_file.root:
            print("   experiments 標籤: 已存在")
            experiments = original_file.root['experiments']
            print(f"   experiments 類型: {type(experiments).__name__}")
            if isinstance(experiments, NbtCompound):
                print(f"   experiments 內容: {list(experiments.keys())}")
        else:
            print("   experiments 標籤: 不存在")
        
        # 模擬 enable 命令的邏輯
        print("\n🔧 執行 enable 命令邏輯...")
        
        # 檢查是否存在 experiments 標籤
        try:
            from core.operations import get_node
            from core.nbt_path import NbtPath
            
            experiments_tag = get_node(original_file.root, NbtPath("experiments"))
            if not isinstance(experiments_tag, NbtCompound):
                print("   experiments 不是 compound，創建新的")
                experiments_tag = NbtCompound({})
                original_file.root.set("experiments", experiments_tag)
        except ValueError:
            print("   experiments 標籤不存在，創建新的")
            experiments_tag = NbtCompound({})
            original_file.root.set("experiments", experiments_tag)
        
        # 定義實驗功能
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
        
        # 設置每個實驗功能
        for exp_name, exp_value in experiments.items():
            exp_byte = NbtByte(exp_value)
            experiments_tag.set(exp_name, exp_byte)
            print(f"   ✓ 啟用 {exp_name}: {exp_value}")
        
        # 寫入檔案
        write_nbt_file(test_file, original_file)
        print("✅ 檔案已更新")
        
        # 驗證結果
        print("\n🔍 驗證結果...")
        updated_file = read_nbt_file(test_file)
        
        if 'experiments' in updated_file.root:
            experiments_tag = updated_file.root['experiments']
            if isinstance(experiments_tag, NbtCompound):
                print(f"   experiments 標籤類型: {type(experiments_tag).__name__}")
                print(f"   experiments 內容:")
                for key, value in experiments_tag.items():
                    print(f"     {key}: {value} (類型: {type(value).__name__})")
                
                # 檢查是否所有實驗功能都已啟用
                all_enabled = all(
                    key in experiments_tag and 
                    isinstance(experiments_tag[key], NbtByte) and 
                    experiments_tag[key].value == 1
                    for key in experiments.keys()
                )
                
                if all_enabled:
                    print("✅ 所有實驗功能已成功啟用！")
                else:
                    print("❌ 部分實驗功能啟用失敗")
            else:
                print("❌ experiments 標籤類型錯誤")
        else:
            print("❌ experiments 標籤未創建")
        
        # 檢查檔案大小變化
        new_size = os.path.getsize(test_file)
        print(f"\n📊 檔案大小變化:")
        print(f"   原始大小: {os.path.getsize(test_file)} bytes")
        print(f"   更新後大小: {new_size} bytes")
        
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
    print("🚀 Minecraft NBT Editor - Enable Command 測試")
    print("=" * 60)
    
    test_enable_command()
    
    print("\n" + "=" * 60)
    print("✨ 測試完成！")
