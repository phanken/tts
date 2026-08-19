from flask import Flask, render_template, request, jsonify, send_file
import edge_tts, asyncio, tempfile, os, uuid

app = Flask(__name__)

VOICES = {
    'nam_thoi_su': {'voice':'vi-VN-NamMinhNeural','rate':'-5%','pitch':'-2Hz','label':'Nam thời sự'},
    'nu_thoi_su': {'voice':'vi-VN-HoaiMyNeural','rate':'-5%','pitch':'0Hz','label':'Nữ thời sự'},
    'ban_tin_nhanh': {'voice':'vi-VN-NamMinhNeural','rate':'+8%','pitch':'0Hz','label':'Bản tin nhanh'},
    'thuyet_minh': {'voice':'vi-VN-NamMinhNeural','rate':'-10%','pitch':'-3Hz','label':'Thuyết minh'},
    'quang_cao': {'voice':'vi-VN-NamMinhNeural','rate':'+12%','pitch':'+2Hz','label':'Quảng cáo'},
}

OUT = os.path.join(tempfile.gettempdir(), 'tts_nhadai')
os.makedirs(OUT, exist_ok=True)

@app.get('/')
def index():
    return render_template('index.html', voices=VOICES)

@app.post('/api/tts')
def tts():
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    preset = data.get('preset','nam_thoi_su')
    rate = data.get('rate')
    pitch = data.get('pitch')
    if not text:
        return jsonify({'ok':False,'error':'Vui lòng nhập văn bản.'}), 400
    if len(text) > 12000:
        return jsonify({'ok':False,'error':'Mỗi lần tối đa 12.000 ký tự.'}), 400
    cfg = VOICES.get(preset, VOICES['nam_thoi_su'])
    rate = rate or cfg['rate']
    pitch = pitch or cfg['pitch']
    fn = f"{uuid.uuid4().hex}.mp3"
    path = os.path.join(OUT, fn)
    async def run():
        c = edge_tts.Communicate(text=text, voice=cfg['voice'], rate=rate, pitch=pitch)
        await c.save(path)
    try:
        asyncio.run(run())
    except Exception as e:
        return jsonify({'ok':False,'error':f'Lỗi tạo giọng: {e}'}), 500
    return jsonify({'ok':True,'url':f'/audio/{fn}','filename':fn})

@app.get('/audio/<name>')
def audio(name):
    if not name.endswith('.mp3'):
        return 'Not found', 404
    path = os.path.join(OUT, os.path.basename(name))
    if not os.path.exists(path):
        return 'Not found', 404
    return send_file(path, mimetype='audio/mpeg', as_attachment=False, download_name='nha-dai.mp3')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
