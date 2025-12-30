"""
Test script for Intent Recognizer
"""
import sys
sys.path.insert(0, 'f:\\bn\\assitant')

from ai_assistant.ai.intent_recognizer import IntentRecognizer

# Create recognizer
recognizer = IntentRecognizer()

# Test cases
test_commands = [
    "open whatsapp",
    "whatsapp kholo",
    "whatsapp on kro",
    "whats app kholo",
    "chrome open karo",
    "calculator chalao",
    "open chrome",
    "spotify kholo",
    "whatsapp open",
]

print("="*60)
print("INTENT RECOGNIZER TEST RESULTS")
print("="*60)

for cmd in test_commands:
    result = recognizer.parse_command(cmd)
    print(f"\nCommand: '{cmd}'")
    print(f"  Intent: {result.get('intent')}")
    print(f"  App: {result.get('app_name')}")
    print(f"  Confidence: {result.get('confidence'):.2f}")

print("\n" + "="*60)
print("WHATSAPP VARIATIONS TEST")
print("="*60)

whatsapp_tests = [
    "whatsapp",
    "whats app",
    "whats",
    "whatsap",
    "whatapp",
]

for variation in whatsapp_tests:
    normalized = recognizer.normalize_app_name(variation)
    print(f"'{variation}' -> '{normalized}'")
