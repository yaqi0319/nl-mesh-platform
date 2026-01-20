"""
主智能体模块 - 协调自然语言处理和几何分析工作流

注意：此文件现在使用基于大模型的LangGraph智能体架构
"""

from typing import Dict, Any, Optional

from nl_mesh_inspect.models import AnalysisRequest, AnalysisResult, ModelInfo
from nl_mesh_inspect.llm_agent import LLMNLMeshAgent


class NLMeshInspectAgent:
    """NL-Mesh-Inspect 主智能体（兼容层）

    此智能体使用基于DeepSeek-V3.1大模型的LangGraph架构，保持向后兼容的接口
    """

    def __init__(self, upload_dir: str = "uploads"):
        # 使用基于大模型的LangGraph智能体
        self.langgraph_agent = LLMNLMeshAgent(upload_dir)
        # 向后兼容的属性
        self.current_state_id = self.langgraph_agent.current_state_id

    def process_upload(self, file_content: bytes, filename: str, file_format: str) -> Dict[str, Any]:
        """处理模型上传"""
        return self.langgraph_agent.process_upload(file_content, filename, file_format)

    def analyze_model(self, request: AnalysisRequest) -> AnalysisResult:
        """分析模型"""
        return self.langgraph_agent.analyze_model(request)


    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """获取模型信息"""
        return self.langgraph_agent.get_model_info(model_id)

    def cleanup_model(self, model_id: str) -> bool:
        """清理模型数据"""
        return self.langgraph_agent.cleanup_model(model_id)

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.langgraph_agent.get_system_prompt()

    def get_current_state(self) -> str:
        """获取当前状态ID"""
        return self.langgraph_agent.get_current_state()