## FEATURE:

**NL-Mesh-Inspect: 自然语言 3D 模型交互与检测平台**

构建一个基于自然语言的 3D 模型分析与质量检测平台，平台可以主动解析用户导入的模型（如："这是一个带有四个 M6 螺纹孔的长方形支架，中心有一个直径为 20mm 的圆槽，边缘进行了 2mm 的倒角处理" ），用户也可以通过简单的自然语言指令（如："这个模型是否密闭"或"选中所有直径大于 10cm 的孔洞"）完成复杂的 3D 模型交互、几何分析和拓扑检测，无需学习复杂的 CAD 软件。

### 核心功能需求

1. **自然语言处理引擎**
   - 意图识别：区分查询、操作、修改三类指令
   - 实体提取：识别几何特征（边、面、孔、法线）和数值约束
   - 代码生成：将自然语言转换为结构化几何操作指令

2. **3D 模型渲染与交互**
   - WebGL 3D 渲染器支持主流格式（STL, OBJ, PLY）
   - 实时高亮反馈和视觉反馈
   - 多轮对话上下文支持

3. **几何检测算法库**
   - 拓扑检查：非流形边缘、自相交面检测
   - 特征识别：自动识别圆柱面、平面、曲率区域

4. **用户界面与体验**
   - 鼠标式与对话式丝滑交互体验
   - 3D 视图与检测结果可视化
   - 检测报告生成与导出

## EXAMPLES:

参考项目中的现有模式：

- `use-cases/agent-factory-with-subagents/` - 多智能体架构模式
- `use-cases/agent-factory-with-subagents/agents/rag_agent/` - 完整的智能体实现示例
- 重点关注：
  - `agent.py` - 智能体定义和架构
  - `tools.py` - 工具函数实现
  - `cli.py` - 命令行接口设计
  - 模块化组织模式

**注意事项：不要直接复制代码，而是学习其架构模式和最佳实践。**

## DOCUMENTATION:

### 核心技术栈文档

**3D 引擎与几何处理**
- Three.js: https://threejs.org/docs/
- PyVista: https://docs.pyvista.org/
- Trimesh: https://trimsh.org/
- CGAL: https://doc.cgal.org/latest/Manual/index.html
- libigl: https://libigl.github.io/tutorial/

**AI 与自然语言处理**
- LangChain: https://python.langchain.com/docs/get_started/introduction
- OpenAI API: https://platform.openai.com/docs/api-reference
- Claude API: https://docs.anthropic.com/en/docs/welcome

**Web 开发框架**
- FastAPI: https://fastapi.tiangolo.com/
- Streamlit: https://docs.streamlit.io/
- React + Three.js: https://threejs.org/docs/index.html#manual/en/introduction/Creating-a-scene

**空间索引与性能优化**
- three-mesh-bvh: https://github.com/gkjohnson/three-mesh-bvh
- Spatial indexing algorithms for real-time interaction

## OTHER CONSIDERATIONS:

### 技术架构约束
- **依赖管理**：使用uv
- **文件大小限制**：单个文件不超过 500 行代码
- **模块化设计**：按功能分离为独立模块
- **虚拟环境**：使用 uv 执行 Python 命令
- **环境变量**：使用 python_dotenv 和 load_env()

### 开发规范
- **PEP8 标准**：代码格式化使用 black
- **类型注解**：所有函数使用类型提示
- **测试要求**：每个功能模块都需要 pytest 单元测试
- **文档规范**：Google 风格的 docstring

### 性能与用户体验要求
- **实时响应**：几何检测算法需要优化性能
- **大模型支持**：支持 100MB+ 的 3D 模型文件
- **多格式支持**：STL, OBJ, PLY, STEP 等主流格式
- **跨平台兼容**：Web 端和桌面端支持
- **丝滑交互**：用户交互体验一定要丝滑

### 3D 领域专有约束
- **表示层转换**：区分网格 (Mesh) 与 边界表示 (B-Rep)。检测算法优先使用 B-Rep 数据（如 STEP），渲染层使用压缩后的 Mesh。
- **空间感知语义**：Agent 必须理解方位词（上下左右、内外、前后），解析时需参考当前相机的 LookAt 向量。

### CONCURRENCY_RULE:
- **原则**：我们不能让后端“慢速计算”的瓶颈影响前端的“丝滑交互”。解决方案是：允许用户连续操作，但通过“状态 ID”让后端只执行最后一条有效的操作
- All user modification commands must be timestamped and assigned a unique State_ID.
- The Backend Agent must only commit results to the database if the input State_ID matches the system's latest state.
- Frontend UI must implement an 'optimistic update' strategy with visual rollback functionality upon receiving a stale state conflict error.

### 常见 AI 实现陷阱
- **几何算法复杂性**：避免简单的暴力算法，使用空间索引优化
- **自然语言歧义**：处理几何术语的多义性
- **内存管理**：大模型加载时的内存优化
- **错误处理**：几何操作失败时的优雅降级
- **指令协议化**：：LLM 不得直接生成任意 Python 代码，必须通过定义的 Tools/Actions 执行。例如定义 select_by_diameter(min, max) 或 check_thickness(threshold)，确保安全性

### 扩展性考虑
- **插件架构**：支持自定义检测算法
- **多语言支持**：中英文自然语言处理
- **API 接口**：RESTful API 供第三方集成
- **云端部署**：支持 Docker 容器化部署

### 安全与合规
- **文件上传安全**：模型文件格式验证
- **数据隐私**：本地处理优先，避免敏感数据上传
- **开源合规**：遵守使用的开源库许可证要求

### AI上下文工程与源代码仓库隔离
- Context-Engineering-Intro 上下文工程负责 “Why & What”（逻辑、意图、记忆）。
- NL-Mesh-Inspect 源代码工程负责 “How”（具体实现、工程优化）。