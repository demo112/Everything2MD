const API_BASE = '/api';
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_URL = `${WS_PROTOCOL}//${window.location.host}/ws/logs`;

let socket = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    connectWebSocket();
});

// WebSocket Connection
function connectWebSocket() {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return;

    console.log(`Connecting to WebSocket at ${WS_URL}...`);
    socket = new WebSocket(WS_URL);
    
    socket.onopen = () => {
        console.log("WebSocket connected");
        document.getElementById('statusText').textContent = '就绪';
    };

    socket.onmessage = (event) => {
        logToTerminal(event.data);
        if (event.data.includes("Task Finished")) {
             document.getElementById('loadingIndicator').style.display = 'none';
             document.getElementById('convertBtn').disabled = false;
             document.getElementById('statusText').textContent = '已完成';
        }
    };
    
    socket.onclose = () => {
        console.log("WebSocket disconnected");
        setTimeout(connectWebSocket, 3000);
    };
    
    socket.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}

// Load Configuration
async function loadConfig() {
    try {
        const res = await fetch(`${API_BASE}/config`);
        const config = await res.json();
        const settings = config.conversion_settings;

        document.getElementById('logLevel').value = settings.log_level;
        document.getElementById('outputFormat').value = settings.output_format;
        document.getElementById('batchProcessing').checked = settings.batch_processing.enabled === 'true' || settings.batch_processing.enabled === true;
        document.getElementById('maxJobs').value = settings.batch_processing.max_parallel_jobs;
        document.getElementById('fileFilters').value = Array.isArray(settings.batch_processing.file_filters) 
            ? settings.batch_processing.file_filters.join(',') 
            : settings.batch_processing.file_filters;

    } catch (err) {
        console.error('Failed to load config:', err);
        logToTerminal('加载配置失败。\n', 'error');
    }
}

// Save Configuration
async function saveConfig() {
    const config = {
        conversion_settings: {
            log_level: document.getElementById('logLevel').value,
            output_format: document.getElementById('outputFormat').value,
            batch_processing: {
                enabled: document.getElementById('batchProcessing').checked ? "true" : "false",
                max_parallel_jobs: document.getElementById('maxJobs').value,
                file_filters: document.getElementById('fileFilters').value.split(',').map(s => s.trim()).filter(s => s)
            }
        }
    };

    try {
        await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
    } catch (err) {
        console.error('Failed to save config:', err);
    }
}

let currentModalPath = "";
let currentModalType = "file"; // 'file' or 'folder'
let currentTargetInput = null;
let selectedPath = null;
let lastData = null; // NEW: Store last fetched data for navigation

function openFilePicker(inputId, type) {
    currentTargetInput = document.getElementById(inputId);
    currentModalType = type;
    selectedPath = null;
    
    const modal = document.getElementById("filePickerModal");
    const display = document.getElementById("selectedItemDisplay");
    
    modal.classList.add("active");
    display.textContent = "";
    
    let initialPath = currentTargetInput ? currentTargetInput.value : "";
    fetchFileList(initialPath);
}

function closeFilePicker() {
    document.getElementById("filePickerModal").classList.remove("active");
}

function confirmSelection() {
    if (selectedPath && currentTargetInput) {
        // If nothing selected but mode is folder, maybe use currentModalPath?
        if (!selectedPath && currentModalType === 'folder') {
             selectedPath = currentModalPath;
        }
        
        if (selectedPath) {
             currentTargetInput.value = selectedPath;
        }
    }
    closeFilePicker();
}

async function fetchFileList(path) {
    try {
        const onlyDir = false; 
        let url = `/api/fs/list?only_dir=${onlyDir}`;
        if (path) {
            url += `&path=${encodeURIComponent(path)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            // Only alert if it's not an initial load attempt that failed
            if (path) {
                 alert(data.error);
                 fetchFileList(""); // Fallback to root
            }
            return;
        }
        
        lastData = data;
        renderFileList(data);
    } catch (error) {
        console.error('Error fetching file list:', error);
        alert("获取文件列表失败");
    }
}

function renderFileList(data) {
    currentModalPath = data.current_path;
    document.getElementById("currentPathInput").value = currentModalPath === "ROOT" ? "我的电脑" : currentModalPath;
    
    const listContainer = document.getElementById("fileList");
    listContainer.innerHTML = "";
    
    // .. (Parent Dir)
    if (data.parent_path) {
        const itemDiv = document.createElement("div");
        itemDiv.className = "file-item";
        itemDiv.innerHTML = `<span class="file-icon folder-icon">📁</span> ..`;
        itemDiv.onclick = () => fetchFileList(data.parent_path);
        listContainer.appendChild(itemDiv);
    }
    
    // Folders
    data.folders.forEach(item => {
        const name = item.name || item;
        const path = item.path || `${data.current_path}/${name}`.replace(/\/+/g, '/');
        
        const itemDiv = document.createElement("div");
        itemDiv.className = "file-item";
        itemDiv.innerHTML = `<span class="file-icon folder-icon">📁</span> ${name}`;
        
        itemDiv.onclick = () => selectItem(itemDiv, path);
        itemDiv.ondblclick = () => fetchFileList(path);
        listContainer.appendChild(itemDiv);
    });
    
    // Files
    if (currentModalType === 'file') {
        data.files.forEach(item => {
            const name = item.name || item;
            const path = item.path || `${data.current_path}/${name}`.replace(/\/+/g, '/');

            const itemDiv = document.createElement("div");
            itemDiv.className = "file-item";
            itemDiv.innerHTML = `<span class="file-icon file-icon-default">📄</span> ${name}`;
            
            itemDiv.onclick = () => selectItem(itemDiv, path);
            listContainer.appendChild(itemDiv);
        });
    }
}

function selectItem(element, path) {
    const prev = document.querySelector(".file-item.selected");
    if (prev) prev.classList.remove("selected");
    
    element.classList.add("selected");
    selectedPath = path;
    
    document.getElementById("selectedItemDisplay").textContent = `已选择: ${path}`;
}

function navigateUp() {
    if (lastData && lastData.parent_path) {
        fetchFileList(lastData.parent_path);
    }
}

async function selectPath(target, type) {
    let inputId = target;
    if (target === 'input') inputId = 'inputPath';
    else if (target === 'output') inputId = 'outputPath';
    
    openFilePicker(inputId, type);
}

async function startConversion() {
    const inputPath = document.getElementById('inputPath').value;
    const outputPath = document.getElementById('outputPath').value;

    if (!inputPath) {
        alert('请选择输入文件或目录。');
        return;
    }

    const btn = document.getElementById('convertBtn');
    const terminal = document.getElementById('terminal');
    const statusText = document.getElementById('statusText');
    const loading = document.getElementById('loadingIndicator');

    btn.disabled = true;
    loading.style.display = 'inline';
    statusText.textContent = '启动中...';
    terminal.textContent = '正在提交任务...\n';

    await saveConfig();

    try {
        const res = await fetch(`${API_BASE}/convert`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input_path: inputPath,
                output_path: outputPath || null
            })
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || '未知错误');
        }

        const result = await res.json();
        
        logToTerminal('任务已启动，等待日志...\n', 'success');
        statusText.textContent = '运行中';

    } catch (err) {
        logToTerminal('错误: ' + err.message + '\n', 'error');
        statusText.textContent = '错误';
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

function logToTerminal(text, type = 'info') {
    const terminal = document.getElementById('terminal');
    const div = document.createElement('div');
    div.textContent = text;
    if (type === 'error') div.style.color = '#ff5555';
    else if (type === 'success') div.style.color = '#50fa7b';
    
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}
