# K-Means Training Script
# Script để train và test thuật toán K-Means với dữ liệu từ file CSV

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Thêm đường dẫn để import thuật toán
sys.path.append(os.path.join(os.path.dirname(__file__), '../../data_mining'))
from service.kmeans_algorithm import KMeansClustering

# Đường dẫn đến thư mục data
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
BAI1_FILE = os.path.join(DATA_DIR, 'Bai1_k2_data.csv')
BAI2_FILE = os.path.join(DATA_DIR, 'Bai2_k3_data.csv')

# ====================================================================
# BÀI 1: Gom cụm k = 2 với 4 điểm
# ====================================================================
def run_example_1():
    print("=" * 60)
    print("BÀI 1: Gom cụm k = 2 với 4 điểm")
    print("=" * 60)
    
    # Đọc dữ liệu từ file CSV
    try:
        df = pd.read_csv(BAI1_FILE, index_col=0)
        print(f"\nĐã load dữ liệu từ: {BAI1_FILE}")
        print(f"Số điểm: {len(df)}")
        print("\nDữ liệu:")
        print(df)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {BAI1_FILE}")
        return None
    
    # Lấy tọa độ x, y
    data = df[['x', 'y']].values
    k = 2
    
    print(f"\nDữ liệu đầu vào ({len(data)} điểm):")
    for i, (idx, row) in enumerate(df.iterrows(), 1):
        print(f"  {idx}: ({row['x']}, {row['y']})")
    
    print(f"\nSố cụm k = {k}")
    print("\n" + "-" * 60)
    
    # Tạo và train model
    kmeans = KMeansClustering(k=k, max_iters=100)
    result = kmeans.fit(data, verbose=True)
    
    # Hiển thị kết quả
    print("\n" + "=" * 60)
    print("KẾT QUẢ:")
    print("=" * 60)
    print(f"Số lần lặp: {result['iterations']}")
    print(f"SSE (Sum of Squared Errors): {result['sse']:.4f}")
    
    print("\nCentroids cuối cùng:")
    for i, centroid in enumerate(result['centroids']):
        print(f"  Cụm {i}: ({centroid[0]:.4f}, {centroid[1]:.4f})")
    
    print("\nPhân cụm:")
    for i in range(k):
        cluster_key = f'cluster_{i}'
        cluster_points = result['clusters'][cluster_key]
        print(f"\n  Cụm {i} ({len(cluster_points)} điểm):")
        for point in cluster_points:
            print(f"    ({point[0]:.4f}, {point[1]:.4f})")
    
    # Vẽ biểu đồ
    plot_clustering_result(data, result, "Bài 1: K-Means với k=2")
    
    return result


# ====================================================================
# BÀI 2: Gom cụm k = 3 với 9 điểm
# ====================================================================
def run_example_2():
    print("\n\n" + "=" * 60)
    print("BÀI 2: Gom cụm k = 3 với 9 điểm")
    print("=" * 60)
    
    # Đọc dữ liệu từ file CSV
    try:
        df = pd.read_csv(BAI2_FILE, index_col=0)
        print(f"\nĐã load dữ liệu từ: {BAI2_FILE}")
        print(f"Số điểm: {len(df)}")
        print("\nDữ liệu:")
        print(df)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {BAI2_FILE}")
        return None
    
    # Lấy tọa độ x, y
    data = df[['x', 'y']].values
    k = 3
    
    print(f"\nDữ liệu đầu vào ({len(data)} điểm):")
    for i, (idx, row) in enumerate(df.iterrows(), 1):
        print(f"  {idx}: ({row['x']}, {row['y']})")
    
    print(f"\nSố cụm k = {k}")
    print("\n" + "-" * 60)
    
    # Tạo và train model
    kmeans = KMeansClustering(k=k, max_iters=100)
    result = kmeans.fit(data, verbose=True)
    
    # Hiển thị kết quả
    print("\n" + "=" * 60)
    print("KẾT QUẢ:")
    print("=" * 60)
    print(f"Số lần lặp: {result['iterations']}")
    print(f"SSE (Sum of Squared Errors): {result['sse']:.4f}")
    
    print("\nCentroids cuối cùng:")
    for i, centroid in enumerate(result['centroids']):
        print(f"  Cụm {i}: ({centroid[0]:.4f}, {centroid[1]:.4f})")
    
    print("\nPhân cụm:")
    for i in range(k):
        cluster_key = f'cluster_{i}'
        cluster_points = result['clusters'][cluster_key]
        print(f"\n  Cụm {i} ({len(cluster_points)} điểm):")
        for point in cluster_points:
            print(f"    ({point[0]:.4f}, {point[1]:.4f})")
    
    # Vẽ biểu đồ
    plot_clustering_result(data, result, "Bài 2: K-Means với k=3")
    
    return result


