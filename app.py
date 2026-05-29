import base64
import json
import os

from dash import Dash, html, dcc, Input, Output, State, ctx, no_update
import dash_cytoscape as cyto

cyto.load_extra_layouts()

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "sample_data.json")

STATUS_COLORS = {
    "done": "#EDE9FE",
    "pending": "#DCFCE7",
    "failed": "#FEF3C7",
}

MACRO_LAYOUT = {
    "name": "dagre",
    "rankDir": "LR",
    "nodeSep": 50,
    "rankSep": 90,
    "edgeSep": 10,
    "padding": 24,
    "nodeDimensionsIncludeLabels": True,
}

MICRO_LAYOUT = {
    "name": "dagre",
    "rankDir": "LR",
    "nodeSep": 40,
    "rankSep": 80,
    "edgeSep": 8,
    "padding": 24,
    "nodeDimensionsIncludeLabels": True,
}

MACRO_STYLESHEET = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "background-color": "data(color)",
            "shape": "round-rectangle",
            "text-wrap": "wrap",
            "text-max-width": 160,
            "color": "#111827",
            "font-size": 11,
            "text-valign": "center",
            "text-halign": "center",
            "width": 180,
            "height": 80,
            "border-width": 1,
            "border-color": "#e5e7eb",
        },
    },
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "line-color": "#6b7280",
            "target-arrow-color": "#6b7280",
            "width": 2,
        },
    },
]

MICRO_STYLESHEET = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "text-wrap": "wrap",
            "text-max-width": 150,
            "color": "#111827",
            "font-size": 11,
            "text-valign": "center",
            "text-halign": "center",
            "width": 170,
            "height": 70,
            "border-width": 1,
            "border-color": "#e5e7eb",
            "shape": "round-rectangle",
        },
    },
    {
        "selector": "node[node_type = 'evidence']",
        "style": {"background-color": "#DBEAFE"},
    },
    {
        "selector": "node[node_type = 'reasoning_block']",
        "style": {"background-color": "#FEF9C3"},
    },
    {
        "selector": "node[node_type = 'claim']",
        "style": {"background-color": "#E0F2FE"},
    },
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",
            "target-arrow-shape": "triangle",
            "line-color": "data(lineColor)",
            "target-arrow-color": "data(lineColor)",
            "line-style": "data(lineStyle)",
            "width": 2,
        },
    },
]


def clip(text, limit=42):
    value = str(text or "")
    return value if len(value) <= limit else f"{value[:limit]}..."


def get_graph_root(data):
    if not data:
        return None
    return data.get("dag_visualization", {}).get("json", {}).get("graph")


def read_json(path):
    if not path:
        raise ValueError("未提供文件路径。")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_upload(contents):
    if not contents:
        raise ValueError("上传内容为空。")
    _, encoded = contents.split(",", 1)
    decoded = base64.b64decode(encoded)
    return json.loads(decoded.decode("utf-8"))


try:
    DEFAULT_DATA = read_json(SAMPLE_PATH)
    DEFAULT_ERROR = ""
except Exception as exc:
    DEFAULT_DATA = None
    DEFAULT_ERROR = f"默认样例加载失败：{exc}"


def build_edges_from_dependencies(nodes):
    edges = []
    for node in nodes:
        node_id = node.get("id")
        for dep in node.get("dependencies") or []:
            edges.append({"source": dep, "target": node_id})
    return edges


def build_macro_elements(graph):
    macro = (graph or {}).get("macro", {})
    nodes = macro.get("nodes") or []
    edges = macro.get("edges") or build_edges_from_dependencies(nodes)

    node_map = {}
    node_ids = set()
    elements = []

    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            continue
        node_map[node_id] = node
        node_ids.add(node_id)
        label = node.get("label") or node.get("task_type") or node_id
        status = node.get("status", "")
        goal = clip(node.get("goal", ""), 26)
        conclusion = clip(node.get("conclusion", ""), 26)
        lines = [label]
        if status:
            lines.append(status)
        if goal:
            lines.append(goal)
        if conclusion:
            lines.append(conclusion)
        elements.append(
            {
                "data": {
                    "id": node_id,
                    "label": "\n".join(lines),
                    "color": node.get("color") or STATUS_COLORS.get(status, "#E0E7FF"),
                    "status": status,
                }
            }
        )

    for idx, edge in enumerate(edges):
        source = edge.get("source")
        target = edge.get("target")
        if source in node_ids and target in node_ids:
            elements.append(
                {"data": {"id": f"{source}->{target}-{idx}", "source": source, "target": target}}
            )

    return elements, node_map, len(nodes), len(edges)


