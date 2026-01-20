"""
数据模型定义 - Pydantic模型用于数据验证和序列化
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ModelFormat(str, Enum):
    """支持的3D模型格式"""
    STL = "stl"
    OBJ = "obj"
    PLY = "ply"
    STEP = "step"


class AnalysisIntent(str, Enum):
    """分析意图类型"""
    QUERY = "query"  # 查询信息
    OPERATION = "operation"  # 执行操作
    MODIFICATION = "modification"  # 修改模型


class GeometricEntity(str, Enum):
    """几何实体类型"""
    VERTEX = "vertex"
    EDGE = "edge"
    FACE = "face"
    HOLE = "hole"
    CYLINDER = "cylinder"
    PLANE = "plane"
    SPHERE = "sphere"


class ModelUploadRequest(BaseModel):
    """模型上传请求"""
    file_name: str = Field(..., description="文件名")
    file_format: ModelFormat = Field(..., description="文件格式")
    file_size: int = Field(..., description="文件大小(字节)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class GeometricFeature(BaseModel):
    """几何特征"""
    entity_type: GeometricEntity = Field(..., description="实体类型")
    indices: List[int] = Field(..., description="索引列表")
    properties: Dict[str, Any] = Field(default_factory=dict, description="属性")
    bounding_box: Optional[List[float]] = Field(default=None, description="边界框")


class TopologyCheckResult(BaseModel):
    """拓扑检查结果"""
    is_manifold: bool = Field(..., description="是否为流形")
    has_self_intersections: bool = Field(..., description="是否有自相交")
    is_watertight: bool = Field(..., description="是否水密")
    issues: List[str] = Field(default_factory=list, description="问题列表")


class AnalysisRequest(BaseModel):
    """分析请求"""
    model_id: str = Field(..., description="模型ID")
    natural_language_query: str = Field(..., description="自然语言查询")
    intent: Optional[AnalysisIntent] = Field(default=None, description="分析意图")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数")
    state_id: str = Field(..., description="状态ID用于并发控制")


class AnalysisResult(BaseModel):
    """分析结果"""
    success: bool = Field(..., description="是否成功")
    result_type: str = Field(..., description="结果类型")
    data: Dict[str, Any] = Field(..., description="结果数据")
    message: str = Field(..., description="消息")
    features: List[GeometricFeature] = Field(default_factory=list, description="检测到的特征")
    execution_time: float = Field(..., description="执行时间(秒)")
    state_id: str = Field(..., description="状态ID")


class ModelInfo(BaseModel):
    """模型信息"""
    model_id: str = Field(..., description="模型ID")
    file_name: str = Field(..., description="文件名")
    file_format: ModelFormat = Field(..., description="文件格式")
    file_size: int = Field(..., description="文件大小")
    vertex_count: int = Field(..., description="顶点数量")
    face_count: int = Field(..., description="面片数量")
    bounding_box: List[float] = Field(..., description="边界框")
    upload_time: datetime = Field(..., description="上传时间")
    features: List[GeometricFeature] = Field(default_factory=list, description="特征列表")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(default=None, description="详细信息")
    state_id: Optional[str] = Field(default=None, description="状态ID")


class RealTimeUpdate(BaseModel):
    """实时更新消息"""
    type: str = Field(..., description="更新类型")
    model_id: str = Field(..., description="模型ID")
    data: Dict[str, Any] = Field(..., description="更新数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")