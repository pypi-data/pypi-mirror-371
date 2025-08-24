#!/usr/bin/env python3
"""
统一版本号管理脚本
==================

此脚本用于在所有项目文件中同步更新版本号，确保版本一致性。

使用方法:
    python scripts/update_version.py 0.2.0
    python scripts/update_version.py --show  # 显示当前版本
    python scripts/update_version.py --check # 检查版本一致性
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class VersionManager:
    """版本号管理器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        
        # 定义需要更新版本号的文件和对应的正则表达式
        self.version_files = {
            # Python 包版本
            "src/mcp_sqlserver_filesystem/__init__.py": [
                (r'__version__ = "[^"]*"', r'__version__ = "{version}"')
            ],
            
            # 项目配置
            "pyproject.toml": [
                (r'version = "[^"]*"', r'version = "{version}"'),
                (r'version = "[^"]*"  # Desktop app version', r'version = "{version}"  # Desktop app version')
            ],
            
            # Tauri 配置
            "src-tauri/Cargo.toml": [
                (r'version = "[^"]*"', r'version = "{version}"')
            ],
            
            "src-tauri/tauri.conf.json": [
                (r'"version": "[^"]*"', r'"version": "{version}"')
            ],
            
            # 桌面应用清单
            "src/mcp_sqlserver_filesystem/desktop_binaries/manifest.json": [
                (r'"version": "[^"]*"', r'"version": "{version}"')
            ]
        }
    
    def get_current_version(self) -> str:
        """从主源文件获取当前版本号"""
        init_file = self.project_root / "src/mcp_sqlserver_filesystem/__init__.py"
        
        if not init_file.exists():
            raise FileNotFoundError(f"主版本文件不存在: {init_file}")
        
        content = init_file.read_text(encoding='utf-8')
        match = re.search(r'__version__ = "([^"]*)"', content)
        
        if not match:
            raise ValueError("无法在 __init__.py 中找到版本号")
        
        return match.group(1)
    
    def update_version(self, new_version: str) -> List[Tuple[str, bool]]:
        """更新所有文件中的版本号
        
        Returns:
            List of (file_path, success) tuples
        """
        results = []
        
        for relative_path, patterns in self.version_files.items():
            file_path = self.project_root / relative_path
            success = self._update_file_version(file_path, patterns, new_version)
            results.append((relative_path, success))
        
        return results
    
    def _update_file_version(self, file_path: Path, patterns: List[Tuple[str, str]], new_version: str) -> bool:
        """更新单个文件中的版本号"""
        try:
            if not file_path.exists():
                print(f"⚠️  文件不存在，跳过: {file_path}")
                return False
                
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # 应用所有匹配模式
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement.format(version=new_version), content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print(f"✅ 已更新: {file_path}")
                return True
            else:
                print(f"ℹ️  无需更新: {file_path}")
                return True
                
        except Exception as e:
            print(f"❌ 更新失败 {file_path}: {e}")
            return False
    
    def check_version_consistency(self) -> Dict[str, str]:
        """检查所有文件中的版本号一致性"""
        versions = {}
        
        for relative_path, patterns in self.version_files.items():
            file_path = self.project_root / relative_path
            
            if not file_path.exists():
                versions[relative_path] = "文件不存在"
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                found_version = None
                
                # 尝试从任何模式中提取版本号
                for pattern, _ in patterns:
                    # 将替换模式转换为捕获模式
                    capture_pattern = pattern.replace('[^"]*', '([^"]*)')
                    match = re.search(capture_pattern, content)
                    if match:
                        found_version = match.group(1)
                        break
                
                versions[relative_path] = found_version or "未找到版本号"
                
            except Exception as e:
                versions[relative_path] = f"读取错误: {e}"
        
        return versions

def main():
    """主入口点"""
    parser = argparse.ArgumentParser(description="统一版本号管理工具")
    parser.add_argument("version", nargs="?", help="新版本号 (例如: 0.2.0)")
    parser.add_argument("--show", action="store_true", help="显示当前版本")
    parser.add_argument("--check", action="store_true", help="检查版本一致性")
    
    args = parser.parse_args()
    
    try:
        manager = VersionManager()
        
        if args.show:
            current_version = manager.get_current_version()
            print(f"当前版本: {current_version}")
            
        elif args.check:
            print("检查版本一致性...")
            versions = manager.check_version_consistency()
            
            # 显示所有版本
            print("\n📋 文件版本信息:")
            print("-" * 60)
            for file_path, version in versions.items():
                print(f"{file_path:<50} {version}")
            
            # 检查一致性
            unique_versions = set(v for v in versions.values() 
                                if v not in ["文件不存在", "未找到版本号"] 
                                and not v.startswith("读取错误"))
            
            if len(unique_versions) == 1:
                print(f"\n✅ 所有文件版本一致: {list(unique_versions)[0]}")
            else:
                print(f"\n⚠️  发现版本不一致:")
                for version in unique_versions:
                    files = [f for f, v in versions.items() if v == version]
                    print(f"  版本 {version}: {len(files)} 个文件")
                    
        elif args.version:
            new_version = args.version
            
            # 验证版本号格式
            if not re.match(r'^\d+\.\d+\.\d+$', new_version):
                print("❌ 版本号格式错误，应为 x.y.z 格式")
                sys.exit(1)
            
            print(f"更新版本号到: {new_version}")
            results = manager.update_version(new_version)
            
            # 统计结果
            success_count = sum(1 for _, success in results if success)
            total_count = len(results)
            
            print(f"\n📊 更新结果: {success_count}/{total_count} 个文件更新成功")
            
            # 显示失败的文件
            failed_files = [path for path, success in results if not success]
            if failed_files:
                print("\n❌ 更新失败的文件:")
                for file_path in failed_files:
                    print(f"  - {file_path}")
            else:
                print("\n🎉 所有文件更新成功！")
                
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()