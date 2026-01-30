"""
WebSocket Voice Command Handlers

Handles real-time voice communication between frontend and backend.
"""

from flask_socketio import emit
import logging
import base64
import io

# Import intelligent responder
try:
    from ai_assistant.ai.intelligent_responder import generate_intelligent_response
    INTELLIGENT_RESPONDER_AVAILABLE = True
except ImportError:
    INTELLIGENT_RESPONDER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Store active voice sessions
voice_sessions = {}

def register_voice_handlers(socketio, assistant):
    """Register all voice-related Socket handlers"""
    
    @socketio.on('voice_audio_data')
    def handle_voice_audio(data):
        """Process audio data from frontend"""
        try:
            audio_data = data.get('audio_data')
            if not audio_data:
                emit('voice_error', {'error': 'No audio data provided'})
                return
            
            logger.info(f"Received audio data from client")
            
            # Decode base64 audio
            try:
                audio_bytes = base64.b64decode(audio_data)
                logger.info(f"Decoded audio: {len(audio_bytes)} bytes")
            except Exception as e:
                logger.error(f"Failed to decode audio: {e}")
                emit('voice_error', {'error': 'Invalid audio data'})
                return
            
            # TODO: Process audio with speech recognition
            # For now, send acknowledgment
            emit('voice_transcript', {
                'text': '[Audio received - processing not implemented]',
                'confidence': 0.0
            })
            
        except Exception as e:
            logger.error(f"Voice audio processing error: {e}")
            emit('voice_error', {'error': str(e)})
    
    @socketio.on('voice_command')
    def handle_voice_command(data):
        """Process voice command text"""
        try:
            text = data.get('text', '').strip()
            confidence = data.get('confidence', 0.8)
            
            if not text:
                emit('voice_error', {'error': 'No text provided'})
                return
            
            logger.info(f"Processing voice command: '{text}' (confidence: {confidence})")
            
            # Set processing state
            emit('voice_status', {'state': 'processing'})
            
            # First, generate intelligent response based on intent/mood
            if INTELLIGENT_RESPONDER_AVAILABLE:
                try:
                    intelligent_result = generate_intelligent_response(text)
                    analysis = intelligent_result['analysis']
                    logger.info(f"Intent: {analysis['intent']}, Mood: {analysis['mood']}, Urgency: {analysis['urgency_level']}")
                    
                    # If it's a greeting or appreciation, just return the intelligent response
                    if analysis['intent'] in ['greeting', 'appreciation']:
                        emit('voice_response', {
                            'response': intelligent_result['response'],
                            'success': True,
                            'intent': analysis['intent']
                        })
                        return
                except Exception as e:
                    logger.warning(f"Intelligent responder failed: {e}")
            
            # Process with assistant for commands/questions
            try:
                response = assistant.process_query(text)
                logger.info(f"Assistant response: {response[:100]}...")
                
                # Send response back
                emit('voice_response', {
                    'response': response,
                    'success': True
                })
                
            except Exception as e:
                logger.error(f"Assistant processing error: {e}")
                emit('voice_response', {
                    'response': f"Sorry, I encountered an error: {str(e)}",
                    'success': False
                })
            
        except Exception as e:
            logger.error(f"Voice command error: {e}")
            emit('voice_error', {'error': str(e)})
    
    @socketio.on('voice_start')
    def handle_voice_start():
        """Handle voice listening start"""
        logger.info("Voice listening started")
        emit('voice_status', {'listening': True, 'state': 'listening'})
    
    @socketio.on('voice_stop')
    def handle_voice_stop():
        """Handle voice listening stop"""
        logger.info("Voice listening stopped")
        emit('voice_status', {'listening': False, 'state': 'idle'})
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info(f"Client connected to voice interface")
        emit('voice_status', {
            'connected': True,
            'listening': False,
            'state': 'idle'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info("Client disconnected from voice interface")
    
    logger.info("✅ Voice WebSocket handlers registered")