# ====================================================================
# Hàm vẽ biểu đồ kết quả
# ====================================================================
def plot_clustering_result(data, result, title):
    """Vẽ biểu đồ scatter plot cho kết quả clustering."""
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    plt.figure(figsize=(10, 8))
    
    # Vẽ các điểm theo cụm
    for i in range(result['k']):
        cluster_key = f'cluster_{i}'
        cluster_points = result['clusters'][cluster_key]
        if cluster_points:
            cluster_array = np.array(cluster_points)
            plt.scatter(cluster_array[:, 0], cluster_array[:, 1], 
                       c=colors[i % len(colors)], label=f'Cụm {i}', 
                       s=100, alpha=0.6, edgecolors='black', linewidths=1)
    
    # Vẽ centroids
    centroids = np.array(result['centroids'])
    plt.scatter(centroids[:, 0], centroids[:, 1], 
               c='black', marker='*', s=500, label='Centroids',
               edgecolors='yellow', linewidths=2)
    
    # Vẽ đường nối từ điểm đến centroid
    labels = result['labels']
    for i, point in enumerate(data):
        cluster_id = labels[i]
        centroid = centroids[cluster_id]
        plt.plot([point[0], centroid[0]], [point[1], centroid[1]], 
                'k--', alpha=0.3, linewidth=0.5)
    
    plt.xlabel('X', fontsize=12)
    plt.ylabel('Y', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Lưu biểu đồ vào thư mục data
    output_file = os.path.join(DATA_DIR, f"{title.replace(' ', '_').replace(':', '')}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nĐã lưu biểu đồ: {output_file}")
    plt.show()


# ====================================================================
# Hàm lưu kết quả ra file CSV
# ====================================================================
def save_results_to_csv(result, df_original, filename):
    """Lưu kết quả clustering ra file CSV."""
    output_file = os.path.join(DATA_DIR, filename)
    
    # Tạo DataFrame từ dữ liệu gốc
    df_result = df_original.copy()
    df_result['cluster'] = result['labels']
    df_result['centroid_x'] = [result['centroids'][label][0] for label in result['labels']]
    df_result['centroid_y'] = [result['centroids'][label][1] for label in result['labels']]
    
    # Tính khoảng cách đến centroid
    df_result['distance_to_centroid'] = np.sqrt(
        (df_result['x'] - df_result['centroid_x'])**2 + (df_result['y'] - df_result['centroid_y'])**2
    )
    
    df_result.to_csv(output_file, index=True)
    print(f"Đã lưu kết quả: {output_file}")


# ====================================================================
# MAIN
# ====================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("K-MEANS CLUSTERING - TRAINING SCRIPT")
    print("=" * 60)
    
    # Chạy Bài 1
    result1 = run_example_1()
    if result1:
        # Đọc lại file để lấy DataFrame gốc
        df1 = pd.read_csv(BAI1_FILE, index_col=0)
        save_results_to_csv(result1, df1, "kmeans_result_bai1.csv")
    
    # Chạy Bài 2
    result2 = run_example_2()
    if result2:
        # Đọc lại file để lấy DataFrame gốc
        df2 = pd.read_csv(BAI2_FILE, index_col=0)
        save_results_to_csv(result2, df2, "kmeans_result_bai2.csv")
    
    print("\n" + "=" * 60)
    print("HOÀN TẤT!")
    print("=" * 60)

