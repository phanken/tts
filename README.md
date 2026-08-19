# Giọng Nhà Đài

Web TTS tiếng Việt dùng `edge-tts`.

## Chạy local
```bash
pip install -r requirements.txt
python app.py
```
Mở http://localhost:10000

## Render
Push toàn bộ thư mục lên GitHub, tạo Web Service trên Render.
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`

Giọng mặc định: `vi-VN-NamMinhNeural`.


## Preset
- Nam thời sự
- Nữ thời sự
- Bản tin nhanh
- Thuyết minh
- Quảng cáo (nhịp nhanh hơn, cao độ sáng hơn)
