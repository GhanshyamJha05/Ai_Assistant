from typing import List
from .registry import AgentRegistry
from .base_agent import BaseAgent

# Import agent classes
from .productivity.productivity_agent import ProductivityAgent
from .research.research_agent import ResearchAgent
from .writer.writer_agent import WriterAgent
from .video.video_agent import VideoAgent
from .creative.creative_agent import CreativeAgent
from .data.data_analyst_agent import DataAnalystAgent
from .data.database_agent import DatabaseAgent
from .communication.communication_agent import CommunicationAgent
from .web.web_agent import WebAgent
from .teacher.student_agent import StudentAgent
from .file.file_manager_agent import FileManagerAgent
from .audio.audio_agent import AudioAgent

class AgentLoader:
    """
    Helper to load agents into the registry
    """
    
    @staticmethod
    def load_all_agents() -> AgentRegistry:
        registry = AgentRegistry()
        
        # Instantiate and register
        agents: List[BaseAgent] = [
            ProductivityAgent(),
            ResearchAgent(),
            WriterAgent(),
            VideoAgent(),
            CreativeAgent(),
            DataAnalystAgent(),
            DatabaseAgent(),
            CommunicationAgent(),
            WebAgent(),
            StudentAgent(),
            FileManagerAgent(),
            AudioAgent()
        ]
        
        for agent in agents:
            try:
                registry.register_agent(agent)
            except Exception as e:
                print(f"Failed to register agent {agent.name}: {e}")
                
        return registry
