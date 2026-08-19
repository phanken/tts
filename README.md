# Giọng Nhà Đài - Viettel AI

Web chuyển văn bản tiếng Việt thành giọng nói miền Bắc bằng Viettel AI TTS.

## Giọng/preset
- Nam Bắc - Thời sự: Thanh Tùng
- Nữ Bắc - Thời sự: Quỳnh Anh
- Nam Bắc - Quảng cáo: Nam Khánh
- Nữ Bắc - Quảng cáo: Thảo Chi
- Nam Bắc - Thuyết minh: Tiến Quân
- Có thể chọn thêm các giọng Bắc khác trong giao diện.

## Deploy Render
1. Upload thư mục này lên GitHub.
2. Render -> New -> Web Service -> chọn repository.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
5. Environment -> Add Environment Variable:
   - Key: `VIETTEL_AI_TOKEN`
   - Value: token Viettel AI của bạn
6. Deploy.

## Bảo mật
Token chỉ được đọc từ biến môi trường phía server, không xuất hiện trong HTML/JavaScript trình duyệt.
