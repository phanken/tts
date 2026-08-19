from flask import Flask, render_template, request, jsonify, send_file
import os, tempfile, uuid
import requests

app = Flask(__name__)

VIETTEL_TTS_URL = 'https://viettelai.vn/tts/speech_synthesis'
OUT = os.path.join(tempfile.gettempdir(), 'tts_viettel_nhadai')
os.makedirs(OUT, exist_ok=True)

# Viettel AI Northern voices. IDs are sent directly to Viettel's TTS API.
VOICES = {
    'hn-thanhtung': {'label': 'Thanh Tùng', 'gender': 'Nam', 'region': 'Miền Bắc'},
    'hn-namkhanh': {'label': 'Nam Khánh', 'gender': 'Nam', 'region': 'Miền Bắc'},
    'hn-tienquan': {'label': 'Tiến Quân', 'gender': 'Nam', 'region': 'Miền Bắc'},
    'hn-quynhanh': {'label': 'Quỳnh Anh', 'gender': 'Nữ', 'region': 'Miền Bắc'},
    'hn-thaochi': {'label': 'Thảo Chi', 'gender': 'Nữ', 'region': 'Miền Bắc'},
    'hn-phuongtrang': {'label': 'Phương Trang', 'gender': 'Nữ', 'region': 'Miền Bắc'},
    'hn-thanhha': {'label': 'Thanh Hà', 'gender': 'Nữ', 'region': 'Miền Bắc'},
    'hn-thanhphuong': {'label': 'Thanh Phương', 'gender': 'Nữ', 'region': 'Miền Bắc'},
}

PRESETS = {
    'nam_thoi_su': {'voice': 'hn-thanhtung', 'speed': 0.95, 'label': 'Nam Bắc - Thời sự'},
    'nu_thoi_su': {'voice': 'hn-quynhanh', 'speed': 0.95, 'label': 'Nữ Bắc - Thời sự'},
    'nam_quang_cao': {'voice': 'hn-namkhanh', 'speed': 1.10, 'label': 'Nam Bắc - Quảng cáo'},
    'nu_quang_cao': {'voice': 'hn-thaochi', 'speed': 1.10, 'label': 'Nữ Bắc - Quảng cáo'},
    'thuyet_minh': {'voice': 'hn-tienquan', 'speed': 0.90, 'label': 'Nam Bắc - Thuyết minh'},
}

@app.get('/')
def index():
    return render_template('index.html', presets=PRESETS, voices=VOICES, token_ready=bool(os.environ.get('VIETTEL_AI_TOKEN')))

@app.get('/api/status')
def status():
    return jsonify({'ok': True, 'token_ready': bool(os.environ.get('VIETTEL_AI_TOKEN'))})

@app.post('/api/tts')
def tts():
    token = os.environ.get('VIETTEL_AI_TOKEN', '').strip()
    if not token:
        return jsonify({'ok': False, 'error': 'Chưa cấu hình VIETTEL_AI_TOKEN trên Render.'}), 500

    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    preset_id = data.get('preset', 'nam_thoi_su')
    voice = (data.get('voice') or '').strip()

    if not text:
        return jsonify({'ok': False, 'error': 'Vui lòng nhập văn bản.'}), 400
    if len(text) > 5000:
        return jsonify({'ok': False, 'error': 'Bản web giới hạn 5.000 ký tự mỗi lần để xử lý ổn định.'}), 400

    preset = PRESETS.get(preset_id, PRESETS['nam_thoi_su'])
    if voice not in VOICES:
        voice = preset['voice']

    try:
        speed = float(data.get('speed', preset['speed']))
    except (TypeError, ValueError):
        speed = preset['speed']
    speed = max(0.8, min(1.2, speed))

    payload = {
        'text': text,
        'voice': voice,
        'speed': speed,
        'tts_return_option': 3,
        'token': token,
        'without_filter': False,
    }

    try:
        r = requests.post(
            VIETTEL_TTS_URL,
            json=payload,
            headers={'accept': '*/*', 'Content-Type': 'application/json'},
            timeout=120,
        )
    except requests.RequestException as e:
        return jsonify({'ok': False, 'error': f'Không kết nối được Viettel AI: {e}'}), 502

    if not r.ok:
        msg = r.text[:500] if r.text else f'HTTP {r.status_code}'
        return jsonify({'ok': False, 'error': f'Viettel AI trả lỗi: {msg}'}), 502

    content_type = (r.headers.get('content-type') or '').lower()
    if 'application/json' in content_type:
        try:
            info = r.json()
        except Exception:
            info = {'raw': r.text[:500]}
        return jsonify({'ok': False, 'error': f'API chưa trả file âm thanh: {info}'}), 502

    if len(r.content) < 200:
        return jsonify({'ok': False, 'error': 'Dữ liệu âm thanh trả về quá ngắn hoặc không hợp lệ.'}), 502

    fn = f'{uuid.uuid4().hex}.mp3'
    path = os.path.join(OUT, fn)
    with open(path, 'wb') as f:
        f.write(r.content)

    return jsonify({'ok': True, 'url': f'/audio/{fn}', 'filename': fn, 'voice': voice, 'speed': speed})

@app.get('/audio/<name>')
def audio(name):
    safe = os.path.basename(name)
    if not safe.endswith('.mp3'):
        return 'Not found', 404
    path = os.path.join(OUT, safe)
    if not os.path.exists(path):
        return 'Not found', 404
    return send_file(path, mimetype='audio/mpeg', as_attachment=False, download_name='giong-nha-dai-viettel.mp3')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
