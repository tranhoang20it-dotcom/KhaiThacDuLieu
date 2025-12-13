# your_app/views/classification_decisionTrees_views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import joblib
import os
import pandas as pd
from django.conf import settings
from typing import Dict, List, Any


# ====================================================================
# A. CẤU HÌNH VÀ QUẢN LÝ CACHE (Độc lập cho 3 models)
# ====================================================================

# 1. Định nghĩa TÊN FILE và TÊN FEATURE cho mỗi model
MODEL_CONFIGS = {
    'GINI_CART': {
        'pipeline': 'decision_tree_gini_pipeline.joblib',
        'encoder': 'gini_target_encoder.joblib',
        # Đảm bảo các feature này khớp CHÍNH XÁC với UI gửi lên
        'features': ['Outlook', 'Temperature', 'Humidity', 'Wind'] 
    },
    'ID3_Entropy': {
        'pipeline': 'decision_tree_id3_pipeline.joblib',
        'encoder': 'id3_target_encoder.joblib',
        'features': ['Outlook', 'Temp', 'Humidity', 'Wind'] 
    },
    'NAIVE_BAYES': {
        'pipeline': 'naive_bayes_pipeline.joblib',
        'encoder': 'nb_target_encoder.joblib',
        'features': ['Outlook', 'Temperature', 'Humidity', 'Wind']
    }
}

# Cache toàn cục để lưu trữ model đã load
MODEL_CACHE: Dict[str, Any] = {}
ENCODER_CACHE: Dict[str, Any] = {}


def _load_model(model_name: str):
    """Tải pipeline và encoder cho một model cụ thể vào cache."""
    if model_name in MODEL_CACHE and model_name in ENCODER_CACHE:
        return

    config = MODEL_CONFIGS.get(model_name)
    if not config:
        raise ValueError(f"Model '{model_name}' không được cấu hình.")

    # Xây dựng đường dẫn file tuyệt đối
    # CHỈNH SỬA ĐƯỜNG DẪN NÀY NẾU CẦN
    MODEL_DIR = os.path.join(settings.BASE_DIR, 'data_mining', 'models')

    pipeline_path = os.path.join(MODEL_DIR, config['pipeline'])
    encoder_path = os.path.join(MODEL_DIR, config['encoder'])

    try:
        MODEL_CACHE[model_name] = joblib.load(pipeline_path)
        ENCODER_CACHE[model_name] = joblib.load(encoder_path)
        print(f"   [OK] Đã tải Model/Encoder: {model_name}")
    except Exception as e:
        # Nếu lỗi tải file, báo lỗi ngay lập tức
        raise RuntimeError(f"Lỗi tải file {model_name}: {e}. Kiểm tra đường dẫn: {pipeline_path}")


def _run_single_prediction(model_name: str, raw_data: Dict) -> str:
    """
    Hàm lõi để chạy dự đoán cho bất kỳ model nào.
    """
    # 1. Tải Model (Nếu chưa có trong cache)
    _load_model(model_name)
    
    pipeline = MODEL_CACHE[model_name]
    encoder = ENCODER_CACHE[model_name]
    features = MODEL_CONFIGS[model_name]['features']
    
    # 2. Xử lý input thô thành DataFrame (Dạng chuỗi)
    input_data = {col: [raw_data.get(col, '')] for col in features}
    input_df = pd.DataFrame(input_data, columns=features)
    
    # 3. Dự đoán (Pipeline tự xử lý tiền xử lý)
    prediction_int = pipeline.predict(input_df)[0]
    
    # 4. Giải mã và trả về label
    prediction_label = encoder.inverse_transform([prediction_int])[0]
    
    return prediction_label

# Tải tất cả các models khi file views được import lần đầu
try:
    for name in MODEL_CONFIGS.keys():
        _load_model(name)
except Exception as e:
    # Lỗi tải sẽ được in ra, nhưng không làm crash toàn bộ ứng dụng
    print(f"Lỗi lớn khi khởi tạo Models: {e}")


# ====================================================================
# HÀM CHUẨN HÓA TÊN THUỘC TÍNH
# ====================================================================

def _normalize_input_data(model_name: str, raw_data: Dict) -> Dict:
    """
    Chuẩn hóa tên key 'Temp' thành 'Temperature' nếu mô hình yêu cầu.
    Giả định FE luôn gửi tên Select Box là 'Temp' (tên ngắn gọn).
    """
    normalized_data = raw_data.copy()
    
    # Chỉ áp dụng chuyển đổi cho GINI và NAIVE_BAYES
    if model_name in ['GINI_CART', 'NAIVE_BAYES']:
        if 'Temp' in normalized_data:
            temp_value = normalized_data.pop('Temp')  # Xóa key cũ
            normalized_data['Temperature'] = temp_value # Thêm key mới
    
    # ID3 giữ nguyên tên 'Temp'
    return normalized_data


# ====================================================================
# B. CÁC VIEW ENDPOINT RIÊNG (Dành cho Postman)
# ====================================================================

# Sử dụng csrf_exempt cho API test trên Postman
@csrf_exempt 
def predict_gini_view(request):
    """API endpoint cho mô hình GINI/CART."""
    if request.method == 'POST':
        try:
            # Đọc JSON data từ body request
            raw_data = json.loads(request.body)
            
            # Gọi hàm lõi
            # prediction = _run_single_prediction('GINI_CART', raw_data)

            # BƯỚC SỬA LỖI: Chuẩn hóa tên thuộc tính cho GINI/CART
            processed_data = _normalize_input_data('GINI_CART', raw_data)

            prediction = _run_single_prediction('GINI_CART', processed_data)
            
            return JsonResponse({
                "status": "success",
                "model": "GINI_CART (Decision Tree)",
                "prediction": prediction
            })
        except Exception as e:
            return JsonResponse({"error": f"Lỗi xử lý GINI: {e}"}, status=400)
    return JsonResponse({"error": "Chỉ chấp nhận POST"}, status=405)


@csrf_exempt
def predict_id3_view(request):
    """API endpoint cho mô hình ID3/Entropy."""
    if request.method == 'POST':
        try:
            raw_data = json.loads(request.body)

            # BƯỚC CHUẨN HÓA
            processed_data = _normalize_input_data('ID3_Entropy', raw_data)

            prediction = _run_single_prediction('ID3_Entropy', raw_data)
            
            return JsonResponse({
                "status": "success",
                "model": "ID3_Entropy (Decision Tree)",
                "prediction": prediction
            })
        except Exception as e:
            return JsonResponse({"error": f"Lỗi xử lý ID3: {e}"}, status=400)
    return JsonResponse({"error": "Chỉ chấp nhận POST"}, status=405)


@csrf_exempt
def predict_bayes_view(request):
    """API endpoint cho mô hình Naive Bayes."""
    if request.method == 'POST':
        try:
            raw_data = json.loads(request.body)

            # BƯỚC CHUẨN HÓA: Chuẩn hóa tên thuộc tính cho NAIVE_BAYES
            processed_data = _normalize_input_data('NAIVE_BAYES', raw_data)

            prediction = _run_single_prediction('NAIVE_BAYES', processed_data)
            
            return JsonResponse({
                "status": "success",
                "model": "NAIVE_BAYES",
                "prediction": prediction
            })
        except Exception as e:
            return JsonResponse({"error": f"Lỗi xử lý Naive Bayes: {e}"}, status=400)
    return JsonResponse({"error": "Chỉ chấp nhận POST"}, status=405)