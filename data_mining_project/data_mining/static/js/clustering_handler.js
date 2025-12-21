// ======================================================================
// clustering_handler.js
// Xử lý UI và API cho K-Means Clustering
// ======================================================================

let pointCounter = 0;
let clusteringChart = null;

$(document).ready(function() {
    // Khởi tạo với 2 điểm mặc định
    addPoint();
    addPoint();
    
    // Lấy các thành phần UI
    const form = $('#clustering_form');
    const runBtn = $('#run_algo_btn');
    const loadingBar = $('#loading_progress');
    const resultSection = $('#result_section');
    const csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
    
    // Theo dõi thay đổi để tự động xóa kết quả cũ
    setupChangeListeners();
    
    // Xử lý sự kiện gửi form
    form.on('submit', function(e) {
        e.preventDefault();
        
        // Thu thập dữ liệu
        const k = parseInt($('#k_input').val());
        const points = collectPoints();
        
        if (points.length === 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Thiếu dữ liệu',
                text: 'Vui lòng nhập ít nhất một điểm!',
                confirmButtonColor: '#0d6efd',
                confirmButtonText: 'Đã hiểu'
            });
            return;
        }
        
        if (k < 1 || k > points.length) {
            Swal.fire({
                icon: 'error',
                title: 'Giá trị k không hợp lệ',
                html: `Số cụm k phải >= 1 và <= ${points.length} (số điểm)<br>Hiện tại bạn có ${points.length} điểm`,
                confirmButtonColor: '#0d6efd',
                confirmButtonText: 'Đã hiểu'
            });
            return;
        }
        
        // Chuẩn bị dữ liệu gửi lên server
        const requestData = {
            points: points,
            k: k,
            max_iters: 100
        };
        
        // Bắt đầu loading
        runBtn.prop('disabled', true);
        runBtn.html('<i class="fas fa-spinner fa-spin me-2"></i> Đang chạy...');
        loadingBar.show();
        resultSection.hide();
        
        // Gửi request
        $.ajax({
            url: '/data_mining/cluster/kmeans/',
            type: 'POST',
            data: JSON.stringify(requestData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrftoken
            },
            
            success: function(result) {
                if (result.status === 'success') {
                    displayResults(result);
                    resultSection.show();
                    // Thông báo thành công
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công!',
                        text: `Đã hoàn thành gom cụm với ${result.iterations} lần lặp`,
                        timer: 2000,
                        timerProgressBar: true,
                        showConfirmButton: false
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi xử lý',
                        text: result.error || 'Lỗi không xác định',
                        confirmButtonColor: '#dc3545',
                        confirmButtonText: 'Đã hiểu'
                    });
                }
            },
            
            error: function(xhr, status, error) {
                let errorMsg = 'Lỗi kết nối hoặc lỗi server.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi kết nối',
                    html: `<strong>Chi tiết lỗi:</strong><br>${errorMsg}`,
                    confirmButtonColor: '#dc3545',
                    confirmButtonText: 'Đã hiểu'
                });
            },
            
            complete: function() {
                runBtn.prop('disabled', false);
                runBtn.html('<i class="fas fa-play me-2"></i> CHẠY K-MEANS');
                loadingBar.hide();
            }
        });
    });
});

// Thiết lập event listeners để theo dõi thay đổi
function setupChangeListeners() {
    // Theo dõi thay đổi giá trị k
    $(document).on('input change', '#k_input', function() {
        clearOldResults();
    });
    
    // Theo dõi thay đổi các điểm (sử dụng event delegation cho các điểm được thêm động)
    $(document).on('input change', '.point-x, .point-y', function() {
        clearOldResults();
    });
    
    // Theo dõi khi thêm/xóa điểm
    const observer = new MutationObserver(function(mutations) {
        clearOldResults();
    });
    
    const pointsContainer = document.getElementById('points_container');
    if (pointsContainer) {
        observer.observe(pointsContainer, {
            childList: true,
            subtree: true
        });
    }
}

// Xóa biểu đồ và kết quả cũ
function clearOldResults() {
    // Hủy biểu đồ cũ nếu có
    if (clusteringChart) {
        clusteringChart.destroy();
        clusteringChart = null;
    }
    
    // Ẩn phần kết quả
    $('#result_section').hide();
    
    // Xóa nội dung kết quả (tùy chọn - có thể giữ lại để so sánh)
    // $('#result_info').empty();
    // $('#clusters_detail').empty();
}

