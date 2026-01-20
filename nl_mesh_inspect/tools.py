"""
几何分析工具模块 - 实现3D模型处理和几何分析功能
"""

import os
import tempfile
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

from nl_mesh_inspect.models import (
    ModelFormat, GeometricFeature, GeometricEntity, TopologyCheckResult, ModelInfo
)


try:
    import trimesh
    import pyvista as pv
except ImportError:
    # 在测试环境中可能不需要这些依赖
    trimesh = None
    pv = None


class ModelLoader:
    """3D模型加载器"""

    def __init__(self):
        self.supported_formats = {
            ModelFormat.STL: ['.stl'],
            ModelFormat.OBJ: ['.obj'],
            ModelFormat.PLY: ['.ply'],
            ModelFormat.STEP: ['.step', '.stp']
        }

    def validate_file_format(self, file_path: str, expected_format: ModelFormat) -> bool:
        """验证文件格式"""
        if not trimesh:
            raise ImportError("trimesh库未安装")

        file_ext = Path(file_path).suffix.lower()
        valid_extensions = self.supported_formats.get(expected_format, [])

        if file_ext not in valid_extensions:
            return False

        # 尝试加载文件验证格式
        try:
            mesh = trimesh.load_mesh(file_path)
            return mesh is not None
        except Exception:
            return False

    def load_model(self, file_path: str, format: ModelFormat) -> Optional[Any]:
        """加载3D模型"""
        if not trimesh:
            raise ImportError("trimesh库未安装")

        try:
            mesh = trimesh.load_mesh(file_path)
            return mesh
        except Exception as e:
            raise ValueError(f"无法加载模型文件 {file_path}: {str(e)}")

    def get_model_info(self, mesh) -> ModelInfo:
        """获取模型基本信息"""
        if not trimesh:
            raise ImportError("trimesh库未安装")

        bbox = mesh.bounds
        bounding_box = [bbox[0][0], bbox[0][1], bbox[0][2],
                       bbox[1][0], bbox[1][1], bbox[1][2]]

        return ModelInfo(
            model_id="",  # 由调用者设置
            file_name="",  # 由调用者设置
            file_format=ModelFormat.STL,  # 由调用者设置
            file_size=0,  # 由调用者设置
            vertex_count=len(mesh.vertices),
            face_count=len(mesh.faces),
            bounding_box=bounding_box,
            upload_time=None,  # 由调用者设置
            features=[]
        )


class GeometryAnalyzer:
    """几何分析器"""

    def __init__(self):
        self.model_loader = ModelLoader()

    def check_topology(self, mesh) -> TopologyCheckResult:
        """检查模型拓扑"""
        if not trimesh:
            raise ImportError("trimesh库未安装")

        try:
            # 检查是否为流形
            is_manifold = mesh.is_watertight

            # 检查自相交
            has_self_intersections = mesh.self_intersecting

            # 检查水密性
            is_watertight = mesh.is_watertight

            issues = []
            if not is_manifold:
                issues.append("模型不是流形")
            if has_self_intersections:
                issues.append("模型存在自相交面")
            if not is_watertight:
                issues.append("模型不是水密的")

            return TopologyCheckResult(
                is_manifold=is_manifold,
                has_self_intersections=has_self_intersections,
                is_watertight=is_watertight,
                issues=issues
            )
        except Exception as e:
            return TopologyCheckResult(
                is_manifold=False,
                has_self_intersections=False,
                is_watertight=False,
                issues=[f"拓扑检查失败: {str(e)}"]
            )

    def detect_features(self, mesh) -> List[GeometricFeature]:
        """检测几何特征"""
        if not trimesh:
            raise ImportError("trimesh库未安装")

        features = []

        try:
            # 检测平面
            planar_faces = self._detect_planar_faces(mesh)
            features.extend(planar_faces)

            # 检测圆柱面
            cylindrical_faces = self._detect_cylindrical_faces(mesh)
            features.extend(cylindrical_faces)

            # 检测孔洞
            holes = self._detect_holes(mesh)
            features.extend(holes)

        except Exception as e:
            # 特征检测失败时返回空列表
            print(f"特征检测失败: {str(e)}")

        return features

    def _detect_planar_faces(self, mesh) -> List[GeometricFeature]:
        """检测平面特征"""
        features = []

        # 简化的平面检测逻辑
        # 在实际实现中，这里应该使用更复杂的算法
        try:
            # 计算面法线
            face_normals = mesh.face_normals

            # 这里可以添加更复杂的平面检测逻辑
            # 目前返回空列表，等待后续实现
            return features

        except Exception:
            return features

    def _detect_cylindrical_faces(self, mesh) -> List[GeometricFeature]:
        """检测圆柱面特征"""
        features = []

        # 简化的圆柱面检测逻辑
        # 在实际实现中，这里应该使用更复杂的算法
        try:
            # 这里可以添加圆柱面检测逻辑
            # 目前返回空列表，等待后续实现
            return features

        except Exception:
            return features

    def _detect_holes(self, mesh) -> List[GeometricFeature]:
        """检测孔洞特征"""
        features = []

        # 简化的孔洞检测逻辑
        # 在实际实现中，这里应该使用更复杂的算法
        try:
            # 这里可以添加孔洞检测逻辑
            # 目前返回空列表，等待后续实现
            return features

        except Exception:
            return features

    def measure_distance(self, mesh, point1: List[float], point2: List[float]) -> float:
        """测量两点间距离"""
        if len(point1) != 3 or len(point2) != 3:
            raise ValueError("点坐标必须是3维")

        return np.linalg.norm(np.array(point1) - np.array(point2))

    def measure_volume(self, mesh) -> float:
        """测量体积"""
        if not trimesh:
            raise ImportError("trimesh库未安装")

        try:
            return mesh.volume
        except Exception:
            return 0.0

    def measure_surface_area(self, mesh) -> float:
        """测量表面积"""
        if not trimesh:
            raise ImportError("trimesh库未安装")

        try:
            return mesh.area
        except Exception:
            return 0.0


class ModelProcessor:
    """模型处理器 - 负责模型文件的管理和处理"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.geometry_analyzer = GeometryAnalyzer()

    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """保存上传的文件"""
        file_path = self.upload_dir / filename

        with open(file_path, 'wb') as f:
            f.write(file_content)

        return str(file_path)

    def process_model(self, file_path: str, format: ModelFormat) -> Dict[str, Any]:
        """处理模型文件"""
        try:
            # 加载模型
            mesh = self.geometry_analyzer.model_loader.load_model(file_path, format)

            # 获取模型信息
            model_info = self.geometry_analyzer.model_loader.get_model_info(mesh)

            # 检查拓扑
            topology_result = self.geometry_analyzer.check_topology(mesh)

            # 检测特征
            features = self.geometry_analyzer.detect_features(mesh)

            return {
                "mesh": mesh,
                "model_info": model_info,
                "topology_result": topology_result,
                "features": features
            }

        except Exception as e:
            raise ValueError(f"模型处理失败: {str(e)}")

    def cleanup_file(self, file_path: str) -> None:
        """清理临时文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            # 文件清理失败不影响主要功能
            pass