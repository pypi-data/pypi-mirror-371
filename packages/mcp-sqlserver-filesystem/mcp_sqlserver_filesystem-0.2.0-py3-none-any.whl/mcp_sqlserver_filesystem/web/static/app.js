// Check if running in Tauri
const isTauri = window.__TAURI__ !== undefined;

class MCPDesktopApp {
    constructor() {
        this.serverStatus = 'connecting';
        this.websocket = null;
        this.currentTab = 'database';
        this.settings = {
            dbServer: 'localhost\\SQLEXPRESS',
            dbName: 'master', 
            authType: 'windows',
            dbUser: '',
            dbPassword: ''
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.initWebSocket();
        
        if (isTauri) {
            this.initTauriFeatures();
        }
        
        // Set initial tab
        this.switchTab('database');
    }
    
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const tabName = item.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
        
        // Settings modal
        const settingsBtn = document.getElementById('settingsBtn');
        const settingsModal = document.getElementById('settingsModal');
        const closeBtns = document.querySelectorAll('.close-btn');
        
        settingsBtn.addEventListener('click', () => {
            settingsModal.style.display = 'block';
            this.populateSettingsForm();
        });
        
        closeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                settingsModal.style.display = 'none';
            });
        });
        
        window.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.style.display = 'none';
            }
        });
        
        // Settings form
        document.getElementById('authType').addEventListener('change', (e) => {
            const sqlAuthGroup = document.getElementById('sqlAuthGroup');
            sqlAuthGroup.style.display = e.target.value === 'sql' ? 'block' : 'none';
        });
        
        document.getElementById('saveSettingsBtn').addEventListener('click', () => {
            this.saveSettings();
        });
        
        // Database operations
        document.getElementById('connectBtn').addEventListener('click', () => {
            this.connectDatabase();
        });
        
        document.getElementById('executeBtn').addEventListener('click', () => {
            this.executeSQLQuery();
        });
        
        document.getElementById('clearBtn').addEventListener('click', () => {
            document.getElementById('sqlEditor').value = '';
        });
        
        // File system operations
        document.getElementById('browseBtn').addEventListener('click', () => {
            this.browseFolder();
        });
        
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshFileList();
        });
        
        // Console operations
        document.getElementById('executeCommandBtn').addEventListener('click', () => {
            this.executeCommand();
        });
        
        document.getElementById('clearConsoleBtn').addEventListener('click', () => {
            document.getElementById('consoleOutput').innerHTML = '';
        });
        
        document.getElementById('consoleCommand').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeCommand();
            }
        });
    }
    
    initTauriFeatures() {
        // Listen for Tauri events
        if (window.__TAURI__?.event) {
            window.__TAURI__.event.listen('server-started', (event) => {
                console.log('Python server started:', event.payload);
                this.updateServerStatus('connected');
            });
        }
        
        // Start Python server automatically
        this.startPythonServer();
    }
    
    async startPythonServer() {
        if (!isTauri) return;
        
        try {
            const result = await window.__TAURI__.invoke('start_python_server');
            console.log('Server started:', result);
            this.updateServerStatus('connected');
        } catch (error) {
            console.error('Failed to start server:', error);
            this.updateServerStatus('disconnected');
        }
    }
    
    initWebSocket() {
        const wsUrl = 'ws://127.0.0.1:8765/ws';
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.updateServerStatus('connected');
            };
            
            this.websocket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateServerStatus('disconnected');
                
                // Retry connection after 3 seconds
                setTimeout(() => {
                    this.initWebSocket();
                }, 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateServerStatus('disconnected');
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateServerStatus('disconnected');
        }
    }
    
    updateServerStatus(status) {
        this.serverStatus = status;
        const statusElement = document.getElementById('serverStatus');
        const indicator = statusElement.querySelector('.status-indicator');
        const text = statusElement.querySelector('.status-text');
        
        indicator.className = `status-indicator ${status}`;
        
        switch (status) {
            case 'connected':
                text.textContent = '已连接';
                break;
            case 'disconnected':
                text.textContent = '已断开';
                break;
            default:
                text.textContent = '连接中...';
        }
    }
    
    handleWebSocketMessage(message) {
        console.log('Received message:', message);
        
        switch (message.type) {
            case 'sql_result':
                this.displaySQLResults(message.data);
                break;
            case 'file_list':
                this.displayFileList(message.data);
                break;
            case 'command_output':
                this.displayCommandOutput(message.data);
                break;
            case 'error':
                this.displayError(message.data);
                break;
        }
    }
    
    sendWebSocketMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        } else {
            console.error('WebSocket not connected');
            this.displayError('服务器连接已断开，请刷新页面重试');
        }
    }
    
    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
        
        this.currentTab = tabName;
    }
    
    loadSettings() {
        const saved = localStorage.getItem('mcp-settings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
    }
    
    saveSettings() {
        this.settings = {
            dbServer: document.getElementById('dbServer').value,
            dbName: document.getElementById('dbName').value,
            authType: document.getElementById('authType').value,
            dbUser: document.getElementById('dbUser').value,
            dbPassword: document.getElementById('dbPassword').value
        };
        
        localStorage.setItem('mcp-settings', JSON.stringify(this.settings));
        document.getElementById('settingsModal').style.display = 'none';
        
        this.displayInfo('设置已保存');
    }
    
    populateSettingsForm() {
        document.getElementById('dbServer').value = this.settings.dbServer;
        document.getElementById('dbName').value = this.settings.dbName;
        document.getElementById('authType').value = this.settings.authType;
        document.getElementById('dbUser').value = this.settings.dbUser;
        document.getElementById('dbPassword').value = this.settings.dbPassword;
        
        // Show/hide SQL auth fields
        const sqlAuthGroup = document.getElementById('sqlAuthGroup');
        sqlAuthGroup.style.display = this.settings.authType === 'sql' ? 'block' : 'none';
    }
    
    connectDatabase() {
        const message = {
            type: 'connect_database',
            data: this.settings
        };
        
        this.sendWebSocketMessage(message);
        this.displayInfo('正在连接数据库...');
    }
    
    executeSQLQuery() {
        const query = document.getElementById('sqlEditor').value.trim();
        if (!query) {
            this.displayError('请输入SQL查询语句');
            return;
        }
        
        const message = {
            type: 'execute_sql',
            data: { query }
        };
        
        this.sendWebSocketMessage(message);
        this.displayInfo('正在执行查询...');
    }
    
    displaySQLResults(data) {
        const resultsDiv = document.getElementById('sqlResults');
        
        if (data.error) {
            resultsDiv.innerHTML = `<div class="error-message">错误: ${data.error}</div>`;
            return;
        }
        
        if (data.rows && data.rows.length > 0) {
            let html = '<table class="results-table"><thead><tr>';
            
            // Headers
            data.columns.forEach(col => {
                html += `<th>${col}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            // Rows
            data.rows.forEach(row => {
                html += '<tr>';
                row.forEach(cell => {
                    html += `<td>${cell || ''}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            html += `<div class="results-info">查询返回 ${data.rows.length} 行记录</div>`;
            
            resultsDiv.innerHTML = html;
        } else {
            resultsDiv.innerHTML = '<div class="empty-state"><p>查询执行成功，但没有返回数据</p></div>';
        }
        
        // Update connection info if provided
        if (data.connection_info) {
            this.updateConnectionInfo(data.connection_info);
        }
    }
    
    updateConnectionInfo(info) {
        document.getElementById('connectionInfo').style.display = 'block';
        document.getElementById('serverName').textContent = info.server || '-';
        document.getElementById('databaseName').textContent = info.database || '-';
        document.getElementById('authMethod').textContent = info.auth_method || '-';
        
        // Enable execute button
        document.getElementById('executeBtn').disabled = false;
    }
    
    browseFolder() {
        if (isTauri && window.__TAURI__?.dialog) {
            // Use Tauri file dialog
            window.__TAURI__.dialog.open({
                directory: true,
                multiple: false
            }).then(path => {
                if (path) {
                    document.getElementById('currentPath').value = path;
                    this.loadFileList(path);
                }
            });
        } else {
            // Fallback to input
            const path = prompt('请输入文件夹路径:', 'C:\\');
            if (path) {
                document.getElementById('currentPath').value = path;
                this.loadFileList(path);
            }
        }
    }
    
    loadFileList(path) {
        const message = {
            type: 'list_files',
            data: { path }
        };
        
        this.sendWebSocketMessage(message);
    }
    
    refreshFileList() {
        const path = document.getElementById('currentPath').value;
        if (path) {
            this.loadFileList(path);
        }
    }
    
    displayFileList(data) {
        const fileList = document.getElementById('fileList');
        
        if (data.error) {
            fileList.innerHTML = `<div class="error-message">错误: ${data.error}</div>`;
            return;
        }
        
        if (data.files && data.files.length > 0) {
            let html = '';
            
            data.files.forEach(file => {
                const icon = file.type === 'directory' ? '📁' : '📄';
                html += `
                    <div class="file-item" onclick="app.handleFileClick('${file.path}', '${file.type}')">
                        <div class="file-icon">${icon}</div>
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-details">
                                ${file.type === 'file' ? this.formatFileSize(file.size) : '文件夹'} • 
                                ${new Date(file.modified).toLocaleString()}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            fileList.innerHTML = html;
        } else {
            fileList.innerHTML = '<div class="empty-state"><p>文件夹为空</p></div>';
        }
    }
    
    handleFileClick(path, type) {
        if (type === 'directory') {
            document.getElementById('currentPath').value = path;
            this.loadFileList(path);
        } else {
            // Handle file click (could open file, show properties, etc.)
            this.displayInfo(`文件: ${path}`);
        }
    }
    
    executeCommand() {
        const command = document.getElementById('consoleCommand').value.trim();
        if (!command) return;
        
        // Clear input
        document.getElementById('consoleCommand').value = '';
        
        // Add command to output
        const output = document.getElementById('consoleOutput');
        output.innerHTML += `<div class="command-line">$ ${command}</div>`;
        
        const message = {
            type: 'execute_command',
            data: { command }
        };
        
        this.sendWebSocketMessage(message);
        
        // Scroll to bottom
        output.scrollTop = output.scrollHeight;
    }
    
    displayCommandOutput(data) {
        const output = document.getElementById('consoleOutput');
        
        if (data.output) {
            output.innerHTML += `<div class="command-output">${data.output}</div>`;
        }
        
        if (data.error) {
            output.innerHTML += `<div class="command-error">${data.error}</div>`;
        }
        
        // Scroll to bottom
        output.scrollTop = output.scrollHeight;
    }
    
    displayError(message) {
        this.displayNotification('error', message);
    }
    
    displayInfo(message) {
        this.displayNotification('info', message);
    }
    
    displayNotification(type, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MCPDesktopApp();
});

// Add notification styles
const notificationStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 24px;
    border-radius: 6px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    animation: slideIn 0.3s ease;
}

.notification.info {
    background: #17a2b8;
}

.notification.error {
    background: #dc3545;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.command-line {
    color: #4fc3f7;
    margin: 5px 0;
}

.command-output {
    color: #d4d4d4;
    margin: 5px 0;
    white-space: pre-wrap;
}

.command-error {
    color: #f48771;
    margin: 5px 0;
}

.error-message {
    color: #dc3545;
    padding: 15px;
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    margin: 10px 0;
}

.results-info {
    padding: 10px 0;
    color: #666;
    font-size: 12px;
    border-top: 1px solid #e9ecef;
    margin-top: 10px;
}
`;

// Add styles to document
const style = document.createElement('style');
style.textContent = notificationStyles;
document.head.appendChild(style);