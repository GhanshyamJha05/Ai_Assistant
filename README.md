# YourDaddy AI Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-4.3.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20TypeScript-61dafb)
![Backend](https://img.shields.io/badge/backend-Flask%20%2B%20Socket.IO-black)

## Command the chaos. Speak. Done. Next.

Windows-first AI assistant with chat, voice, automation, learning, memory, and a React dashboard.

**Last Updated:** July 8, 2026

[Quick Start](#quick-start) •
[Running Modes](#running-modes) •
[Feature Tour](#feature-tour) •
[Developer Guide](#developer-guide) •
[Project Layout](#project-layout)

</div>

---

## Overview

YourDaddy AI Assistant is built as a practical desktop AI companion rather than a single chatbot screen. It combines:

- real-time LLM responses with Gemini and OpenAI
- voice input and neural voice output
- Windows app and file automation
- learning, memory, and personalization layers
- a Flask + Socket.IO backend
- a React + TypeScript frontend for a more visual workflow

The project also includes newer platform pieces that make it feel more like an assistant platform than a single app:

- an agent layer for specialized behaviors
- intent extraction and workflow dispatch
- onboarding for personalization
- proactive suggestions based on usage/context
- dashboard APIs for learning and memory views

---

## Choose Your Path

### If you are a user

Start here if you want to run the assistant quickly:

1. install dependencies
2. configure local API keys from examples
3. run the backend
4. launch the React UI
5. interact through chat, voice, automation, or dashboard views

### If you are a developer

Start here if you want to understand or extend the system:

1. review the runtime layers in [README.md](file:///d:/Projects/Ai_Assistant/README.md#L69-L105)
2. inspect the backend entry in [main.py](file:///d:/Projects/Ai_Assistant/main.py)
3. inspect the core backend in [modern_web_backend.py](file:///d:/Projects/Ai_Assistant/src/ai_assistant/services/modern_web_backend.py)
4. inspect the agent and workflow routing pieces in [dispatcher.py](file:///d:/Projects/Ai_Assistant/src/ai_assistant/agents/dispatcher.py) and [intent_registry.py](file:///d:/Projects/Ai_Assistant/src/ai_assistant/workflow/intent_registry.py)
5. inspect the frontend app in [App.tsx](file:///d:/Projects/Ai_Assistant/src/project/src/App.tsx)

---

## Feature Tour

### Conversational AI

- Context-aware chat flows
- Memory-aware responses
- Multiple model providers
- Personalization hooks for future adaptation

### Voice Experience

- Wake-word and speech-recognition support
- Online and offline voice paths
- Neural text-to-speech output
- Multilingual-oriented voice usage

### Automation and Control

- Launch and manage Windows apps
- File and utility automation
- Scheduled workflows
- Browser and integration-oriented actions

### Learning and Memory

- Knowledge-graph style memory APIs
- Feedback submission endpoints
- Usage-pattern analysis

### Standalone Windows App & Onboarding
- **Zero-Dependency Executable**: Packaged into a single native `.exe` using PyInstaller and `pywebview`.
- **First-Run Experience**: A guided EULA and privacy agreement modal ensuring users consent to local data storage.
- **Interactive Tour**: Uses `driver.js` to spotlight key UI elements (chat, voice control) on the user's first launch.
- Learning dashboard data surfaces

### Platform Additions

- Agent dispatcher for natural-language workflow routing
- Autonomous learning agent scaffold
- First-run onboarding manager
- Proactive anticipator for contextual suggestions

---

## Why The UI Matters

This project is no longer just a script-first assistant. The UI layer gives users:

- a cleaner dashboard-driven experience
- clearer status and system visibility
- a more discoverable command surface
- better separation between chat, memory, apps, and settings
- a mobile/PWA-friendly frontend path

For developers, the UI also helps by:

- making state and assistant behavior easier to inspect
- exposing a more testable frontend/backend contract
- making future observability and analytics integration easier

---

## Architecture At A Glance

The system is organized around four practical runtime layers:

1. `main.py`
   Launches the assistant in web, CLI, desktop, or modern desktop mode.

2. `src/ai_assistant/`
   Core assistant package containing AI logic, agents, automation, auth, services, NLP, workflow, vision, and voice modules.

3. `src/project/`
   React + TypeScript frontend used as the main modern UI.

4. `scripts/`
   Setup, validation, diagnostics, and launch helpers.

### Important Runtime Pieces

- [main.py](file:///d:/Projects/Ai_Assistant/main.py)
  Main entry point and mode selector.

- [modern_web_backend.py](file:///d:/Projects/Ai_Assistant/src/ai_assistant/services/modern_web_backend.py)
  Primary Flask + Socket.IO backend.

- [learning_dashboard_api.py](file:///d:/Projects/Ai_Assistant/src/ai_assistant/services/learning_dashboard_api.py)
  Memory graph and feedback endpoints.

- [dispatcher.py](file:///d:/Projects/Ai_Assistant/src/ai_assistant/agents/dispatcher.py)
  Connects natural-language intent extraction to workflow execution and scheduling.

- [onboarding.py](file:///d:/Projects/Ai_Assistant/src/ai_assistant/core/onboarding.py)
  Captures first-run user preferences.

- [proactive_anticipator.py](file:///d:/Projects/Ai_Assistant/src/ai_assistant/core/proactive_anticipator.py)
  Generates contextual prompts from time and usage patterns.

---

## Quick Start

### 1. Clone and create a virtual environment

```bash
git clone <repository-url>
cd Ai_Assistant
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install backend dependencies

```bash
pip install -r config/requirements/requirements.txt
```

Optional dev tooling:

```bash
pip install pytest pytest-cov black flake8
```

### 3. Install frontend dependencies

```bash
cd src/project
npm install
cd ../..
```

### 4. Create your local config

Use the example files in `config/` as templates:

- `config/.env.example`
- `config/api_keys.json.example`
- `config/app_integration.env.example`
- `config/user_settings.json.example`
- `config/multimodal_config.json.example`

Guided setup:

```bash
python scripts/utilities/quick_ai_setup.py
```

### 5. Start the assistant backend

```bash
python main.py --interface web --port 8000
```

### 6. Start the React UI

In a second terminal:

```bash
cd src/project
npm run dev
```

### 7. Open the app

- Backend/UI entry: `http://localhost:8000`
- React frontend: `http://localhost:5173`

---

## Running Modes

| Mode | Command | Purpose |
|---|---|---|
| Web | `python main.py --interface web --port 8000` | Primary backend mode |
| CLI | `python main.py --interface cli` | Lightweight terminal interaction |
| Desktop | `python main.py --interface desktop` | Legacy desktop path |
| Modern Desktop | `python main.py --interface desktop_modern` | Modern desktop/webview path |
| PIN Setup | `python main.py --setup-pin` | First-time or updated auth setup |

Alternative PIN setup script:

```bash
python scripts/setup/setup_pin.py
```

---

## Interactive Workflows

### Onboarding and Personalization

The onboarding flow captures lightweight preferences like:

- profession or daily role
- preferred answer length
- preferred tone

This lets the assistant shape responses earlier instead of waiting for long-term history.

### Intent-to-Workflow Dispatch

The newer dispatch layer supports:

- rule-based intent extraction
- entity extraction
- workflow lookup
- scheduled or immediate execution

Example intents represented in code today:

- research and summarize
- scrape and summarize
- create file
- notify
- summarize text

### Proactive Assistance

The proactive anticipator can surface context-aware prompts such as:

- morning briefing suggestions
- home/evening prompts
- late-night reminders

This gives the assistant a more interactive, assistant-like feel rather than waiting for every command.

### Learning Dashboard APIs

The dashboard API currently supports:

- reading memory graph nodes and edges
- submitting response feedback
- deleting memory nodes

This is useful both for future UI work and for developer inspection workflows.

---

## UI Direction

The React frontend in `src/project/` is the best place to improve the product experience further.

### Current UI strengths

- clear separation of dashboard areas
- component-based frontend structure
- live communication through Socket.IO
- mobile-friendly/PWA direction

### Good next UI improvements

- stronger visual hierarchy and spacing
- richer command composer with suggestions
- clearer task/progress feedback
- more guided onboarding screens
- memory graph and learning views with better visualization
- unified notifications/toasts/activity feed

---

## Developer Guide

### Backend checks

```bash
python scripts/validation/check_dependencies.py
python scripts/validation/check_ai_status.py
```

### Frontend checks

```bash
cd src/project
npm run lint
npm run typecheck
```

### Python tests

```bash
pytest
pytest -v
pytest --cov=src/ai_assistant --cov-report=html
```

### Key extension points

- `src/ai_assistant/agents/`
  Add specialized assistant behaviors and orchestration logic.

- `src/ai_assistant/automation/`
  Extend Windows, browser, and workflow actions.

- `src/ai_assistant/core/`
  Add cross-cutting assistant services such as onboarding, context, auth, and proactive behavior.

- `src/ai_assistant/services/`
  Extend APIs, websockets, and web-backend routes.

- `src/project/src/`
  Improve UI, UX, state handling, and feature discoverability.

### Useful mental model

For most product changes, think in this order:

1. What user experience should happen?
2. Which backend service owns it?
3. Which assistant/core module powers it?
4. Which frontend component exposes it?

---

## Project Layout

```text
Ai_Assistant/
├── main.py
├── config/
│   ├── requirements/
│   ├── *.example
│   └── app_settings.json
├── scripts/
│   ├── setup/
│   ├── utilities/
│   ├── validation/
│   ├── diagnostics/
│   └── launchers/
├── src/
│   ├── ai_assistant/
│   │   ├── agents/
│   │   ├── ai/
│   │   ├── automation/
│   │   ├── auth/
│   │   ├── core/
│   │   ├── integrations/
│   │   ├── nlp/
│   │   ├── services/
│   │   ├── vision/
│   │   ├── voice/
│   │   └── workflow/
│   └── project/
│       ├── src/
│       ├── public/
│       └── package.json
└── docs/
```

---

## Configuration Notes

Keep secrets local and out of Git. Use example files as templates for:

- API keys
- user settings
- multimodal settings
- app integration settings

Typical integrations include:

- Gemini
- OpenAI
- Spotify
- Google services
- local/offline voice models

---

## Troubleshooting

### Import errors

- verify the virtual environment is active
- reinstall dependencies from `config/requirements/requirements.txt`
- confirm commands are run from the repository root

### Frontend not loading

- confirm both backend and React dev server are running
- check whether ports `8000` or `5173` are already occupied
- re-run `npm install` in `src/project/`

### AI keys not loading

- confirm local config was created from example files
- run `python scripts/validation/check_ai_status.py`
- keep local key files on your machine only

### Voice stack issues

- check microphone permissions
- install PyAudio if required
- install OCR and speech dependencies only if you plan to use them

---

## Contributing

Suggested workflow:

```bash
git checkout -b feature/my-change
pytest
git commit -m "Describe change"
git push origin feature/my-change
```

Keep generated files, secrets, local databases, and environment-specific configs out of commits.

---

## License

This project is licensed under the MIT License. See `docs/LICENSE.txt`.
