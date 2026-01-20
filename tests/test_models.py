"""
数据模型测试
"""

import pytest
from datetime import datetime

from nl_mesh_inspect.models import (
    ModelFormat, AnalysisIntent, GeometricEntity,
    ModelUploadRequest, GeometricFeature, TopologyCheckResult,
    AnalysisRequest, AnalysisResult, ModelInfo, ErrorResponse
)


class TestModelFormats:
    """模型格式测试"""

    def test_model_format_values(self):
        """测试模型格式枚举值"""
        assert ModelFormat.STL == "stl"
        assert ModelFormat.OBJ == "obj"
        assert ModelFormat.PLY == "ply"
        assert ModelFormat.STEP == "step"

    def test_model_format_membership(self):
        """测试模型格式成员"""
        assert "stl" in ModelFormat.__members__.values()
        assert "obj" in ModelFormat.__members__.values()


class TestAnalysisIntent:
    """分析意图测试"""

    def test_analysis_intent_values(self):
        """测试分析意图枚举值"""
        assert AnalysisIntent.QUERY == "query"
        assert AnalysisIntent.OPERATION == "operation"
        assert AnalysisIntent.MODIFICATION == "modification"


class TestGeometricEntity:
    """几何实体测试"""

    def test_geometric_entity_values(self):
        """测试几何实体枚举值"""
        assert GeometricEntity.VERTEX == "vertex"
        assert GeometricEntity.EDGE == "edge"
        assert GeometricEntity.FACE == "face"
        assert GeometricEntity.HOLE == "hole"


class TestModelUploadRequest:
    """模型上传请求测试"""

    def test_valid_upload_request(self):
        """测试有效的上传请求"""
        request = ModelUploadRequest(
            file_name="test.stl",
            file_format=ModelFormat.STL,
            file_size=1024
        )

        assert request.file_name == "test.stl"
        assert request.file_format == ModelFormat.STL
        assert request.file_size == 1024
        assert request.metadata is None

    def test_upload_request_with_metadata(self):
        """测试带元数据的上传请求"""
        metadata = {"author": "test", "version": "1.0"}
        request = ModelUploadRequest(
            file_name="test.stl",
            file_format=ModelFormat.STL,
            file_size=1024,
            metadata=metadata
        )

        assert request.metadata == metadata

    def test_upload_request_validation(self):
        """测试上传请求验证"""
        # 缺少必需字段应该抛出异常
        with pytest.raises(ValueError):
            ModelUploadRequest(
                file_name="test.stl",
                # 缺少 file_format 和 file_size
            )


class TestGeometricFeature:
    """几何特征测试"""

    def test_geometric_feature_creation(self):
        """测试几何特征创建"""
        feature = GeometricFeature(
            entity_type=GeometricEntity.FACE,
            indices=[0, 1, 2],
            properties={"area": 10.5, "normal": [0, 0, 1]}
        )

        assert feature.entity_type == GeometricEntity.FACE
        assert feature.indices == [0, 1, 2]
        assert feature.properties["area"] == 10.5
        assert feature.bounding_box is None

    def test_geometric_feature_with_bounding_box(self):
        """测试带边界框的几何特征"""
        bbox = [0, 0, 0, 10, 10, 10]
        feature = GeometricFeature(
            entity_type=GeometricEntity.CYLINDER,
            indices=[0],
            properties={},
            bounding_box=bbox
        )

        assert feature.bounding_box == bbox


class TestTopologyCheckResult:
    """拓扑检查结果测试"""

    def test_topology_result_creation(self):
        """测试拓扑结果创建"""
        result = TopologyCheckResult(
            is_manifold=True,
            has_self_intersections=False,
            is_watertight=True,
            issues=[]
        )

        assert result.is_manifold is True
        assert result.has_self_intersections is False
        assert result.is_watertight is True
        assert result.issues == []

    def test_topology_result_with_issues(self):
        """测试带问题的拓扑结果"""
        issues = ["非流形边缘", "自相交面"]
        result = TopologyCheckResult(
            is_manifold=False,
            has_self_intersections=True,
            is_watertight=False,
            issues=issues
        )

        assert result.issues == issues


class TestAnalysisRequest:
    """分析请求测试"""

    def test_analysis_request_creation(self):
        """测试分析请求创建"""
        request = AnalysisRequest(
            model_id="test-model-123",
            natural_language_query="测量体积",
            state_id="state-123"
        )

        assert request.model_id == "test-model-123"
        assert request.natural_language_query == "测量体积"
        assert request.intent is None
        assert request.parameters == {}
        assert request.state_id == "state-123"

    def test_analysis_request_with_intent(self):
        """测试带意图的分析请求"""
        request = AnalysisRequest(
            model_id="test-model-123",
            natural_language_query="高亮所有孔洞",
            intent=AnalysisIntent.OPERATION,
            parameters={"min_diameter": 5},
            state_id="state-123"
        )

        assert request.intent == AnalysisIntent.OPERATION
        assert request.parameters["min_diameter"] == 5


class TestAnalysisResult:
    """分析结果测试"""

    def test_successful_analysis_result(self):
        """测试成功的分析结果"""
        result = AnalysisResult(
            success=True,
            result_type="measurement",
            data={"volume": 1000.0},
            message="体积测量完成",
            features=[],
            execution_time=0.5,
            state_id="state-123"
        )

        assert result.success is True
        assert result.result_type == "measurement"
        assert result.data["volume"] == 1000.0
        assert result.execution_time == 0.5

    def test_failed_analysis_result(self):
        """测试失败的分析结果"""
        result = AnalysisResult(
            success=False,
            result_type="error",
            data={"error": "模型不存在"},
            message="分析失败",
            features=[],
            execution_time=0.1,
            state_id="state-123"
        )

        assert result.success is False
        assert "error" in result.data


class TestModelInfo:
    """模型信息测试"""

    def test_model_info_creation(self):
        """测试模型信息创建"""
        model_info = ModelInfo(
            model_id="test-model-123",
            file_name="test.stl",
            file_format=ModelFormat.STL,
            file_size=1024,
            vertex_count=100,
            face_count=200,
            bounding_box=[0, 0, 0, 10, 10, 10],
            upload_time=datetime(2026, 1, 19, 12, 0, 0),
            features=[]
        )

        assert model_info.model_id == "test-model-123"
        assert model_info.vertex_count == 100
        assert model_info.face_count == 200
        assert len(model_info.bounding_box) == 6


class TestErrorResponse:
    """错误响应测试"""

    def test_error_response_creation(self):
        """测试错误响应创建"""
        error = ErrorResponse(
            error="文件格式不支持",
            details={"supported_formats": ["stl", "obj"]},
            state_id="state-123"
        )

        assert error.error == "文件格式不支持"
        assert "supported_formats" in error.details
        assert error.state_id == "state-123"

    def test_error_response_without_details(self):
        """测试无详细信息的错误响应"""
        error = ErrorResponse(error="未知错误")

        assert error.error == "未知错误"
        assert error.details is None
        assert error.state_id is None