from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import subprocess
import uuid
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Dosya yükleme ve çıktı klasörleri oluşturma
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Klasörler yoksa oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB limit

# Dosya uzantısı kontrolü
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Video yükleme
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return redirect(request.url)
    
    file = request.files['video']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Benzersiz dosya adı oluştur
        original_filename = secure_filename(file.filename)
        filename_base = str(uuid.uuid4())
        extension = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{filename_base}.{extension}"
        
        # Dosyayı kaydet
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return redirect(url_for('video_info', filename=filename))
    
    return "Desteklenmeyen dosya formatı!"

# Video bilgisi sayfası
@app.route('/video/<filename>')
def video_info(filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template('video_info.html', filename=filename)

# Wide efekti uygulama
@app.route('/apply_wide_effect', methods=['POST'])
def apply_wide_effect():
    filename = request.form['filename']
    width_factor = request.form['width_factor']
    
    # Giriş dosyasının tam yolu
    input_video = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Çıkış dosyası için benzersiz isim
    output_filename = f"wide_{uuid.uuid4()}.mp4"
    output_video = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    try:
        # FFmpeg komutu - genişliği belirtilen faktör kadar arttır
        ffmpeg_command = [
            "ffmpeg",
            "-i", input_video,
            "-vf", f"scale=iw*{width_factor}:ih,setsar=1",
            "-c:a", "copy",
            output_video
        ]
        
        # Komutu çalıştır
        subprocess.run(ffmpeg_command, check=True)
        
        return redirect(url_for('result', filename=output_filename))
    except subprocess.CalledProcessError as e:
        return f"İşlem sırasında hata oluştu: {e}"
    except Exception as e:
        return f"Beklenmeyen bir hata oluştu: {e}"

# İşlem sonucu sayfası
@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)

# Video oynatma
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/outputs/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

# Uygulamayı başlat
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
