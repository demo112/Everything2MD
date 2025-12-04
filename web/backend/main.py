import os
import json
import asyncio
import subprocess
import logging
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket 管理 ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃，也可以接收前端指令
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# --- 配置 API ---
CONFIG_FILE = "/work/config.json"

@app.get("/api/config")
def get_config():
    default_config = {
        "conversion_settings": {
            "log_level": "INFO",
            "output_format": "markdown",
            "batch_processing": {
                "enabled": False,
                "max_parallel_jobs": 4,
                "file_filters": []
            }
        }
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return default_config
    return default_config

@app.post("/api/config")
def update_config(config: dict = Body(...)):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 文件列表 API (Web文件选择器优化及全盘访问) ---
@app.get("/api/fs/list")
def list_files(path: str = "", only_dir: bool = False):
    """
    列出指定目录下的文件和文件夹
    """
    try:
        # 特殊处理根视图 ROOT
        if path == "ROOT":
            items = []
            # 扫描挂载的盘符
            if os.path.exists("/mnt"):
                for d in os.listdir("/mnt"):
                    # 简单过滤，通常盘符是单字母
                    if len(d) == 1:
                        items.append({"name": f"{d.upper()}: 盘", "path": f"/mnt/{d}"})
            
            # 添加项目工作目录
            items.append({"name": "项目目录 (Work)", "path": "/work"})
            
            return {
                "current_path": "ROOT",
                "parent_path": None,
                "folders": items,
                "files": []
            }

        # 默认为当前工作目录
        if not path:
            path = "/work" # 默认使用容器内的 /work
        
        # 路径安全检查（防止遍历到系统敏感目录，但在容器内相对安全）
        # 这里直接使用绝对路径
        if not os.path.isabs(path):
             path = os.path.abspath(os.path.join("/work", path))

        if not os.path.exists(path):
            return {"error": f"路径不存在: {path}"}
            
        if not os.path.isdir(path):
            return {"error": f"路径不是文件夹: {path}"}

        items = os.listdir(path)
        folders = []
        files = []
        
        # 排序，文件夹在前
        items.sort()
        
        for item in items:
            full_path = os.path.join(path, item)
            # 忽略隐藏文件
            if item.startswith('.'):
                continue
                
            try:
                if os.path.isdir(full_path):
                    folders.append({"name": item, "path": full_path})
                elif not only_dir:
                    files.append({"name": item, "path": full_path})
            except OSError:
                pass # 忽略权限错误
        
        # 计算父级路径
        parent = os.path.dirname(path)
        # 如果当前是 /work 或 /mnt/x，父级指向 ROOT
        # 注意 Windows 挂载到 /mnt/c， dirname 是 /mnt
        if path == "/work" or path == "/mnt" or os.path.dirname(path) == "/mnt":
            parent = "ROOT"
        elif parent == path: # 已经是系统根目录
            parent = "ROOT"
        
        return {
            "current_path": path,
            "parent_path": parent,
            "folders": folders,
            "files": files
        }
    except Exception as e:
        return {"error": str(e)}

# --- 转换 API ---
class ConvertRequest(BaseModel):
    input_path: str
    output_path: Optional[str] = None

@app.post("/api/convert")
async def convert_files(request: ConvertRequest):
    input_path = request.input_path
    output_path = request.output_path
    
    if not input_path:
        raise HTTPException(status_code=400, detail="Input path is required")

    # 异步执行转换任务
    asyncio.create_task(run_conversion(input_path, output_path))
    return {"status": "started", "message": "Conversion task started"}

async def run_conversion(input_path: str, output_path: str = None):
    cmd = ["bash", "src/main.sh", "-i", input_path]
    if output_path:
        cmd.extend(["-o", output_path])
        
    # 添加配置参数
    # 这里简单处理，实际应该解析 config.json 并传递参数
    # 假设 main.sh 会读取环境变量或默认配置
    
    try:
        await manager.broadcast(f"Starting conversion for: {input_path}\n")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/work"
        )
        
        # 读取 stdout
        async def read_stream(stream, is_stderr=False):
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode('utf-8', errors='replace')
                # 发送给前端
                await manager.broadcast(text)
        
        await asyncio.gather(
            read_stream(process.stdout),
            read_stream(process.stderr, is_stderr=True)
        )
        
        await process.wait()
        
        if process.returncode == 0:
            await manager.broadcast("\nTask Finished Successfully!\n")
        else:
            await manager.broadcast(f"\nTask Finished with Error (Code: {process.returncode})\n")
            
    except Exception as e:
        await manager.broadcast(f"Error executing task: {str(e)}\n")

# --- 静态文件服务 (最后注册) ---
# 挂载前端静态文件
FRONTEND_DIR = "/work/web/frontend"
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"message": "Frontend directory not found. Please check deployment."}