// Thêm một điểm mới vào form
function addPoint() {
    pointCounter++;
    const pointHtml = `
        <div class="row mb-2 point-row" data-point-id="${pointCounter}">
            <div class="col-5">
                <input type="number" step="0.01" class="form-control form-control-sm point-x" 
                       placeholder="x" required>
            </div>
            <div class="col-5">
                <input type="number" step="0.01" class="form-control form-control-sm point-y" 
                       placeholder="y" required>
            </div>
            <div class="col-2">
                <button type="button" class="btn btn-sm btn-danger" onclick="removePoint(${pointCounter})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
    $('#points_container').append(pointHtml);
    // MutationObserver sẽ tự động xóa kết quả khi thêm điểm
}

// Xóa một điểm
function removePoint(pointId) {
    $(`.point-row[data-point-id="${pointId}"]`).remove();
    // MutationObserver sẽ tự động xóa kết quả khi xóa điểm
}

// Xóa tất cả điểm
function clearPoints() {
    Swal.fire({
        icon: 'warning',
        title: 'Xác nhận xóa',
        text: 'Bạn có chắc muốn xóa tất cả điểm?',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Xóa tất cả',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            $('#points_container').empty();
            pointCounter = 0;
            // Xóa kết quả khi xóa tất cả điểm
            clearOldResults();
            Swal.fire({
                icon: 'success',
                title: 'Đã xóa',
                text: 'Tất cả điểm đã được xóa',
                timer: 1500,
                timerProgressBar: true,
                showConfirmButton: false
            });
        }
    });
}

// Thu thập tất cả điểm từ form
function collectPoints() {
    const points = [];
    $('.point-row').each(function() {
        const x = parseFloat($(this).find('.point-x').val());
        const y = parseFloat($(this).find('.point-y').val());
        if (!isNaN(x) && !isNaN(y)) {
            points.push({x: x, y: y});
        }
    });
    return points;
}

// Hiển thị kết quả
function displayResults(result) {
    // Hiển thị thông tin kết quả
    const infoHtml = `
        <p><strong>Số cụm (k):</strong> ${result.k}</p>
        <p><strong>Số lần lặp:</strong> ${result.iterations}</p>
        <p><strong>SSE (Sum of Squared Errors):</strong> ${result.sse}</p>
        <p><strong>Centroids:</strong></p>
        <ul>
            ${result.centroids.map((c, i) => 
                `<li>Cụm ${i}: (${c[0].toFixed(2)}, ${c[1].toFixed(2)})</li>`
            ).join('')}
        </ul>
    `;
    $('#result_info').html(infoHtml);
    
    // Hiển thị chi tiết các cụm
    let clustersHtml = '<div class="row">';
    for (let i = 0; i < result.k; i++) {
        const clusterKey = `cluster_${i}`;
        const clusterPoints = result.clusters[clusterKey] || [];
        const centroid = result.centroids[i];
        
        clustersHtml += `
            <div class="col-md-4 mb-3">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <strong>Cụm ${i}</strong> - ${clusterPoints.length} điểm
                    </div>
                    <div class="card-body">
                        <p><strong>Centroid:</strong> (${centroid[0].toFixed(2)}, ${centroid[1].toFixed(2)})</p>
                        <p><strong>Điểm:</strong></p>
                        <ul class="small">
                            ${clusterPoints.map(p => 
                                `<li>(${p[0].toFixed(2)}, ${p[1].toFixed(2)})</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }
    clustersHtml += '</div>';
    $('#clusters_detail').html(clustersHtml);
    
    // Vẽ biểu đồ
    drawChart(result);
}

// Vẽ biểu đồ kết quả
function drawChart(result) {
    const ctx = document.getElementById('clustering_chart').getContext('2d');
    
    // Chuẩn bị dữ liệu cho Chart.js
    const datasets = [];
    const colors = [
        'rgba(255, 99, 132, 0.6)',
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(75, 192, 192, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(255, 159, 64, 0.6)'
    ];
    
    // Thêm các điểm theo cụm
    for (let i = 0; i < result.k; i++) {
        const clusterKey = `cluster_${i}`;
        const clusterPoints = result.clusters[clusterKey] || [];
        const color = colors[i % colors.length];
        
        datasets.push({
            label: `Cụm ${i}`,
            data: clusterPoints.map(p => ({x: p[0], y: p[1]})),
            backgroundColor: color,
            borderColor: color.replace('0.6', '1'),
            pointRadius: 6,
            pointHoverRadius: 8
        });
    }
    
    // Thêm centroids
    datasets.push({
        label: 'Centroids',
        data: result.centroids.map(c => ({x: c[0], y: c[1]})),
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: 'rgba(0, 0, 0, 1)',
        pointRadius: 10,
        pointHoverRadius: 12,
        pointStyle: 'star'
    });
    
    // Hủy biểu đồ cũ nếu có
    if (clusteringChart) {
        clusteringChart.destroy();
    }
    
    // Tạo biểu đồ mới
    clusteringChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'X'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Y'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: (${context.parsed.x.toFixed(2)}, ${context.parsed.y.toFixed(2)})`;
                        }
                    }
                }
            }
        }
    });
}

