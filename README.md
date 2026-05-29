# DAG-visualize

基于 Python + Dash + Cytoscape 的 DAG 可视化应用，支持你给出的 JSON 结构（`dag_visualization.json.graph.macro` 与 `micro`）。

## 快速开始

1. （可选）创建虚拟环境：`python -m venv .venv && source .venv/bin/activate`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动应用：`python app.py`
4. 浏览器打开：`http://127.0.0.1:8050`

## 使用方式

- 应用启动后默认加载仓库内的 `sample_data.json`。
- 上传 JSON 文件可直接替换当前视图数据。
- 点击 **加载示例** 可重新加载 `sample_data.json`。
- 初始只显示宏观 DAG；点击节点后展开三栏视图（宏观/微观/详情）。
- 点击 **返回总体视图** 可折叠回单一宏观视图。

## 功能

- 宏观 DAG（macro）渲染：节点内展示任务目标与结论概览
- 微观 DAG（micro）渲染：推理块 / 证据节点 + 边类型样式
- 点击任务节点后同步刷新中栏和右栏
- 右侧展示任务 id、类型、目标、结论、子结论、引用信息
- 使用 DAG 布局避免节点重叠