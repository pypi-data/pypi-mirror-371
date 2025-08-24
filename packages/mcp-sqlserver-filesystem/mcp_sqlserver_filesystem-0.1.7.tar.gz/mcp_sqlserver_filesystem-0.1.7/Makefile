# Makefile for MCP SQL Server Filesystem Desktop Application

.PHONY: help install-deps build-desktop build-desktop-release test-desktop clean-desktop dev-desktop

# Default target
help:
	@echo "Available targets:"
	@echo "  install-deps         - Install development dependencies (Rust, Tauri CLI)"
	@echo "  build-desktop        - Build desktop application (debug mode)"
	@echo "  build-desktop-release- Build desktop application (release mode)"
	@echo "  test-desktop         - Test desktop application"
	@echo "  dev-desktop          - Run desktop application in development mode"
	@echo "  clean-desktop        - Clean desktop build artifacts"
	@echo "  package              - Build and package for distribution"

# Install development dependencies
install-deps:
	@echo "Installing Rust..."
	@if ! command -v rustc >/dev/null 2>&1; then \
		echo "Rust not found. Please install from https://rustup.rs/"; \
		exit 1; \
	fi
	@echo "Installing Tauri CLI..."
	cargo install tauri-cli --version "^1.0"
	@echo "Dependencies installed successfully"

# Build desktop application (debug mode)
build-desktop:
	@echo "Building desktop application (debug)..."
	cd src-tauri && cargo tauri build --debug
	@echo "Desktop application built successfully (debug)"

# Build desktop application (release mode)
build-desktop-release:
	@echo "Building desktop application (release)..."
	cd src-tauri && cargo tauri build
	@echo "Desktop application built successfully (release)"

# Test desktop application
test-desktop:
	@echo "Testing desktop application..."
	python -m pytest tests/test_desktop.py -v
	@echo "Desktop application tests passed"

# Run desktop application in development mode
dev-desktop:
	@echo "Starting desktop application in development mode..."
	cd src-tauri && cargo tauri dev

# Clean desktop build artifacts
clean-desktop:
	@echo "Cleaning desktop build artifacts..."
	cd src-tauri && cargo clean
	rm -rf src-tauri/target
	@echo "Desktop build artifacts cleaned"

# Package for distribution
package: build-desktop-release
	@echo "Creating distribution package..."
	@mkdir -p dist/desktop
	@if [ -f "src-tauri/target/release/bundle/msi/mcp-sqlserver-filesystem_0.1.2_x64_en-US.msi" ]; then \
		cp "src-tauri/target/release/bundle/msi/mcp-sqlserver-filesystem_0.1.2_x64_en-US.msi" "dist/desktop/"; \
	fi
	@if [ -f "src-tauri/target/release/bundle/deb/mcp-sqlserver-filesystem_0.1.2_amd64.deb" ]; then \
		cp "src-tauri/target/release/bundle/deb/mcp-sqlserver-filesystem_0.1.2_amd64.deb" "dist/desktop/"; \
	fi
	@if [ -f "src-tauri/target/release/bundle/dmg/mcp-sqlserver-filesystem_0.1.2_x64.dmg" ]; then \
		cp "src-tauri/target/release/bundle/dmg/mcp-sqlserver-filesystem_0.1.2_x64.dmg" "dist/desktop/"; \
	fi
	@echo "Distribution package created in dist/desktop/"

# Test functional desktop features
test-func:
	@echo "Running functional tests..."
	python -m mcp_sqlserver_filesystem test

# Test web UI
test-web:
	@echo "Running web UI tests..."
	python -m mcp_sqlserver_filesystem test --web

# Test desktop application (functional)
test-desktop-func:
	@echo "Running desktop application functional tests..."
	python -m mcp_sqlserver_filesystem test --desktop