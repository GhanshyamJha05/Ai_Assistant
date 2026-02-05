# ==============================================
# Fixed Chat & Voice Integration - Socket.IO Events
# ==============================================
"""
Unified command handler with proper routing:
1. Local Tools First (AdvancedConversationalAI) - for system commands
2. External AI Fallback (UnifiedChatInterface) - for general queries
"""

from datetime import datetime
from flask_socketio import emit
from flask import request
import time
import threading

# Import required modules
try:
    from ai_assistant.modules.llm_provider import UnifiedChatInterface
    LLM_PROVIDER_AVAILABLE = True
except ImportError:
    LLM_PROVIDER_AVAILABLE = False

try:
    from ai_assistant.modules.conversational_ai import AdvancedConversationalAI
    CONVERSATIONAL_AI_AVAILABLE = True
except ImportError:
    CONVERSATIONAL_AI_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Learning router (set by modern_web_backend.py)
learning_router = None

def set_learning_router(router):
    """Set learning router for this module"""
    global learning_router
    learning_router = router

# SocketIO will be injected
_socketio = None

def set_socketio(sio):
    """Set SocketIO instance and register handlers"""
    global _socketio
    _socketio = sio
    
    # Register all handlers
    sio.on_event('connect', handle_connect)
    sio.on_event('disconnect', handle_disconnect)
    sio.on_event('command', handle_command)
    sio.on_event('voice_command', handle_voice_command)
    
    print("✅ Command handlers registered with socketio")

# ==============================================
# WebSocket Event Handlers (as regular functions)
# ==============================================

def handle_connect():
    """Handle client connection"""
    print(f'✅ Client connected: {request.sid}')
    emit('connection_established', {
        'status': 'connected',
        'sid': request.sid,
        'timestamp': datetime.now().isoformat()
    })

def handle_disconnect():
    """Handle client disconnection"""
    print(f'❌ Client disconnected: {request.sid}')

