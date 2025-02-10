import pandas as pd
import plotly.graph_objects as go

# 读取数据
nodes_df = pd.read_csv("nodes.tsv", sep="\t")
smoothed_edges_df = pd.read_csv("smoothed_edges.tsv", sep="\t")

# 构建 **ID 到坐标** 的字典，方便快速查找 source 和 target 的坐标
node_dict = nodes_df.set_index("id")[["x", "y", "z"]].to_dict(orient="index")

# 1️⃣ **绘制节点**
node_trace = go.Scatter3d(
    x=nodes_df["x"], 
    y=nodes_df["y"], 
    z=nodes_df["z"], 
    mode="markers",
    marker=dict(size=3, color="blue", opacity=0.8),
    text=nodes_df["id"],  # 显示节点 ID
    name="Nodes"
)

# 2️⃣ **绘制平滑后的边**
edge_traces = []
for _, row in smoothed_edges_df.iterrows():
    source_id = row["source_id"]
    target_id = row["target_id"]
    # **找到真实的起点和终点坐标**
    if source_id in node_dict and target_id in node_dict:
        source_x, source_y, source_z = node_dict[source_id].values()
        target_x, target_y, target_z = node_dict[target_id].values()
    else:
        continue  # 跳过无效的 ID
    # 取平滑后的 8 个插值点
    smooth_x = [source_x] + [row[f"p{i}_x"] for i in range(8)] + [target_x]
    smooth_y = [source_y] + [row[f"p{i}_y"] for i in range(8)] + [target_y]
    smooth_z = [source_z] + [row[f"p{i}_z"] for i in range(8)] + [target_z]
    
    # 创建 3D 线条
    edge_trace = go.Scatter3d(
        x=smooth_x, y=smooth_y, z=smooth_z,
        mode="lines",
        line=dict(color="red", width=2),
        opacity=0.6,
        name=f"Edge {row['source_id']} → {row['target_id']}"
    )
    edge_traces.append(edge_trace)

# 3️⃣ **创建 3D 图表**
fig = go.Figure(data=[node_trace] + edge_traces)

# 4️⃣ **设置布局**
fig.update_layout(
    title="FFTEB Network Visualization (Plotly 3D)",
    showlegend=False,
    margin=dict(l=0, r=0, b=0, t=40),
    scene=dict(
        xaxis=dict(title="X"),
        yaxis=dict(title="Y"),
        zaxis=dict(title="Z"),
        aspectmode="cube"  # 保持 x, y, z 轴比例相同
    )
)

# 5️⃣ **显示交互式图表**
fig.show()