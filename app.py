from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
import os
import json
import moviepy.editor as moviepy
from video_transcriber import transcribe_video
from video_processor import generate_segments, generate_summary
import ffmpeg

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mpg', 'mpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Limit to 100MB

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_mpg_to_mp4(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, vcodec="libx264", acodec="aac")
        .run()
    )


# Allow users to upload video and store
@app.route('/', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        # Check if a file is submitted
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Ensure mp4
            extension = os.path.splitext(filename)[1]
            if extension == ".mpg":
                output_file = os.path.splitext(filepath)[0] + ".mp4"
                convert_mpg_to_mp4(filepath, output_file)
                filename = os.path.splitext(filename)[0] + ".mp4"
                filepath = output_file
            print(filepath, filename)
            session['video_filename'] = filename
            session['video_filepath'] = filepath
            session['transcription_status'] = 'in_progress'

            # Run transcription synchronously and store the output file
            transcription_file = transcribe_video(filepath)

            # Once transcription is done, mark status as complete
            session['transcription_status'] = 'completed'
            session['transcription_file'] = transcription_file

            return render_template('index.html', video_url=url_for('static', filename=f'uploads/{filename}'), transcription_status=session['transcription_status'])
    return render_template('index.html', video_url=None, transcription_status=None)


# Process the video
@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video_filepath' not in session or session['transcription_status'] != 'completed':
        return jsonify({'success': False, 'message': 'Transcription not completed yet'})

    action_type = request.form.get('action')
    if action_type not in ['segments', 'summary']:
        return jsonify({'success': False, 'message': 'Invalid process type'})

    video_path = session['video_filepath']

    try:
        if action_type == 'segments':
            json_path = generate_segments(video_path, session.get('transcription_file'))
            session['json_path'] = json_path
        elif action_type == 'summary':
            json_path = generate_summary(video_path)
            session['json_path'] = json_path

        # Read the generated JSON file
        with open(json_path, 'r') as f:
            json_data = json.load(f)

        return jsonify({'success': True, 'data': json_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# Show results
@app.route('/result/<result_type>')
def show_result(result_type):
    if 'json_path' not in session:
        return redirect(url_for('upload_video'))

    json_path = session['json_path']
    video_filename = session['video_filename']

    try:
        with open(json_path, 'r') as f:
            json_data = json.load(f)

        return render_template('index.html',
                               video_url=url_for(
                                   'static', filename=f'uploads/{video_filename}'),
                               json_data=json.dumps(json_data, indent=4))
    except Exception as e:
        return render_template('index.html',
                               video_url=url_for(
                                   'static', filename=f'uploads/{video_filename}'),
                               json_data=f"Error loading results: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
