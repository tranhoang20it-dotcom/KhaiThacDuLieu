// ======================================================================
// decision_tree_handler.js (SỬ DỤNG JQUERY AJAX)
// Kết nối UI (Select Box) với Backend API
// ======================================================================

$(document).ready(function() {
    // 1. Lấy các thành phần UI bằng JQuery
    const form = $('#prediction_form');
    const modelChoice = $('#model_choice');
    const runBtn = $('#run_algo_btn');
    const loadingBar = $('#loading_progress');
    const resultSection = $('#result_section');
    const predictionResult = $('#api_prediction_result');
    const modelUsedDisplay = $('#model_used_display');
    const apiResponseRaw = $('#api_response_raw');
    
    // Lấy CSRF token từ thẻ input ẩn trong form
    const csrftoken = $('input[name="csrfmiddlewaretoken"]').val(); 

    // 2. Xử lý sự kiện gửi form
    form.on('submit', function(e) {
        e.preventDefault(); // Ngăn form gửi theo cách truyền thống

        // Lấy model đã chọn (gini, id3, hoặc bayes)
        const model = modelChoice.val();
        
        // Thu thập dữ liệu từ tất cả các Select Box có thuộc tính 'name'
        const rawData = {};
        
        // Sử dụng JQuery .each() để lặp qua các select box
        $('select[name]').each(function() {
            rawData[$(this).attr('name')] = $(this).val().trim();
        });
        
        // 3. Chọn API Endpoint (Ví dụ: /data_mining/api/predict/id3/)
        const endpoint = `/data_mining/predict/${model}/`; 

        // 4. Bắt đầu trạng thái Loading
        runBtn.prop('disabled', true); // prop() dùng cho thuộc tính boolean
        runBtn.html('<i class="fas fa-spinner fa-spin me-2"></i> Đang chạy...');
        loadingBar.show(); // show() là hàm JQuery tương đương display: block
        resultSection.hide(); // hide() là hàm JQuery tương đương display: none
        
        predictionResult.removeClass('text-success text-danger text-warning');

        // 5. Gửi Request POST bằng JQuery AJAX
        $.ajax({
            url: endpoint,
            type: 'POST',
            data: JSON.stringify(rawData), // Chuyển đổi object thành JSON string
            contentType: 'application/json', // Đặt Content-Type là JSON
            headers: {
                // Đính kèm CSRF Token để Django chấp nhận POST request
                'X-CSRFToken': csrftoken 
            },
            
            // Xử lý khi yêu cầu thành công (HTTP 2xx)
            success: function(result) {
                // // Debug: hiển thị phản hồi API thô
                // apiResponseRaw.text(JSON.stringify(result, null, 2));

                if (result.status === 'success') {
                    const prediction = result.prediction;
                    
                    predictionResult.text(prediction);
                    modelUsedDisplay.text(`Sử dụng mô hình: ${result.model}`);
                    
                    // Cập nhật màu sắc kết quả
                    if (prediction.toLowerCase() === 'yes') {
                        predictionResult.addClass('text-success');
                        apiResponseRaw.text("Kết quả dự đoán là có chơi goft");
                    } else if (prediction.toLowerCase() === 'no') {
                        predictionResult.addClass('text-danger');
                        apiResponseRaw.text("Kết quả dự đoán là không chơi goft");
                    } else {
                        predictionResult.addClass('text-warning');
                    }
                    
                } else {
                    // Xử lý lỗi logic từ Backend (Lỗi xử lý GINI, lỗi thiếu trường)
                    predictionResult.text('Lỗi');
                    modelUsedDisplay.text(`Lỗi Backend: ${result.error || 'Lỗi không xác định.'}`);
                    predictionResult.addClass('text-danger');
                }
                
                resultSection.show(); // Hiện kết quả

            },
            
            // Xử lý khi yêu cầu thất bại (Lỗi kết nối, HTTP 4xx, 5xx)
            error: function(xhr, status, error) {
                let errorMsg = 'Lỗi kết nối hoặc lỗi server.';
                let backendResponse = xhr.responseJSON ? xhr.responseJSON.error : 'Không có phản hồi từ server.';
                
                predictionResult.text('Lỗi API');
                modelUsedDisplay.text(`Lỗi: ${backendResponse}`);
                predictionResult.addClass('text-danger');
                
                apiResponseRaw.text(`Trạng thái: ${status}\nLỗi: ${error}\nPhản hồi Server: ${JSON.stringify(xhr.responseJSON, null, 2)}`);
                    
                resultSection.show();
            },
            
            // Luôn chạy sau khi request hoàn tất (dù thành công hay thất bại)
            complete: function() {
                // 7. Kết thúc trạng thái Loading
                runBtn.prop('disabled', false);
                runBtn.html('<i class="fas fa-play me-2"></i> CHẠY DỰ ĐOÁN');
                loadingBar.hide();
            }
        });
    });
});