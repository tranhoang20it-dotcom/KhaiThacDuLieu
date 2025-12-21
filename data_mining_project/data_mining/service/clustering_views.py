# service/clustering_views.py
# API Views cho K-Means Clustering

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .kmeans_algorithm import KMeansClustering, parse_points_from_list


@csrf_exempt
def kmeans_cluster_view(request):
    """
    API endpoint cho K-Means Clustering.
    
    Input JSON:
    {
        "points": [
            {"x": 1, "y": 3},
            {"x": 1.5, "y": 3.2},
            ...
        ],
        "k": 2,
        "max_iters": 100
    }
    """
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            
            # Lấy dữ liệu
            points_list = data.get('points', [])
            k = int(data.get('k', 2))
            max_iters = int(data.get('max_iters', 100))
            
            if not points_list:
                return JsonResponse({
                    "error": "Danh sách điểm không được để trống"
                }, status=400)
            
            if k < 1:
                return JsonResponse({
                    "error": "Số cụm k phải >= 1"
                }, status=400)
            
            if len(points_list) < k:
                return JsonResponse({
                    "error": f"Số điểm ({len(points_list)}) phải >= số cụm k ({k})"
                }, status=400)
            
            # Parse points
            points = parse_points_from_list(points_list)
            
            if not points:
                return JsonResponse({
                    "error": "Không thể parse điểm từ dữ liệu đầu vào"
                }, status=400)
            
            # Chuyển đổi sang numpy array
            data_array = np.array(points)
            
            # Kiểm tra tất cả điểm có cùng số chiều
            if len(set(len(p) for p in points)) > 1:
                return JsonResponse({
                    "error": "Tất cả các điểm phải có cùng số chiều"
                }, status=400)
            
            # Tạo và huấn luyện mô hình
            kmeans = KMeansClustering(k=k, max_iters=max_iters)
            result = kmeans.fit(data_array, verbose=False)
            
            # Chuẩn bị kết quả trả về
            response_data = {
                "status": "success",
                "algorithm": "K-Means Clustering",
                "k": k,
                "iterations": result['iterations'],
                "sse": round(result['sse'], 4),
                "centroids": result['centroids'],
                "labels": result['labels'],
                "clusters": result['clusters'],
                "points": points,  # Trả lại điểm gốc
                "history": result['history']  # Lịch sử các lần lặp
            }
            
            return JsonResponse(response_data)
            
        except ValueError as e:
            return JsonResponse({
                "error": f"Lỗi giá trị: {str(e)}"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "error": f"Lỗi xử lý: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        "error": "Chỉ chấp nhận POST"
    }, status=405)


@csrf_exempt
def kmeans_predict_view(request):
    """
    API endpoint để dự đoán cụm cho điểm mới (sau khi đã train).
    
    Input JSON:
    {
        "centroids": [[1.2, 2.8], [3.0, 1.0]],
        "points": [{"x": 1.1, "y": 2.9}]
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            centroids = data.get('centroids', [])
            points_list = data.get('points', [])
            
            if not centroids:
                return JsonResponse({
                    "error": "Centroids không được để trống"
                }, status=400)
            
            if not points_list:
                return JsonResponse({
                    "error": "Danh sách điểm không được để trống"
                }, status=400)
            
            # Parse points
            points = parse_points_from_list(points_list)
            data_array = np.array(points)
            
            # Tạo model với centroids đã biết
            k = len(centroids)
            kmeans = KMeansClustering(k=k)
            kmeans.centroids = np.array(centroids)
            
            # Dự đoán
            labels = kmeans.predict(data_array)
            
            return JsonResponse({
                "status": "success",
                "labels": labels.tolist(),
                "points": points
            })
            
        except Exception as e:
            return JsonResponse({
                "error": f"Lỗi xử lý: {str(e)}"
            }, status=400)
    
    return JsonResponse({
        "error": "Chỉ chấp nhận POST"
    }, status=405)


@csrf_exempt
def load_example_data_view(request):
    """
    API endpoint để load dữ liệu ví dụ từ file CSV.
    
    GET /data_mining/cluster/load-example/?file=bai1 hoặc ?file=bai2
    """
    if request.method == 'GET':
        try:
            file_name = request.GET.get('file', 'bai1')
            
            # Xác định file CSV cần đọc
            if file_name == 'bai1':
                csv_file = 'Bai1_k2_data.csv'
            elif file_name == 'bai2':
                csv_file = 'Bai2_k3_data.csv'
            else:
                return JsonResponse({
                    "error": "File không hợp lệ. Chỉ chấp nhận 'bai1' hoặc 'bai2'"
                }, status=400)
            
            # Đường dẫn đến file CSV
            csv_path = os.path.join(
                settings.BASE_DIR, 
                'train_model', 
                'KMeans', 
                'data', 
                csv_file
            )
            
            # Kiểm tra file tồn tại
            if not os.path.exists(csv_path):
                return JsonResponse({
                    "error": f"Không tìm thấy file {csv_file}"
                }, status=404)
            
            # Đọc file CSV
            df = pd.read_csv(csv_path, index_col=0)
            
            # Chuyển đổi sang định dạng JSON
            points = []
            for idx, row in df.iterrows():
                points.append({
                    'id': str(idx),
                    'x': float(row['x']),
                    'y': float(row['y'])
                })
            
            # Xác định giá trị k mặc định
            k_default = 2 if file_name == 'bai1' else 3
            
            return JsonResponse({
                "status": "success",
                "file": csv_file,
                "points": points,
                "k": k_default,
                "num_points": len(points)
            })
            
        except Exception as e:
            return JsonResponse({
                "error": f"Lỗi đọc file: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        "error": "Chỉ chấp nhận GET"
    }, status=405)

