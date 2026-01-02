"""
Simple Voice Handler - Minimal WebSocket Implementation

Handles voice commands with clear logging and simple response logic.
"""

from flask_socketio import emit
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def register_voice_handlers(socketio, assistant):
    """
    Register minimal voice WebSocket handlers
    
    Events:
    - voice_command: Receive text from speech recognition
    - connect: Client connection tracking
    """
    
    # Test handler to verify SocketIO is working
    @socketio.on('test_ping')
    def handle_test_ping(data):
        logger.info("🔔 TEST PING RECEIVED!")
        emit('test_pong', {'message': 'Backend is alive!'})
    
    @socketio.on('voice_command')
    def handle_voice_command(data):
        """Process voice command from frontend"""
        try:
            text = data.get('text', '').strip()
            confidence = data.get('confidence', 0.0)
            
            if not text:
                logger.warning("⚠️ Empty voice command received")
                return
            
            logger.info(f"🎤 Voice Command Received: '{text}' (confidence: {confidence:.2f})")
            
            # Simple greeting detection
            greeting_words = ['hey', 'hello', 'hi', 'daddy', 'good morning', 'good evening']
            is_greeting = any(word in text.lower() for word in greeting_words)
            
            if is_greeting:
                # Time-based greeting
                hour = datetime.now().hour
                if 5 <= hour < 12:
                    response = "Good morning! Ready to help you today."
                elif 12 <= hour < 17:
                    response = "Hey! Good afternoon. What can I do for you?"
                elif 17 <= hour < 22:
                    response = "Good evening! How can I assist you?"
                else:
                    response = "Hey! Burning the midnight oil? I'm here to help."
                
                logger.info(f"💬 Greeting Response: {response}")
            else:
                # Use assistant for other commands
                try:
                    logger.info(f"🤔 Processing with assistant...")
                    response = assistant.process_query(text)
                    logger.info(f"✅ Assistant responded: {response[:100]}...")
                except Exception as e:
                    logger.error(f"❌ Assistant error: {e}")
                    response = f"I heard you say: {text}. Let me help you with that."
            
            # Send response back to frontend
            emit('voice_response', {
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
            logger.info(f"📤 Response sent to frontend")
            
        except Exception as e:
            logger.error(f"❌ Voice command handler error: {e}", exc_info=True)
            emit('voice_response', {
                'response': "Sorry, I encountered an error processing that.",
                'success': False,
                'error': str(e)
            })
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        logger.info("✅ Voice client connected")
        emit('voice_status', {
            'connected': True,
            'timestamp': datetime.now().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info("👋 Voice client disconnected")
    
    logger.info("=" * 60)
    logger.info("✅ Simple Voice Handlers Registered Successfully")
    logger.info("   Events: test_ping, voice_command, connect, disconnect")
    logger.info("=" * 60)
