# 🤖 YourDaddy AI Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-4.2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/status-production-brightgreen)

**A sophisticated AI-powered personal assistant featuring voice recognition, smart automation, multilingual support, and real-time AI responses powered by Google Gemini and OpenAI.**

[Features](#-key-features) • [Quick Start](#-quick-start-2-minutes) • [Installation](#-installation) • [Configuration](#-configuration) • [Documentation](#-documentation)

**Last Updated:** December 21, 2025

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start-2-minutes)
- [Architecture](#-architecture)
- [Installation](#-detailed-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Integration](#-api-integrations)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🌟 Overview

**YourDaddy AI Assistant** is a comprehensive, voice-activated AI assistant that combines the power of **Google Gemini 2.0**, **OpenAI GPT**, advanced speech recognition, and intelligent automation to create a seamless personal assistant experience. Built with Python and modern web technologies, it offers multilingual support, multimodal capabilities (text, voice, vision), and extensive system integration.

### 🎯 What Makes This Special

- 🧠 **Real-Time AI**: Intelligent responses using Google Gemini 2.0 Pro and OpenAI GPT-3.5/4
- 🎤 **Voice Control**: Google Assistant-quality voice recognition with wake word detection
- 🌍 **Multilingual**: Support for English, Hindi, Hinglish, and multiple Indian languages
- 👁️ **Vision AI**: Image analysis, OCR, and visual understanding
- 🔄 **Smart Automation**: Windows app control, file operations, and task scheduling
- 🎵 **Media Integration**: Spotify and YouTube Music control with voice commands
- 🌐 **Modern Web UI**: React + TypeScript interface with real-time WebSocket updates
- 🔒 **Secure**: PIN-based authentication and encrypted API key management
- 📚 **Learning System**: Adaptive learning with feedback loop and pattern recognition
- 🚫 **Offline Capable**: Core features work without internet using Vosk and local models

---

## ✨ Key Features

### 🤖 AI & Intelligence
- **Conversational AI**: Context-aware conversations with memory persistence
- **Google Gemini 2.0**: Latest multimodal AI models with vision support
- **OpenAI GPT Integration**: GPT-3.5 Turbo and GPT-4 support
- **Advanced Memory System**: Long-term context retention and relationship mapping
- **Adaptive Learning**: Pattern recognition and personalized responses with feedback loop
- **Knowledge Graphs**: Intelligent associations and context understanding
- **Feedback Learning**: User feedback integration for continuous improvement
- **Graph Neural Networks**: Advanced learning with relationship mapping
- **Intent Classification**: Smart command understanding with neural networks
- **Learning Dashboard**: Real-time visualization of learning progress and metrics

### 🎙️ Voice & Speech
- **Wake Word Detection**: "Hey Daddy", "OK Daddy" activation with local processing
- **Advanced Speech Recognition**: 
  - OpenAI Whisper API (online, highest accuracy)
  - Google Cloud Speech-to-Text
  - Vosk offline recognition (English & Hindi)
  - Browser-based Web Speech API
- **Neural Text-to-Speech**:
  - Microsoft Edge-TTS (natural neural voices)
  - Google Cloud TTS
  - Coqui TTS (offline fallback)
  - pyttsx3 (system voices)
- **Multilingual Support**: English, Hindi, Hinglish, Spanish, French, and more
- **Continuous Listening Mode**: Always-on voice detection with smart activation
- **Voice Activity Detection**: Advanced VAD with spectral feature analysis
- **Speaker Verification**: Voice profile management for secure access

### 🖥️ System Integration & Automation
- **Smart App Discovery**: Automatic detection of 500+ installed Windows applications
- **Application Control**: Launch, close, and manage any Windows application
- **File Operations**: Create, move, copy, search, organize files and folders
- **Taskbar Detection**: Real-time window and application monitoring
- **System Control**: Volume, brightness, power management
- **Automation Tools**: Scheduled tasks, batch operations, system optimization

### 📅 Productivity & Communication
- **Google Calendar Integration**: Event creation, reminders, scheduling
- **Email Automation**: Send, read, and manage emails via voice or text
- **Task Scheduling**: APScheduler-based automation with cron-like syntax
- **Document OCR**: Extract text from images and PDFs using Tesseract
- **Web Scraping**: Intelligent data extraction from websites
- **News & Weather**: Real-time news updates and weather forecasts
- **Stock & Crypto Prices**: Financial data monitoring

### 🎵 Media & Entertainment
- **Spotify Integration**: 
  - Play, pause, skip, control playback
  - Create and manage playlists
  - Search songs, artists, albums
  - Get music recommendations
- **YouTube Music**: Search and play music videos
- **Music Downloader**: yt-dlp integration for audio/video downloads
- **Media Player Control**: System-wide media control

### 🌐 Modern Web Interface
- **React + TypeScript Frontend**: Modern, responsive UI built with Vite
- **Real-Time Communication**: WebSocket support for live updates
- **Flask Backend**: RESTful API with Flask-SocketIO
- **Mobile-Friendly**: Responsive design works on all devices
- **Dark/Light Themes**: Customizable appearance
- **Voice Web Commands**: Browser-based voice interaction
- **Live Status Updates**: Real-time system and AI status monitoring
- **Application Grid**: Smart app discovery and control interface
- **Conversation Space**: Modern chat interface with enhanced UX
- **Learning Dashboard**: Interactive visualization of learning metrics and feedback

### 👁️ Multimodal & Vision
- **Image Analysis**: Visual understanding using Gemini Vision API
- **Video Processing**: Frame extraction and multi-frame analysis
- **Screen Capture Analysis**: Screenshot understanding and OCR
- **Object Detection**: Identify objects, faces, and scenes
- **Document Understanding**: Analyze document structure and content
- **Batch Processing**: Process multiple images/documents simultaneously

### 🔒 Security & Privacy
- **PIN-Based Authentication**: Secure access control with configurable PIN
- **Encrypted Credentials**: Secure storage of API keys and tokens
- **Environment Variables**: Secure configuration management
- **Rate Limiting**: API request throttling and protection
- **JWT Tokens**: Secure session management
- **Local Processing**: Offline modes protect privacy

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Install Dependencies
```bash
# Clone the repository
git clone <repository-url>
cd assitant

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Setup API Keys (Free - 1 Minute)
```bash
# Run the quick setup wizard
python quick_ai_setup.py

# Get FREE Gemini API key:
# 1. Visit: https://aistudio.google.com/app/apikey
# 2. Sign in with Google account
# 3. Click "Create API Key"
# 4. Copy and paste when prompted
```

### Step 3: Start the Assistant
```bash
# Start with web interface (recommended)
python main.py

# Start the modern web backend
python start_backend.bat  # Windows
# or
python ai_assistant/services/modern_web_backend.py

# Start React frontend (in new terminal)
cd project
npm install
npm run dev

# Or use specific interface
python main.py --interface web --port 8000
python main.py --interface cli
```

### Step 4: Access & Test
```
🌐 Web Interface: http://localhost:8000
🚀 React Frontend: http://localhost:5173
🎤 Test Voice: "Hey Daddy, what's the weather today?"
💬 Test Chat: "Explain quantum computing"
📊 Learning Dashboard: http://localhost:8000/learning_dashboard.html
```

**Expected**: Intelligent AI responses (not templates!)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Web UI   │  │ Voice UI │  │ CLI      │  │ Desktop  │   │
│  │ (React)  │  │ (Speech) │  │ (Python) │  │ GUI (Tk) │   │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘   │
└────────┼─────────────┼─────────────┼─────────────┼─────────┘
         │             │             │             │
         └─────────────┴─────────────┴─────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │      Flask Backend (Port 8000)      │
         │    WebSocket + REST API Server       │
         └──────────────────┬──────────────────┘
                            │
         ┌──────────────────┴──────────────────┐
         │         Core AI System              │
         │  ┌────────────────────────────┐     │
         │  │   Conversational AI        │     │
         │  │   - Context Management     │     │
         │  │   - Multi-turn Dialog      │     │
         │  │   - Memory System          │     │
         │  └────────────────────────────┘     │
         └──────────────────┬──────────────────┘
                            │
      ┌──────────┬──────────┴───────┬──────────┐
      │          │                  │          │
┌─────▼────┐ ┌──▼─────┐ ┌─────────▼─────┐ ┌──▼─────┐
│ AI/LLM   │ │ Voice  │ │  Automation   │ │ Integr │
│          │ │        │ │               │ │ -ations│
│ •Gemini  │ │ •ASR   │ │ •App Control  │ │ •Google│
│ •OpenAI  │ │ •TTS   │ │ •File Ops     │ │ •Spotify│
│ •Memory  │ │ •Wake  │ │ •System Cmds  │ │ •Email │
│ •Learn   │ │ •VAD   │ │ •Scheduling   │ │ •Web   │
└──────────┘ └────────┘ └───────────────┘ └────────┘
```

---

## 📦 Detailed Installation

### Prerequisites
- **Python**: 3.8 or higher
- **OS**: Windows 10/11 (primary), Linux/Mac (experimental)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for dependencies and models

### Complete Installation Steps

#### 1. Clone Repository
```bash
git clone <repository-url>
cd assitant
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements.txt pytest pytest-cov black flake8
```

#### 4. Install Vosk Models (For Offline Voice)
```bash
# Download English model
python -c "from ai_assistant.voice import download_vosk_model; download_vosk_model('en')"

# Download Hindi model
python -c "from ai_assistant.voice import download_vosk_model; download_vosk_model('hi')"
```

#### 5. Install System Dependencies (Windows)
```bash
# Install Tesseract OCR (for document processing)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# PyAudio (for microphone access)
pip install pipwin
pipwin install pyaudio
```

#### 6. Setup Configuration
```bash
# Run setup wizard
python quick_ai_setup.py

# Or manually create config files
cp config/app_integration.env.example config/app_integration.env
cp config/multimodal_config.json.example config/multimodal_config.json
```

#### 7. Setup API Keys

**Option A: Using Setup Wizard (Recommended)**
```bash
python quick_ai_setup.py
```

**Option B: Manual Setup**
Create `api_keys.json`:
```json
{
    "GEMINI_API_KEY": "your-gemini-api-key",
    "OPENAI_API_KEY": "your-openai-api-key",
    "SPOTIFY_CLIENT_ID": "your-spotify-client-id",
    "SPOTIFY_CLIENT_SECRET": "your-spotify-client-secret"
}
```

#### 8. Verify Installation
```bash
# Check dependencies
python check_dependencies.py

# Test AI integration
python test_ai_quick.py

# Test voice recognition
python test_import_core.py
```

---

## 🔧 Configuration

### API Keys Configuration

#### Required Keys
1. **Gemini API** (Free - Recommended)
   - Get it: https://aistudio.google.com/app/apikey
   - Free tier: 60 requests/minute
   - Required for: AI conversations, vision analysis

2. **OpenAI API** (Optional - Paid)
   - Get it: https://platform.openai.com/api-keys
   - Cost: ~$0.002 per conversation (GPT-3.5)
   - Required for: OpenAI GPT models, Whisper API

#### Optional Keys
3. **Spotify API** (Free)
   - Get it: https://developer.spotify.com/dashboard
   - Required for: Music control features

4. **Google Cloud** (Free tier available)
   - Services: Calendar, Gmail, Speech-to-Text
   - Setup: https://console.cloud.google.com

### Configuration Files

#### 1. `api_keys.json` (Recommended)
```json
{
    "GEMINI_API_KEY": "AIza...",
    "OPENAI_API_KEY": "sk-...",
    "SPOTIFY_CLIENT_ID": "your-client-id",
    "SPOTIFY_CLIENT_SECRET": "your-client-secret",
    "GOOGLE_CLOUD_KEY_PATH": "path/to/credentials.json"
}
```

#### 2. `config/user_settings.json`
```json
{
    "language": "en",
    "voice_enabled": true,
    "wake_word": "hey daddy",
    "tts_engine": "edge-tts",
    "theme": "dark"
}
```

#### 3. `config/multimodal_config.json`
```json
{
    "vision_enabled": true,
    "max_image_size": 4096,
    "ocr_enabled": true,
    "video_processing": false
}
```

#### 4. Environment Variables (Alternative)
```bash
# Windows
set GEMINI_API_KEY=your-key-here
set OPENAI_API_KEY=your-key-here

# Linux/Mac
export GEMINI_API_KEY=your-key-here
export OPENAI_API_KEY=your-key-here
```

### Security Settings

#### Setup PIN Authentication
```bash
# First time setup
python setup_pin.py

# Or during startup
python main.py --setup-pin

# Skip for development (not recommended)
python main.py --skip-auth
```

---

## 🎮 Usage

### Starting the Assistant

#### Web Interface (Recommended)
```bash
# Default (port 8000)
python main.py

# Custom port
python main.py --port 5000

# With verbose logging
python main.py --verbose

# Access at: http://localhost:8000
```

#### Command Line Interface
```bash
python main.py --interface cli
```

#### Desktop GUI
```bash
python main.py --interface desktop
```

### Using Voice Commands

#### Wake Word Activation
```
Say: "Hey Daddy" or "OK Daddy"
Wait for: Activation sound/beep
Then say: Your command
```

#### Example Voice Commands
```
"Hey Daddy, what's the weather today?"
"Open Chrome and search for Python tutorials"
"Play some relaxing music on Spotify"
"Create a meeting for tomorrow at 3 PM"
"Send an email to john@example.com"
"What's in this image?" (with image upload)
"Translate 'Hello' to Hindi"
"Set a reminder for 5 PM"
```

### Using Text Commands

#### Web Interface
1. Open http://localhost:8000
2. Type your query in the chat box
3. Press Enter or click Send

#### CLI Interface
```bash
$ python main.py --interface cli
> What's the capital of France?
> Open notepad
> Play music by Coldplay
> quit  # To exit
```

### Advanced Usage

#### Automation Scripts
```bash
# Schedule automated tasks
python scripts/setup/setup_automation.py

# Run batch file operations
python -c "from ai_assistant.file_ops import organize_files_by_type; organize_files_by_type('~/Downloads')"
```

#### API Endpoints

**Health Check**
```bash
curl http://localhost:8000/api/health
```

**Send Message**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "user_id": "user123"}'
```

**Get Features**
```bash
curl http://localhost:8000/api/features
```

**Voice Recognition**
```bash
curl -X POST http://localhost:8000/api/voice/recognize \
  -F "audio=@recording.wav"
```

---

## 📁 Project Structure

```
assitant/
├── main.py                          # Main entry point with interface selection
├── pyproject.toml                   # Project metadata and configuration
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Testing configuration
├── api_keys.json                    # API keys (gitignored)
├── start_backend.bat                # Quick start backend (Windows)
├── check_systems_status.py          # System status checker
├── view_feedback.py                 # View learning feedback
│
├── ai_assistant/                    # Main package
│   ├── __init__.py                  # Package initialization
│   │
│   ├── ai/                          # AI & Machine Learning
│   │   ├── conversational_ai.py     # Main conversation engine
│   │   ├── llm_provider.py          # LLM abstraction layer
│   │   ├── memory.py                # Context and memory management
│   │   ├── advanced_feedback_learning.py  # Adaptive learning system
│   │   ├── graph_neural_networks.py # GNN-based learning
│   │   ├── intent_classification.py # Intent understanding
│   │   └── knowledge_graph.py       # Relationship mapping
│   │
│   ├── voice/                       # Voice Processing
│   │   ├── advanced_speech_recognizer.py  # ASR (Whisper, Google, Vosk)
│   │   ├── neural_voice_engine.py   # TTS (Edge-TTS, Google, Coqui)
│   │   ├── wake_word_detector.py    # Wake word detection
│   │   ├── voice_activity_detection.py   # VAD with spectral analysis
│   │   ├── speaker_verification.py  # Voice profile management
│   │   └── advanced_voice.py        # Unified voice interface
│   │
│   ├── integrations/                # External Services
│   │   ├── google_calendar.py       # Calendar integration
│   │   ├── email_handler.py         # Email automation
│   │   ├── spotify_integration.py   # Spotify control
│   │   ├── youtube_music.py         # YouTube Music
│   │   ├── web_search_integration.py # Web search
│   │   ├── learning_integration.py  # Learning system integration
│   │   ├── learning_automation.py   # Learning automation
│   │   └── google_assistant_voice_integration.py  # Voice integration
│   │
│   ├── automation/                  # System Automation
│   │   ├── smart_automation.py      # Intelligent automation
│   │   ├── app_discovery.py         # Application detection (500+ apps)
│   │   ├── windows_control.py       # Windows automation
│   │   └── task_scheduler.py        # Task scheduling
│   │
│   ├── services/                    # Backend Services
│   │   ├── modern_web_backend.py    # Modern Flask backend server
│   │   └── learning_integration.py  # Learning service integration
│   │
│   ├── interfaces/                  # User Interfaces
│   │   ├── modern_interfaces.py     # Interface management
│   │   ├── websocket_handlers.py    # WebSocket communication
│   │   └── rest_api.py              # REST API endpoints
│   │
│   ├── apps/                        # Application Entry Points
│   │   ├── modern_web_backend.py    # Flask web server
│   │   ├── app.py                   # CLI application
│   │   └── yourdaddy_app.py         # Desktop GUI
│   │
│   ├── modules/                     # Utility Modules
│   │   ├── conversational_ai.py     # Enhanced conversation
│   │   ├── multilingual.py          # Language support
│   │   ├── multimodal.py            # Multimodal processing
│   │   ├── youtube_ops.py           # YouTube operations
│   │   ├── app_discovery.py         # App discovery module
│   │   └── modern_interfaces.py     # Interface utilities
│   │
│   ├── core/                        # Core Functionality
│   │   ├── core.py                  # Core system
│   │   ├── system.py                # System utilities
│   │   └── config.py                # Configuration management
│   │
│   ├── auth/                        # Authentication
│   │   ├── pin_auth.py              # PIN authentication
│   │   └── security.py              # Security utilities
│   │
│   ├── database/                    # Data Persistence
│   │   ├── conversation_db.py       # Conversation storage
│   │   ├── feedback_db.py           # Feedback data
│   │   └── memory_db.py             # Memory management
│   │
│   ├── utils/                       # Utilities
│   │   ├── logging_config.py        # Logging setup
│   │   ├── file_utils.py            # File operations
│   │   └── validators.py            # Input validation
│   │
│   └── services/                    # Background Services
│       ├── scheduler_service.py     # Task scheduling
│       └── monitoring_service.py    # System monitoring
│
├── config/                          # Configuration Files
│   ├── app_integration.env          # App configuration
│   ├── multimodal_config.json       # Multimodal settings
│   ├── user_settings.json           # User preferences
│   └── discovered_apps.json         # Discovered applications
│
├── scripts/                         # Utility Scripts
│   ├── setup/                       # Setup scripts
│   │   ├── setup_google_assistant_voice.py
│   │   ├── setup_automation.py
│   │   └── install_dependencies.py
│   ├── analysis/                    # Analysis tools
│   └── debug/                       # Debugging utilities
│
├── tests/                           # Test Suite
│   ├── test_ai_quick.py             # Quick AI tests
│   ├── test_advanced_learning.py    # Learning system tests
│   ├── test_all_27_systems.py       # Integration tests
│   ├── test_voice_recognition.py    # Voice tests
│   └── test_api_endpoints.py        # API tests
│
├── project/                         # Frontend Project
│   ├── src/                         # React TypeScript source
│   │   ├── components/              # React components
│   │   │   ├── ApplicationGrid.tsx  # App grid interface
│   │   │   ├── VoiceInterface.tsx   # Voice control UI
│   │   │   └── ConversationSpace.tsx # Chat interface
│   │   ├── App.tsx                  # Main app component
│   │   └── main.tsx                 # Entry point
│   ├── public/                      # Static assets
│   ├── package.json                 # npm dependencies
│   ├── vite.config.ts               # Vite configuration
│   └── tsconfig.json                # TypeScript config
│
├── static/                          # Static Web Files
│   ├── learning_dashboard.html      # Learning metrics dashboard
│   └── assets/                      # Images, CSS, JS
│
├── templates/                       # HTML Templates
│   ├── enhanced_chat.html           # Enhanced chat interface
│   └── index.html                   # Main web interface
│
├── docs/                            # Documentation
│   ├── API_REFERENCE_COMPLETE.md    # Complete API reference
│   ├── ADVANCED_LEARNING_SYSTEMS.md # Learning system docs
│   ├── APP_INTEGRATION_SECURITY.md  # Security documentation
│   ├── DATABASE_SCHEMAS.md          # Database schemas
│   └── TROUBLESHOOTING.md           # Troubleshooting guide
│
├── data/                            # Data Storage
│   ├── conversations/               # Conversation history
│   ├── feedback/                    # User feedback data
│   └── models/                      # Offline models
│
└── logs/                            # Application Logs
    ├── app.log                      # Main application log
    ├── voice.log                    # Voice system log
    └── error.log                    # Error log
├── docs/                            # Documentation
│   ├── README.md                    # Comprehensive docs
│   ├── API_REFERENCE_COMPLETE.md    # API documentation
│   ├── CHANGELOG.md                 # Version history
│   └── INTEGRATION_GUIDE.md         # Integration guide
│
├── data/                            # Runtime Data
├── logs/                            # Application Logs
├── static/                          # Static Web Assets
├── templates/                       # HTML Templates
├── user_data/                       # User-Specific Data
├── offline_cache/                   # Offline Model Cache
└── model/                           # ML Models

```

---

## 🔌 API Integrations

### 1. Google Gemini AI
- **Purpose**: Primary AI conversational engine
- **Features**: Text generation, vision analysis, multimodal understanding
- **Setup**: Get free API key from https://aistudio.google.com/app/apikey
- **Usage**: 60 requests/minute free tier

### 2. OpenAI
- **Purpose**: Alternative LLM, Whisper speech recognition
- **Models**: GPT-3.5-Turbo, GPT-4, Whisper API
- **Setup**: https://platform.openai.com/api-keys
- **Cost**: Pay-per-use (~$0.002/conversation)

### 3. Spotify
- **Purpose**: Music playback and playlist management
- **Setup**: https://developer.spotify.com/dashboard
- **Scopes**: streaming, playlist-modify, user-library-read

### 4. Google Cloud Services
- **Speech-to-Text**: High-accuracy voice recognition
- **Text-to-Speech**: Natural voice synthesis
- **Calendar API**: Event management
- **Gmail API**: Email automation
- **Setup**: https://console.cloud.google.com

### 5. Vosk (Offline)
- **Purpose**: Offline speech recognition
- **Languages**: English, Hindi, 20+ others
- **Setup**: Automatic model download
- **No API Key Required**

---

## 🧪 Testing

### Run All Tests
```bash
# Run all tests
pytest

# With coverage report
pytest --cov=ai_assistant --cov-report=html

# Specific test file
pytest tests/test_ai_quick.py

# Verbose output
pytest -v
```

### Test Specific Components

#### AI Integration
```bash
python test_ai_quick.py
python test_real_ai.py
```

#### Voice Recognition
```bash
python test_import_core.py
python ai_assistant/voice/test_voice_recognition.py
```

#### All 27 Systems
```bash
python test_all_27_systems.py
```

#### Web Backend
```bash
python test_api_endpoints.py
```

### Manual Testing

#### Test AI Response
```python
from ai_assistant.ai import get_ai_response

response = get_ai_response("What is quantum computing?")
print(response)
```

#### Test Voice Recognition
```python
from ai_assistant.voice import recognize_speech

text, confidence = recognize_speech()
print(f"You said: {text} (confidence: {confidence})")
```

#### Test Automation
```python
from ai_assistant.automation import open_application

open_application("Chrome")
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

#### 2. API Key Not Working
```bash
# Check AI status
python check_ai_status.py

# Verify keys are loaded
python -c "from ai_assistant.ai import check_api_keys; check_api_keys()"
```

#### 3. Voice Recognition Not Working
```bash
# Check microphone permissions (Windows)
# Settings > Privacy > Microphone > Allow apps

# Test PyAudio installation
python -c "import pyaudio; print('PyAudio OK')"

# Download Vosk models
python -c "from ai_assistant.voice import download_vosk_model; download_vosk_model('en')"
```

#### 4. Web Interface Not Loading
```bash
# Check port availability
netstat -ano | findstr :8000

# Try different port
python main.py --port 5000

# Check firewall settings
```

#### 5. Tesseract OCR Not Found
```bash
# Windows: Download and install from
# https://github.com/UB-Mannheim/tesseract/wiki

# Add to PATH or set environment variable
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Debug Mode
```bash
# Enable verbose logging
python main.py --verbose

# Check logs
cat logs/assistant.log

# Debug specific module
python debug_launcher.py
```

### Getting Help
1. Check [docs/](docs/) directory for detailed documentation
2. Review [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Check [logs/](logs/) for error messages
4. Run diagnostic tools: `python check_dependencies.py`

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Fork and clone repository
git clone https://github.com/yourusername/assitant.git

# Create feature branch
git checkout -b feature/amazing-feature

# Install development dependencies
pip install -r requirements.txt pytest black flake8

# Make changes and test
pytest
black ai_assistant/
flake8 ai_assistant/

# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE.txt](docs/LICENSE.txt) for details.

---

## 🙏 Acknowledgments

- **Google Gemini**: Advanced AI capabilities
- **OpenAI**: GPT and Whisper models
- **Vosk**: Offline speech recognition
- **Edge-TTS**: Neural text-to-speech
- **Flask & React**: Web framework and UI
- **All Contributors**: Thank you for your contributions!

---

## 📞 Support

- **Documentation**: [docs/README.md](docs/README.md)
- **API Reference**: [docs/API_REFERENCE_COMPLETE.md](docs/API_REFERENCE_COMPLETE.md)
- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Integration Guide**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

---

<div align="center">

**Made with ❤️ by the YourDaddy AI Team**

⭐ Star us on GitHub if you find this helpful!

</div>