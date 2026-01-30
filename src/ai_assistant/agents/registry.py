from typing import Dict, List, Optional, Type
from .base_agent import BaseAgent
from .models import Task

class AgentRegistry:
    """
    Manages all available agents and their capabilities
    """
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._capabilities: Dict[str, List[str]] = {}  # capability -> agent_ids
        
    def register_agent(self, agent: BaseAgent):
        """Register a new agent instance"""
        self._agents[agent.agent_id] = agent
        
        # Register capabilities
        for cap in agent.capabilities:
            if cap not in self._capabilities:
                self._capabilities[cap] = []
            self._capabilities[cap].append(agent.agent_id)
            
        print(f"Registered agent: {agent.name} ({agent.agent_id})")
            
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self._agents.get(agent_id)
        
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self._agents.values())
        
    def find_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """Find agents that have a specific capability"""
        agent_ids = self._capabilities.get(capability, [])
        return [self._agents[aid] for aid in agent_ids]
        
    async def find_best_agent(self, task: Task) -> Optional[BaseAgent]:
        """Find the best agent for a given task"""
        # Improved: Score capabilities
        candidates = []
        for agent in self._agents.values():
            if await agent.can_handle(task):
                candidates.append(agent)
                
        if not candidates:
            return None
            
        # Priority Logic: if multiple candidates, pick relevant capability match if possible, else first
        # For now, simplistic
        return candidates[0]
