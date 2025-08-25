/**
 * MCP SQL Server Results Display - 简化版本
 * 专门用于显示SQL查询结果，无用户交互功能
 */

class SQLResultsDisplay {
    constructor() {
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        
        this.init();
    }
    
    init() {
        console.log('Initializing SQL Results Display...');
        this.initWebSocket();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // 页面可见性变化时重连WebSocket
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && (!this.websocket || this.websocket.readyState !== WebSocket.OPEN)) {
                this.initWebSocket();
            }
        });
        
        // 窗口关闭前清理
        window.addEventListener('beforeunload', () => {
            if (this.websocket) {
                this.websocket.close();
            }
        });
    }
    
    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        console.log(`Connecting to WebSocket: ${wsUrl}`);
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.updateServerStatus('connected');
                this.displayInfo('已连接到服务器，等待SQL查询结果...');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                this.updateServerStatus('disconnected');
                
                // 自动重连
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                    setTimeout(() => {
                        this.initWebSocket();
                    }, this.reconnectDelay);
                } else {
                    this.displayError('连接已断开，请刷新页面重试');
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateServerStatus('disconnected');
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateServerStatus('disconnected');
            this.displayError('无法连接到服务器');
        }
    }
    
    handleWebSocketMessage(message) {
        console.log('Received message:', message);
        
        switch (message.type) {
            case 'sql_result':
            case 'query_results':
                this.displaySQLResults(message.data);
                break;
            case 'table_schema':
                this.displayTableSchema(message.data);
                break;
            case 'error':
                this.displayError(message.data);
                break;
            case 'info':
                this.displayInfo(message.data);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    updateServerStatus(status) {
        const statusElement = document.getElementById('serverStatus');
        const statusText = statusElement.querySelector('.status-text');
        
        statusElement.className = `server-status ${status}`;
        
        switch (status) {
            case 'connected':
                statusText.textContent = '已连接';
                break;
            case 'disconnected':
                statusText.textContent = '连接断开';
                break;
            default:
                statusText.textContent = '连接中...';
        }
    }
    
    displaySQLResults(data) {
        const resultsDiv = document.getElementById('sqlResults');
        const queryTitle = document.getElementById('queryTitle');
        const queryInfo = document.getElementById('queryInfo');
        const queryTime = document.getElementById('queryTime');
        const rowCount = document.getElementById('rowCount');
        
        // 更新查询信息
        if (data.query) {
            queryTitle.textContent = `查询结果: ${data.query.substring(0, 50)}${data.query.length > 50 ? '...' : ''}`;
        }
        
        if (data.timestamp) {
            queryTime.textContent = `执行时间: ${new Date(data.timestamp * 1000).toLocaleString()}`;
            queryInfo.style.display = 'flex';
        }
        
        // 显示错误
        if (data.error) {
            resultsDiv.innerHTML = `<div class="error-message">查询错误: ${data.error}</div>`;
            return;
        }
        
        // 显示结果
        const results = data.results || data.rows || [];
        const columns = data.columns || (results.length > 0 ? Object.keys(results[0]) : []);
        
        if (results.length > 0) {
            rowCount.textContent = `共 ${results.length} 行记录`;
            
            let html = '<table class="results-table"><thead><tr>';
            
            // 表头
            columns.forEach(col => {
                html += `<th>${this.escapeHtml(col)}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            // 数据行
            results.forEach(row => {
                html += '<tr>';
                if (Array.isArray(row)) {
                    // 数组格式
                    row.forEach(cell => {
                        html += `<td>${this.escapeHtml(this.formatCellValue(cell))}</td>`;
                    });
                } else {
                    // 对象格式
                    columns.forEach(col => {
                        html += `<td>${this.escapeHtml(this.formatCellValue(row[col]))}</td>`;
                    });
                }
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            html += `<div class="results-info">查询成功执行，返回 ${results.length} 行记录</div>`;
            
            resultsDiv.innerHTML = html;
        } else {
            resultsDiv.innerHTML = '<div class="empty-state"><p>查询执行成功，但没有返回数据</p></div>';
            rowCount.textContent = '0 行记录';
        }
        
        this.displayInfo('SQL查询结果已更新');
    }
    
    displayTableSchema(data) {
        const resultsDiv = document.getElementById('sqlResults');
        const queryTitle = document.getElementById('queryTitle');
        const queryInfo = document.getElementById('queryInfo');
        const queryTime = document.getElementById('queryTime');
        const rowCount = document.getElementById('rowCount');
        
        queryTitle.textContent = `表结构: ${data.schema_name}.${data.table_name}`;
        
        if (data.timestamp) {
            queryTime.textContent = `查询时间: ${new Date(data.timestamp * 1000).toLocaleString()}`;
            queryInfo.style.display = 'flex';
        }
        
        const schemaInfo = data.schema_info || [];
        
        if (schemaInfo.length > 0) {
            rowCount.textContent = `共 ${schemaInfo.length} 个字段`;
            
            let html = '<table class="results-table"><thead><tr>';
            html += '<th>字段名</th><th>数据类型</th><th>允许空值</th><th>默认值</th><th>说明</th>';
            html += '</tr></thead><tbody>';
            
            schemaInfo.forEach(field => {
                html += '<tr>';
                html += `<td><strong>${this.escapeHtml(field.column_name || field.name || '')}</strong></td>`;
                html += `<td>${this.escapeHtml(field.data_type || field.type || '')}</td>`;
                html += `<td>${field.is_nullable ? '是' : '否'}</td>`;
                html += `<td>${this.escapeHtml(field.default_value || field.default || '-')}</td>`;
                html += `<td>${this.escapeHtml(field.description || field.comment || '-')}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            html += `<div class="results-info">表结构信息，共 ${schemaInfo.length} 个字段</div>`;
            
            resultsDiv.innerHTML = html;
        } else {
            resultsDiv.innerHTML = '<div class="empty-state"><p>未找到表结构信息</p></div>';
            rowCount.textContent = '0 个字段';
        }
        
        this.displayInfo('表结构信息已更新');
    }
    
    formatCellValue(value) {
        if (value === null || value === undefined) {
            return 'NULL';
        }
        if (typeof value === 'string' && value.length > 100) {
            return value.substring(0, 100) + '...';
        }
        return String(value);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    displayError(message) {
        this.displayNotification('error', typeof message === 'string' ? message : JSON.stringify(message));
    }
    
    displayInfo(message) {
        this.displayNotification('info', message);
    }
    
    displayNotification(type, message) {
        const container = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        // 自动移除通知
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.sqlDisplay = new SQLResultsDisplay();
});
