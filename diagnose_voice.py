#!/usr/bin/env python3
"""
Voice Listening Diagnostic Script
Tests and diagnoses voice recognition issues in the AI Assistant.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 70)
print("🔍 VOICE LISTENING DIAGNOSTICS")
print("=" * 70)
print()

# Test 1: Check if voice libraries are available
print("1️⃣ Checking voice recognition libraries...")
print("-" * 70)

try:
    import speech_recognition as sr
    print("✅ speech_recognition: INSTALLED")
    print(f"   Version: {sr.__version__}")
except ImportError as e:
    print(f"❌ speech_recognition: NOT INSTALLED - {e}")
    print("   Fix: pip install SpeechRecognition")

try:
    import pyaudio
    print("✅ pyaudio: INSTALLED")
except ImportError as e:
    print(f"❌ pyaudio: NOT INSTALLED - {e}")
    print("   Fix: pip install pyaudio")

try:
    import numpy
    print("✅ numpy: INSTALLED")
except ImportError as e:
    print(f"❌ numpy: NOT INSTALLED - {e}")

print()

# Test 2: Check microphone access
print("2️⃣ Testing microphone access...")
print("-" * 70)

try:
    import speech_recognition as sr
    r = sr.Recognizer()
    
    # List available microphones
    print("Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"   [{index}] {name}")
    
    print()
    print("Testing default microphone...")
    
    with sr.Microphone() as source:
        print(f"✅ Microphone accessible: {source.CHUNK} chunk size, {source.SAMPLE_RATE} sample rate")
        print("   Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"   Energy threshold set to: {r.energy_threshold}")
        
except Exception as e:
    print(f"❌ Microphone test failed: {e}")
    print()
    print("Common fixes:")
    print("  1. Check microphone is plugged in/enabled")
    print("  2. Grant microphone permissions to Python")
    print("  3. Check Windows Sound Settings")
    print("  4. Try: pip uninstall pyaudio && pip install pyaudio")

print()

# Test 3: Test Google Speech Recognition
print("3️⃣ Testing Google Speech Recognition...")
print("-" * 70)

try:
    import speech_recognition as sr
    r = sr.Recognizer()
    
    print("This test will record for 3 seconds - please speak!")
    print("Say something like: 'Hello, this is a test'")
    print()
    input("Press ENTER when ready to record...")
    
    with sr.Microphone() as source:
        print("🔴 RECORDING... (3 seconds)")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=5, phrase_time_limit=3)
        print("✅ Recording complete!")
    
    print("Sending to Google Speech Recognition...")
    try:
        text = r.recognize_google(audio)
        print(f"✅ RECOGNIZED: '{text}'")
        print("   Google Speech Recognition is working!")
    except sr.UnknownValueError:
        print("⚠️ Google could not understand the audio")
        print("   This might mean:")
        print("   - Speech was unclear")
        print("   - Background noise too high")
        print("   - Microphone volume too low")
    except sr.RequestError as e:
        print(f"❌ Google Speech API error: {e}")
        print("   This means:")
        print("   - No internet connection, OR")
        print("   - Google service is down")
    
except Exception as e:
    print(f"❌ Speech recognition test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Backend voice configuration
print("4️⃣ Checking backend voice configuration...")
print("-" * 70)

try:
    with open('config/voice_config.json', 'r') as f:
        import json
        config = json.load(f)
        print("✅ voice_config.json found")
        print(f"   Default STT engine: {config.get('stt', {}).get('default_engine', 'N/A')}")
        print(f"   Language: {config.get('stt', {}).get('language', 'N/A')}")
        print(f"   Noise reduction: {config.get('stt', {}).get('noise_reduction', 'N/A')}")
        print(f"   Energy threshold: {config.get('stt', {}).get('energy_threshold', 'N/A')}")
except FileNotFoundError:
    print("⚠️ voice_config.json not found")
except Exception as e:
    print(f"❌ Config error: {e}")

print()

# Test 5: Check if backend is running
print("5️⃣ Checking if backend is running...")
print("-" * 70)

try:
    import requests
    response = requests.get('http://localhost:5000/api/status', timeout=2)
    if response.status_code == 200:
        data = response.json()
        print("✅ Backend is running (http://localhost:5000)")
        print(f"   Voice available: {data.get('services', {}).get('voice', False)}")
        print(f"   Automation available: {data.get('services', {}).get('automation', False)}")
    else:
        print(f"⚠️ Backend returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Backend is NOT running")
    print("   Start with: python modern_web_backend.py")
except Exception as e:
    print(f"❌ Backend check failed: {e}")

print()

# Summary and recommendations
print("=" * 70)
print("📋 DIAGNOSTIC SUMMARY")
print("=" * 70)
print()
print("Common issues and fixes:")
print()
print("1. 'Microphone not accessible'")
print("   → Check Windows Privacy Settings > Microphone")
print("   → Allow apps to access microphone")
print()
print("2. 'Google Speech API error'")
print("   → Check internet connection")
print("   → Try recognize_google with language='en-IN' or 'hi-IN'")
print()
print("3. 'No speech detected'")
print("   → Increase microphone volume in Windows settings")
print("   → Reduce background noise")
print("   → Adjust energy_threshold in voice_config.json")
print()
print("4. 'Hindi/Hinglish not recognized'")
print("   → Restart backend to use enhanced recognition")
print("   → Test with: python test_hindi_recognition.py")
print()
print("=" * 70)
