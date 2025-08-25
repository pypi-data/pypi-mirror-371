#!/usr/bin/env python3
"""
測試真實的 level.dat 文件
"""

import sys
import os
import shutil

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.nbt_file import read_nbt_file, write_nbt_file
from core.operations import NbtSetEdit, apply_edit_tag

def test_real_level_dat(file_path: str):
    """測試真實的 level.dat 文件"""
    print(f"🔍 測試真實文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        # 創建備份
        backup_path = f"{file_path}.backup"
        shutil.copy2(file_path, backup_path)
        print(f"✅ 創建備份: {backup_path}")
        
        # 讀取原始文件
        print(f"\n📖 讀取原始文件...")
        original_file = read_nbt_file(file_path)
        print(f"   根標籤類型: {type(original_file.root).__name__}")
        print(f"   根標籤內容: {list(original_file.root.keys())}")
        print(f"   壓縮: {original_file.compression}")
        print(f"   字節序: {'little-endian' if original_file.little_endian else 'big-endian'}")
        print(f"   Bedrock 頭部: {original_file.bedrock_header}")
        
        # 檢查文件大小
        original_size = os.path.getsize(file_path)
        print(f"   原始文件大小: {original_size:,} bytes")
        
        # 測試簡單編輯
        print(f"\n🔧 測試簡單編輯...")
        
        # 檢查是否有 Data 標籤
        if 'Data' in original_file.root:
            data = original_file.root['Data']
            if isinstance(data, type(original_file.root)):  # 檢查是否為 NbtCompound
                print(f"   ✅ Data 標籤存在且是 compound 類型")
                
                # 嘗試設置一個簡單的值
                try:
                    edit = NbtSetEdit("Data.LevelName", data.get('LevelName', 'Unknown'))
                    print(f"   創建編輯操作: {edit}")
                    
                    # 檢查編輯前的根標籤類型
                    print(f"   編輯前根標籤類型: {type(original_file.root).__name__}")
                    
                    apply_edit_tag(original_file.root, edit)
                    print(f"   ✅ 編輯操作成功")
                    
                    # 檢查編輯後的根標籤類型
                    print(f"   編輯後根標籤類型: {type(original_file.root).__name__}")
                    
                except Exception as e:
                    print(f"   ❌ 編輯操作失敗: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"   ❌ Data 標籤類型錯誤: {type(data).__name__}")
        else:
            print(f"   ⚠️  Data 標籤不存在")
        
        # 檢查最終結構
        print(f"\n📋 最終文件結構:")
        print(f"   根標籤類型: {type(original_file.root).__name__}")
        print(f"   根標籤內容: {list(original_file.root.keys())}")
        
        # 寫入文件
        print(f"\n💾 寫入文件...")
        write_nbt_file(file_path, original_file)
        print(f"✅ 文件已保存")
        
        # 檢查文件大小變化
        new_size = os.path.getsize(file_path)
        print(f"   新文件大小: {new_size:,} bytes")
        print(f"   大小變化: {new_size - original_size:+,} bytes")
        
        # 重新讀取文件驗證
        print(f"\n🔍 重新讀取文件驗證...")
        try:
            updated_file = read_nbt_file(file_path)
            print(f"   ✅ 重新讀取成功")
            print(f"   根標籤類型: {type(updated_file.root).__name__}")
            print(f"   根標籤內容: {list(updated_file.root.keys())}")
            
            # 檢查是否仍然可以被 ref 讀取
            print(f"\n🔍 檢查 NBT 結構完整性...")
            if isinstance(updated_file.root, type(original_file.root)):
                print(f"   ✅ 根標籤類型正確: {type(updated_file.root).__name__}")
                print(f"   ✅ 結構完整，應該可以被 ref 讀取")
            else:
                print(f"   ❌ 根標籤類型錯誤: {type(updated_file.root).__name__}")
                print(f"   ❌ 這就是 'Top tag should be a compound' 錯誤的原因！")
                
        except Exception as e:
            print(f"   ❌ 重新讀取失敗: {e}")
            import traceback
            traceback.print_exc()
        
        # 恢復備份
        print(f"\n🔄 恢復備份...")
        shutil.copy2(backup_path, file_path)
        print(f"✅ 文件已恢復")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    if len(sys.argv) != 2:
        print("用法: python test_real_file.py <level.dat文件路徑>")
        print("例如: python test_real_file.py /path/to/level.dat")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print("🚀 Minecraft NBT Editor - 真實文件測試")
    print("=" * 60)
    
    test_real_level_dat(file_path)
    
    print("\n" + "=" * 60)
    print("✨ 測試完成！")

if __name__ == "__main__":
    main()
