"""
大模型配置模块 - 配置LLM并绑定3D模型分析工具
"""

from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import os


class MeasureVolumeTool(BaseModel):
    """测量体积工具"""

    mesh_data: Dict[str, Any] = Field(description="3D模型数据")

    def measure_volume(self) -> Dict[str, Any]:
        """测量体积"""
        return {
            "tool": "measure_volume",
            "result": {
                "volume": 1000.0,  # 模拟数据
                "unit": "mm³"
            }
        }


class MeasureSurfaceAreaTool(BaseModel):
    """测量表面积工具"""

    mesh_data: Dict[str, Any] = Field(description="3D模型数据")

    def measure_surface_area(self) -> Dict[str, Any]:
        """测量表面积"""
        return {
            "tool": "measure_surface_area",
            "result": {
                "surface_area": 500.0,  # 模拟数据
                "unit": "mm²"
            }
        }


class DetectHolesTool(BaseModel):
    """检测孔洞工具"""

    mesh_data: Dict[str, Any] = Field(description="3D模型数据")

    def detect_holes(self) -> Dict[str, Any]:
        """检测孔洞"""
        return {
            "tool": "detect_holes",
            "result": {
                "holes_count": 5,
                "holes": [
                    {"id": 1, "diameter": 10.0, "depth": 20.0},
                    {"id": 2, "diameter": 8.0, "depth": 15.0}
                ]
            }
        }


class DetectFacesTool(BaseModel):
    """检测面工具"""

    mesh_data: Dict[str, Any] = Field(description="3D模型数据")

    def detect_faces(self) -> Dict[str, Any]:
        """检测面"""
        return {
            "tool": "detect_faces",
            "result": {
                "faces_count": 12,
                "faces": [
                    {"id": 1, "area": 50.0, "normal": [0, 0, 1]},
                    {"id": 2, "area": 30.0, "normal": [1, 0, 0]}
                ]
            }
        }


class CheckTopologyTool(BaseModel):
    """检查拓扑工具"""

    mesh_data: Dict[str, Any] = Field(description="3D模型数据")

    def check_topology(self) -> Dict[str, Any]:
        """检查拓扑"""
        return {
            "tool": "check_topology",
            "result": {
                "is_watertight": True,
                "manifold": True,
                "issues": []
            }
        }


class AnalyzeConnectivityTool(BaseModel):
    """分析连通性工具"""

    mesh_data: Dict[str, Any] = Field(description="3D模型数据")

    def analyze_connectivity(self) -> Dict[str, Any]:
        """分析连通性"""
        return {
            "tool": "analyze_connectivity",
            "result": {
                "connected_components": 1,
                "edges_count": 100,
                "vertices_count": 50
            }
        }


# 工具列表（使用函数定义）
MESH_ANALYSIS_TOOLS = [
    MeasureVolumeTool,
    MeasureSurfaceAreaTool,
    DetectHolesTool,
    DetectFacesTool,
    CheckTopologyTool,
    AnalyzeConnectivityTool
]


def create_llm_with_tools(use_mock: bool = True):
    """
    创建绑定3D模型分析工具的LLM实例

    Args:
        use_mock: 是否使用模拟LLM（用于开发测试）

    Returns:
        ChatOpenAI: 绑定工具的大模型实例
    """
    if use_mock:
        # 使用模拟LLM进行开发测试
        from nl_mesh_inspect.mock_llm import mock_llm
        return mock_llm
    else:
        # 使用真实的OpenAI兼容接口配置
        llm = ChatOpenAI(
            openai_api_key="",  # 使用提供的API密钥
            openai_api_base="",  # 使用提供的API地址
            model_name="DeepSeek-V3.1",  # 使用DeepSeek模型
            temperature=0,  # 设置为0确保稳定性
            max_tokens=1000
        )

        # 绑定3D模型分析工具
        llm_with_tools = llm.bind_tools(MESH_ANALYSIS_TOOLS)

        return llm_with_tools


# 工具函数映射
def execute_tool(tool_name: str, tool_args: Dict[str, Any], mesh_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行工具函数

    Args:
        tool_name: 工具名称
        tool_args: 工具参数
        mesh_data: 模型数据

    Returns:
        Dict: 执行结果
    """
    # 将mesh_data添加到参数中
    tool_args["mesh_data"] = mesh_data

    if tool_name == "MeasureVolumeTool":
        tool = MeasureVolumeTool(**tool_args)
        return tool.measure_volume()
    elif tool_name == "MeasureSurfaceAreaTool":
        tool = MeasureSurfaceAreaTool(**tool_args)
        return tool.measure_surface_area()
    elif tool_name == "DetectHolesTool":
        tool = DetectHolesTool(**tool_args)
        return tool.detect_holes()
    elif tool_name == "DetectFacesTool":
        tool = DetectFacesTool(**tool_args)
        return tool.detect_faces()
    elif tool_name == "CheckTopologyTool":
        tool = CheckTopologyTool(**tool_args)
        return tool.check_topology()
    elif tool_name == "AnalyzeConnectivityTool":
        tool = AnalyzeConnectivityTool(**tool_args)
        return tool.analyze_connectivity()
    else:
        return {"error": f"未知工具: {tool_name}"}


# 创建模型实例（使用模拟模式进行开发测试）
llm_with_tools = create_llm_with_tools(use_mock=True)