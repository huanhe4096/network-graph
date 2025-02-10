import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm

# 1️⃣ **读取数据**
print("Loading nodes.tsv...")
nodes_df = pd.read_csv("nodes.tsv", sep="\t")
print(f"✔ Loaded {len(nodes_df)} nodes.")

print("Loading smoothed_edges.tsv...")
smoothed_edges_df = pd.read_csv("smoothed_edges.tsv", sep="\t")
print(f"✔ Loaded {len(smoothed_edges_df)} edges.")

# 构建 **ID 到坐标** 的字典，方便快速查找 source 和 target 的坐标
node_dict = nodes_df.set_index("id")[["x", "y", "z"]].to_dict(orient="index")

# 2️⃣ **创建 3D 图形**
print("Initializing 3D plot...")
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

# 3️⃣ **绘制节点**
print("Rendering nodes...")
ax.scatter(
    nodes_df["x"], nodes_df["y"], nodes_df["z"],
    c="blue", s=0.2, alpha=0.2, label="Nodes"  # 调整大小 & 透明度
)
print("✔ Nodes rendered.")

# 4️⃣ **绘制平滑后的边**
print("Rendering smoothed edges...")
for _, row in tqdm(smoothed_edges_df.iterrows(), total=len(smoothed_edges_df), desc="Processing edges"):
    source_id = row["source_id"]
    target_id = row["target_id"]

    # **找到真实的起点和终点坐标**
    if source_id in node_dict and target_id in node_dict:
        source_x, source_y, source_z = node_dict[source_id].values()
        target_x, target_y, target_z = node_dict[target_id].values()
    else:
        continue  # 跳过无效的 ID

    # 提取插值点 p0 - p7
    smooth_x = [source_x] + [row[f"p{i}_x"] for i in range(8)] + [target_x]
    smooth_y = [source_y] + [row[f"p{i}_y"] for i in range(8)] + [target_y]
    smooth_z = [source_z] + [row[f"p{i}_z"] for i in range(8)] + [target_z]
    
    # **绘制平滑边**
    ax.plot(smooth_x, smooth_y, smooth_z, c="red", alpha=0.05, linewidth=0.5)

print("✔ Smoothed edges rendered.")

# 5️⃣ **调整可视化参数**
ax.set_xlabel("X Axis")
ax.set_ylabel("Y Axis")
ax.set_zlabel("Z Axis")
ax.set_title("3D FFTEB Network Visualization")
ax.view_init(elev=30, azim=45)  # 设置观察角度

# 6️⃣ **保存 PNG**
output_file = "network_visualization.png"
print(f"Saving figure to {output_file}...")
plt.legend()
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print("✔ Figure saved successfully.")