#!/usr/bin/env python3
"""
NL-Mesh-Inspect 演示脚本
展示平台的核心功能
"""

from nl_mesh_inspect.agent import NLMeshInspectAgent
from nl_mesh_inspect.models import AnalysisRequest
from nl_mesh_inspect.nlp_engine import QueryParser


def demo_nlp_engine():
    """演示自然语言处理引擎"""
    print("自然语言处理引擎演示")
    print("=" * 50)

    parser = QueryParser()

    # 测试查询
    test_queries = [
        "测量这个模型的体积",
        "选择所有直径大于10mm的孔洞",
        "检查模型是否有自相交面",
        "高亮所有平面表面",
        "这个圆柱面的直径是多少？"
    ]

    for query in test_queries:
        result = parser.parse_query(query)
        print(f"\n查询: {query}")
        print(f"意图: {result['intent']}")
        print(f"查询类型: {result['query_type']}")
        print(f"实体: {[e['type'] for e in result['entities']]}")
        print(f"参数: {result['parameters']}")
        print(f"有效: {result['is_valid']}")


def demo_agent():
    """演示主智能体功能"""
    print("\n主智能体演示")
    print("=" * 50)

    agent = NLMeshInspectAgent()

    # 演示系统提示词
    print("系统提示词:")
    print(agent.get_system_prompt()[:200] + "...")

    # 演示状态管理
    print(f"\n当前状态ID: {agent.get_current_state()}")

    # 演示分析请求（无实际模型）
    request = AnalysisRequest(
        model_id="demo-model",
        natural_language_query="测量体积",
        state_id=agent.get_current_state()
    )

    # 由于没有实际模型，这会返回模型未找到错误
    result = agent.analyze_model(request)
    print(f"\n分析结果:")
    print(f"成功: {result.success}")
    print(f"结果类型: {result.result_type}")
    print(f"消息: {result.message}")


def demo_cli():
    """演示命令行接口"""
    print("\n命令行接口演示")
    print("=" * 50)

    print("可用命令:")
    print("  nl-mesh-inspect upload <文件路径> --format <格式>")
    print("  nl-mesh-inspect analyze <模型ID> <查询>")
    print("  nl-mesh-inspect info <模型ID>")
    print("  nl-mesh-inspect interactive")

    print("\n示例:")
    print("  nl-mesh-inspect upload model.stl --format stl")
    print("  nl-mesh-inspect analyze model-123 \"测量体积\"")


def main():
    """主演示函数"""
    print("NL-Mesh-Inspect 平台演示")
    print("=" * 50)

    demo_nlp_engine()
    demo_agent()
    demo_cli()

    print("\n演示完成!")
    print("\n下一步:")
    print("1. 安装3D处理依赖: uv add trimesh pyvista")
    print("2. 启动API服务: uv run python nl_mesh_inspect/api/main.py")
    print("3. 使用命令行工具: uv run nl-mesh-inspect interactive")


if __name__ == "__main__":
    main()