def build_micro_elements(graph, task_id):
    micro = (graph or {}).get("micro", {})
    task_micro = micro.get(task_id)
    if not task_micro:
        return []

    nodes = task_micro.get("nodes") or []
    edges = task_micro.get("edges") or []
    node_ids = {node.get("id") for node in nodes if node.get("id")}

    elements = []
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            continue
        node_type = node.get("node_type", "node")
        label = node.get("title") or node.get("content") or node_id
        elements.append(
            {
                "data": {
                    "id": node_id,
                    "label": "\n".join([node_type, clip(label, 40)]),
                    "node_type": node_type,
                }
            }
        )

    for idx, edge in enumerate(edges):
        source = edge.get("source_id") or edge.get("source")
        target = edge.get("target_id") or edge.get("target")
        if source not in node_ids or target not in node_ids:
            continue
        elements.append(
            {
                "data": {
                    "id": f"{source}->{target}-{idx}",
                    "source": source,
                    "target": target,
                    "lineStyle": edge.get("dash", "solid"),
                    "lineColor": edge.get("color", "#6b7280"),
                }
            }
        )

    return elements


def kv(label, value):
    return html.Div([html.Div(label, className="k"), html.Div(value, className="v")], className="kv")


def render_section(title, items):
    if not items:
        return html.Div([
            html.Div(title, className="section-title"),
            html.Div("无", className="muted"),
        ])
    return html.Div([
        html.Div(title, className="section-title"),
        *[
            html.Div(
                html.Pre(json.dumps(item, ensure_ascii=False, indent=2), className="code"),
                className="block",
            )
            for item in items
        ],
    ])


def render_evidence_section(items):
    if not items:
        return html.Div([
            html.Div("引用信息（evidence_list）", className="section-title"),
            html.Div("无", className="muted"),
        ])

    blocks = []
    for item in items:
        score = ""
        if item.get("relevance_score") is not None or item.get("trust_score") is not None:
            score = (
                f"relevance={item.get('relevance_score', '-')}"
                f"/trust={item.get('trust_score', '-')}"
            )
        blocks.append(
            html.Div(
                [
                    kv("source_id", item.get("source_id", "")),
                    kv("source_type", item.get("source_type", "")),
                    kv("title", item.get("title", "")),
                    kv("snippet", item.get("snippet", "")),
                    kv("score", score),
                ],
                className="block",
            )
        )

    return html.Div([html.Div("引用信息（evidence_list）", className="section-title"), *blocks])


def render_detail(task):
    if not task:
        return html.Div("请点击左侧任务节点查看详情。", className="muted")

    dependencies = task.get("dependencies") or []
    dependency_text = "无" if not dependencies else ", ".join(dependencies)

    return html.Div(
        [
            kv("任务ID", task.get("id", "")),
            kv("任务类型", task.get("task_type", "")),
            kv("状态", task.get("status", "")),
            kv("任务目标", task.get("goal", "")),
            kv("结论", task.get("conclusion", "")),
            kv("依赖任务", dependency_text),
            render_evidence_section(task.get("evidence_list") or []),
            render_section("子结论信息（sub_conclusions）", task.get("sub_conclusions") or []),
            render_section("结论链（conclusion_chain）", task.get("conclusion_chain") or []),
        ]
    )


app = Dash(__name__)
app.title = "DAG Visualize"

