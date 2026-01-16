from typing import List
from .registry import AgentRegistry
from .base_agent import BaseAgent

# Import agent classes
from .productivity.productivity_agent import ProductivityAgent
from .research.research_agent import ResearchAgent
from .writer.writer_agent import WriterAgent

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
            WriterAgent()
        ]
        
        for agent in agents:
            try:
                registry.register_agent(agent)
            except Exception as e:
                print(f"Failed to register agent {agent.name}: {e}")
                
        return registry
