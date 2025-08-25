#!/usr/bin/env python3
"""
版本更新腳本 - 自動更新所有文件中的版本號
"""

import os
import re
import sys
from pathlib import Path

def update_version_in_file(file_path: str, old_version: str, new_version: str) -> bool:
    """更新文件中的版本號"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替換版本號
        updated_content = content.replace(old_version, new_version)
        
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏭️  無需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失敗 {file_path}: {e}")
        return False

def update_version_in_pyproject_toml(file_path: str, new_version: str) -> bool:
    """更新 pyproject.toml 中的版本號"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正則表達式更新版本號
        pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        updated_content = re.sub(pattern, f'version = "{new_version}"', content)
        
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏭️  無需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失敗 {file_path}: {e}")
        return False

def update_version_in_setup_py(file_path: str, new_version: str) -> bool:
    """更新 setup.py 中的版本號"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正則表達式更新版本號
        pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        updated_content = re.sub(pattern, f'version="{new_version}"', content)
        
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏭️  無需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失敗 {file_path}: {e}")
        return False

def update_version_in_changelog(file_path: str, old_version: str, new_version: str) -> bool:
    """更新 CHANGELOG.md 中的版本號"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替換版本號
        updated_content = content.replace(f'## [{old_version}]', f'## [{new_version}]')
        
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏭️  無需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失敗 {file_path}: {e}")
        return False

def main():
    """主函數"""
    if len(sys.argv) != 3:
        print("用法: python update_version.py <舊版本> <新版本>")
        print("例如: python update_version.py 0.2.0 0.2.1")
        sys.exit(1)
    
    old_version = sys.argv[1]
    new_version = sys.argv[2]
    
    print(f"🚀 版本更新: {old_version} → {new_version}")
    print("=" * 50)
    
    # 需要更新的文件列表
    files_to_update = [
        # Python 文件
        "src/__init__.py",
        "src/cli/main.py",
        "minecraft_nbt.py",
        
        # 配置文件
        "pyproject.toml",  # 添加這個
        "setup.py",
        
        # 腳本文件
        "build_release.py",
        "Makefile",
        
        # 文檔文件
        "CHANGELOG.md"
    ]
    
    updated_count = 0
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            if file_path == "pyproject.toml":
                success = update_version_in_pyproject_toml(file_path, new_version)
            elif file_path == "setup.py":
                success = update_version_in_setup_py(file_path, new_version)
            elif file_path == "CHANGELOG.md":
                success = update_version_in_changelog(file_path, old_version, new_version)
            else:
                success = update_version_in_file(file_path, old_version, new_version)
            
            if success:
                updated_count += 1
        else:
            print(f"⚠️  文件不存在: {file_path}")
    
    print("\n" + "=" * 50)
    print(f"✨ 版本更新完成！")
    print(f"📊 更新了 {updated_count} 個文件")
    
    print(f"\n📋 下一步:")
    print(f"   1. 檢查更新結果: git diff")
    print(f"   2. 提交更改: git add . && git commit -m 'Bump version to {new_version}'")
    print(f"   3. 創建標籤: git tag -a v{new_version} -m 'Release {new_version}'")
    print(f"   4. 推送更改: git push origin main && git push origin v{new_version}")

if __name__ == "__main__":
    main()
