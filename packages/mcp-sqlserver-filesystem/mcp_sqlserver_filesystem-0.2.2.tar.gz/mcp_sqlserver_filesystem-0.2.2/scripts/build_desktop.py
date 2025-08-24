#!/usr/bin/env python3
"""
Build script for MCP SQL Server Filesystem Desktop Application

This script automates the build process for the desktop application,
including dependency installation, building, testing, and packaging.
"""

import argparse
import os
import subprocess
import sys
import shutil
from pathlib import Path


class DesktopBuilder:
    """Desktop application builder."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tauri_dir = self.project_root / "src-tauri"
        self.dist_dir = self.project_root / "dist" / "desktop"
    
    def check_rust(self) -> bool:
        """Check if Rust is installed."""
        try:
            result = subprocess.run(["rustc", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Rust found: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        
        print("❌ Rust not found. Please install from https://rustup.rs/")
        return False
    
    def check_tauri_cli(self) -> bool:
        """Check if Tauri CLI is installed."""
        try:
            result = subprocess.run(["cargo", "tauri", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Tauri CLI found: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        
        print("❌ Tauri CLI not found")
        return False
    
    def install_deps(self) -> bool:
        """Install development dependencies."""
        print("📦 Installing development dependencies...")
        
        if not self.check_rust():
            return False
        
        if not self.check_tauri_cli():
            print("📦 Installing Tauri CLI...")
            try:
                result = subprocess.run([
                    "cargo", "install", "tauri-cli", "--version", "^1.0"
                ], check=True)
                print("✅ Tauri CLI installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install Tauri CLI: {e}")
                return False
        
        return True
    
    def build_desktop(self, release: bool = False) -> bool:
        """Build the desktop application."""
        mode = "release" if release else "debug"
        print(f"🔨 Building desktop application ({mode} mode)...")
        
        if not self.tauri_dir.exists():
            print(f"❌ Tauri directory not found: {self.tauri_dir}")
            return False
        
        try:
            cmd = ["cargo", "tauri", "build"]
            if not release:
                cmd.append("--debug")
            
            result = subprocess.run(cmd, cwd=self.tauri_dir, check=True)
            print(f"✅ Desktop application built successfully ({mode})")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build desktop application: {e}")
            return False
    
    def test_desktop(self) -> bool:
        """Test the desktop application."""
        print("🧪 Testing desktop application...")
        
        try:
            # Run Python tests if they exist
            test_file = self.project_root / "tests" / "test_desktop.py"
            if test_file.exists():
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    str(test_file), "-v"
                ], check=True)
            else:
                # Run functional test
                result = subprocess.run([
                    sys.executable, "-m", "mcp_sqlserver_filesystem", 
                    "test", "--desktop"
                ], check=True)
            
            print("✅ Desktop application tests passed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Desktop application tests failed: {e}")
            return False
    
    def dev_desktop(self) -> bool:
        """Run desktop application in development mode."""
        print("🚀 Starting desktop application in development mode...")
        
        if not self.tauri_dir.exists():
            print(f"❌ Tauri directory not found: {self.tauri_dir}")
            return False
        
        try:
            subprocess.run(["cargo", "tauri", "dev"], cwd=self.tauri_dir, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start development mode: {e}")
            return False
        except KeyboardInterrupt:
            print("\n🛑 Development mode stopped")
            return True
    
    def clean_desktop(self) -> bool:
        """Clean desktop build artifacts."""
        print("🧹 Cleaning desktop build artifacts...")
        
        try:
            if self.tauri_dir.exists():
                # Clean Cargo artifacts
                subprocess.run(["cargo", "clean"], cwd=self.tauri_dir)
                
                # Remove target directory
                target_dir = self.tauri_dir / "target"
                if target_dir.exists():
                    shutil.rmtree(target_dir)
            
            print("✅ Desktop build artifacts cleaned")
            return True
            
        except Exception as e:
            print(f"❌ Failed to clean artifacts: {e}")
            return False
    
    def package(self) -> bool:
        """Package the desktop application for distribution."""
        print("📦 Creating distribution package...")
        
        # Build release version
        if not self.build_desktop(release=True):
            return False
        
        # Create dist directory
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy platform-specific packages
        target_dir = self.tauri_dir / "target" / "release"
        bundle_dir = target_dir / "bundle"
        
        copied_files = []
        
        # Windows MSI installer
        msi_pattern = f"mcp-sqlserver-filesystem_*_x64_en-US.msi"
        msi_dir = bundle_dir / "msi"
        if msi_dir.exists():
            for msi_file in msi_dir.glob(msi_pattern):
                dest = self.dist_dir / msi_file.name
                shutil.copy2(msi_file, dest)
                copied_files.append(dest.name)
        
        # Linux DEB package
        deb_pattern = f"mcp-sqlserver-filesystem_*_amd64.deb"
        deb_dir = bundle_dir / "deb"
        if deb_dir.exists():
            for deb_file in deb_dir.glob(deb_pattern):
                dest = self.dist_dir / deb_file.name
                shutil.copy2(deb_file, dest)
                copied_files.append(dest.name)
        
        # macOS DMG
        dmg_pattern = f"mcp-sqlserver-filesystem_*_x64.dmg"
        dmg_dir = bundle_dir / "dmg"
        if dmg_dir.exists():
            for dmg_file in dmg_dir.glob(dmg_pattern):
                dest = self.dist_dir / dmg_file.name
                shutil.copy2(dmg_file, dest)
                copied_files.append(dest.name)
        
        # Raw executable
        executable_name = self._get_executable_name()
        executable_path = target_dir / executable_name
        if executable_path.exists():
            dest = self.dist_dir / executable_name
            shutil.copy2(executable_path, dest)
            copied_files.append(executable_name)
        
        if copied_files:
            print("✅ Distribution package created in dist/desktop/:")
            for file in copied_files:
                print(f"   📄 {file}")
            return True
        else:
            print("⚠️  No distribution files found to package")
            return False
    
    def _get_executable_name(self) -> str:
        """Get the executable name for the current platform."""
        if sys.platform == "win32":
            return "mcp-sqlserver-filesystem.exe"
        elif sys.platform == "darwin":
            return "mcp-sqlserver-filesystem.app"
        else:
            return "mcp-sqlserver-filesystem"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build script for MCP SQL Server Filesystem Desktop Application"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install dependencies
    subparsers.add_parser("install-deps", 
                         help="Install development dependencies (Rust, Tauri CLI)")
    
    # Build commands
    build_parser = subparsers.add_parser("build-desktop", 
                                        help="Build desktop application")
    build_parser.add_argument("--release", action="store_true",
                             help="Build in release mode")
    
    subparsers.add_parser("build-desktop-release",
                         help="Build desktop application (release mode)")
    
    # Test commands
    subparsers.add_parser("test-desktop", 
                         help="Test desktop application")
    
    # Development commands
    subparsers.add_parser("dev-desktop",
                         help="Run desktop application in development mode")
    
    # Utility commands
    subparsers.add_parser("clean-desktop",
                         help="Clean desktop build artifacts")
    
    subparsers.add_parser("package",
                         help="Build and package for distribution")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    builder = DesktopBuilder()
    
    if args.command == "install-deps":
        success = builder.install_deps()
    elif args.command == "build-desktop":
        success = builder.build_desktop(release=args.release)
    elif args.command == "build-desktop-release":
        success = builder.build_desktop(release=True)
    elif args.command == "test-desktop":
        success = builder.test_desktop()
    elif args.command == "dev-desktop":
        success = builder.dev_desktop()
    elif args.command == "clean-desktop":
        success = builder.clean_desktop()
    elif args.command == "package":
        success = builder.package()
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())