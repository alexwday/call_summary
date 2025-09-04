from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import io
import soundfile as sf
from mlx_audio.tts.models.kokoro import KokoroPipeline
from mlx_audio.tts.utils import load_model
import numpy as np
import time

app = Flask(__name__)
CORS(app)

# Initialize Kokoro pipeline
print("Loading Kokoro 82M model...")
model_id = 'mlx-community/Kokoro-82M-4bit'
model = load_model(model_id)
pipeline = KokoroPipeline(lang_code='a', model=model, repo_id=model_id)
print("Model loaded successfully!")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "model": "Kokoro-82M-4bit"})

@app.route('/generate', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        text = data.get('text', '')
        # Accept speed parameter from client, default to 1.27 for slightly faster speech
        speed = data.get('speed', 1.27)
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        print(f"Generating audio for: {text} (speed: {speed})")
        start_time = time.time()
        
        # Generate audio using Kokoro
        # The pipeline returns a generator of (graphemes, phonemes, audio)
        result = list(pipeline(text, voice='af_heart', speed=speed))
        if result:
            _, _, audio_array = result[0]
        else:
            raise ValueError("No audio generated")
        
        # Convert to numpy array if needed
        if hasattr(audio_array, 'numpy'):
            audio_array = audio_array.numpy()
        
        # Ensure audio is in the right format (float32, -1 to 1 range)
        audio_array = np.array(audio_array, dtype=np.float32)
        
        # If audio is 2D, take the first channel
        if len(audio_array.shape) > 1:
            audio_array = audio_array[0]
        
        # Normalize if needed
        max_val = np.max(np.abs(audio_array))
        if max_val > 1.0:
            audio_array = audio_array / max_val
        
        generation_time = time.time() - start_time
        print(f"Audio generated in {generation_time:.2f} seconds")
        
        # Convert to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio_array, samplerate=24000, format='WAV')
        buffer.seek(0)
        
        return Response(
            buffer.getvalue(),
            mimetype='audio/wav',
            headers={
                'Content-Disposition': 'inline; filename="output.wav"',
                'X-Generation-Time': str(generation_time)
            }
        )
        
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_stream', methods=['POST'])
def generate_stream():
    """Stream audio generation for longer texts"""
    try:
        data = request.json
        text = data.get('text', '')
        # Accept speed parameter from client, default to 1.27 for slightly faster speech
        speed = data.get('speed', 1.27)
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        def generate():
            try:
                print(f"Streaming audio for: {text} (speed: {speed})")
                
                # Generate audio
                # The pipeline returns a generator of (graphemes, phonemes, audio)
                result = list(pipeline(text, voice='af_heart', speed=speed))
                if result:
                    _, _, audio_array = result[0]
                else:
                    raise ValueError("No audio generated")
                
                # Convert to numpy array
                if hasattr(audio_array, 'numpy'):
                    audio_array = audio_array.numpy()
                
                audio_array = np.array(audio_array, dtype=np.float32)
                
                # If audio is 2D, take the first channel
                if len(audio_array.shape) > 1:
                    audio_array = audio_array[0]
                
                # Normalize
                max_val = np.max(np.abs(audio_array))
                if max_val > 1.0:
                    audio_array = audio_array / max_val
                
                # Stream in chunks
                chunk_size = 8192  # samples per chunk
                for i in range(0, len(audio_array), chunk_size):
                    chunk = audio_array[i:i+chunk_size]
                    
                    # Convert chunk to WAV bytes
                    buffer = io.BytesIO()
                    sf.write(buffer, chunk, samplerate=24000, format='WAV')
                    buffer.seek(0)
                    
                    yield buffer.getvalue()
                    
            except Exception as e:
                print(f"Error in stream generation: {str(e)}")
                yield b''
        
        return Response(generate(), mimetype='audio/wav')
        
    except Exception as e:
        print(f"Error in stream endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting TTS server on http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)