def handle_command(data):
    """
    Handle command with intelligent routing:
    1. Local Tools First (AdvancedConversationalAI) - for system commands  
    2. External AI Fallback (UnifiedChatInterface) - for general queries
    """
    try:
        command_text = data.get('command') or data.get('message', '')
        source = data.get('source', 'chat')
        
        if not command_text:
            emit('command_response', {
                'success': False,
                'error': 'No command provided',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        print(f'📨 Command received ({source}): {command_text}')
        print(f'🔍 DEBUG: Full Data Payload: {data}')  # Log entire payload to see if provider is sent
        
        # Define safe emit helper to catch Errno 22
        def safe_emit(event, payload):
            try:
                emit(event, payload)
            except OSError as e:
                # Errno 22 often happens with socketio emit on windows if payload is too large or socket closed
                print(f"⚠️ Socket emit error (ignored): {e}")
            except Exception as e:
                print(f"⚠️ General emit error: {e}")
        
        # ============================================
        # PRIORITY 1: Local Command Processing
        # ============================================
        # Try AdvancedConversationalAI first (has built-in intent detection & tool execution)
        response_text = None
        used_local_tools = False
        
        if CONVERSATIONAL_AI_AVAILABLE:
            try:
                # Create instance with automation callback
                def automation_callback(action, param):
                    """Execute automation actions"""
                    try:
                        if action == 'open_application':
                            from ai_assistant.modules.core import open_application
                            return open_application(param)
                        elif action == 'close_application':
                            from ai_assistant.modules.core import close_application
                            return close_application(param)
                        elif action == 'get_running_apps':
                            from ai_assistant.modules.core import get_running_processes
                            return get_running_processes()
                    except Exception as e:
                        return f"Action error: {str(e)}"
                    return None
                
                conv_ai = AdvancedConversationalAI(automation_callback=automation_callback)
                
                # Process through conversational AI (has intent detection built-in)
                response_text = conv_ai.process_message(command_text)
                
                # Check if it actually executed something or just returned generic response
                if response_text and not any(phrase in response_text.lower() for phrase in [
                    "i don't understand", 
                    "i'm not sure",
                    "could you rephrase",
                    "what would you like"
                ]):
                    used_local_tools = True
                    print(f'✅ [LOCAL TOOLS] {response_text[:100]}...')
                    
                    # Emit response
                    safe_emit('command_response', {
                        'success': True,
                        'response': response_text,
                        'command': command_text,
                        'source': 'local_tools',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Log learning
                    if learning_router:
                        learning_router.log_user_query(command_text, source=source)
                        learning_router.log_ai_response(command_text, response_text)
                    
                    return  # Successfully handled
                    
            except ImportError:
                print('⚠️ AdvancedConversationalAI import failed')
            except Exception as e:
                print(f'⚠️ Local processing attempt failed: {e}')
                import traceback
                traceback.print_exc()
        
        # ============================================
        # PRIORITY 2: External AI Fallback (for general queries)
        # ============================================
        if LLM_PROVIDER_AVAILABLE and not used_local_tools:
            try:
                # Extract provider/model preference from request
                preferred_provider = data.get('provider')
                preferred_model = data.get('model')
                
                print(f"🔧 Initializing Chat with Provider: {preferred_provider}, Model: {preferred_model}")

                # Initialize Chat with user preference
                chat = UnifiedChatInterface(
                    provider=preferred_provider,
                    model=preferred_model,
                    use_fallback=True
                )
                
                # Set provider-specific system message
                provider_name = chat.provider_name.lower()
                model_name = chat.model
                
                print(f"ℹ️ Actual Provider: {provider_name}, Actual Model: {model_name}")

                if 'openai' in provider_name or 'gpt' in model_name:
                    system_msg = (
                        "You are an AI assistant powered by OpenAI. "
                        f"You are using the {model_name} model. "
                        "You can answer general knowledge questions, help with information, "
                        "and provide assistance."
                    )
                elif 'gemini' in provider_name or 'gemini' in model_name:
                    system_msg = (
                        "You are YourDaddy Assistant, powered by Google Gemini. "
                        f"You are using the {model_name} model. "
                        "You can answer general knowledge questions, help with information, "
                        "and provide assistance."
                    )
                else:
                    system_msg = (
                        "You are YourDaddy, a helpful AI assistant. "
                        "You can answer general knowledge questions, help with information, "
                        "and provide assistance."
                    )
                
                chat.add_system_message(system_msg)
                
                # Get response from external AI
                response_text = chat.chat(command_text)
                
                print(f'✅ [EXTERNAL AI - {provider_name.upper()}] {response_text[:100]}...')
                
                # Log learning
                if learning_router:
                    learning_router.log_user_query(command_text, source=source)
                    learning_router.log_ai_response(command_text, response_text)
                
                # Emit response (safe_emit will catch any socket errors)
                safe_emit('command_response', {
                    'success': True,
                    'response': response_text,
                    'command': command_text,
                    'source': f'external_ai_{provider_name}',
                    'provider': provider_name,
                    'model': model_name,
                    'timestamp': datetime.now().isoformat()
                })
                
                return  # Successfully handled
                
            except Exception as llm_error:
                print(f'❌ External AI error: {llm_error}')
                # Don't return here, let it fall through to fallback if needed, or emit error silently
                # But typically if AI fails we want to know, just not crash socket
        
        # ============================================
        # FALLBACK: Simple acknowledgment
        # ============================================
        if not response_text:
            response_text = f'I received your command: "{command_text}". Processing...'
            
        safe_emit('command_response', {
            'success': True,
            'response': response_text,
            'command': command_text,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
            
    except OSError as e:
         print(f"⚠️ Critical Socket/OS Error caught in handle_command: {e}")
         # DO NOT EMIT TO USER, just log it. This prevents the "Error: [Errno 22]" chat message
    except Exception as e:
        print(f'❌ Command handling error: {e}')
        import traceback
        print(traceback.format_exc())
        
        # Only emit operational errors, not low-level system errors
        if "[Errno 22]" not in str(e):
            safe_emit('command_response', {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

def handle_voice_command(data):
    """Handle voice command specifically"""
    try:
        transcript = data.get('transcript', '')
        confidence = data.get('confidence', 0.0)
        
        if not transcript:
            emit('voice_response', {
                'success': False,
                'error': 'No transcript provided'
            })
            return
        
        print(f'🎤 Voice command: {transcript} (confidence: {confidence})')
        
        # Forward to command handler
        handle_command({'command': transcript, 'source': 'voice'})
        
    except Exception as e:
        print(f'❌ Voice command error: {e}')
        emit('voice_response', {
            'success': False,
            'error': str(e)
        })

# System stats broadcaster
def broadcast_system_stats():
    """Broadcast system statistics periodically"""
    while True:
        try:
            if PSUTIL_AVAILABLE and _socketio:
                stats = {
                    'cpu_usage': psutil.cpu_percent(interval=1),
                    'memory_usage': psutil.virtual_memory().percent,
                    'network_speed': 0  # Placeholder
                }
                _socketio.emit('system_stats_update', stats)
        except Exception as e:
            print(f'Stats broadcast error: {e}')
        time.sleep(5)  # Update every 5 seconds

# Start stats broadcaster thread
stats_thread = threading.Thread(target=broadcast_system_stats, daemon=True)
stats_thread.start()
