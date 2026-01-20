"""
NL-Mesh-Inspect: 自然语言3D模型交互与检测平台

基于自然语言的3D模型分析与质量检测平台，支持用户通过简单自然语言指令
完成复杂的3D模型交互、几何分析和拓扑检测。
"""

__version__ = "0.1.0"
__author__ = "NL-Mesh-Platform Team"
__email__ = "team@nl-mesh-platform.com"

from nl_mesh_inspect.agent import NLMeshInspectAgent
from nl_mesh_inspect.models import (
    ModelUploadRequest,
    AnalysisRequest,
    AnalysisResult,
    GeometricFeature,
    TopologyCheckResult
)

__all__ = [
    "NLMeshInspectAgent",
    "ModelUploadRequest",
    "AnalysisRequest",
    "AnalysisResult",
    "GeometricFeature",
    "TopologyCheckResult"
]