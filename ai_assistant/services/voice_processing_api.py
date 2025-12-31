"""
Voice Processing Endpoints for Modern Web Backend

Provides VAD and Noise Reduction preprocessing endpoints.
"""

from flask import Blueprint, jsonify, request
import logging
import numpy as np

# Will be imported from main backend
vad_detector = None
noise_reducer = None

def init_voice_processing(vad_instance, noise_instance):
    """Initialize module with instances from main backend"""
    global vad_detector, noise_reducer
    vad_detector = vad_instance
    noise_reducer = noise_instance

voice_processing_bp = Blueprint('voice_processing', __name__)

@voice_processing_bp.route('/vad/detect', methods=['POST'])
def api_voice_activity_detection():
    """Detect voice activity in audio data"""
    if not vad_detector:
        return jsonify({
            "success": False,
            "error": "Voice Activity Detection not available"
        }), 503
    
    try:
        # Get audio data from request
        if 'audio' not in request.files:
            return jsonify({
                "success": False,
                "error": "No audio file provided"
            }), 400
        
        audio_file = request.files['audio']
        audio_data = np.frombuffer(audio_file.read(), dtype=np.int16)
        
        # Detect voice activity
        result = vad_detector.detect_voice_activity(audio_data)
        
        return jsonify({
            "success": True,
            "is_speech": result.is_speech,
            "confidence": result.confidence,
            "energy_level": result.energy_level
        }), 200
        
    except Exception as e:
        logging.error(f"VAD detection error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Voice activity detection failed"
        }), 500

@voice_processing_bp.route('/denoise', methods=['POST'])
def api_noise_reduction():
    """Apply noise reduction to audio data"""
    if not noise_reducer:
        return jsonify({
            "success": False,
            "error": "Noise Reduction not available"
        }), 503
    
    try:
        # Get audio data from request
        if 'audio' not in request.files:
            return jsonify({
                "success": False,
                "error": "No audio file provided"
            }), 400
        
        audio_file = request.files['audio']
        audio_data = np.frombuffer(audio_file.read(), dtype=np.int16)
        
        # Apply noise reduction
        clean_audio = noise_reducer.process(audio_data)
        
        # Convert back to bytes
        clean_bytes = clean_audio.astype(np.int16).tobytes()
        
        return jsonify({
            "success": True,
            "audio_data": clean_bytes.hex(),  # Return as hex string
            "original_length": len(audio_data),
            "processed_length": len(clean_audio)
        }), 200
        
    except Exception as e:
        logging.error(f"Noise reduction error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Noise reduction failed"
        }), 500

@voice_processing_bp.route('/status', methods=['GET'])
def api_processing_status():
    """Get status of voice processing systems"""
    return jsonify({
        "success": True,
        "vad_available": vad_detector is not None,
        "noise_reduction_available": noise_reducer is not None
    }), 200
