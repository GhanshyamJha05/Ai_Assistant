from typing import Dict, Any, List, Optional
import os
import subprocess

from ..base_agent import BaseAgent
from ..models import Task, TaskResult

class VideoAgent(BaseAgent):
    """
    Handles video editing, creation, and transcription.
    """
    
    def __init__(self, agent_id: str = "video-001", config: Dict[str, Any] = None):
        super().__init__(agent_id, config or {})
        self.name = "Video Agent"
        self.category = "video"
        self.capabilities = [
            "edit_video",
            "transcribe_video",
            "extract_audio",
            "create_thumbnail"
        ]
        
        # Lazy load libraries to prevent startup lag
        self._moviepy = None
        self._whisper = None
        self._whisper_model = None
        
    async def can_handle(self, task: Task) -> bool:
        """Check if task involves video"""
        keywords = ["video", "movie", "clip", "edit", "trim", "cut", "transcribe", "subtitle", "caption"]
        return any(kw in task.description.lower() for kw in keywords)
    
    async def execute(self, task: Task) -> TaskResult:
        """Execute video task"""
        try:
            desc = task.description.lower()
            
            if "transcribe" in desc or "caption" in desc:
                return await self._transcribe_video(task)
            elif "cut" in desc or "trim" in desc or "edit" in desc:
                return await self._edit_video(task)
            elif "extract audio" in desc:
                return await self._extract_audio(task)
            else:
                return TaskResult(success=False, error=f"Unknown video task: {desc}")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return TaskResult(success=False, error=str(e))
            
    # --- Library Loading ---
    
    def _load_moviepy(self):
        if not self._moviepy:
            try:
                import moviepy.editor as mp
                self._moviepy = mp
            except ImportError:
                raise ImportError("moviepy not installed.")
        return self._moviepy
        
    def _load_whisper(self):
        if not self._whisper:
            try:
                import whisper
                self._whisper = whisper
            except ImportError:
                raise ImportError("openai-whisper not installed.")
        return self._whisper

    # --- Capabilities ---

    async def _edit_video(self, task: Task) -> TaskResult:
        """Simple editing: Trim, Concatenate"""
        mp = self._load_moviepy()
        
        input_file = task.params.get("input_file")
        if not input_file or not os.path.exists(input_file):
             return TaskResult(success=False, error=f"Input file not found: {input_file}")
             
        start_time = task.params.get("start_time", 0) # Seconds
        end_time = task.params.get("end_time", None)  # Seconds
        
        try:
            # Load video
            clip = mp.VideoFileClip(input_file)
            
            # Trim
            if end_time:
                clip = clip.subclip(start_time, end_time)
            elif start_time > 0:
                clip = clip.subclip(start_time)
                
            # Save
            filename = task.params.get("output_filename", f"edited_{task.task_id[:8]}.mp4")
            output_path = os.path.abspath(os.path.join("outputs", filename))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            clip.close()
            
            return TaskResult(
                success=True,
                output_path=output_path,
                data={"duration": clip.duration}
            )
        except Exception as e:
             return TaskResult(success=False, error=f"Editing failed: {e}")

    async def _extract_audio(self, task: Task) -> TaskResult:
        """Extract audio from video"""
        mp = self._load_moviepy()
        
        input_file = task.params.get("input_file")
        if not input_file or not os.path.exists(input_file):
             return TaskResult(success=False, error=f"Input file not found: {input_file}")
             
        try:
            clip = mp.VideoFileClip(input_file)
            
            filename = task.params.get("output_filename", f"audio_{task.task_id[:8]}.mp3")
            output_path = os.path.abspath(os.path.join("outputs", filename))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            clip.audio.write_audiofile(output_path)
            clip.close()
            
            return TaskResult(
                success=True,
                output_path=output_path
            )
        except Exception as e:
            return TaskResult(success=False, error=f"Audio extraction failed: {e}")

    async def _transcribe_video(self, task: Task) -> TaskResult:
        """Transcribe video using Whisper"""
        whisper = self._load_whisper()
        
        input_file = task.params.get("input_file")
        if not input_file or not os.path.exists(input_file):
             return TaskResult(success=False, error=f"Input file not found: {input_file}")
        
        model_size = task.params.get("model", "base")
        
        try:
            # Check if model loaded
            if not self._whisper_model:
                print(f"Loading Whisper model '{model_size}'...")
                self._whisper_model = whisper.load_model(model_size)
                
            # Transcribe
            print(f"Transcribing {input_file}...")
            result = self._whisper_model.transcribe(input_file)
            text = result["text"]
            
            # Save text
            filename = task.params.get("output_filename", f"transcription_{task.task_id[:8]}.txt")
            output_path = os.path.abspath(os.path.join("outputs", filename))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
                
            return TaskResult(
                success=True,
                output_path=output_path,
                data={"text": text[:500]} # Return preview
            )
            
        except Exception as e:
            return TaskResult(success=False, error=f"Transcription failed: {e}")
