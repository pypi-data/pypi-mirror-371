#!/usr/bin/env python3
"""
版本一致性檢查腳本
"""

import os
import re
import sys
from pathlib import Path

def extract_version_from_file(file_path: str) -> str:
    """從文件中提取版本號"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 不同的版本號格式
        patterns = [
            r'version\s*=\s*["\']([^"\']+)["\']',  # pyproject.toml, setup.py
            r'@click\.version_option\(version=["\']([^"\']+)["\']',  # CLI files
            r'__version__\s*=\s*["\']([^"\']+)["\']',  # __init__.py
            r'## \[([^\]]+)\]',  # CHANGELOG.md
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return "未找到"
        
    except Exception as e:
        return f"讀取失敗: {e}"

def main():
    """主函數"""
    print("🔍 版本一致性檢查")
    print("=" * 50)
    
    # 需要檢查的文件列表
    files_to_check = [
        ("pyproject.toml", "項目配置"),
        ("src/__init__.py", "包版本"),
        ("src/cli/main.py", "CLI 版本"),
        ("minecraft_nbt.py", "舊版 CLI"),
        ("setup.py", "傳統配置"),
        ("CHANGELOG.md", "更新日誌"),
    ]
    
    versions = {}
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            version = extract_version_from_file(file_path)
            versions[file_path] = version
            status = "✅" if version != "未找到" else "❌"
            print(f"{status} {description:12} ({file_path:20}): {version}")
        else:
            print(f"⚠️  {description:12} ({file_path:20}): 文件不存在")
    
    print("\n" + "=" * 50)
    
    # 檢查版本一致性
    found_versions = [v for v in versions.values() if v != "未找到" and not v.startswith("讀取失敗")]
    
    if found_versions:
        unique_versions = set(found_versions)
        if len(unique_versions) == 1:
            print(f"🎉 版本一致！所有文件都是 {list(unique_versions)[0]}")
        else:
            print(f"⚠️  版本不一致！發現以下版本:")
            for version in sorted(unique_versions):
                files_with_version = [f for f, v in versions.items() if v == version]
                print(f"   {version}: {', '.join(files_with_version)}")
    else:
        print("❌ 未找到任何版本號")
    
    print(f"\n📋 建議:")
    if len(unique_versions) > 1:
        print("   1. 使用 update_version.py 腳本統一版本號")
        print("   2. 檢查是否有遺漏的文件")
    else:
        print("   1. 版本號已統一，可以準備發布")
        print("   2. 運行 make release 建置發布包")

if __name__ == "__main__":
    main()
