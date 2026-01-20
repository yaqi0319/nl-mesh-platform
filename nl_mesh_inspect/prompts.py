"""
系统提示词模块 - 包含AI交互的系统提示词和模板
"""

from typing import Dict, Any, List


class SystemPrompts:
    """系统提示词定义"""

    @staticmethod
    def get_analysis_prompt() -> str:
        """获取几何分析系统提示词"""
        return """
你是一个专业的3D几何分析助手，专门帮助用户理解和分析3D模型。

## 你的能力
- 理解自然语言描述的几何查询
- 分析3D模型的拓扑结构和几何特征
- 提供准确的测量结果和检测报告
- 解释复杂的几何概念和问题

## 响应指南
1. **准确性优先**: 确保所有几何分析结果准确无误
2. **清晰解释**: 用通俗易懂的语言解释专业概念
3. **提供上下文**: 结合具体的3D模型特征进行回答
4. **建议改进**: 发现问题时提供具体的改进建议

## 可用工具
你可以使用以下工具来帮助分析：
- 几何测量工具 (距离、角度、体积、面积等)
- 特征检测工具 (孔洞、圆柱、平面等)
- 拓扑检查工具 (流形检查、自相交检测等)
- 模型可视化工具 (高亮显示、截面查看等)

请根据用户的具体查询，选择适当的工具进行分析并返回清晰的结果。
"""

    @staticmethod
    def get_intent_classification_prompt() -> str:
        """获取意图分类提示词"""
        return """
请分析用户的自然语言查询，识别其意图和所需的几何操作类型。

## 意图分类
1. **查询意图 (QUERY)**: 用户想要获取模型信息或测量结果
   - 示例: "这个模型的体积是多少？", "显示所有孔洞"

2. **操作意图 (OPERATION)**: 用户想要执行可视化或选择操作
   - 示例: "高亮所有直径大于10mm的孔", "旋转模型到正面视图"

3. **修改意图 (MODIFICATION)**: 用户想要修改或优化模型
   - 示例: "删除这个多余的孔", "增加壁厚到5mm"

## 查询类型分类
- **测量类 (MEASUREMENT)**: 涉及尺寸、距离、角度等测量
- **特征检测类 (FEATURE_DETECTION)**: 识别特定的几何特征
- **拓扑检查类 (TOPOLOGY_CHECK)**: 检查模型的拓扑完整性
- **选择类 (SELECTION)**: 选择特定的几何元素

请返回JSON格式的解析结果，包含意图类型、查询类型、检测到的实体和参数。
"""

    @staticmethod
    def get_geometric_explanation_prompt() -> str:
        """获取几何解释提示词"""
        return """
你是一个几何教育专家，擅长用简单易懂的方式解释复杂的3D几何概念。

## 解释原则
1. **从简单到复杂**: 先介绍基本概念，再深入细节
2. **使用比喻**: 用日常生活中的例子帮助理解
3. **可视化描述**: 描述空间关系和几何形状
4. **强调应用**: 说明几何概念的实际意义

## 常见几何概念解释模板
- **拓扑概念**: 解释流形、水密性、自相交等
- **几何特征**: 解释平面、圆柱、孔洞等特征
- **测量概念**: 解释距离、角度、体积等的几何意义

请根据用户的具体问题，提供专业且易于理解的几何解释。
"""


class ResponseTemplates:
    """响应模板"""

    @staticmethod
    def measurement_result(value: float, unit: str, description: str) -> str:
        """测量结果模板"""
        return f"""
📏 **测量结果**

**{description}**: {value:.2f} {unit}

这个测量值表示模型的{description.lower()}尺寸。
"""

    @staticmethod
    def feature_detection_result(features: List[Dict[str, Any]]) -> str:
        """特征检测结果模板"""
        if not features:
            return "🔍 **特征检测结果**\n\n未检测到明显的几何特征。"

        result = "🔍 **特征检测结果**\n\n"

        feature_counts = {}
        for feature in features:
            feature_type = feature.get('type', '未知')
            feature_counts[feature_type] = feature_counts.get(feature_type, 0) + 1

        for feature_type, count in feature_counts.items():
            result += f"- **{feature_type}**: {count}个\n"

        return result

    @staticmethod
    def topology_check_result(result: Dict[str, Any]) -> str:
        """拓扑检查结果模板"""
        status_icon = "✅" if result.get('is_manifold', False) and not result.get('has_self_intersections', True) else "⚠️"

        response = f"{status_icon} **拓扑检查结果**\n\n"

        # 基本状态
        response += f"- **流形检查**: {'✅ 通过' if result.get('is_manifold') else '❌ 失败'}\n"
        response += f"- **自相交检查**: {'✅ 通过' if not result.get('has_self_intersections') else '❌ 失败'}\n"
        response += f"- **水密性检查**: {'✅ 通过' if result.get('is_watertight') else '❌ 失败'}\n"

        # 问题列表
        issues = result.get('issues', [])
        if issues:
            response += "\n**发现的问题**:\n"
            for issue in issues:
                response += f"- {issue}\n"

        return response

    @staticmethod
    def error_response(error_type: str, message: str, suggestion: str = "") -> str:
        """错误响应模板"""
        response = f"❌ **错误**: {error_type}\n\n{message}"

        if suggestion:
            response += f"\n\n💡 **建议**: {suggestion}"

        return response

    @staticmethod
    def selection_result(selected_count: int, entity_type: str, criteria: str = "") -> str:
        """选择操作结果模板"""
        response = f"🎯 **选择结果**\n\n"
        response += f"已选择 **{selected_count}** 个{entity_type}"

        if criteria:
            response += f"，筛选条件: {criteria}"

        return response


class QueryExamples:
    """查询示例库"""

    @staticmethod
    def get_example_queries() -> List[Dict[str, Any]]:
        """获取示例查询"""
        return [
            {
                "query": "这个模型的体积是多少？",
                "intent": "QUERY",
                "type": "MEASUREMENT",
                "description": "测量模型体积"
            },
            {
                "query": "显示所有直径大于10mm的孔",
                "intent": "OPERATION",
                "type": "SELECTION",
                "description": "筛选并高亮特定尺寸的孔洞"
            },
            {
                "query": "检查模型是否有自相交面",
                "intent": "QUERY",
                "type": "TOPOLOGY_CHECK",
                "description": "拓扑完整性检查"
            },
            {
                "query": "这个圆柱面的直径是多少？",
                "intent": "QUERY",
                "type": "MEASUREMENT",
                "description": "测量特定特征的尺寸"
            },
            {
                "query": "高亮所有平面表面",
                "intent": "OPERATION",
                "type": "SELECTION",
                "description": "识别并可视化平面特征"
            }
        ]

    @staticmethod
    def get_tutorial_queries() -> List[str]:
        """获取教学查询"""
        return [
            "什么是流形模型？",
            "如何检查模型的水密性？",
            "孔洞检测的原理是什么？",
            "自相交面会影响3D打印吗？",
            "如何优化模型的拓扑结构？"
        ]