// Load ví dụ Bài 1: k=2 với 4 điểm
function loadExample1() {
    // Xóa điểm hiện tại mà không cần confirm
    $('#points_container').empty();
    pointCounter = 0;
    
    // Xóa kết quả cũ
    clearOldResults();
    
    // Hiển thị loading
    Swal.fire({
        title: 'Đang tải dữ liệu...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Gọi API để load dữ liệu từ file CSV
    $.ajax({
        url: '/data_mining/cluster/load-example/',
        type: 'GET',
        data: { file: 'bai1' },
        success: function(result) {
            if (result.status === 'success') {
                // Thêm các điểm vào form
                result.points.forEach(p => {
                    addPoint();
                    const rows = $('.point-row');
                    const lastRow = rows.last();
                    lastRow.find('.point-x').val(p.x);
                    lastRow.find('.point-y').val(p.y);
                });
                
                // Set giá trị k
                $('#k_input').val(result.k);
                
                Swal.fire({
                    icon: 'success',
                    title: 'Đã tải ví dụ',
                    text: `Bài 1: k=${result.k} với ${result.num_points} điểm`,
                    timer: 2000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi tải dữ liệu',
                    text: result.error || 'Lỗi không xác định',
                    confirmButtonColor: '#dc3545',
                    confirmButtonText: 'Đã hiểu'
                });
            }
        },
        error: function(xhr, status, error) {
            let errorMsg = 'Lỗi kết nối hoặc lỗi server.';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMsg = xhr.responseJSON.error;
            }
            Swal.fire({
                icon: 'error',
                title: 'Lỗi tải dữ liệu',
                html: `<strong>Chi tiết lỗi:</strong><br>${errorMsg}`,
                confirmButtonColor: '#dc3545',
                confirmButtonText: 'Đã hiểu'
            });
        }
    });
}

// Load ví dụ Bài 2: k=3 với 9 điểm
function loadExample2() {
    // Xóa điểm hiện tại mà không cần confirm
    $('#points_container').empty();
    pointCounter = 0;
    
    // Xóa kết quả cũ
    clearOldResults();
    
    // Hiển thị loading
    Swal.fire({
        title: 'Đang tải dữ liệu...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Gọi API để load dữ liệu từ file CSV
    $.ajax({
        url: '/data_mining/cluster/load-example/',
        type: 'GET',
        data: { file: 'bai2' },
        success: function(result) {
            if (result.status === 'success') {
                // Thêm các điểm vào form
                result.points.forEach(p => {
                    addPoint();
                    const rows = $('.point-row');
                    const lastRow = rows.last();
                    lastRow.find('.point-x').val(p.x);
                    lastRow.find('.point-y').val(p.y);
                });
                
                // Set giá trị k
                $('#k_input').val(result.k);
                
                Swal.fire({
                    icon: 'success',
                    title: 'Đã tải ví dụ',
                    text: `Bài 2: k=${result.k} với ${result.num_points} điểm`,
                    timer: 2000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi tải dữ liệu',
                    text: result.error || 'Lỗi không xác định',
                    confirmButtonColor: '#dc3545',
                    confirmButtonText: 'Đã hiểu'
                });
            }
        },
        error: function(xhr, status, error) {
            let errorMsg = 'Lỗi kết nối hoặc lỗi server.';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMsg = xhr.responseJSON.error;
            }
            Swal.fire({
                icon: 'error',
                title: 'Lỗi tải dữ liệu',
                html: `<strong>Chi tiết lỗi:</strong><br>${errorMsg}`,
                confirmButtonColor: '#dc3545',
                confirmButtonText: 'Đã hiểu'
            });
        }
    });
}

