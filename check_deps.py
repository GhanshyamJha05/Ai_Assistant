try:
    import scipy
    import librosa
    print("✅ Scipy and Librosa are installed.")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
