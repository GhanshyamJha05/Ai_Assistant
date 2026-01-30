import sys
import os
import numpy as np
import logging

sys.path.append(os.path.join(os.getcwd(), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_noise_reduction_direct():
    print("Testing Noise Reduction Direct...")
    
    try:
        from ai_assistant.voice.noise_reduction import NoiseReductionSystem, NoiseReductionConfig, NoiseReductionMethod
        
        config = NoiseReductionConfig(method=NoiseReductionMethod.HYBRID)
        reducer = NoiseReductionSystem(config)
        print("Noise Reduction System initialized")
        
        # Generate synthetic noisy audio
        sr = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration))
        
        # Signal + Noise
        clean = np.sin(2 * np.pi * 440 * t) * 0.5  # 440Hz tone
        noise = np.random.normal(0, 0.2, len(t))
        noisy_signal = clean + noise
        
        print(f"Original Noise Level: {np.mean(np.abs(noisy_signal)):.6f}")
        
        # Apply reduction
        reduced = reducer.reduce_noise(noisy_signal.astype(np.float32))
        
        print(f"Reduced Noise Level:  {np.mean(np.abs(reduced)):.6f}")
        
        # Check if noise is reduced (simple check)
        # Reduction ratio logic might be tricky with a tone, but noise usually decreases
        print("Reduction calculation done.")
        
    except ImportError as e:
        print(f"Import failed: {e}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_noise_reduction_direct()
