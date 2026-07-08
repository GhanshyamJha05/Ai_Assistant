from datetime import datetime
import platform
import socket
import json
from pathlib import Path
from typing import Dict, Any

class ContextOptimizer:
    def __init__(self, settings_path: str = None):
        if settings_path is None:
            current_dir = Path(__file__).parent
            while current_dir.name != 'Ai_Assistant' and current_dir.parent != current_dir:
                current_dir = current_dir.parent
            self.settings_path = current_dir / 'config' / 'user_settings.json'
        else:
            self.settings_path = Path(settings_path)
            
        self.context_profiles = {
            "work": {
                "formality": "formal",
                "conciseness": "high",
                "focus_mode": True
            },
            "home": {
                "formality": "casual",
                "conciseness": "medium",
                "focus_mode": False
            },
            "night": {
                "formality": "casual",
                "conciseness": "high",
                "focus_mode": True
            }
        }
        
    def get_time_context(self) -> str:
        hour = datetime.now().hour
        if 8 <= hour < 18:
            return "work"
        elif 18 <= hour < 22:
            return "home"
        else:
            return "night"
            
    def get_device_context(self) -> Dict[str, str]:
        return {
            "os": platform.system(),
            "hostname": socket.gethostname(),
            "python_version": platform.python_version()
        }
        
    def get_current_profile(self) -> Dict[str, Any]:
        time_context = self.get_time_context()
        profile = self.context_profiles.get(time_context, self.context_profiles["home"]).copy()
        profile["device"] = self.get_device_context()
        profile["time_context"] = time_context
        return profile
        
    def inject_context_into_prompt(self, base_prompt: str) -> str:
        profile = self.get_current_profile()
        context_str = (
            f"\n\n[SYSTEM CONTEXT]\n"
            f"- Current Profile: {profile['time_context'].upper()}\n"
            f"- Tone Formality: {profile['formality']}\n"
            f"- Verbosity: {profile['conciseness']}\n"
            f"- Focus Mode: {profile['focus_mode']}\n"
            f"Adapt your response style to match this current context."
        )
        return base_prompt + context_str