app.layout = html.Div(
    className="layout",
    children=[
        html.Div(
            className="toolbar",
            children=[
                html.H2("DAG 可视化（Python + Cytoscape）"),
                html.Div(
                    className="input-row",
                    children=[
                        dcc.Upload(
                            id="upload-data",
                            children=html.Button("上传 JSON 文件"),
                            multiple=False,
                        ),
                        html.Button("加载示例", id="load-sample-btn", className="primary"),
                        html.Button("返回总体视图", id="reset-selection-btn"),
                    ],
                ),
                html.Div(id="error-box", className="error", children=DEFAULT_ERROR),
                html.Div(
                    "默认加载示例数据；上传 JSON 后可替换视图内容。",
                    className="hint",
                ),
            ],
        ),
        dcc.Store(id="data-store", data=DEFAULT_DATA),
        dcc.Store(id="selection-store"),
        html.Div(
            id="columns",
            className="columns single",
            children=[
                html.Div(
                    className="card",
                    children=[
                        html.Div(
                            className="card-header",
                            children=[
                                html.H3("总体视图（任务目标 + 结论概览）", className="card-title"),
                                html.Div(id="macro-meta", className="meta"),
                            ],
                        ),
                        cyto.Cytoscape(
                            id="macro-graph",
                            layout=MACRO_LAYOUT,
                            stylesheet=MACRO_STYLESHEET,
                            elements=[],
                            className="cyto",
                        ),
                    ],
                ),
                html.Div(
                    id="micro-card",
                    className="card hidden",
                    children=[
                        html.Div(
                            className="card-header",
                            children=[
                                html.H3("细粒度推理链（当前任务）", className="card-title"),
                                html.Div(id="micro-meta", className="meta"),
                            ],
                        ),
                        html.Div(id="micro-empty", className="muted"),
                        cyto.Cytoscape(
                            id="micro-graph",
                            layout=MICRO_LAYOUT,
                            stylesheet=MICRO_STYLESHEET,
                            elements=[],
                            className="cyto",
                        ),
                    ],
                ),
                html.Div(
                    id="detail-card",
                    className="card hidden",
                    children=[
                        html.Div(
                            className="card-header",
                            children=[
                                html.H3("任务完整信息", className="card-title"),
                            ],
                        ),
                        html.Div(id="task-detail", className="detail-panel"),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("data-store", "data"),
    Output("error-box", "children"),
    Input("upload-data", "contents"),
    Input("load-sample-btn", "n_clicks"),
    prevent_initial_call=True,
)
def load_data(upload_contents, sample_clicks):
    trigger = ctx.triggered_id
    try:
        if trigger == "upload-data" and upload_contents:
            data = parse_upload(upload_contents)
            return data, ""
        if trigger == "load-sample-btn":
            data = read_json(SAMPLE_PATH)
            return data, ""
    except Exception as exc:
        return no_update, f"加载失败：{exc}"
    return no_update, ""


@app.callback(
    Output("selection-store", "data"),
    Input("macro-graph", "tapNodeData"),
    Input("reset-selection-btn", "n_clicks"),
    Input("data-store", "data"),
    prevent_initial_call=True,
)
def update_selection(tap_data, reset_clicks, data):
    if ctx.triggered_id in {"reset-selection-btn", "data-store"}:
        return None
    if tap_data and tap_data.get("id"):
        return tap_data.get("id")
    return no_update


@app.callback(
    Output("columns", "className"),
    Output("micro-card", "className"),
    Output("detail-card", "className"),
    Output("macro-meta", "children"),
    Output("micro-meta", "children"),
    Output("macro-graph", "elements"),
    Output("micro-graph", "elements"),
    Output("micro-empty", "children"),
    Output("task-detail", "children"),
    Input("data-store", "data"),
    Input("selection-store", "data"),
)
def update_view(data, selected_id):
    graph = get_graph_root(data)
    if not graph:
        return (
            "columns single",
            "card hidden",
            "card hidden",
            "请先加载 JSON 数据",
            "",
            [],
            [],
            "",
            html.Div("请先加载 JSON 数据。", className="muted"),
        )

    macro_elements, node_map, node_count, edge_count = build_macro_elements(graph)
    macro_meta = f"任务数 {node_count} · 边 {edge_count}"

    if selected_id in node_map:
        micro_elements = build_micro_elements(graph, selected_id)
        node_total = sum(1 for element in micro_elements if "source" not in element["data"])
        micro_meta = f"节点数 {node_total}"
        micro_hint = "" if micro_elements else "当前任务没有 micro 数据。"
        detail = render_detail(node_map[selected_id])
        return (
            "columns triple",
            "card",
            "card",
            macro_meta,
            micro_meta,
            macro_elements,
            micro_elements,
            micro_hint,
            detail,
        )

    return (
        "columns single",
        "card hidden",
        "card hidden",
        macro_meta,
        "",
        macro_elements,
        [],
        "点击左侧节点查看细粒度推理链。",
        html.Div("点击左侧任务节点查看详情。", className="muted"),
    )


if __name__ == "__main__":
    app.run_server(debug=True)
