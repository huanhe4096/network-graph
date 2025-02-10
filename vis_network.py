import pandas as pd
import plotly.graph_objects as go

# 1. 读取 TSV 文件
nodes_df = pd.read_csv("nodes.tsv", sep="\t")
edges_df = pd.read_csv("edges.tsv", sep="\t")

# 为便于查找，构造一个字典：node_id -> (x, y, z)
node_coords = {row['id']: (row['x'], row['y'], row['z']) for _, row in nodes_df.iterrows()}

# 2. 构造所有边的线段数据（每条边用两点构成，中间用 None 隔开）
edge_x, edge_y, edge_z = [], [], []
for _, row in edges_df.iterrows():
    src, tgt = row['source_id'], row['target_id']
    # 若某些 edge 中的 node id 不存在（理论上不会出现），可加判断
    if src in node_coords and tgt in node_coords:
        x0, y0, z0 = node_coords[src]
        x1, y1, z1 = node_coords[tgt]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

# 3. 定义绘制边的 trace
edge_trace = go.Scatter3d(
    x=edge_x,
    y=edge_y,
    z=edge_z,
    mode='lines',
    line=dict(color='#ff1231', width=1),
    hoverinfo='none'
)

# 4. 定义绘制节点的 trace  
# 这里用节点 id 给颜色编码（也可以按其他属性上色），marker 大小设置为 2，可根据数据量适当调整
node_trace = go.Scatter3d(
    x=nodes_df['x'],
    y=nodes_df['y'],
    z=nodes_df['z'],
    mode='markers',
    marker=dict(
        size=2,
        color=nodes_df['id'],  # 使用 id 值上色，颜色映射自动计算
        colorscale='Viridis',
        opacity=0.8
    ),
    text=nodes_df['id'],  # 鼠标悬停时显示 node id，也可以加入其他信息
    hoverinfo='text'
)

# 5. 生成 Figure，并设置交互式布局
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Interactive Network Visualization',
                    showlegend=False,
                    scene=dict(
                        xaxis=dict(title='X', showgrid=False, zeroline=False),
                        yaxis=dict(title='Y', showgrid=False, zeroline=False),
                        zaxis=dict(title='Z', showgrid=False, zeroline=False)
                    ),
                    margin=dict(l=0, r=0, b=0, t=40)
                ))

# 6. 在浏览器中展示
fig.show()