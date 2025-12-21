# service/kmeans_algorithm.py
# Thuật toán K-Means Clustering 

import numpy as np
from typing import List, Tuple, Dict, Any
import math


class KMeansClustering:
    """
    Triển khai thuật toán K-Means Clustering từ đầu.
    """
    
    def __init__(self, k: int, max_iters: int = 100, tolerance: float = 1e-4):
        """
        Khởi tạo K-Means.
        
        Args:
            k: Số cụm (clusters)
            max_iters: Số lần lặp tối đa
            tolerance: Ngưỡng dừng (khi centroids thay đổi < tolerance)
        """
        self.k = k
        self.max_iters = max_iters
        self.tolerance = tolerance
        self.centroids = None
        self.labels = None
        self.iterations = 0
        self.history = []  # Lưu lịch sử để hiển thị
        
    def _euclidean_distance(self, point1: np.ndarray, point2: np.ndarray) -> float:
        """Tính khoảng cách Euclidean giữa 2 điểm."""
        return np.sqrt(np.sum((point1 - point2) ** 2))
    
    def _initialize_centroids(self, data: np.ndarray) -> np.ndarray:
        """
        Khởi tạo centroids bằng phương pháp Forgy (chọn ngẫu nhiên k điểm).
        """
        n_samples = data.shape[0]
        indices = np.random.choice(n_samples, self.k, replace=False)
        centroids = data[indices].copy()
        return centroids
    
    def _assign_clusters(self, data: np.ndarray, centroids: np.ndarray) -> np.ndarray:
        """
        Gán mỗi điểm vào cụm gần nhất (bước Assignment).
        
        Returns:
            labels: Mảng chứa chỉ số cụm cho mỗi điểm
        """
        n_samples = data.shape[0]
        labels = np.zeros(n_samples, dtype=int)
        
        for i in range(n_samples):
            distances = [self._euclidean_distance(data[i], centroid) for centroid in centroids]
            labels[i] = np.argmin(distances)
        
        return labels
    
    def _update_centroids(self, data: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """
        Cập nhật centroids bằng cách tính trung bình của các điểm trong cụm (bước Update).
        
        Returns:
            new_centroids: Centroids mới
        """
        n_features = data.shape[1]
        new_centroids = np.zeros((self.k, n_features))
        
        for cluster_id in range(self.k):
            # Lấy tất cả các điểm thuộc cụm này
            cluster_points = data[labels == cluster_id]
            
            if len(cluster_points) > 0:
                # Tính trung bình
                new_centroids[cluster_id] = np.mean(cluster_points, axis=0)
            else:
                # Nếu cụm rỗng, giữ nguyên centroid cũ
                new_centroids[cluster_id] = self.centroids[cluster_id]
        
        return new_centroids
    
    def _calculate_sse(self, data: np.ndarray, labels: np.ndarray, centroids: np.ndarray) -> float:
        """
        Tính Sum of Squared Errors (SSE) - tổng bình phương khoảng cách.
        """
        sse = 0.0
        for i in range(len(data)):
            cluster_id = labels[i]
            distance = self._euclidean_distance(data[i], centroids[cluster_id])
            sse += distance ** 2
        return sse
    
    def fit(self, data: np.ndarray, verbose: bool = False) -> Dict[str, Any]:
        """
        Huấn luyện mô hình K-Means.
        
        Args:
            data: Mảng numpy 2D (n_samples, n_features)
            verbose: In ra thông tin chi tiết
            
        Returns:
            Dictionary chứa thông tin kết quả
        """
        data = np.array(data)
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
        
        n_samples, n_features = data.shape
        
        # Khởi tạo centroids
        self.centroids = self._initialize_centroids(data)
        
        # Lưu lịch sử
        self.history = []
        
        for iteration in range(self.max_iters):
            # Bước 1: Gán cụm
            self.labels = self._assign_clusters(data, self.centroids)
            
            # Bước 2: Cập nhật centroids
            new_centroids = self._update_centroids(data, self.labels)
            
            # Tính SSE
            sse = self._calculate_sse(data, self.labels, self.centroids)
            
            # Lưu lịch sử
            iteration_info = {
                'iteration': iteration + 1,
                'centroids': self.centroids.tolist(),
                'labels': self.labels.tolist(),
                'sse': float(sse),
                'clusters': {}
            }
            
            # Nhóm điểm theo cụm
            for cluster_id in range(self.k):
                cluster_points = data[self.labels == cluster_id]
                iteration_info['clusters'][f'cluster_{cluster_id}'] = cluster_points.tolist()
            
            self.history.append(iteration_info)
            
            # Kiểm tra điều kiện dừng
            centroid_shift = np.sum([self._euclidean_distance(self.centroids[i], new_centroids[i]) 
                                    for i in range(self.k)])
            
            if verbose:
                print(f"Iteration {iteration + 1}: SSE = {sse:.4f}, Centroid shift = {centroid_shift:.6f}")
            
            # Cập nhật centroids
            self.centroids = new_centroids
            
            # Dừng nếu centroids thay đổi ít
            if centroid_shift < self.tolerance:
                self.iterations = iteration + 1
                if verbose:
                    print(f"Converged after {iteration + 1} iterations")
                break
            
            self.iterations = iteration + 1
        
        # Kết quả cuối cùng
        final_sse = self._calculate_sse(data, self.labels, self.centroids)
        
        return {
            'centroids': self.centroids.tolist(),
            'labels': self.labels.tolist(),
            'sse': float(final_sse),
            'iterations': self.iterations,
            'history': self.history,
            'clusters': {
                f'cluster_{i}': data[self.labels == i].tolist() 
                for i in range(self.k)
            }
        }
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """
        Dự đoán cụm cho dữ liệu mới.
        """
        if self.centroids is None:
            raise ValueError("Model chưa được huấn luyện. Gọi fit() trước.")
        
        data = np.array(data)
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
        
        return self._assign_clusters(data, self.centroids)


def parse_points_from_string(points_str: str) -> List[List[float]]:
    """
    Parse chuỗi điểm từ input text.
    Ví dụ: "x1={1,3}, x2={1.5,3.2}" -> [[1, 3], [1.5, 3.2]]
    """
    points = []
    # Tách theo dấu phẩy giữa các điểm
    point_strings = points_str.split(',')
    
    current_point = []
    for part in point_strings:
        # Tìm các số trong phần này
        if '{' in part:
            # Bắt đầu điểm mới
            current_point = []
            # Lấy số sau dấu {
            numbers = part.split('{')[1].strip()
            if '}' in numbers:
                numbers = numbers.split('}')[0]
            # Tách các số
            for num_str in numbers.split(','):
                try:
                    current_point.append(float(num_str.strip()))
                except:
                    pass
        elif '}' in part:
            # Kết thúc điểm
            numbers = part.split('}')[0].strip()
            for num_str in numbers.split(','):
                try:
                    current_point.append(float(num_str.strip()))
                except:
                    pass
            if current_point:
                points.append(current_point)
                current_point = []
        else:
            # Tiếp tục điểm hiện tại
            try:
                current_point.append(float(part.strip()))
            except:
                pass
    
    return points


def parse_points_from_list(points_list: List[Dict]) -> List[List[float]]:
    """
    Parse danh sách điểm từ JSON input.
    Ví dụ: [{"x": 1, "y": 3}, {"x": 1.5, "y": 3.2}] hoặc [[1, 3], [1.5, 3.2]]
    """
    points = []
    for item in points_list:
        if isinstance(item, dict):
            # Ưu tiên x, y nếu có, nếu không thì lấy tất cả giá trị số theo thứ tự
            if 'x' in item and 'y' in item:
                point = [float(item['x']), float(item['y'])]
            else:
                # Lấy tất cả các giá trị số theo thứ tự key
                point = [float(v) for k, v in sorted(item.items()) if isinstance(v, (int, float))]
            if point:
                points.append(point)
        elif isinstance(item, list):
            # Nếu là list trực tiếp
            point = [float(x) for x in item if isinstance(x, (int, float))]
            if point:
                points.append(point)
    return points

