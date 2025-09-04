#!/usr/bin/env python3
"""
Pre-download ML models with SSL certificate support.
This script can be run to download models before starting the app.
"""

import os
import sys
import ssl
import urllib.request

def configure_ssl():
    """Configure SSL settings based on environment."""
    ssl_verify = os.environ.get('SSL_VERIFY', 'true').lower() == 'true'
    ssl_cert_file = os.environ.get('SSL_CERT_FILE', 'rbc-ca-bundle.cer')
    
    if ssl_verify and os.path.exists(ssl_cert_file):
        print(f"🔒 Using SSL certificate: {ssl_cert_file}")
        ssl_context = ssl.create_default_context(cafile=ssl_cert_file)
        urllib.request.install_opener(urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl_context)))
        os.environ['REQUESTS_CA_BUNDLE'] = ssl_cert_file
        return ssl_context
    elif not ssl_verify:
        print("⚠️  SSL verification disabled")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        urllib.request.install_opener(urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl_context)))
        os.environ['CURL_CA_BUNDLE'] = ""
        os.environ['REQUESTS_CA_BUNDLE'] = ""
        # For HuggingFace
        os.environ['HF_HUB_DISABLE_SSL_VERIFY'] = "1"
        return ssl_context
    else:
        print("✓ Using system default SSL settings")
        return None

def download_models():
    """Pre-download the ML models."""
    print("\n" + "="*50)
    print("ML Model Downloader")
    print("="*50 + "\n")
    
    # Configure SSL first
    configure_ssl()
    
    try:
        # Import after SSL configuration
        import mlx_whisper
        from mlx_audio.tts.utils import load_model
        
        print("📥 Downloading Whisper models...")
        whisper_models = {
            'small': 'mlx-community/whisper-small-mlx',
            'medium': 'mlx-community/whisper-medium-mlx',
            'base': 'mlx-community/whisper-base-mlx'
        }
        
        for name, repo in whisper_models.items():
            print(f"  • Downloading {name} model from {repo}...")
            try:
                # This will download if not cached
                mlx_whisper.load_models(repo)
                print(f"    ✓ {name} model ready")
            except Exception as e:
                print(f"    ⚠ Failed to download {name}: {e}")
        
        print("\n📥 Downloading TTS model...")
        tts_model_id = 'mlx-community/Kokoro-82M-4bit'
        print(f"  • Downloading Kokoro from {tts_model_id}...")
        try:
            load_model(tts_model_id)
            print("    ✓ Kokoro TTS model ready")
        except Exception as e:
            print(f"    ⚠ Failed to download Kokoro: {e}")
        
        print("\n✅ Model download complete!")
        
    except ImportError as e:
        print(f"❌ Error: Required packages not installed: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check for SSL certificate argument
    if len(sys.argv) > 1:
        os.environ['SSL_CERT_FILE'] = sys.argv[1]
        print(f"Using SSL certificate from argument: {sys.argv[1]}")
    
    download_models()