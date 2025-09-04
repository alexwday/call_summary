from flask import Flask, request, jsonify
from flask_cors import CORS
import mlx_whisper
import tempfile
import os
import time

app = Flask(__name__)
CORS(app)

# Load Whisper model path
print("Loading Whisper Small model...")
model_path = "mlx-community/whisper-small-mlx"
print("Whisper model ready!")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "model": "whisper-small-mlx"})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        # Check if audio file is in the request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        
        # Check if file is empty
        audio_file.seek(0, os.SEEK_END)
        file_size = audio_file.tell()
        audio_file.seek(0)
        
        if file_size == 0:
            print("Received empty audio file")
            return jsonify({"error": "Audio file is empty"}), 400
        
        print(f"Received audio file, size: {file_size} bytes")
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
            audio_file.save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            print(f"Transcribing audio file: {temp_path}")
            start_time = time.time()
            
            # Check file size on disk
            disk_size = os.path.getsize(temp_path)
            print(f"Saved file size: {disk_size} bytes")
            
            if disk_size < 100:  # Too small to be valid audio
                print("Audio file too small to process")
                return jsonify({"error": "Audio file too small"}), 400
            
            # Transcribe the audio
            result = mlx_whisper.transcribe(
                temp_path,
                path_or_hf_repo=model_path,
                verbose=False
            )
            
            transcription = result["text"].strip()
            
            transcription_time = time.time() - start_time
            print(f"Transcription complete in {transcription_time:.2f}s: {transcription}")
            
            if not transcription:
                return jsonify({"error": "No speech detected"}), 400
            
            return jsonify({
                "text": transcription,
                "time": transcription_time
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting STT server on http://127.0.0.1:5002")
    app.run(host='0.0.0.0', port=5002, debug=False)