# Voice endpoints added by AI assistant
# Location: f:\bn\assitant\ai_assistant\services\voice_api.py

from flask import Blueprint, jsonify, request
import logging
import os

voice_bp = Blueprint('voice', __name__)

# Available Voice Options for TTS
AVAILABLE_VOICES = [
    {"id": "en-US-AriaNeural", "name": "Aria", "gender": "female", "accent": "US", "language": "en-US", "description": "Warm and friendly", "personality": "Friendly and conversational"},
    {"id": "en-US-JennyNeural", "name": "Jenny", "gender": "female", "accent": "US", "language": "en-US", "description": "Professional and clear", "personality": "Professional and articulate"},
    {"id": "en-US-GuyNeural", "name": "Guy", "gender": "male", "accent": "US", "language": "en-US", "description": "Confident and professional", "personality": "Confident and authoritative"},
    {"id": "en-US-DavisNeural", "name": "Davis", "gender": "male", "accent": "US", "language": "en-US", "description": "Warm and conversational", "personality": "Warm and approachable"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia", "gender": "female", "accent": "UK", "language": "en-GB", "description": "British elegance", "personality": "Elegant and refined"},
    {"id": "en-GB-RyanNeural", "name": "Ryan", "gender": "male", "accent": "UK", "language": "en-GB", "description": "British sophistication", "personality": "Sophisticated and clear"},
    {"id": "en-IN-NeerjaNeural", "name": "Neerja", "gender": "female", "accent": "Indian", "language": "en-IN", "description": "Indian warmth", "personality": "Warm and expressive"},
    {"id": "en-IN-PrabhatNeural", "name": "Prabhat", "gender": "male", "accent": "Indian", "language": "en-IN", "description": "Indian clarity", "personality": "Clear and professional"},
    {"id": "en-US-AnaNeural", "name": "Ana", "gender": "female", "accent": "US", "language": "en-US", "description": "Energetic and cheerful", "personality": "Cheerful and enthusiastic"},
    {"id": "en-US-ChristopherNeural", "name": "Christopher", "gender": "male", "accent": "US", "language": "en-US", "description": "Deep and reassuring", "personality": "Calm and reassuring"},
    {"id": "en-GB-LibbyNeural", "name": "Libby", "gender": "female", "accent": "UK", "language": "en-GB", "description": "Young and friendly British", "personality": "Youthful and energetic"},
    {"id": "en-US-EricNeural", "name": "Eric", "gender": "male", "accent": "US", "language": "en-US", "description": "Natural and friendly", "personality": "Casual and friendly"}
]

@voice_bp.route('/list', methods=['GET'])
def api_list_voices():
    """Get list of available AI voices"""
    try:
        return jsonify({
            "success": True,
            "voices": AVAILABLE_VOICES,
            "default": "en-US-AriaNeural"
        })
    except Exception as e:
        logging.error(f"Error fetching voice list: {str(e)}")
        return jsonify({"error": "Failed to fetch voices"}), 500

@voice_bp.route('/preview', methods=['POST'])
def api_preview_voice():
    """Generate preview audio for a voice"""
    try:
        data = request.get_json()
        voice_id = data.get('voice_id', 'en-US-AriaNeural')
        sample_text = data.get('text', "Hello! This is a sample of my voice. I'm here to assist you with anything you need.")
        
        voice_info = next((v for v in AVAILABLE_VOICES if v['id'] == voice_id), None)
        if not voice_info:
            return jsonify({"error": "Voice not found"}), 404
        
        try:
            import edge_tts
            import tempfile
            import asyncio
            import base64
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
            
            async def generate():
                communicate = edge_tts.Communicate(sample_text, voice_id)
                await communicate.save(output_path)
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(generate())
            
            with open(output_path, 'rb') as f:
                audio_data = f.read()
            
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            os.unlink(output_path)
            
            return jsonify({
                "success": True,
                "voice_id": voice_id,
                "voice_name": voice_info['name'],
                "audio_data": f"data:audio/mp3;base64,{audio_base64}"
            })
            
        except Exception as e:
            logging.error(f"Edge-TTS preview failed: {str(e)}")
            return jsonify({"error": f"Preview generation failed: {str(e)}"}), 500
            
    except Exception as e:
        logging.error(f"Voice preview error: {str(e)}")
        return jsonify({"error": "Failed to generate preview"}), 500
