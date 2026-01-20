# NL-Mesh-Inspect: 自然语言3D模型交互与检测平台

## 项目概述

NL-Mesh-Inspect是一个基于自然语言的3D模型分析与质量检测平台，允许用户通过简单的自然语言指令完成复杂的3D模型交互、几何分析和拓扑检测。

## 核心功能

- **自然语言查询**：使用中文或英文描述3D模型的分析需求
- **3D模型分析**：自动检测几何特征、拓扑问题、尺寸测量
- **实时交互**：WebGL支持的3D模型可视化与高亮反馈
- **智能检测**：基于AI的意图识别和几何算法

## 快速开始

### 环境要求
- Python 3.8+
- Node.js (前端开发)
- uv包管理器

### 安装和运行

1. **安装依赖**
```bash
uv sync
```

2. **启动后端服务**
```bash
uv run python nl_mesh_inspect/api/main.py
```

3. **使用命令行工具**
```bash
uv run nl-mesh-inspect interactive
```

4. **运行演示**
```bash
uv run python demo.py
```

## 项目文档体系

### 核心文档

- **[PLANNING.md](PLANNING.md)** - 宏观规划文档，多智能体协作桥梁
- **[TASK.md](TASK.md)** - 当前对话任务跟踪，微观实施细节
- **[INITIAL.md](INITIAL.md)** - 产品需求文档
- **[PRPs/nl_mesh_inspect_platform.md](PRPs/nl_mesh_inspect_platform.md)** - 详细实现计划

### 技术文档

- **架构设计**：参见PLANNING.md中的架构蓝图
- **API文档**：启动服务后访问 `/docs` 查看Swagger文档
- **开发指南**：遵循CLAUDE.md中的开发规范

## 技术架构

### 后端技术栈
- **框架**：FastAPI + Uvicorn
- **数据验证**：Pydantic
- **3D处理**：trimesh + pyvista
- **AI集成**：LangChain + OpenAI/Claude API

### 前端技术栈 (开发中)
- **3D渲染**：Three.js
- **UI框架**：React
- **实时通信**：WebSocket

### 开发工具
- **包管理**：uv
- **代码格式化**：black + ruff
- **测试框架**：pytest
- **类型检查**：mypy

## 项目状态

### 已完成 ✅
- 核心后端架构实现
- NLP自然语言处理引擎
- 几何分析工具框架
- RESTful API接口
- WebSocket实时通信
- 完整测试套件 (44个测试通过)

### 进行中 ⏳
- Three.js前端界面开发
- 高级几何算法集成
- 性能优化和缓存机制

### 规划中 📋
- 用户认证和权限管理
- 云端部署和扩展
- 第三方算法插件系统

## 开发规范

### 代码组织
- 每个Python文件不超过500行代码
- 模块化设计：agent.py/tools.py/prompts.py模式
- 遵循PEP8规范，使用black格式化

### 测试要求
- 所有功能模块都需要单元测试
- 测试文件组织镜像主应用结构
- 包含正常用例、边界用例和错误用例

### 文档标准
- 所有公共API都有完整的文档字符串
- 重大架构决策记录在PLANNING.md中
- 保持文档与代码同步更新

## 贡献指南

### 新功能开发流程
1. 阅读PLANNING.md了解项目整体架构
2. 在TASK.md中记录当前对话任务
3. 遵循模块化设计原则实现功能
4. 编写对应的单元测试
5. 更新相关文档

### 代码提交规范
- 提交信息清晰描述变更内容
- 关联对应的任务或问题编号
- 确保所有测试通过后再提交

## 联系方式

- **项目团队**：NL-Mesh-Platform Team
- **邮箱**：team@nl-mesh-platform.com
- **许可证**：MIT License

---

**最后更新**：2026-01-19

*NL-Mesh-Inspect - 让3D模型分析变得简单自然*