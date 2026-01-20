"""
自然语言处理引擎 - 解析自然语言查询并转换为几何操作
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from nl_mesh_inspect.models import AnalysisIntent, GeometricEntity, AnalysisRequest


class QueryType(str, Enum):
    """查询类型"""
    MEASUREMENT = "measurement"  # 测量查询
    FEATURE_DETECTION = "feature_detection"  # 特征检测
    TOPOLOGY_CHECK = "topology_check"  # 拓扑检查
    SELECTION = "selection"  # 选择操作
    MODIFICATION = "modification"  # 修改操作


class EntityExtractor:
    """实体提取器 - 从自然语言中提取几何实体和参数"""

    def __init__(self):
        # 几何实体关键词映射
        self.entity_keywords = {
            GeometricEntity.VERTEX: ["顶点", "点", "vertex", "point"],
            GeometricEntity.EDGE: ["边", "边缘", "edge", "边界"],
            GeometricEntity.FACE: ["面", "表面", "face", "surface"],
            GeometricEntity.HOLE: ["孔", "洞", "hole", "opening"],
            GeometricEntity.CYLINDER: ["圆柱", "柱面", "cylinder", "cylindrical"],
            GeometricEntity.PLANE: ["平面", "plate", "plane", "flat"],
            GeometricEntity.SPHERE: ["球体", "球面", "sphere", "spherical"]
        }

        # 测量单位映射
        self.unit_conversion = {
            "mm": 1.0,
            "厘米": 10.0,
            "cm": 10.0,
            "米": 1000.0,
            "m": 1000.0,
            "英寸": 25.4,
            "inch": 25.4,
            "in": 25.4
        }

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取几何实体"""
        entities = []

        # 检测实体类型
        for entity_type, keywords in self.entity_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    entities.append({
                        "type": entity_type,
                        "keyword": keyword,
                        "position": text.lower().index(keyword.lower())
                    })

        return sorted(entities, key=lambda x: x["position"])

    def extract_numerical_constraints(self, text: str) -> List[Dict[str, Any]]:
        """提取数值约束"""
        constraints = []

        # 匹配数值和比较运算符
        patterns = [
            # 大于/小于/等于 + 数值 + 单位
            r'(大于|大于等于|小于|小于等于|等于|不小于|不大于)\s*([\d.]+)\s*(mm|厘米|cm|米|m|英寸|inch|in)?',
            # 数值范围
            r'([\d.]+)\s*到\s*([\d.]+)\s*(mm|厘米|cm|米|m|英寸|inch|in)?',
            # 简单的数值
            r'([\d.]+)\s*(mm|厘米|cm|米|m|英寸|inch|in)'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) >= 2:
                    constraint = {
                        "pattern": pattern,
                        "match": match.group(),
                        "groups": match.groups()
                    }
                    constraints.append(constraint)

        return constraints

    def normalize_units(self, value: float, unit: str) -> float:
        """统一单位到毫米"""
        if unit in self.unit_conversion:
            return value * self.unit_conversion[unit]
        return value  # 默认单位为毫米


class IntentClassifier:
    """意图分类器 - 识别查询意图"""

    def __init__(self):
        # 意图关键词映射
        self.intent_patterns = {
            AnalysisIntent.QUERY: [
                r'(查询|查看|显示|展示|什么是|有多少|多大|多长|多宽|多高|体积|面积|周长)',
                r'(measure|show|display|what is|how many|how big|how long|how wide|how tall|volume|area|perimeter)',
                r'(检测|检查|分析|analyze|check|detect|inspect)'
            ],
            AnalysisIntent.OPERATION: [
                r'(选择|高亮|标记|highlight|select|mark|identify)',
                r'(旋转|移动|缩放|rotate|move|scale|translate)',
                r'(比较|对比|compare|contrast)'
            ],
            AnalysisIntent.MODIFICATION: [
                r'(修改|编辑|改变|调整|modify|edit|change|adjust|alter)',
                r'(添加|删除|创建|add|remove|delete|create)',
                r'(优化|改进|improve|optimize|enhance)'
            ]
        }

        # 查询类型模式
        self.query_type_patterns = {
            QueryType.MEASUREMENT: [
                r'(距离|长度|宽度|高度|直径|半径|角度|measure|distance|length|width|height|diameter|radius|angle)',
                r'(体积|面积|表面积|周长|volume|area|surface area|perimeter)'
            ],
            QueryType.FEATURE_DETECTION: [
                r'(特征|孔洞|圆柱|平面|球体|feature|hole|cylinder|plane|sphere)',
                r'(检测|识别|detect|identify|find|locate)'
            ],
            QueryType.TOPOLOGY_CHECK: [
                r'(拓扑|流形|水密|自相交|topology|manifold|watertight|self-intersection)',
                r'(检查|验证|check|verify|validate)'
            ],
            QueryType.SELECTION: [
                r'(选择|高亮|标记|select|highlight|mark)',
                r'(所有|全部|all|every)'
            ]
        }

    def classify_intent(self, text: str) -> AnalysisIntent:
        """分类查询意图"""
        text_lower = text.lower()

        # 统计每个意图的匹配次数
        intent_scores = {intent: 0 for intent in AnalysisIntent}

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    intent_scores[intent] += 1

        # 返回得分最高的意图
        return max(intent_scores.items(), key=lambda x: x[1])[0]

    def classify_query_type(self, text: str) -> QueryType:
        """分类查询类型"""
        text_lower = text.lower()

        # 统计每个查询类型的匹配次数
        type_scores = {qtype: 0 for qtype in QueryType}

        for qtype, patterns in self.query_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    type_scores[qtype] += 1

        # 返回得分最高的类型
        best_type = max(type_scores.items(), key=lambda x: x[1])[0]
        return best_type if type_scores[best_type] > 0 else QueryType.MEASUREMENT


