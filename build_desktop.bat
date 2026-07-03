@echo off
echo Building YourDaddy Assistant Desktop App...
call .venv\Scripts\activate
pyinstaller --name="YourDaddy_Assistant" ^
  --windowed ^
  --add-data="src/project/dist;web_assets" ^
  --add-data="config;config" ^
  --add-data="data;data" ^
  --hidden-import="ai_assistant.multimodal" ^
  --hidden-import="ai_assistant.modules.conversational_ai" ^
  --hidden-import="ai_assistant.multilingual" ^
  --hidden-import="ai_assistant.modules.advanced_chat_system" ^
  --hidden-import="ai_assistant.modules.llm_provider" ^
  --hidden-import="ai_assistant.core.enhanced_integration" ^
  --hidden-import="engineio.async_drivers.threading" ^
  --hidden-import="flask_socketio" ^
  --noconfirm ^
  --clean ^
  src\ai_assistant\apps\modern_desktop_app.py
echo Build complete! The executable is in the 'dist' folder.
