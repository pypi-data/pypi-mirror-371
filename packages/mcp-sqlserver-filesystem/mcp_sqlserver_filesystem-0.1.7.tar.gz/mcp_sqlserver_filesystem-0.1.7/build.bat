@echo off
REM Build script for MCP SQL Server Filesystem Desktop Application

if "%1"=="help" goto help
if "%1"=="install-deps" goto install-deps
if "%1"=="build-desktop" goto build-desktop
if "%1"=="build-desktop-release" goto build-desktop-release
if "%1"=="test-desktop" goto test-desktop
if "%1"=="dev-desktop" goto dev-desktop
if "%1"=="clean-desktop" goto clean-desktop
if "%1"=="package" goto package
if "%1"=="" goto help

:help
echo Available commands:
echo   install-deps          - Install development dependencies (Rust, Tauri CLI)
echo   build-desktop         - Build desktop application (debug mode)
echo   build-desktop-release - Build desktop application (release mode)
echo   test-desktop          - Test desktop application
echo   dev-desktop           - Run desktop application in development mode
echo   clean-desktop         - Clean desktop build artifacts
echo   package               - Build and package for distribution
goto end

:install-deps
echo Installing development dependencies...
echo Checking Rust installation...
where rustc >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Rust not found. Please install from https://rustup.rs/
    exit /b 1
)
echo Installing Tauri CLI...
cargo install tauri-cli --version "^1.0"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install Tauri CLI
    exit /b 1
)
echo Dependencies installed successfully
goto end

:build-desktop
echo Building desktop application (debug mode)...
cd src-tauri
cargo tauri build --debug
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build desktop application
    cd ..
    exit /b 1
)
cd ..
echo Desktop application built successfully (debug)
goto end

:build-desktop-release
echo Building desktop application (release mode)...
cd src-tauri
cargo tauri build
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build desktop application
    cd ..
    exit /b 1
)
cd ..
echo Desktop application built successfully (release)
goto end

:test-desktop
echo Testing desktop application...
python -m pytest tests/test_desktop.py -v
if %ERRORLEVEL% NEQ 0 (
    echo Desktop application tests failed
    exit /b 1
)
echo Desktop application tests passed
goto end

:dev-desktop
echo Starting desktop application in development mode...
cd src-tauri
cargo tauri dev
cd ..
goto end

:clean-desktop
echo Cleaning desktop build artifacts...
cd src-tauri
cargo clean
if exist target rmdir /s /q target
cd ..
echo Desktop build artifacts cleaned
goto end

:package
echo Creating distribution package...
call :build-desktop-release
if %ERRORLEVEL% NEQ 0 (
    echo Failed to build release version
    exit /b 1
)

if not exist dist\desktop mkdir dist\desktop

REM Copy Windows MSI installer if it exists
if exist "src-tauri\target\release\bundle\msi\mcp-sqlserver-filesystem_0.1.2_x64_en-US.msi" (
    copy "src-tauri\target\release\bundle\msi\mcp-sqlserver-filesystem_0.1.2_x64_en-US.msi" "dist\desktop\"
    echo Windows installer copied to dist\desktop\
)

REM Copy executable if it exists
if exist "src-tauri\target\release\mcp-sqlserver-filesystem.exe" (
    copy "src-tauri\target\release\mcp-sqlserver-filesystem.exe" "dist\desktop\"
    echo Executable copied to dist\desktop\
)

echo Distribution package created in dist\desktop\
goto end

:end