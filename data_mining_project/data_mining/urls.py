from django.urls import path
from . import views
from .service.classification_decisionTrees_views import (
    predict_gini_view,
    predict_id3_view,
    predict_bayes_view
)
from .service.clustering_views import (
    kmeans_cluster_view,
    kmeans_predict_view,
    load_example_data_view
)

urlpatterns = [
    # URL Cho API Dự Đoán (Classification)
    path('predict/gini/', predict_gini_view, name='api_predict_gini'),
    path('predict/id3/', predict_id3_view, name='api_predict_id3'),
    path('predict/naivebayes/', predict_bayes_view, name='api_predict_bayes'),

    # URL Cho API Gom cụm (Clustering)
    path('cluster/kmeans/', kmeans_cluster_view, name='api_kmeans_cluster'),
    path('cluster/kmeans/predict/', kmeans_predict_view, name='api_kmeans_predict'),
    path('cluster/load-example/', load_example_data_view, name='api_load_example_data'),

    # URL Cho Giao Diện UI (Pages)
    # ------------------
    path('index/', views.index_view, name='home'), # Trang chủ
    # URL cho trang Lab Cây Quyết định (để kiểm tra liên kết sidebar)
    path('lab/dt/', views.decision_tree_lab_view, name='decision_tree_lab'),
    # URL cho trang Lab Gom cụm K-Means
    path('lab/clustering/', views.clustering_lab_view, name='clustering_lab'),
    
]