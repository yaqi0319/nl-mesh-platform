"""
命令行接口 - 提供命令行工具用于测试和调试
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from nl_mesh_inspect.agent import NLMeshInspectAgent
from nl_mesh_inspect.models import AnalysisRequest, ModelFormat


def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description="NL-Mesh-Inspect 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  nl-mesh-inspect upload model.stl --format stl
  nl-mesh-inspect analyze <model_id> "测量体积"
  nl-mesh-inspect interactive
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # upload 命令
    upload_parser = subparsers.add_parser('upload', help='上传3D模型')
    upload_parser.add_argument('file_path', help='模型文件路径')
    upload_parser.add_argument('--format', required=True,
                              choices=['stl', 'obj', 'ply', 'step'],
                              help='模型文件格式')

    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析模型')
    analyze_parser.add_argument('model_id', help='模型ID')
    analyze_parser.add_argument('query', help='自然语言查询')

    # info 命令
    info_parser = subparsers.add_parser('info', help='获取模型信息')
    info_parser.add_argument('model_id', help='模型ID')

    # interactive 命令
    subparsers.add_parser('interactive', help='交互式模式')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    agent = NLMeshInspectAgent()

    try:
        if args.command == 'upload':
            handle_upload(agent, args)
        elif args.command == 'analyze':
            handle_analyze(agent, args)
        elif args.command == 'info':
            handle_info(agent, args)
        elif args.command == 'interactive':
            handle_interactive(agent)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


def handle_upload(agent: NLMeshInspectAgent, args):
    """处理上传命令"""
    file_path = Path(args.file_path)

    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}")
        return

    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()

        result = agent.process_upload(
            file_content=file_content,
            filename=file_path.name,
            file_format=args.format
        )

        if result['success']:
            print("✅ 模型上传成功")
            print(f"模型ID: {result['model_id']}")
            print(f"状态ID: {result['state_id']}")

            model_info = result['model_info']
            print(f"\n模型信息:")
            print(f"  文件名: {model_info['file_name']}")
            print(f"  格式: {model_info['file_format']}")
            print(f"  顶点数: {model_info['vertex_count']}")
            print(f"  面片数: {model_info['face_count']}")

            topology = result['topology_result']
            print(f"\n拓扑检查:")
            print(f"  流形: {'✅' if topology['is_manifold'] else '❌'}")
            print(f"  自相交: {'✅' if not topology['has_self_intersections'] else '❌'}")
            print(f"  水密性: {'✅' if topology['is_watertight'] else '❌'}")
        else:
            print(f"❌ 上传失败: {result['error']}")

    except Exception as e:
        print(f"❌ 上传过程中发生错误: {e}")


def handle_analyze(agent: NLMeshInspectAgent, args):
    """处理分析命令"""
    # 获取当前状态ID
    state_id = agent.get_current_state()

    request = AnalysisRequest(
        model_id=args.model_id,
        natural_language_query=args.query,
        state_id=state_id
    )

    result = agent.analyze_model(request)

    print(f"🔍 分析结果 (状态ID: {result.state_id})")
    print(f"成功: {'✅' if result.success else '❌'}")
    print(f"类型: {result.result_type}")
    print(f"执行时间: {result.execution_time:.2f}秒")
    print(f"\n消息:\n{result.message}")

    if result.features:
        print(f"\n检测到的特征 ({len(result.features)}个):")
        for i, feature in enumerate(result.features):
            print(f"  {i+1}. {feature.entity_type}: {feature.properties}")


def handle_info(agent: NLMeshInspectAgent, args):
    """处理信息命令"""
    model_info = agent.get_model_info(args.model_id)

    if not model_info:
        print(f"❌ 未找到模型: {args.model_id}")
        return

    print(f"📋 模型信息: {args.model_id}")
    print(f"文件名: {model_info.file_name}")
    print(f"格式: {model_info.file_format}")
    print(f"大小: {model_info.file_size} 字节")
    print(f"顶点数: {model_info.vertex_count}")
    print(f"面片数: {model_info.face_count}")
    print(f"边界框: {model_info.bounding_box}")
    print(f"上传时间: {model_info.upload_time}")

    if model_info.features:
        print(f"检测到的特征: {len(model_info.features)}个")


def handle_interactive(agent: NLMeshInspectAgent):
    """处理交互式模式"""
    print("🚀 NL-Mesh-Inspect 交互式模式")
    print("输入 'quit' 退出，'help' 查看帮助")
    print("=" * 50)

    current_model_id: Optional[str] = None

    while True:
        try:
            user_input = input("\n> ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() in ['help', '?']:
                print_help()
            elif user_input.startswith('upload '):
                current_model_id = handle_interactive_upload(agent, user_input)
            elif user_input.startswith('analyze '):
                if not current_model_id:
                    print("❌ 请先上传模型")
                    continue
                handle_interactive_analyze(agent, current_model_id, user_input)
            elif user_input == 'info':
                if not current_model_id:
                    print("❌ 请先上传模型")
                    continue
                handle_interactive_info(agent, current_model_id)
            else:
                print("❌ 未知命令，输入 'help' 查看可用命令")

        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


def handle_interactive_upload(agent: NLMeshInspectAgent, command: str) -> Optional[str]:
    """处理交互式上传"""
    parts = command.split()
    if len(parts) < 3:
        print("用法: upload <文件路径> <格式>")
        return None

    file_path = parts[1]
    file_format = parts[2]

    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()

        result = agent.process_upload(file_content, Path(file_path).name, file_format)

        if result['success']:
            print(f"✅ 上传成功，模型ID: {result['model_id']}")
            return result['model_id']
        else:
            print(f"❌ 上传失败: {result['error']}")
            return None

    except Exception as e:
        print(f"❌ 上传错误: {e}")
        return None


def handle_interactive_analyze(agent: NLMeshInspectAgent, model_id: str, command: str):
    """处理交互式分析"""
    query = command[8:].strip()  # 移除 'analyze '

    if not query:
        print("❌ 请输入查询内容")
        return

    state_id = agent.get_current_state()
    request = AnalysisRequest(
        model_id=model_id,
        natural_language_query=query,
        state_id=state_id
    )

    result = agent.analyze_model(request)

    print(f"\n🔍 分析结果:")
    print(f"成功: {'✅' if result.success else '❌'}")
    print(f"执行时间: {result.execution_time:.2f}秒")
    print(f"\n{result.message}")


def handle_interactive_info(agent: NLMeshInspectAgent, model_id: str):
    """处理交互式信息查询"""
    model_info = agent.get_model_info(model_id)

    if model_info:
        print(f"📋 模型 {model_id} 信息:")
        print(f"  顶点: {model_info.vertex_count}")
        print(f"  面片: {model_info.face_count}")
        print(f"  边界框: {model_info.bounding_box}")
    else:
        print("❌ 模型不存在")


def print_help():
    """打印帮助信息"""
    print("""
可用命令:
  upload <文件路径> <格式>   上传3D模型文件
  analyze <查询内容>         分析当前模型
  info                      查看当前模型信息
  quit                      退出程序

格式支持: stl, obj, ply, step

示例:
  upload model.stl stl
  analyze "测量体积"
  analyze "检查拓扑"
    """)


if __name__ == "__main__":
    main()