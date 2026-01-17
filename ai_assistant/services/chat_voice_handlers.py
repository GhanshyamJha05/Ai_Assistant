# ==============================================
# Chat & Voice Integration - Socket.IO Events
# ==============================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'✅ Client connected: {request.sid}')
    emit('connection_established', {
        'status': 'connected',
        'sid': request.sid,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'❌ Client disconnected: {request.sid}')

@socketio.on('command')
def handle_command(data):
    """
    Handle command from voice or chat input
    Expected data: {'command': 'user command text', 'source': 'voice'|'chat'}
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
        
        # ----------------------------------------------------
        # NEW: Chain of Actions Integration (Autonomy Engine)
        # ----------------------------------------------------
        # Basic heuristic to detect executable commands vs. chat
        # In a perfect world, we'd use an intent classifier here.
        action_keywords = [
            'open', 'close', 'click', 'minimize', 'maximize', 
            'type', 'write', 'search', 'play', 'pause', 
            'scroll', 'select', 'clear', 'delete', 'create',
            'save', 'check', 'verify', 'scan', 'start', 'stop',
            'go to', 'navigate'
        ]
        
        is_action_request = any(kw in command_text.lower() for kw in action_keywords)
        
        # Exception for simple questions starting with these keywords, but keeping it simple for now
        # If Multi-Agent is available and it looks like an action...
        if is_action_request:
            try:
                from ai_assistant.core.chain_of_actions_manager import get_chain_manager
                manager = get_chain_manager()
                
                # Notify client we are taking action
                emit('command_response', {
                    'success': True,
                    'response': f"🤖 I'm on it. Starting execution for: '{command_text}'...",
                    'command': command_text,
                    'source': source,
                    'is_action': True,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Define progress callback for WebSocket
                def ws_progress_callback(progress_data):
                    emit('chain_progress', progress_data)
                
                # Executing in background thread to not block SocketIO
                import threading
                import asyncio
                
                def run_chain_executor():
                    async def _run():
                        # Execute and pipe progress to WebSocket
                        await manager.execute_command(command_text, on_progress=ws_progress_callback)
                        
                        # Fetch final status (optional, notification handles it mostly)
                        # But we can emit a final 'command_completed' event here if we want
                        emit('log_update', {
                            'type': 'success', 
                            'message': 'Chain execution finished',
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        })

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(_run())
                    loop.close()

                threading.Thread(target=run_chain_executor).start()
                
                return # Stop processing, we handed it off to the Agent

            except ImportError:
                print("⚠️ Chain Manager not available, falling back to legacy chat.")
            except Exception as e:
                print(f"⚠️ Chain dispatch failed: {e}, falling back.")
        
        # ------------------------------------------------_
        # Standard Chat / Fallback Processing
        # -------------------------------------------------
        # Log the command
        if learning_router:
            learning_router.log_user_query(command_text, source=source)
        
        # Process the command through LLM if available
        if LLM_PROVIDER_AVAILABLE:
            try:
                from ai_assistant.llm.llm_provider import process_query_with_llm
                
                # Get LLM response with context
                response_text = process_query_with_llm(
                    query=command_text,
                    context={'source': source, 'timestamp': datetime.now().isoformat()}
                )
                
                # Log the response
                if learning_router:
                    learning_router.log_ai_response(command_text, response_text)
                
                # Emit response back to client
                emit('command_response', {
                    'success': True,
                    'response': response_text,
                    'command': command_text,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Emit system log
                emit('log_update', {
                    'type': 'info',
                    'message': f'Processed {source} command successfully',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                
            except Exception as llm_error:
                print(f'❌ LLM error: {llm_error}')
                # Fallback to simple response
                emit('command_response', {
                    'success': True,
                    'response': f'I received your command: "{command_text}". Processing...',
                    'command': command_text,
                    'source': source,
                    'timestamp': datetime.now().isoformat()
                })
        else:
            # No LLM available, send acknowledgment
            emit('command_response', {
                'success': True,
                'response': f'Command received: "{command_text}"',
                'command': command_text,
                'source': source,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        print(f'❌ Command handling error: {e}')
        emit('command_response', {
 'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('voice_command')
def handle_voice_command(data):
    """
    Handle voice command specifically
    Expected data: {'transcript': 'recognized text', 'confidence': 0.95}
    """
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
            if PSUTIL_AVAILABLE:
                stats = {
                    'cpu_usage': psutil.cpu_percent(interval=1),
                    'memory_usage': psutil.virtual_memory().percent,
                    'network_speed': 0  # Placeholder
                }
                socketio.emit('system_stats_update', stats)
        except Exception as e:
            print(f'Stats broadcast error: {e}')
        time.sleep(5)  # Update every 5 seconds

# Start stats broadcaster thread
stats_thread = threading.Thread(target=broadcast_system_stats, daemon=True)
stats_thread.start()

# ==============================================
# REST API Endpoints for Chat & Voice
# ==============================================

@app.route('/api/command', methods=['POST'])
def api_command():
    """
    REST endpoint for sending commands
    Alternative to Socket.IO for simpler clients
    """
    try:
        data = request.get_json()
        command_text = data.get('command', '')
        
        if not command_text:
            return jsonify({
                'success': False,
                'error': 'No command provided'
            }), 400
        
        print(f'📨 API Command: {command_text}')
        
        # Process with LLM if available
        if LLM_PROVIDER_AVAILABLE:
            try:
                from ai_assistant.llm.llm_provider import process_query_with_llm
                response_text = process_query_with_llm(command_text)
                
                return jsonify({
                    'success': True,
                    'response': response_text,
                    'command': command_text,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as llm_error:
                print(f'LLM error: {llm_error}')
        
        # Fallback response
        return jsonify({
            'success': True,
            'message': f'Command received: {command_text}',
            'command': command_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Command API error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/voice/process', methods=['POST'])
def api_voice_process():
    """Process voice audio and return transcript"""
    try:
        if not VOICE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Voice processing not available'
            }), 503
        
        # Get audio data from request
        data = request.get_json()
        audio_data = data.get('audio')  # Base64 encoded audio
        
        if not audio_data:
            return jsonify({
                'success': False,
                'error': 'No audio data provided'
            }), 400
        
        # TODO: Implement server-side voice recognition
        # For now, client handles voice recognition
        
        return jsonify({
            'success': True,
            'message': 'Voice processing endpoint ready',
            'note': 'Client-side recognition is recommended for real-time performance'
        })
        
    except Exception as e:
        logger.error(f'Voice processing error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
