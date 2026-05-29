# DAG-visualize

一个纯前端的 DAG 可视化页面，支持你给出的 JSON 结构（`dag_visualization.json.graph.macro` 与 `micro`）。

## 使用方式

1. 打开 `/tmp/workspace/suibianll/DAG-visualize/index.html`
2. 将你的 JSON 粘贴到左侧输入框
3. 点击 **渲染**
4. 在“任务选择”下拉框中切换任务查看 micro 图，或直接点击 macro 节点

## 功能

- 宏观 DAG（macro）渲染：任务节点 + 依赖边
- 微观 DAG（micro）渲染：推理块 / 证据节点 + 边类型样式
- 节点状态与任务类型可视化
- 支持示例数据一键加载