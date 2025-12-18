from django.urls import path
from . import views
from .service.classification_decisionTrees_views import (
    predict_gini_view,
    predict_id3_view,
    predict_bayes_view
)

urlpatterns = [
    # URL Cho API Dự Đoán
    path('predict/gini/', predict_gini_view, name='api_predict_gini'),
    path('predict/id3/', predict_id3_view, name='api_predict_id3'),
    path('predict/naivebayes/', predict_bayes_view, name='api_predict_bayes'),

    # URL Cho Giao Diện UI (Pages)
    # ------------------
    path('index/', views.index_view, name='home'), # Trang chủ
    # URL cho trang Lab Cây Quyết định (để kiểm tra liên kết sidebar)
    path('lab/dt/', views.decision_tree_lab_view, name='decision_tree_lab'),
    
]