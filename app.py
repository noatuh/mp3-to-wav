from flask import Flask, request, send_from_directory, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
from pydub import AudioSegment

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Set the paths to ffmpeg and ffprobe here
AudioSegment.converter = os.path.join(os.getcwd(), "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(os.getcwd(), "ffprobe.exe")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def mp3_to_wav(input_file, output_file):
    audio = AudioSegment.from_mp3(input_file)
    audio.export(output_file, format="wav", bitrate="192k")

def wav_to_mp3(input_file, output_file):
    audio = AudioSegment.from_wav(input_file)
    audio.export(output_file, format="mp3", bitrate="192k")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        conversion_type = request.form['conversion']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            if conversion_type == "mp3_to_wav":
                output_filename = filename.rsplit('.', 1)[0] + ".wav"
                output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
                mp3_to_wav(input_path, output_path)
            elif conversion_type == "wav_to_mp3":
                output_filename = filename.rsplit('.', 1)[0] + ".mp3"
                output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
                wav_to_mp3(input_path, output_path)
            
            return redirect(url_for('download_file', filename=output_filename))
    return render_template('upload.html')

@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    app.run(debug=True)
