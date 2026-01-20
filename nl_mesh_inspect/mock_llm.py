"""
模拟LLM模块 - 用于在没有真实API连接时的开发测试
"""

from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class MockLLM:
    """模拟LLM"""

    def invoke(self, messages: List[BaseMessage]) -> AIMessage:
        """模拟LLM调用"""
        # 提取用户消息
        user_content = ""
        for msg in messages:
            if isinstance(msg, HumanMessage):
                user_content = msg.content
                break

        # 根据用户查询生成响应
        if "测量体积" in user_content or "volume" in user_content.lower():
            return AIMessage(
                content="我将使用测量工具来分析这个3D模型的体积。",
                tool_calls=[{
                    "name": "MeasureVolumeTool",
                    "args": {},
                    "id": "1"
                }]
            )
        elif "测量表面积" in user_content or "surface area" in user_content.lower():
            return AIMessage(
                content="我将使用测量工具来分析这个3D模型的表面积。",
                tool_calls=[{
                    "name": "MeasureSurfaceAreaTool",
                    "args": {},
                    "id": "1"
                }]
            )
        elif "检测孔洞" in user_content or "holes" in user_content.lower():
            return AIMessage(
                content="我将使用特征检测工具来检测这个3D模型的孔洞。",
                tool_calls=[{
                    "name": "DetectHolesTool",
                    "args": {},
                    "id": "1"
                }]
            )
        elif "检查拓扑" in user_content or "topology" in user_content.lower():
            return AIMessage(
                content="我将使用拓扑分析工具来检查这个3D模型的拓扑结构。",
                tool_calls=[{
                    "name": "CheckTopologyTool",
                    "args": {},
                    "id": "1"
                }]
            )
        else:
            return AIMessage(
                content="我将综合分析这个3D模型。",
                tool_calls=[
                    {
                        "name": "MeasureVolumeTool",
                        "args": {},
                        "id": "1"
                    },
                    {
                        "name": "CheckTopologyTool",
                        "args": {},
                        "id": "2"
                    }
                ]
            )

    def bind_tools(self, tools):
        """模拟绑定工具"""
        return self


# 创建模拟LLM实例
mock_llm = MockLLM()