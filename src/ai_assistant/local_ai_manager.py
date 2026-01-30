"""
Local AI Manager - Optimized for 8GB RAM / 1GB GPU
Uses TinyLlama-1.1B with CPU inference via llama.cpp

Hardware Requirements:
- RAM: 8GB (uses ~2GB for model + context)
- GPU: Not required (CPU-only mode)
- Storage: ~1.5GB for model files
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Generator, Union
from dataclasses import dataclass
from datetime import datetime

try:
    from llama_cpp import Llama
except (ImportError, OSError, Exception) as e:
    print(f"⚠️ llama-cpp-python not available: {e}")
    print("ℹ️  Run: pip install llama-cpp-python (and ensure VS C++ Redistributable is installed)")
    Llama = None


@dataclass
class LocalModelConfig:
    """Configuration for local AI model"""
    name: str
    path: str
    context_length: int = 2048
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    threads: int = 4  # CPU threads


class LocalAIManager:
    """Manages local AI inference with TinyLlama"""
    
    def __init__(self, models_dir: str = "model/local_models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_model: Optional[Llama] = None
        self.model_config: Optional[LocalModelConfig] = None
        self.conversation_history: List[Dict] = []
        
        # Performance tracking
        self.stats = {
            "total_queries": 0,
            "avg_tokens_per_sec": 0.0,
            "total_tokens_generated": 0
        }
    
    def find_best_available_model(self) -> Optional[str]:
        """
        Find the best available model in the models directory.
        Priority:
        1. Llama-3 (Best quality)
        2. Qwen2.5 (Fastest)
        3. TinyLlama (Legacy/Tiny)
        4. Any other .gguf file
        """
        # Known models in priority order
        priority_models = [
            "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "qwen2-0_5b-instruct-q4_k_m.gguf",
            "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        ]
        
        # Check specific priority models first
        for model_name in priority_models:
            model_path = self.models_dir / model_name
            if model_path.exists():
                print(f"✅ Found priority model: {model_name}")
                return str(model_path)
                
        # Fallback: Look for any .gguf file
        gguf_files = list(self.models_dir.glob("*.gguf"))
        if gguf_files:
            # Sort by size descending (heuristic: bigger = better/smarter?) 
            # or just pick the first one. Let's pick the largest one assuming it's most capable.
            best_model = sorted(gguf_files, key=lambda x: x.stat().st_size, reverse=True)[0]
            print(f"✅ Found fallback model: {best_model.name}")
            return str(best_model)
            
        print("❌ No models found in", self.models_dir)
        return None

    def download_model(self, model_name: str = "llama3-3b") -> str:
        """
        Download quantized model (GGUF format)
        
        Recommended models for 8GB RAM:
        - Llama-3.2-3B: ~2.2GB, Best balance of smarts/speed
        - Qwen2.5-1.5B: ~1.2GB, Very fast
        - TinyLlama-1.1B: ~700MB, Minimal resource usage
        """
        
        model_files = {
            "llama3-3b": {
                "name": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "url": "https://huggingface.co/Bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "size": "~2.2GB"
            },
            "qwen1.5b": {
                "name": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
                "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
                "size": "~1.2GB"
            },
            "tinyllama": {
                "name": "TinyLlama-1.1B-Chat-v1.0-Q4_K_M.gguf",
                "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                "size": "~700MB"
            }
        }
        
        if model_name not in model_files:
            raise ValueError(f"Unknown model: {model_name}. Choose from: {list(model_files.keys())}")
        
        model_info = model_files[model_name]
        model_path = self.models_dir / model_info["name"]
        
        if model_path.exists():
            print(f"✅ Model already exists: {model_path}")
            return str(model_path)
        
        print(f"📥 Downloading {model_info['name']} ({model_info['size']})...")
        print(f"📍 URL: {model_info['url']}")
        print(f"\n⚠️ Download this file manually and place it in: {self.models_dir}")
        print(f"\nAlternatively, use huggingface-cli:")
        print(f"  pip install huggingface-hub")
        print(f"  huggingface-cli download TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --local-dir {self.models_dir}")
        
        return str(model_path)
    
    def load_model(self, model_path: str, threads: int = 4) -> bool:
        """
        Load model into memory (CPU-only)
        
        Args:
            model_path: Path to .gguf model file
            threads: CPU threads to use (default: 4)
        """
        if Llama is None:
            print("❌ llama-cpp-python not installed")
            return False
        
        model_path = Path(model_path)
        if not model_path.exists():
            print(f"❌ Model file not found: {model_path}")
            return False
        
        print(f"🔄 Loading model: {model_path.name}")
        print(f"💻 CPU threads: {threads}")
        
        try:
            start_time = time.time()
            
            self.current_model = Llama(
                model_path=str(model_path),
                n_ctx=2048,        # Context window
                n_threads=threads,  # CPU threads
                n_gpu_layers=0,    # CPU-only (no GPU)
                use_mlock=True,    # Keep model in RAM
                verbose=False
            )
            
            load_time = time.time() - start_time
            
            self.model_config = LocalModelConfig(
                name=model_path.stem,
                path=str(model_path),
                threads=threads
            )
            
            print(f"✅ Model loaded in {load_time:.2f}s")
            print(f"📊 RAM usage: ~{model_path.stat().st_size / (1024**2):.0f}MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Union[str, Generator]:
        """
        Generate response from local model
        
        Args:
            prompt: Input text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            stream: Stream response token-by-token
        """
        if self.current_model is None:
            return "❌ No model loaded. Call load_model() first."
        
        # TinyLlama chat template
        formatted_prompt = f"<|system|>\nYou are a helpful AI assistant.</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
        
        start_time = time.time()
        
        if stream:
            return self._generate_stream(formatted_prompt, max_tokens, temperature)
        
        try:
            response = self.current_model(
                formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stop=["</s>", "<|user|>"],
                echo=False
            )
            
            generated_text = response["choices"][0]["text"].strip()
            tokens_generated = response["usage"]["completion_tokens"]
            
            # Update stats
            elapsed = time.time() - start_time
            tokens_per_sec = tokens_generated / elapsed if elapsed > 0 else 0
            
            self.stats["total_queries"] += 1
            self.stats["total_tokens_generated"] += tokens_generated
            self.stats["avg_tokens_per_sec"] = (
                (self.stats["avg_tokens_per_sec"] * (self.stats["total_queries"] - 1) + tokens_per_sec) 
                / self.stats["total_queries"]
            )
            
            print(f"⚡ {tokens_per_sec:.1f} tokens/sec ({tokens_generated} tokens in {elapsed:.2f}s)")
            
            return generated_text
            
        except Exception as e:
            return f"❌ Generation error: {e}"
    
    def _generate_stream(self, prompt: str, max_tokens: int, temperature: float) -> Generator:
        """Stream tokens as they're generated"""
        try:
            for chunk in self.current_model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                stop=["</s>", "<|user|>"],
                stream=True
            ):
                token = chunk["choices"][0]["text"]
                yield token
        except Exception as e:
            yield f"❌ Stream error: {e}"
    
    def chat(self, message: str, max_tokens: int = 512) -> str:
        """
        Chat with conversation history
        
        Args:
            message: User message
            max_tokens: Maximum response length
        """
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Build context from history (last 5 messages)
        context = ""
        for msg in self.conversation_history[-5:]:
            if msg["role"] == "user":
                context += f"<|user|>\n{msg['content']}</s>\n"
            else:
                context += f"<|assistant|>\n{msg['content']}</s>\n"
        
        # Generate response
        response = self.generate(
            message,
            max_tokens=max_tokens,
            temperature=0.7,
            stream=False
        )
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️ Conversation history cleared")
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            **self.stats,
            "model": self.model_config.name if self.model_config else None,
            "context_length": self.model_config.context_length if self.model_config else None,
            "history_length": len(self.conversation_history)
        }
    
    def unload_model(self):
        """Free model from memory"""
        if self.current_model:
            del self.current_model
            self.current_model = None
            self.model_config = None
            print("🗑️ Model unloaded from memory")


# === Quick Test Function ===
def quick_test():
    """Quick test of local AI"""
    print("🚀 Local AI Manager - Quick Test\n")
    
    manager = LocalAIManager()
    
    # Download instructions
    model_path = manager.download_model("tinyllama")
    
    if not Path(model_path).exists():
        print("\n⚠️ Please download the model first, then run this test again.")
        return
    
    # Load model
    if not manager.load_model(model_path, threads=4):
        return
    
    # Test queries
    test_queries = [
        "What is the capital of France?",
        "Write a Python function to calculate factorial.",
        "Explain quantum computing in simple terms."
    ]
    
    print("\n" + "="*60)
    for query in test_queries:
        print(f"\n❓ {query}")
        print("-" * 60)
        response = manager.generate(query, max_tokens=256)
        print(f"🤖 {response}")
        print("-" * 60)
    
    # Show stats
    print("\n📊 Performance Statistics:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    manager.unload_model()


if __name__ == "__main__":
    quick_test()