class QueryParser:
    """查询解析器 - 解析自然语言查询并生成结构化命令"""

    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()

    def parse_query(self, text: str) -> Dict[str, Any]:
        """解析自然语言查询"""
        # 分类意图
        intent = self.intent_classifier.classify_intent(text)
        query_type = self.intent_classifier.classify_query_type(text)

        # 提取实体
        entities = self.entity_extractor.extract_entities(text)

        # 提取数值约束
        constraints = self.entity_extractor.extract_numerical_constraints(text)

        # 解析约束参数
        parameters = self._parse_constraints(constraints)

        return {
            "original_text": text,
            "intent": intent,
            "query_type": query_type,
            "entities": entities,
            "parameters": parameters,
            "is_valid": self._validate_query(intent, entities, parameters)
        }

    def _parse_constraints(self, constraints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解析约束参数"""
        parameters = {}

        for constraint in constraints:
            groups = constraint["groups"]
            pattern = constraint["pattern"]

            if "大于" in pattern or ">" in pattern:
                # 大于约束
                value = float(groups[1])
                unit = groups[2] if len(groups) > 2 else "mm"
                normalized_value = self.entity_extractor.normalize_units(value, unit)
                parameters["min_value"] = normalized_value

            elif "小于" in pattern or "<" in pattern:
                # 小于约束
                value = float(groups[1])
                unit = groups[2] if len(groups) > 2 else "mm"
                normalized_value = self.entity_extractor.normalize_units(value, unit)
                parameters["max_value"] = normalized_value

            elif "到" in pattern or "-" in pattern:
                # 范围约束
                min_val = float(groups[0])
                max_val = float(groups[1])
                unit = groups[2] if len(groups) > 2 else "mm"
                parameters["min_value"] = self.entity_extractor.normalize_units(min_val, unit)
                parameters["max_value"] = self.entity_extractor.normalize_units(max_val, unit)

            elif len(groups) >= 2:
                # 简单数值约束
                value = float(groups[0])
                unit = groups[1]
                normalized_value = self.entity_extractor.normalize_units(value, unit)
                parameters["target_value"] = normalized_value

        return parameters

    def _validate_query(self, intent: AnalysisIntent, entities: List[Dict], parameters: Dict) -> bool:
        """验证查询有效性"""
        # 基本验证规则
        if intent == AnalysisIntent.QUERY:
            # 查询意图允许基本的模型查询（如体积、面积等）
            # 即使没有检测到具体实体，也认为是有效的
            return True

        elif intent == AnalysisIntent.OPERATION:
            # 操作意图需要明确的实体
            return len(entities) > 0

        elif intent == AnalysisIntent.MODIFICATION:
            # 修改意图需要谨慎处理
            return len(entities) > 0 and len(parameters) > 0

        return False

    def generate_command(self, parsed_query: Dict[str, Any]) -> str:
        """生成结构化命令"""
        intent = parsed_query["intent"]
        query_type = parsed_query["query_type"]
        entities = parsed_query["entities"]
        parameters = parsed_query["parameters"]

        command_parts = [f"intent:{intent.value}", f"type:{query_type}"]

        # 添加实体信息
        if entities:
            entity_types = [e["type"].value for e in entities]
            command_parts.append(f"entities:{','.join(entity_types)}")

        # 添加参数信息
        for key, value in parameters.items():
            command_parts.append(f"{key}:{value}")

        return "|".join(command_parts)