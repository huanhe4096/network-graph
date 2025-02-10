import numpy as np
import pandas as pd
import scipy.fftpack as fft
import scipy.ndimage as ndimage
from tqdm import tqdm

# 设置体素网格大小
GRID_SIZE = 128  # 3D 体素网格分辨率
N_SMOOTH_POINTS = 8  # 插值点数

# 读取节点数据
nodes_df = pd.read_csv("nodes.tsv", sep="\t")
edges_df = pd.read_csv("edges.tsv", sep="\t")

# 归一化坐标范围 [-100, 100] → [0, GRID_SIZE-1]
def normalize_coords(coords):
    return ((coords + 100) / 200) * (GRID_SIZE - 1)

nodes_df[["x", "y", "z"]] = nodes_df[["x", "y", "z"]].apply(normalize_coords)

# 构建 ID 到坐标的映射
node_dict = nodes_df.set_index("id")[["x", "y", "z"]].to_dict(orient="index")

# 初始化 3D 体素网格
density_grid = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE))

# 遍历所有边，映射到 3D 体素网格
def bresenham3D(p1, p2):
    """ 3D Bresenham 线算法，用于在体素网格中绘制线段 """
    x1, y1, z1 = map(int, p1)
    x2, y2, z2 = map(int, p2)
    points = []
    
    dx, dy, dz = abs(x2 - x1), abs(y2 - y1), abs(z2 - z1)
    xs, ys, zs = np.sign(x2 - x1), np.sign(y2 - y1), np.sign(z2 - z1)
    
    if dx >= dy and dx >= dz:  # x is the driving axis
        p1, p2 = 2 * dy - dx, 2 * dz - dx
        while x1 != x2:
            points.append((x1, y1, z1))
            if p1 >= 0:
                y1 += ys
                p1 -= 2 * dx
            if p2 >= 0:
                z1 += zs
                p2 -= 2 * dx
            p1 += 2 * dy
            p2 += 2 * dz
            x1 += xs
    elif dy >= dx and dy >= dz:  # y is the driving axis
        p1, p2 = 2 * dx - dy, 2 * dz - dy
        while y1 != y2:
            points.append((x1, y1, z1))
            if p1 >= 0:
                x1 += xs
                p1 -= 2 * dy
            if p2 >= 0:
                z1 += zs
                p2 -= 2 * dy
            p1 += 2 * dx
            p2 += 2 * dz
            y1 += ys
    else:  # z is the driving axis
        p1, p2 = 2 * dx - dz, 2 * dy - dz
        while z1 != z2:
            points.append((x1, y1, z1))
            if p1 >= 0:
                x1 += xs
                p1 -= 2 * dz
            if p2 >= 0:
                y1 += ys
                p2 -= 2 * dz
            p1 += 2 * dx
            p2 += 2 * dy
            z1 += zs
    points.append((x2, y2, z2))
    return points

for _, row in tqdm(edges_df.iterrows(), total=len(edges_df), desc="Mapping edges"):
    if row["source_id"] in node_dict and row["target_id"] in node_dict:
        p1 = np.array(list(node_dict[row["source_id"]].values()))
        p2 = np.array(list(node_dict[row["target_id"]].values()))
        for px, py, pz in bresenham3D(p1, p2):
            density_grid[int(px), int(py), int(pz)] += 1

# 应用 3D FFT 平滑
density_grid = ndimage.gaussian_filter(density_grid, sigma=2)  # 初步高斯平滑
fft_result = fft.fftn(density_grid)
fft_result *= (np.abs(fft_result) > np.percentile(np.abs(fft_result), 90))  # 低通滤波
density_smoothed = np.real(fft.ifftn(fft_result))  # 逆 FFT

# 生成平滑路径
smoothed_edges = []
for _, row in tqdm(edges_df.iterrows(), total=len(edges_df), desc="Smoothing edges"):
    if row["source_id"] in node_dict and row["target_id"] in node_dict:
        p1 = np.array(list(node_dict[row["source_id"]].values()))
        p2 = np.array(list(node_dict[row["target_id"]].values()))
        
        # 计算插值点
        smooth_points = []
        for i in range(N_SMOOTH_POINTS):
            t = (i + 1) / (N_SMOOTH_POINTS + 1)
            new_point = (1 - t) * p1 + t * p2
            smooth_points.append(new_point)
        
        smoothed_edges.append([row["source_id"], row["target_id"]] + [coord for p in smooth_points for coord in p])

# 保存平滑后的边文件
columns = ["source_id", "target_id"] + [f"p{i}_{axis}" for i in range(N_SMOOTH_POINTS) for axis in "xyz"]
smoothed_edges_df = pd.DataFrame(smoothed_edges, columns=columns)
smoothed_edges_df.to_csv("smoothed_edges.tsv", sep="\t", index=False)

print("FFTEB 处理完成，结果已保存至 smoothed_edges.tsv")