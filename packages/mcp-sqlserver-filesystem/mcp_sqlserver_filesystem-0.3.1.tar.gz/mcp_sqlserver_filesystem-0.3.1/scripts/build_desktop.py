#!/usr/bin/env python3
"""
桌面应用程序构建脚本

参考 mcp-feedback-enhanced 项目的构建方式，
负责构建 Tauri 桌面应用程序，
确保在 PyPI 发布时包含预编译的二进制文件。

使用方法：
    python scripts/build_desktop.py [--release] [--clean]
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(
    cmd: list[str], cwd: str = None, check: bool = True, show_info: bool = True
) -> subprocess.CompletedProcess:
    """执行命令并返回结果"""
    if show_info:
        print(f"🔧 执行命令: {' '.join(cmd)}")
        if cwd:
            print(f"📁 工作目录: {cwd}")

    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)

    # 处理标准输出
    if result.stdout and show_info:
        print("📤 输出:")
        print(result.stdout.strip())

    # 智能处理标准错误 - 区分信息和真正的错误
    if result.stderr:
        stderr_lines = result.stderr.strip().split("\n")
        info_lines = []
        error_lines = []

        for line in stderr_lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            # 识别信息性消息和正常编译输出
            if (
                stripped_line.startswith("info:")
                or "is up to date" in stripped_line
                or "downloading component" in stripped_line
                or "installing component" in stripped_line
                or stripped_line.startswith("Compiling")
                or stripped_line.startswith("Finished")
                or stripped_line.startswith("Building")
                or "target(s) in" in stripped_line
            ):
                info_lines.append(stripped_line)
            else:
                error_lines.append(stripped_line)

        # 显示信息性消息
        if info_lines and show_info:
            print("ℹ️  信息:")
            for line in info_lines:
                print(f"   {line}")

        # 显示真正的错误
        if error_lines:
            print("❌ 错误:")
            for line in error_lines:
                print(f"   {line}")

    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)

    return result


def check_rust_environment():
    """检查 Rust 开发环境"""
    print("🔍 检查 Rust 开发环境...")

    try:
        result = run_command(["rustc", "--version"])
        print(f"✅ Rust 编译器: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到 Rust 编译器")
        print("💡 请安装 Rust: https://rustup.rs/")
        return False

    try:
        result = run_command(["cargo", "--version"])
        print(f"✅ Cargo: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到 Cargo")
        return False

    try:
        result = run_command(["cargo", "install", "--list"])
        if "tauri-cli" in result.stdout:
            print("✅ Tauri CLI 已安装")
        else:
            print("⚠️  Tauri CLI 未安装，尝试安装...")
            run_command(["cargo", "install", "tauri-cli"])
            print("✅ Tauri CLI 安装完成")
    except subprocess.CalledProcessError:
        print("❌ 无法安装 Tauri CLI")
        return False

    return True


def install_rust_targets():
    """安装跨平台编译所需的 Rust targets"""
    print("🎯 安装跨平台编译 targets...")

    # 定义需要的 targets
    targets = [
        ("x86_64-pc-windows-msvc", "Windows x64"),
        ("x86_64-apple-darwin", "macOS Intel"),
        ("aarch64-apple-darwin", "macOS Apple Silicon"),
        ("x86_64-unknown-linux-gnu", "Linux x64"),
    ]

    installed_count = 0
    updated_count = 0

    for target, description in targets:
        print(f"📦 检查 target: {target} ({description})")
        try:
            result = run_command(
                ["rustup", "target", "add", target], check=False, show_info=False
            )

            if result.returncode == 0:
                # 检查是否是新安装还是已存在
                if "is up to date" in result.stderr:
                    print(f"✅ {description} - 已是最新版本")
                    updated_count += 1
                elif "installing component" in result.stderr:
                    print(f"🆕 {description} - 新安装完成")
                    installed_count += 1
                else:
                    print(f"✅ {description} - 安装成功")
                    installed_count += 1
            else:
                print(f"⚠️  {description} - 安装失败")
                if result.stderr:
                    print(f"   错误: {result.stderr.strip()}")
        except Exception as e:
            print(f"⚠️  安装 {description} 时发生错误: {e}")

    print(
        f"✅ Rust targets 检查完成 (新安装: {installed_count}, 已存在: {updated_count})"
    )


def clean_build_artifacts(project_root: Path):
    """清理构建产物"""
    print("🧹 清理构建产物...")

    # 清理 Rust 构建产物
    rust_target = project_root / "src-tauri" / "target"
    if rust_target.exists():
        print(f"清理 Rust target 目录: {rust_target}")
        shutil.rmtree(rust_target)

    # 清理 Python 构建产物
    python_build_dirs = [
        project_root / "build",
        project_root / "dist",
    ]

    for build_dir in python_build_dirs:
        if build_dir.exists():
            print(f"清理 Python 构建目录: {build_dir}")
            if build_dir.is_dir():
                shutil.rmtree(build_dir)
            else:
                build_dir.unlink()


def build_tauri_app_current_platform(project_root: Path, release: bool = True):
    """构建当前平台的 Tauri 桌面应用程序"""
    print("🖥️ 构建当前平台的 Tauri 桌面应用程序...")

    src_tauri = project_root / "src-tauri"
    if not src_tauri.exists():
        raise FileNotFoundError(f"src-tauri 目录不存在: {src_tauri}")

    # 构建命令
    build_cmd = ["cargo", "tauri", "build"]
    if not release:
        build_cmd.append("--debug")

    try:
        run_command(build_cmd, cwd=str(src_tauri))
        print("✅ 当前平台构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 构建失败")
        return False


def copy_current_platform_artifacts(project_root: Path, release: bool = True):
    """复制当前平台构建产物到适当位置"""
    print("📦 复制当前平台构建产物...")

    src_tauri = project_root / "src-tauri"
    build_type = "release" if release else "debug"

    # 创建目标目录
    desktop_dir = project_root / "src" / "mcp_sqlserver_filesystem" / "desktop_binaries"
    desktop_dir.mkdir(parents=True, exist_ok=True)

    # 确定平台和文件扩展名
    import platform
    current_platform = platform.system().lower()
    
    if current_platform == "windows":
        binary_name = "mcp-sqlserver-filesystem.exe"
        target_name = "mcp-sqlserver-filesystem.exe.windows-x64"
    elif current_platform == "darwin":
        binary_name = "mcp-sqlserver-filesystem"
        arch = platform.machine().lower()
        if arch in ['arm64', 'aarch64']:
            target_name = "mcp-sqlserver-filesystem.macos-arm64"
        else:
            target_name = "mcp-sqlserver-filesystem.macos-x64"
    else:  # linux
        binary_name = "mcp-sqlserver-filesystem"
        target_name = "mcp-sqlserver-filesystem.linux-x64"

    # 查找源文件
    target_dir = src_tauri / "target" / build_type
    src_file = target_dir / binary_name

    if not src_file.exists():
        print(f"❌ 未找到构建产物: {src_file}")
        return False

    # 复制文件
    dest_file = desktop_dir / target_name
    shutil.copy2(src_file, dest_file)
    print(f"✅ 已复制: {src_file} -> {dest_file}")

    # 更新 manifest
    manifest_file = desktop_dir / "manifest.json"
    import json
    import time
    
    # 读取版本号
    init_file = project_root / "src" / "mcp_sqlserver_filesystem" / "__init__.py"
    version = "unknown"
    if init_file.exists():
        import re
        content = init_file.read_text(encoding='utf-8')
        match = re.search(r'__version__ = "([^"]*)"', content)
        if match:
            version = match.group(1)

    manifest = {
        "platform": current_platform,
        "architecture": platform.machine().lower(),
        "files": [target_name],
        "build_time": time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime()),
        "version": version,
        "note": f"Built on {current_platform} for local development"
    }

    with manifest_file.open('w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已更新 manifest: {manifest_file}")
    return True


def main():
    """主入口点"""
    parser = argparse.ArgumentParser(description="桌面应用程序构建脚本")
    parser.add_argument("--release", action="store_true", help="构建 release 版本")
    parser.add_argument("--clean", action="store_true", help="清理构建产物")

    args = parser.parse_args()

    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    print(f"🏠 项目根目录: {project_root}")

    try:
        if args.clean:
            clean_build_artifacts(project_root)
            print("✅ 清理完成")
            return

        # 检查 Rust 环境
        if not check_rust_environment():
            print("❌ Rust 环境检查失败")
            sys.exit(1)

        # 安装必要的 targets（可选）
        install_rust_targets()

        # 构建当前平台的桌面应用
        success = build_tauri_app_current_platform(project_root, args.release)
        
        if success:
            # 复制构建产物
            copy_success = copy_current_platform_artifacts(project_root, args.release)
            if copy_success:
                print("🎉 桌面应用构建完成！")
                print("")
                print("💡 注意：")
                print("   - 目前只构建了当前平台的二进制文件")
                print("   - 完整的多平台支持将在后续版本中实现")
                print("   - 构建的二进制文件位于: src/mcp_sqlserver_filesystem/desktop_binaries/")
            else:
                print("❌ 复制构建产物失败")
                sys.exit(1)
        else:
            print("❌ 构建失败")
            sys.exit(1)

    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()