"""
基于大模型的LangGraph智能体 - 使用DeepSeek-V3.1进行3D模型分析
"""

from typing import Dict, Any, List, TypedDict, Annotated
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

from nl_mesh_inspect.llm_config import llm_with_tools, execute_tool
from nl_mesh_inspect.models import AnalysisRequest, AnalysisResult, ModelInfo
from nl_mesh_inspect.tools import ModelProcessor


class AgentState(TypedDict):
    """智能体状态定义"""

    # 输入
    request: AnalysisRequest

    # 中间状态
    messages: Annotated[List[Dict[str, Any]], "messages"]
    mesh_data: Dict[str, Any]

    # 执行结果
    tool_results: List[Dict[str, Any]]
    final_result: AnalysisResult

    # 控制状态
    max_steps: int
    current_step: int


class LLMNLMeshAgent:
    """基于大模型的NL-Mesh-Inspect智能体"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.model_processor = ModelProcessor(upload_dir)

        # 模型缓存
        self.model_cache: Dict[str, Dict[str, Any]] = {}
        self.current_state_id: str = str(uuid.uuid4())

        # 构建LangGraph工作流
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """构建LangGraph工作流"""

        # 创建工作流图
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("load_model", self._load_model)
        workflow.add_node("llm_analysis", self._llm_analysis)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("generate_final_result", self._generate_final_result)
        workflow.add_node("handle_error", self._handle_error)

        # 设置入口点
        workflow.set_entry_point("validate_input")

        # 添加边（正常流程）
        workflow.add_edge("validate_input", "load_model")
        workflow.add_edge("load_model", "llm_analysis")
        workflow.add_edge("llm_analysis", "execute_tools")
        workflow.add_edge("execute_tools", "generate_final_result")
        workflow.add_edge("generate_final_result", END)

        # 添加条件边
        workflow.add_conditional_edges(
            "validate_input",
            self._should_handle_error,
            {"error": "handle_error", "continue": "load_model"}
        )

        workflow.add_conditional_edges(
            "load_model",
            self._should_handle_error,
            {"error": "handle_error", "continue": "llm_analysis"}
        )

        workflow.add_conditional_edges(
            "llm_analysis",
            self._should_handle_error,
            {"error": "handle_error", "continue": "execute_tools"}
        )

        workflow.add_conditional_edges(
            "execute_tools",
            self._should_handle_error,
            {"error": "handle_error", "continue": "generate_final_result"}
        )

        workflow.add_edge("handle_error", END)

        return workflow.compile()

    def _should_handle_error(self, state: AgentState) -> str:
        """判断是否应该处理错误"""
        return "error" if state.get("error") else "continue"

    def _validate_input(self, state: AgentState) -> AgentState:
        """验证输入参数"""
        try:
            request = state["request"]

            # 验证状态ID
            if request.state_id != self.current_state_id:
                state["error"] = f"状态ID不匹配: 期望 {self.current_state_id}, 实际 {request.state_id}"
                return state

            # 验证模型ID
            if not request.model_id:
                state["error"] = "缺少模型ID"
                return state

            # 验证查询
            if not request.natural_language_query:
                state["error"] = "缺少自然语言查询"
                return state

            return state

        except Exception as e:
            state["error"] = f"输入验证错误: {str(e)}"
            return state

    def _load_model(self, state: AgentState) -> AgentState:
        """加载模型数据"""
        try:
            request = state["request"]

            if request.model_id not in self.model_cache:
                state["error"] = f"未找到模型: {request.model_id}"
                return state

            model_data = self.model_cache[request.model_id]
            state["mesh_data"] = model_data

            return state

        except Exception as e:
            state["error"] = f"模型加载错误: {str(e)}"
            return state

    def _llm_analysis(self, state: AgentState) -> AgentState:
        """使用LLM分析查询意图并决定使用哪些工具"""
        try:
            request = state["request"]
            mesh_data = state["mesh_data"]

            # 构建系统消息
            system_message = {
                "role": "system",
                "content": f"""
                你是一个3D模型分析专家，负责分析用户对3D模型的自然语言查询，并决定使用哪些工具来分析模型。

                可用的工具：
                - 测量工具：测量体积、表面积等
                - 特征检测工具：检测孔洞、面等特征
                - 拓扑分析工具：检查拓扑结构、连通性等

                模型信息：
                - 文件名：{mesh_data.get('model_info', {}).get('file_name', '未知')}
                - 格式：{mesh_data.get('model_info', {}).get('file_format', '未知')}

                用户查询：{request.natural_language_query}

                请分析用户意图并决定使用哪些工具。
                """
            }

            # 构建用户消息
            user_message = {
                "role": "user",
                "content": f"请分析这个3D模型：{request.natural_language_query}"
            }

            # 初始化消息列表
            state["messages"] = [system_message, user_message]

            # 调用LLM
            response = llm_with_tools.invoke(state["messages"])

            # 添加LLM响应到消息列表
            state["messages"].append({
                "role": "assistant",
                "content": response.content
            })

            # 初始化工具结果列表
            state["tool_results"] = []

            return state

        except Exception as e:
            state["error"] = f"LLM分析错误: {str(e)}"
            return state

    def _execute_tools(self, state: AgentState) -> AgentState:
        """执行LLM选择的工具"""
        try:
            if not state.get("messages"):
                state["error"] = "没有可用的LLM响应"
                return state

            # 获取最后一个LLM响应
            last_message = state["messages"][-1]

            # 检查是否有工具调用
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    # 执行工具
                    result = execute_tool(tool_name, tool_args, state["mesh_data"])
                    state["tool_results"].append(result)

                    # 添加工具执行结果到消息列表
                    state["messages"].append({
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": tool_call["id"]
                    })

            # 如果没有工具调用，模拟一些工具执行
            elif not state.get("tool_results"):
                # 模拟执行一些工具
                result1 = execute_tool("MeasureVolumeTool", {}, state["mesh_data"])
                result2 = execute_tool("CheckTopologyTool", {}, state["mesh_data"])
                state["tool_results"].extend([result1, result2])

            return state

        except Exception as e:
            state["error"] = f"工具执行错误: {str(e)}"
            return state

    def _generate_final_result(self, state: AgentState) -> AgentState:
        """生成最终分析结果"""
        try:
            request = state["request"]
            tool_results = state.get("tool_results", [])

            # 构建结果数据
            result_data = {
                "query": request.natural_language_query,
                "tool_results": tool_results,
                "tools_used": len(tool_results)
            }

            # 生成响应消息
            message = f"分析完成。使用了 {len(tool_results)} 个工具进行分析。"

            # 创建最终结果
            final_result = AnalysisResult(
                success=True,
                result_type="llm_analysis",
                data=result_data,
                message=message,
                features=[],
                execution_time=0.0,  # 将在analyze_model中更新
                state_id=self.current_state_id
            )

            state["final_result"] = final_result
            return state

        except Exception as e:
            state["error"] = f"结果生成错误: {str(e)}"
            return state

    def _handle_error(self, state: AgentState) -> AgentState:
        """处理错误"""
        error_message = state.get("error", "未知错误")

        final_result = AnalysisResult(
            success=False,
            result_type="error",
            data={"error": error_message},
            message=f"处理过程中发生错误: {error_message}",
            execution_time=0.0,
            state_id=self.current_state_id
        )

        state["final_result"] = final_result
        return state

    def analyze_model(self, request: AnalysisRequest) -> AnalysisResult:
        """分析模型 - 主入口点"""
        start_time = datetime.now()

        # 初始化状态
        initial_state: AgentState = {
            "request": request,
            "messages": [],
            "mesh_data": {},
            "tool_results": [],
            "final_result": None,
            "max_steps": 10,
            "current_step": 0
        }

        # 执行工作流
        final_state = self.workflow.invoke(initial_state)

        # 计算执行时间
        execution_time = (datetime.now() - start_time).total_seconds()

        # 更新执行时间
        if final_state.get("final_result"):
            final_state["final_result"].execution_time = execution_time

        return final_state.get("final_result", AnalysisResult(
            success=False,
            result_type="unknown_error",
            data={},
            message="处理过程中发生未知错误",
            execution_time=execution_time,
            state_id=self.current_state_id
        ))

    # 以下方法保持与原有接口兼容
    def process_upload(self, file_content: bytes, filename: str, file_format: str) -> Dict[str, Any]:
        """处理模型上传"""
        try:
            # 模拟模型处理
            model_id = str(uuid.uuid4())

            # 创建模拟模型数据
            from nl_mesh_inspect.models import ModelInfo, TopologyCheckResult

            model_info = ModelInfo(
                model_id=model_id,
                file_name=filename,
                file_format=file_format,
                upload_time=datetime.now(),
                file_size=1024,  # 模拟文件大小
                vertex_count=100,  # 模拟顶点数
                face_count=200,  # 模拟面数
                bounding_box=[0, 0, 0, 10, 10, 10],  # 边界框 [min_x, min_y, min_z, max_x, max_y, max_z]
                features=[]
            )

            topology_result = TopologyCheckResult(
                is_manifold=True,
                has_self_intersections=False,
                is_watertight=True,
                issues=[]
            )

            self.model_cache[model_id] = {
                "mesh": {"vertices": 100, "faces": 200},  # 模拟网格数据
                "model_info": model_info,
                "topology_result": topology_result,
                "file_path": f"/uploads/{filename}"
            }

            self.current_state_id = str(uuid.uuid4())

            return {
                "success": True,
                "model_id": model_id,
                "model_info": model_info.dict(),
                "topology_result": topology_result.dict(),
                "state_id": self.current_state_id
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "state_id": self.current_state_id
            }

    def get_model_info(self, model_id: str):
        """获取模型信息"""
        if model_id in self.model_cache:
            return self.model_cache[model_id]["model_info"]
        return None

    def cleanup_model(self, model_id: str) -> bool:
        """清理模型数据"""
        try:
            if model_id in self.model_cache:
                model_data = self.model_cache[model_id]
                self.model_processor.cleanup_file(model_data["file_path"])
                del self.model_cache[model_id]
                self.current_state_id = str(uuid.uuid4())
                return True
        except Exception:
            pass
        return False

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return "基于大模型的3D模型分析智能体"

    def get_current_state(self) -> str:
        """获取当前状态ID"""
        return self.current_state_id