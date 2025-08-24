// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use tauri::{Manager, State, Window};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct ServerInfo {
    host: String,
    port: u16,
    status: String,
}

type ServerState = Arc<Mutex<Option<ServerInfo>>>;

#[tauri::command]
async fn start_python_server(
    state: State<'_, ServerState>,
    window: Window,
) -> Result<ServerInfo, String> {
    println!("Starting Python MCP server...");
    
    // 设置环境变量
    std::env::set_var("MCP_DESKTOP_MODE", "true");
    std::env::set_var("MCP_WEB_HOST", "127.0.0.1");
    std::env::set_var("MCP_WEB_PORT", "8765");
    
    // 启动Python服务器
    let mut cmd = Command::new("python")
        .args(["-m", "mcp_sqlserver_filesystem", "--test-web"])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start Python server: {}", e))?;

    // 等待服务器启动
    thread::sleep(Duration::from_secs(3));
    
    let server_info = ServerInfo {
        host: "127.0.0.1".to_string(),
        port: 8765,
        status: "running".to_string(),
    };
    
    // 更新状态
    {
        let mut state_guard = state.lock().unwrap();
        *state_guard = Some(server_info.clone());
    }
    
    // 通知前端服务器已启动
    window.emit("server-started", &server_info).unwrap();
    
    Ok(server_info)
}

#[tauri::command]
async fn stop_python_server(state: State<'_, ServerState>) -> Result<String, String> {
    println!("Stopping Python MCP server...");
    
    // 更新状态
    {
        let mut state_guard = state.lock().unwrap();
        *state_guard = None;
    }
    
    Ok("Server stopped".to_string())
}

#[tauri::command]
async fn get_server_status(state: State<'_, ServerState>) -> Result<Option<ServerInfo>, String> {
    let state_guard = state.lock().unwrap();
    Ok(state_guard.clone())
}

#[tauri::command]
async fn open_external_url(url: String) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        std::process::Command::new("cmd")
            .args(["/c", "start", &url])
            .spawn()
            .map_err(|e| format!("Failed to open URL: {}", e))?;
    }
    
    #[cfg(target_os = "macos")]
    {
        std::process::Command::new("open")
            .arg(&url)
            .spawn()
            .map_err(|e| format!("Failed to open URL: {}", e))?;
    }
    
    #[cfg(target_os = "linux")]
    {
        std::process::Command::new("xdg-open")
            .arg(&url)
            .spawn()
            .map_err(|e| format!("Failed to open URL: {}", e))?;
    }
    
    Ok(())
}

fn main() {
    let server_state: ServerState = Arc::new(Mutex::new(None));

    tauri::Builder::default()
        .manage(server_state)
        .invoke_handler(tauri::generate_handler![
            start_python_server,
            stop_python_server, 
            get_server_status,
            open_external_url
        ])
        .setup(|app| {
            let window = app.get_window("main").unwrap();
            
            // 自动启动Python服务器
            let state = app.state::<ServerState>();
            let window_clone = window.clone();
            
            tauri::async_runtime::spawn(async move {
                if let Err(e) = start_python_server(state, window_clone).await {
                    println!("Failed to auto-start server: {}", e);
                }
            });
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}