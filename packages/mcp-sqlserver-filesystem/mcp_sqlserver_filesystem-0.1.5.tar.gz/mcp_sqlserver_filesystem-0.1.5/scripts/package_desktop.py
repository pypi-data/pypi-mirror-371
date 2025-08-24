#!/usr/bin/env python3
"""
Build and package desktop application for distribution.

This script builds the Tauri desktop application and prepares it for 
inclusion in the PyPI package, so users don't need to install Rust.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
import platform


class DesktopPackager:
    """Desktop application packager for distribution."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tauri_dir = self.project_root / "src-tauri"
        self.dist_dir = self.project_root / "dist"
        self.package_dir = self.project_root / "src" / "mcp_sqlserver_filesystem" / "desktop_binaries"
    
    def check_requirements(self) -> bool:
        """Check if build requirements are met."""
        print("🔍 Checking build requirements...")
        
        # Check Rust
        try:
            result = subprocess.run(["rustc", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Rust: {result.stdout.strip()}")
            else:
                print("❌ Rust not found")
                return False
        except FileNotFoundError:
            print("❌ Rust not found. Please install from https://rustup.rs/")
            return False
        
        # Check Tauri CLI
        try:
            result = subprocess.run(["cargo", "tauri", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Tauri CLI: {result.stdout.strip()}")
            else:
                print("❌ Tauri CLI not found")
                return False
        except FileNotFoundError:
            print("❌ Tauri CLI not found. Please install with: cargo install tauri-cli")
            return False
        
        # Check Tauri directory
        if not self.tauri_dir.exists():
            print(f"❌ Tauri directory not found: {self.tauri_dir}")
            return False
        
        print("✅ All build requirements met")
        return True
    
    def build_desktop(self) -> bool:
        """Build the desktop application."""
        print("🔨 Building desktop application...")
        
        if not self.check_requirements():
            return False
        
        try:
            # Clean previous builds
            print("🧹 Cleaning previous builds...")
            target_dir = self.tauri_dir / "target"
            if target_dir.exists():
                shutil.rmtree(target_dir)
            
            # Build release version
            print("🚀 Building release version...")
            cmd = ["cargo", "tauri", "build", "--verbose"]
            
            result = subprocess.run(
                cmd, 
                cwd=self.tauri_dir, 
                check=True,
                text=True
            )
            
            print("✅ Desktop application built successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build desktop application: {e}")
            return False
    
    def package_binaries(self) -> bool:
        """Package binaries for distribution."""
        print("📦 Packaging binaries for distribution...")
        
        try:
            # Create package directory
            self.package_dir.mkdir(parents=True, exist_ok=True)
            
            # Get platform info
            current_platform = platform.system().lower()
            current_arch = platform.machine().lower()
            
            print(f"📋 Current platform: {current_platform}-{current_arch}")
            
            # Source directories
            target_dir = self.tauri_dir / "target" / "release"
            bundle_dir = target_dir / "bundle"
            
            copied_files = []
            
            # Copy main executable
            executable_name = self._get_executable_name()
            executable_path = target_dir / executable_name
            
            if executable_path.exists():
                dest_name = f"{executable_name}.{current_platform}-{current_arch}"
                dest_path = self.package_dir / dest_name
                shutil.copy2(executable_path, dest_path)
                copied_files.append(dest_name)
                print(f"📄 Copied executable: {dest_name}")
            
            # Copy platform-specific installers
            if current_platform == "windows":
                # Copy MSI installer
                msi_files = list(bundle_dir.glob("msi/*.msi"))
                for msi_file in msi_files:
                    dest_name = f"{msi_file.name}.{current_platform}-{current_arch}"
                    dest_path = self.package_dir / dest_name
                    shutil.copy2(msi_file, dest_path)
                    copied_files.append(dest_name)
                    print(f"📄 Copied MSI: {dest_name}")
            
            elif current_platform == "linux":
                # Copy DEB package
                deb_files = list(bundle_dir.glob("deb/*.deb"))
                for deb_file in deb_files:
                    dest_name = f"{deb_file.name}.{current_platform}-{current_arch}"
                    dest_path = self.package_dir / dest_name
                    shutil.copy2(deb_file, dest_path)
                    copied_files.append(dest_name)
                    print(f"📄 Copied DEB: {dest_name}")
                
                # Copy AppImage
                appimage_files = list(bundle_dir.glob("appimage/*.AppImage"))
                for appimage_file in appimage_files:
                    dest_name = f"{appimage_file.name}.{current_platform}-{current_arch}"
                    dest_path = self.package_dir / dest_name
                    shutil.copy2(appimage_file, dest_path)
                    copied_files.append(dest_name)
                    print(f"📄 Copied AppImage: {dest_name}")
            
            elif current_platform == "darwin":
                # Copy DMG
                dmg_files = list(bundle_dir.glob("dmg/*.dmg"))
                for dmg_file in dmg_files:
                    dest_name = f"{dmg_file.name}.{current_platform}-{current_arch}"
                    dest_path = self.package_dir / dest_name
                    shutil.copy2(dmg_file, dest_path)
                    copied_files.append(dest_name)
                    print(f"📄 Copied DMG: {dest_name}")
                
                # Copy .app bundle (compress it)
                app_dirs = list(bundle_dir.glob("macos/*.app"))
                for app_dir in app_dirs:
                    archive_name = f"{app_dir.name}.tar.gz"
                    dest_name = f"{archive_name}.{current_platform}-{current_arch}"
                    dest_path = self.package_dir / dest_name
                    
                    # Create tar.gz archive
                    import tarfile
                    with tarfile.open(dest_path, "w:gz") as tar:
                        tar.add(app_dir, arcname=app_dir.name)
                    
                    copied_files.append(dest_name)
                    print(f"📄 Copied .app bundle: {dest_name}")
            
            # Create manifest file
            manifest_path = self.package_dir / "manifest.json"
            manifest_data = {
                "platform": current_platform,
                "architecture": current_arch,
                "files": copied_files,
                "build_time": str(datetime.now()),
                "version": self._get_version()
            }
            
            import json
            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f, indent=2)
            
            print("✅ Binaries packaged successfully")
            print(f"📁 Package directory: {self.package_dir}")
            print(f"📄 Files packaged: {len(copied_files)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to package binaries: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_executable_name(self) -> str:
        """Get the executable name for the current platform."""
        if platform.system() == "Windows":
            return "mcp-sqlserver-filesystem.exe"
        elif platform.system() == "Darwin":
            return "mcp-sqlserver-filesystem"
        else:  # Linux
            return "mcp-sqlserver-filesystem"
    
    def _get_version(self) -> str:
        """Get current version from pyproject.toml."""
        try:
            import tomllib
        except ImportError:
            # For Python < 3.11
            import tomli as tomllib
        
        pyproject_path = self.project_root / "pyproject.toml"
        with open(pyproject_path, 'rb') as f:
            data = tomllib.load(f)
            return data['project']['version']
    
    def clean(self) -> bool:
        """Clean packaged binaries."""
        print("🧹 Cleaning packaged binaries...")
        
        try:
            if self.package_dir.exists():
                shutil.rmtree(self.package_dir)
                print("✅ Package directory cleaned")
            
            target_dir = self.tauri_dir / "target"
            if target_dir.exists():
                shutil.rmtree(target_dir)
                print("✅ Build artifacts cleaned")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to clean: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Build and package desktop application")
    parser.add_argument("command", choices=["build", "package", "clean", "all"],
                       help="Command to execute")
    
    args = parser.parse_args()
    
    packager = DesktopPackager()
    
    if args.command == "build":
        success = packager.build_desktop()
    elif args.command == "package":
        success = packager.package_binaries()
    elif args.command == "clean":
        success = packager.clean()
    elif args.command == "all":
        success = (packager.build_desktop() and 
                  packager.package_binaries())
    else:
        print(f"Unknown command: {args.command}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()