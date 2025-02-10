import numpy as np
from tqdm import tqdm

# 参数设置
np.random.seed(42)
num_nodes = 10000
num_clusters = 100
cluster_means = num_nodes / num_clusters
cluster_std = 200
gamma = 2.5
k_min = 1
k_max = 5
coord_sigma = 10

# 生成簇大小
cluster_sizes = np.random.normal(loc=cluster_means, scale=cluster_std, size=num_clusters)
cluster_sizes = np.round(cluster_sizes).astype(int)
cluster_sizes = np.clip(cluster_sizes, 1, None)

# 调整簇大小总和
current_total = cluster_sizes.sum()
difference = num_nodes - current_total

indices = np.arange(num_clusters)
if difference > 0:
    for _ in range(difference):
        idx = np.random.choice(indices)
        cluster_sizes[idx] += 1
elif difference < 0:
    for _ in range(-difference):
        while True:
            idx = np.random.choice(indices)
            if cluster_sizes[idx] > 1:
                cluster_sizes[idx] -= 1
                break

# 生成簇中心
cluster_centers = np.random.uniform(low=-100, high=100, size=(num_clusters, 3))

# 生成节点
nodes = []
cluster_assignments = []
node_id = 0
for cluster_id in range(num_clusters):
    size = cluster_sizes[cluster_id]
    center = cluster_centers[cluster_id]
    
    x = center[0] + coord_sigma * np.random.randn(size)
    y = center[1] + coord_sigma * np.random.randn(size)
    z = center[2] + coord_sigma * np.random.randn(size)
    
    x = np.clip(x, -100, 100)
    y = np.clip(y, -100, 100)
    z = np.clip(z, -100, 100)
    
    for i in range(size):
        nodes.append((node_id, x[i], y[i], z[i]))
        cluster_assignments.append(cluster_id)
        node_id += 1

# 保存节点
with open('nodes.tsv', 'w') as f:
    f.write("id\tx\ty\tz\n")
    for node in nodes:
        f.write(f"{node[0]}\t{node[1]:.4f}\t{node[2]:.4f}\t{node[3]:.4f}\n")

# 生成度数分布
u = np.random.rand(num_nodes)
k = k_min * (1 - u) ** (-1/(gamma - 1))
k = np.round(k).astype(int)
k = np.clip(k, k_min, k_max)

# 调整度数总和
sum_k = k.sum()
if sum_k % 2 != 0:
    idx = np.random.randint(num_nodes)
    if k[idx] < k_max:
        k[idx] += 1
    else:
        k[idx] -= 1

# 预处理簇数据
clusters = []
all_nodes = np.arange(num_nodes)
external_nodes_per_cluster = []

for c in range(num_clusters):
    start = sum(cluster_sizes[:c])
    end = start + cluster_sizes[c]
    cluster_nodes = list(range(start, end))
    clusters.append(cluster_nodes)
    
    mask = np.ones(num_nodes, dtype=bool)
    mask[cluster_nodes] = False
    external_nodes_per_cluster.append(all_nodes[mask])

# 生成边
edge_count = 0
with open('edges.tsv', 'w') as f_edge:
    f_edge.write("source_id\ttarget_id\n")
    for u in tqdm(range(num_nodes), desc="生成边"):
        cluster_id = cluster_assignments[u]
        cluster_nodes = clusters[cluster_id]
        external_nodes = external_nodes_per_cluster[cluster_id]
        
        k_u = k[u]
        size_c = len(cluster_nodes)
        possible_internal = [n for n in cluster_nodes if n != u]
        
        k_in = min(k_u, len(possible_internal))
        k_out = k_u - k_in
        
        # 生成内部边
        if k_in > 0:
            targets = np.random.choice(possible_internal, size=k_in, replace=True)
            for v in targets:
                f_edge.write(f"{u}\t{v}\n")
                edge_count += 1
        
        # 生成外部边
        if k_out > 0 and len(external_nodes) > 0:
            targets = np.random.choice(external_nodes, size=k_out, replace=True)
            for v in targets:
                f_edge.write(f"{u}\t{v}\n")
                edge_count += 1

print(f"生成完成！总节点数：{num_nodes}，总边数：{edge_count}")