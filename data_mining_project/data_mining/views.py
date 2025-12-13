# data_mining/views.py

from django.shortcuts import render
from django.http import HttpRequest

# Hàm View cho trang Home/Giới thiệu chung (index.html)
def index_view(request: HttpRequest):
    """Render trang giới thiệu chung."""
    return render(request, 'index.html', {
        'project_name': 'Thực hành các thuật toán đã học trên Python'
    })

# Hàm View cho trang Lab Cây Quyết định (lab_decision_tree.html)
def decision_tree_lab_view(request: HttpRequest):
    """Render trang Lab riêng cho Phân lớp Cây Quyết định."""
    return render(request, 'lab_decision_tree.html', {
        'page_title': 'Phân lớp Cây Quyết định Lab'
    })

