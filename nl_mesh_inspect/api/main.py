"""
FastAPI主应用 - 提供RESTful API接口
"""

import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional

from nl_mesh_inspect.agent import NLMeshInspectAgent
from nl_mesh_inspect.models import (
    AnalysisRequest, AnalysisResult, ModelInfo, ModelFormat,
    ErrorResponse, RealTimeUpdate
)

# 创建应用实例
app = FastAPI(
    title="NL-Mesh-Inspect API",
    description="自然语言3D模型交互与检测平台",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建智能体实例
agent = NLMeshInspectAgent(upload_dir="uploads")

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # 移除失效的连接
                self.active_connections.remove(connection)

manager = ConnectionManager()


@app.get("/")
async def root():
    """根端点 - 返回API信息"""
    return {
        "message": "NL-Mesh-Inspect API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": "2026-01-19T00:00:00Z"}


@app.post("/api/models/upload", response_model=dict)
async def upload_model(
    file: UploadFile = File(...),
    file_format: ModelFormat = Form(...)
):
    """上传3D模型文件"""
    try:
        # FastAPI 已自动验证和转换格式，直接使用
        model_format = file_format

        # 读取文件内容
        file_content = await file.read()

        # 处理上传
        result = agent.process_upload(
            file_content=file_content,
            filename=file.filename,
            file_format=model_format.value
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        # 广播上传成功消息
        update = RealTimeUpdate(
            type="model_uploaded",
            model_id=result["model_id"],
            data={"filename": file.filename, "format": model_format.value}
        )
        await manager.broadcast(update.json())

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.post("/api/models/{model_id}/analyze", response_model=AnalysisResult)
async def analyze_model(
    model_id: str,
    request: AnalysisRequest
):
    """分析3D模型"""
    try:
        # 设置模型ID（从路径参数获取）
        request.model_id = model_id

        # 执行分析
        result = agent.analyze_model(request)

        # 广播分析结果
        if result.success:
            update = RealTimeUpdate(
                type="analysis_completed",
                model_id=model_id,
                data={
                    "query": request.natural_language_query,
                    "result_type": result.result_type,
                    "execution_time": result.execution_time
                }
            )
            await manager.broadcast(update.json())

        return result

    except Exception as e:
        return AnalysisResult(
            success=False,
            result_type="api_error",
            data={"error": str(e)},
            message=f"API错误: {str(e)}",
            execution_time=0.0,
            state_id=agent.get_current_state()
        )


@app.get("/api/models/{model_id}", response_model=ModelInfo)
async def get_model_info(model_id: str):
    """获取模型信息"""
    model_info = agent.get_model_info(model_id)

    if not model_info:
        raise HTTPException(status_code=404, detail=f"模型不存在: {model_id}")

    return model_info


@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    """删除模型"""
    success = agent.cleanup_model(model_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"模型不存在或删除失败: {model_id}")

    # 广播删除消息
    update = RealTimeUpdate(
        type="model_deleted",
        model_id=model_id,
        data={"message": "模型已删除"}
    )
    await manager.broadcast(update.json())

    return {"message": "模型删除成功"}


@app.get("/api/models")
async def list_models():
    """列出所有模型"""
    # 这里应该从数据库或文件系统中获取模型列表
    # 目前返回空列表，后续实现
    return {"models": []}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点 - 实时通信"""
    await manager.connect(websocket)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()

            # 处理不同类型的消息
            # 这里可以添加消息处理逻辑

            # 发送确认消息
            response = RealTimeUpdate(
                type="message_received",
                model_id="",
                data={"original_message": data}
            )
            await manager.send_personal_message(response.json(), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            state_id=agent.get_current_state()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="内部服务器错误",
            details={"message": str(exc)},
            state_id=agent.get_current_state()
        ).dict()
    )


# 创建上传目录
os.makedirs("uploads", exist_ok=True)

# 挂载静态文件（用于前端）
# 前端独立部署，暂时注释静态文件挂载
# app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)