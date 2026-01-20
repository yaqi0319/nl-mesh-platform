"""
LangGraph智能体模块 - 使用LangGraph状态机架构的智能体
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from nl_mesh_inspect.models import (
    AnalysisRequest, AnalysisResult, ModelInfo, GeometricFeature, TopologyCheckResult
)
from nl_mesh_inspect.nlp_engine import QueryParser
from nl_mesh_inspect.tools import GeometryAnalyzer, ModelProcessor
from nl_mesh_inspect.prompts import SystemPrompts, ResponseTemplates


class LangGraphNLMeshAgent:
    """基于LangGraph的NL-Mesh-Inspect智能体（简化实现）"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.query_parser = QueryParser()
        self.model_processor = ModelProcessor(upload_dir)
        self.geometry_analyzer = GeometryAnalyzer()

        # 模型缓存
        self.model_cache: Dict[str, Dict[str, Any]] = {}
        self.current_state_id: str = str(uuid.uuid4())

    def analyze_model(self, request: AnalysisRequest) -> AnalysisResult:
        """分析模型 - 主入口点"""
        start_time = datetime.now()

        try:
            # 验证状态ID
            if request.state_id != self.current_state_id:
                return AnalysisResult(
                    success=False,
                    result_type="state_conflict",
                    data={"expected_state": self.current_state_id},
                    message="状态ID不匹配，请刷新后重试",
                    execution_time=0.0,
                    state_id=self.current_state_id
                )

            # 检查模型是否存在
            if request.model_id not in self.model_cache:
                return AnalysisResult(
                    success=False,
                    result_type="model_not_found",
                    data={"model_id": request.model_id},
                    message=f"未找到模型: {request.model_id}",
                    execution_time=0.0,
                    state_id=self.current_state_id
                )

            # 解析自然语言查询
            parsed_query = self.query_parser.parse_query(request.natural_language_query)

            if not parsed_query["is_valid"]:
                return AnalysisResult(
                    success=False,
                    result_type="invalid_query",
                    data={"parsed_query": parsed_query},
                    message="无法理解查询意图，请重新表述",
                    execution_time=0.0,
                    state_id=self.current_state_id
                )

            # 获取模型数据
            model_data = self.model_cache[request.model_id]
            mesh = model_data["mesh"]

            # 执行分析
            result_data = self._execute_specific_analysis(parsed_query, mesh, request.parameters)

            # 生成响应消息
            message = self._generate_response_message(parsed_query, result_data)

            execution_time = (datetime.now() - start_time).total_seconds()

            return AnalysisResult(
                success=True,
                result_type=parsed_query["query_type"],
                data=result_data,
                message=message,
                features=result_data.get("features", []),
                execution_time=execution_time,
                state_id=self.current_state_id
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return AnalysisResult(
                success=False,
                result_type="analysis_error",
                data={"error": str(e)},
                message=f"分析过程中发生错误: {str(e)}",
                execution_time=execution_time,
                state_id=self.current_state_id
            )

    def _execute_specific_analysis(self, parsed_query: Dict[str, Any], mesh, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行具体的分析操作"""
        query_type = parsed_query["query_type"]
        entities = parsed_query["entities"]

        result_data = {
            "query_type": query_type,
            "entities": entities,
            "parameters": parameters
        }

        if query_type == "measurement":
            result_data.update(self._perform_measurement(mesh, entities, parameters))
        elif query_type == "feature_detection":
            result_data.update(self._perform_feature_detection(mesh, entities, parameters))
        elif query_type == "topology_check":
            result_data.update(self._perform_topology_check(mesh))
        elif query_type == "selection":
            result_data.update(self._perform_selection(mesh, entities, parameters))

        return result_data

    def _perform_measurement(self, mesh, entities: List[Dict], parameters: Dict) -> Dict[str, Any]:
        """执行测量操作"""
        measurements = {}
        measurements["volume"] = self.geometry_analyzer.measure_volume(mesh)
        measurements["surface_area"] = self.geometry_analyzer.measure_surface_area(mesh)
        return {"measurements": measurements}

    def _perform_feature_detection(self, mesh, entities: List[Dict], parameters: Dict) -> Dict[str, Any]:
        """执行特征检测"""
        features = self.geometry_analyzer.detect_features(mesh)
        filtered_features = self._filter_features_by_parameters(features, parameters)
        return {
            "features": filtered_features,
            "total_features": len(features),
            "filtered_features": len(filtered_features)
        }

    def _perform_topology_check(self, mesh) -> Dict[str, Any]:
        """执行拓扑检查"""
        topology_result = self.geometry_analyzer.check_topology(mesh)
        return {"topology": topology_result.dict()}

    def _perform_selection(self, mesh, entities: List[Dict], parameters: Dict) -> Dict[str, Any]:
        """执行选择操作"""
        selected_indices = [0, 1, 2]  # 模拟选择的索引
        return {
            "selected_indices": selected_indices,
            "selected_count": len(selected_indices)
        }

    def _filter_features_by_parameters(self, features: List[GeometricFeature], parameters: Dict) -> List[GeometricFeature]:
        """根据参数筛选特征"""
        return features  # 暂时返回所有特征

    def _generate_response_message(self, parsed_query: Dict, result_data: Dict) -> str:
        """生成响应消息"""
        query_type = parsed_query["query_type"]

        if query_type == "measurement":
            measurements = result_data.get("measurements", {})
            if "volume" in measurements:
                return ResponseTemplates.measurement_result(
                    measurements["volume"], "mm³", "体积"
                )
        elif query_type == "feature_detection":
            features = result_data.get("features", [])
            return ResponseTemplates.feature_detection_result(features)
        elif query_type == "topology_check":
            topology = result_data.get("topology", {})
            return ResponseTemplates.topology_check_result(topology)
        elif query_type == "selection":
            selected_count = result_data.get("selected_count", 0)
            entities = parsed_query["entities"]
            entity_type = entities[0]["type"] if entities else "元素"
            return ResponseTemplates.selection_result(selected_count, entity_type)

        return "分析完成"

    # 以下方法保持与原有接口兼容
    def process_upload(self, file_content: bytes, filename: str, file_format: str) -> Dict[str, Any]:
        """处理模型上传"""
        try:
            file_path = self.model_processor.save_uploaded_file(file_content, filename)
            processing_result = self.model_processor.process_model(file_path, file_format)

            model_id = str(uuid.uuid4())
            model_info = processing_result["model_info"]
            model_info.model_id = model_id
            model_info.file_name = filename
            model_info.file_format = file_format
            model_info.upload_time = datetime.now()
            model_info.features = processing_result["features"]

            self.model_cache[model_id] = {
                "mesh": processing_result["mesh"],
                "model_info": model_info,
                "topology_result": processing_result["topology_result"],
                "file_path": file_path
            }

            self.current_state_id = str(uuid.uuid4())

            return {
                "success": True,
                "model_id": model_id,
                "model_info": model_info.dict(),
                "topology_result": processing_result["topology_result"].dict(),
                "state_id": self.current_state_id
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "state_id": self.current_state_id
            }

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
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
        return SystemPrompts.get_analysis_prompt()

    def get_current_state(self) -> str:
        """获取当前状态ID"""
        return self.current_state_id