# DAG-visualize

一个纯前端的 DAG 可视化页面，支持你给出的 JSON 结构（`dag_visualization.json.graph.macro` 与 `micro`）。

## 使用方式

1. 打开 `/tmp/workspace/suibianll/DAG-visualize/index.html`
2. 将你的 JSON 粘贴到左侧输入框
3. 点击 **渲染**
4. 在“任务选择”下拉框中切换任务查看 micro 图，或直接点击 macro 节点

## 功能

- 三栏联动：左（总体视图）/ 中（细粒度推理链）/ 右（任务完整信息）
- 宏观 DAG（macro）渲染：节点内展示任务目标与结论概览
- 微观 DAG（micro）渲染：推理块 / 证据节点 + 边类型样式
- 点击任务节点后同步刷新中栏和右栏
- 右侧展示任务 id、类型、目标、结论、子结论、引用信息
- 支持示例数据一键加载