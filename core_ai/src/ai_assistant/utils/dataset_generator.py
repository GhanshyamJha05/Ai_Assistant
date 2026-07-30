import json
import random
import os
from pathlib import Path

# Intents and their corresponding tool calls
INTENTS = {
    "open_app": {
        "tool_name": "system_automation",
        "action": "open_app",
        "hinglish_verbs": ["khol do", "open kar", "start kar de", "chala de", "khol de bhai", "open kro"],
        "targets": ["chrome", "notepad", "spotify", "vscode", "settings", "calculator"]
    },
    "close_app": {
        "tool_name": "system_automation",
        "action": "close_app",
        "hinglish_verbs": ["band kar", "close kar de", "hata de", "kill kar", "band kro"],
        "targets": ["chrome", "notepad", "spotify", "vscode"]
    },
    "minimize_window": {
        "tool_name": "system_automation",
        "action": "minimize_window",
        "hinglish_verbs": ["minimize kar", "niche kar de", "chhupa de", "hide kar"],
        "targets": ["chrome", "spotify", "current window", "active app"]
    },
    "change_wallpaper": {
        "tool_name": "system_automation",
        "action": "change_wallpaper",
        "hinglish_verbs": ["wallpaper change kar", "naya wallpaper laga de", "background badal de", "wallpaper set kar"],
        "targets": ["nature", "dark", "cyberpunk", "cars", "cars hd"]
    },
    "set_volume": {
        "tool_name": "system_automation",
        "action": "set_volume",
        "hinglish_verbs": ["volume badha", "awaaz tez kar", "volume full kar", "awaaz badha de", "volume set kar"],
        "targets": ["100", "50", "up", "max"]
    },
    "mute": {
        "tool_name": "system_automation",
        "action": "set_volume",
        "hinglish_verbs": ["mute kar de", "awaaz band kar", "silent kar de", "chup kar de"],
        "targets": ["0", "mute"]
    },
    "shutdown": {
        "tool_name": "system_automation",
        "action": "shutdown_pc",
        "hinglish_verbs": ["pc band kar de", "shutdown kar", "system off kar", "laptop band kar do"],
        "targets": ["now", "immediately"]
    }
}

PREFIXES = ["bhai ", "jaldi se ", "yaar ", "hey ", "chalo ", "zara ", "ek kaam kar ", ""]
SUFFIXES = [" jaldi", " yaar", " fast", " please", ""]

def generate_dataset(num_samples=1000):
    dataset = []
    
    for _ in range(num_samples):
        intent_key = random.choice(list(INTENTS.keys()))
        intent = INTENTS[intent_key]
        
        verb = random.choice(intent["hinglish_verbs"])
        target = random.choice(intent["targets"])
        prefix = random.choice(PREFIXES)
        suffix = random.choice(SUFFIXES)
        
        # Construct the user prompt
        # E.g., "bhai chrome khol do jaldi"
        if intent_key in ["shutdown", "mute"]:
            user_prompt = f"{prefix}{verb}{suffix}".strip()
        else:
            user_prompt = f"{prefix}{target} {verb}{suffix}".strip()
            
        # Clean double spaces
        user_prompt = " ".join(user_prompt.split())
        
        # Build the OpenAI tool call format
        arguments = {"action": intent["action"]}
        if intent_key not in ["shutdown"]:
            arguments["target"] = target
            
        message = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are YourDaddy, a snarky but helpful PC assistant. You execute commands natively on the user's PC using tools."
                },
                {
                    "role": "user",
                    "content": user_prompt
                },
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": intent["tool_name"],
                                "arguments": json.dumps(arguments)
                            }
                        }
                    ]
                }
            ]
        }
        
        dataset.append(message)
        
    return dataset

if __name__ == "__main__":
    out_dir = Path("d:/Projects/Ai_Assistant/shared/data/training")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_file = out_dir / "automation_finetune_v1.jsonl"
    
    # Generate 2000 permutations
    data = generate_dataset(2000)
    
    with open(out_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"✅ Generated {len(data)} training examples at {out_file}")
