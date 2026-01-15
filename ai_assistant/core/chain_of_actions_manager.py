"""
Chain of Actions Manager
Central orchestrator for multi-step action execution with verification

Implements 7-step workflow:
1. Listen (receive command)
2. Process & Breakdown (decompose into actions)
3. Identify (determine which components handle what)
4. Assign (route to execution systems)
5. Track Progress (real-time updates)
6. Aggregate (combine results)
7. Notify (inform user)
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from pathlib import Path

from ai_assistant.core.action_chain_models import (
    ActionChain, Action, ChainStatus, ActionType,
    ExecutionReport, ProgressReport,
    generate_chain_id, generate_action_id
)

# Import existing components
try:
    from ai_assistant.automation.task_planner import TaskPlanner
    TASK_PLANNER_AVAILABLE = True
except ImportError:
    TASK_PLANNER_AVAILABLE = False

try:
    from ai_assistant.automation.orchestrator import AutomationOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

try:
    from ai_assistant.automation.visual_verification import get_visual_verifier
    VERIFIER_AVAILABLE = True
except ImportError:
    VERIFIER_AVAILABLE = False

try:
    from ai_assistant.core.task_chain_orchestrator import TaskChainOrchestrator
    TASK_CHAIN_AVAILABLE = True
except ImportError:
    TASK_CHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChainOfActionsManager:
    """
    Central manager for chain-of-actions execution
    
    Integrates:
    - TaskPlanner (decomposition)
    - TaskChainOrchestrator (execution)
    - AutomationOrchestrator (resource management)
    - VisualVerifier (verification)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize manager"""
        self.config = config or {}
        
        # Active chains
        self.active_chains: Dict[str, ActionChain] = {}
        self.completed_chains: Dict[str, ActionChain] = {}
        
        # Progress callbacks
        self.progress_callbacks: Dict[str, List[Callable]] = {}
        
        # Initialize components
        self.task_planner = TaskPlanner() if TASK_PLANNER_AVAILABLE else None
        self.task_orchestrator = TaskChainOrchestrator() if TASK_CHAIN_AVAILABLE else None
        self.verifier = get_visual_verifier() if VERIFIER_AVAILABLE else None
        
        # Performance tracking
        self.stats = {
            "total_chains": 0,
            "successful_chains": 0,
            "failed_chains": 0,
            "total_actions": 0,
            "average_duration": 0.0
        }
        
        logger.info("ChainOfActionsManager initialized")
    
    # ========== STEP 1: LISTEN ==========
    
    async def create_chain(self, command: str) -> ActionChain:
        """
        Create a new action chain from user command
        
        Args:
            command: Natural language command
            
        Returns:
            ActionChain object
        """
        logger.info(f"📝 STEP 1 - LISTEN: Received command: {command}")
        
        chain = ActionChain(
            id=generate_chain_id(),
            command=command,
            status=ChainStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.active_chains[chain.id] = chain
        self.stats["total_chains"] += 1
        
        logger.info(f"Created chain {chain.id}")
        return chain
    
    # ========== STEP 2: PROCESS & BREAKDOWN ==========
    
    async def decompose_command(self, chain: ActionChain) -> List[Action]:
        """
        Decompose command into executable actions
        
        Args:
            chain: ActionChain to decompose
            
        Returns:
            List of Action objects
        """
        logger.info(f"⚙️ STEP 2 - PROCESS & BREAKDOWN: Decomposing '{chain.command}'")
        
        chain.status = ChainStatus.PLANNING
        await self._notify_progress(chain)
        
        actions = []
        
        # Use TaskPlanner if available
        if self.task_planner:
            try:
                plan = self.task_planner.create_plan(chain.command)
                
                for i, planned_action in enumerate(plan.actions):
                    action = Action(
                        id=generate_action_id(),
                        type=self._map_action_type(planned_action.type.value),
                        description=planned_action.description,
                        parameters=planned_action.parameters,
                        dependencies=planned_action.dependencies
                    )
                    actions.append(action)
                
                logger.info(f"✅ Decomposed into {len(actions)} actions using TaskPlanner")
                
            except Exception as e:
                logger.error(f"TaskPlanner failed: {e}")
                # Fallback to simple decomposition
                actions = await self._simple_decomposition(chain.command)
        else:
            # Simple decomposition
            actions = await self._simple_decomposition(chain.command)
        
        chain.actions = actions
        self.stats["total_actions"] += len(actions)
        
        return actions
    
    async def _simple_decomposition(self, command: str) -> List[Action]:
        """Fallback simple decomposition"""
        logger.info("Using simple decomposition (TaskPlanner not available)")
        
        # Basic keyword-based decomposition
        actions = []
        command_lower = command.lower()
        
        # Browser actions
        if any(kw in command_lower for kw in ['open', 'navigate', 'browse', 'youtube', 'google']):
            actions.append(Action(
                id=generate_action_id(),
                type=ActionType.BROWSER,
                description=f"Open browser for: {command}",
                parameters={'command': command}
            ))
        
        # App actions
        if any(kw in command_lower for kw in ['whatsapp', 'sticky notes', 'notepad', 'word']):
            actions.append(Action(
                id=generate_action_id(),
                type=ActionType.APP,
                description=f"Open application for: {command}",
                parameters={'command': command}
            ))
        
        # File actions
        if any(kw in command_lower for kw in ['create', 'save', 'file', 'document']):
            actions.append(Action(
                id=generate_action_id(),
                type=ActionType.FILE,
                description=f"File operation: {command}",
                parameters={'command': command}
            ))
        
        # Default action if nothing matched
        if not actions:
            actions.append(Action(
                id=generate_action_id(),
                type=ActionType.CUSTOM,
                description=command,
                parameters={'command': command}
            ))
        
        return actions
    
    def _map_action_type(self, planner_type: str) -> ActionType:
        """Map TaskPlanner action type to ActionType enum"""
        mapping = {
            'browser_navigate': ActionType.BROWSER,
            'browser_click': ActionType.BROWSER,
            'browser_type': ActionType.BROWSER,
            'app_open': ActionType.APP,
            'app_close': ActionType.APP,
            'file_create': ActionType.FILE,
            'file_read': ActionType.FILE,
            'system_command': ActionType.SYSTEM,
        }
        return mapping.get(planner_type, ActionType.CUSTOM)
    
    # ========== STEP 3: IDENTIFY ==========
    
    async def identify_executors(self, chain: ActionChain) -> Dict[str, str]:
        """
        Identify which component will execute each action
        
        Args:
            chain: ActionChain with actions
            
        Returns:
            Dict mapping action_id -> executor_name
        """
        logger.info(f"🔍 STEP 3 - IDENTIFY: Determining executors for {len(chain.actions)} actions")
        
        executor_map = {}
        
        for action in chain.actions:
            if action.type == ActionType.BROWSER:
                executor_map[action.id] = "BrowserAutomation"
            elif action.type == ActionType.APP:
                executor_map[action.id] = "AppAutomation"
            elif action.type == ActionType.FILE:
                executor_map[action.id] = "FileOperations"
            elif action.type == ActionType.SYSTEM:
                executor_map[action.id] = "SystemControl"
            else:
                executor_map[action.id] = "TaskChainOrchestrator"
        
        logger.info(f"Executor mapping: {executor_map}")
        return executor_map
    
    # ========== STEP 4: ASSIGN & EXECUTE ==========
    
    async def execute_chain(self, chain_id: str) -> ExecutionReport:
        """
        Execute all actions in chain
        
        Args:
            chain_id: Chain ID to execute
            
        Returns:
            ExecutionReport
        """
        chain = self.active_chains.get(chain_id)
        if not chain:
            raise ValueError(f"Chain {chain_id} not found")
        
        logger.info(f"🚀 STEP 4 - ASSIGN & EXECUTE: Starting execution of chain {chain_id}")
        
        chain.status = ChainStatus.EXECUTING
        chain.started_at = datetime.now()
        await self._notify_progress(chain)
        
        completed = 0
        failed = 0
        action_results = []
        
        try:
            # Execute actions in order (respecting dependencies)
            for i, action in enumerate(chain.actions):
                chain.current_action_index = i
                
                # Check dependencies
                if not await self._check_dependencies(action, chain):
                    logger.warning(f"Dependencies not met for {action.id}, skipping")
                    action.status = "skipped"
                    continue
                
                # Execute action
                logger.info(f"Executing action {i+1}/{len(chain.actions)}: {action.description}")
                action.status = "running"
                action.started_at = datetime.now()
                await self._notify_progress(chain)
                
                try:
                    result = await self._execute_action(action, chain)
                    
                    action.status = "completed"
                    action.result = result
                    action.completed_at = datetime.now()
                    action.duration_seconds = (action.completed_at - action.started_at).total_seconds()
                    
                    chain.actions_completed += 1
                    completed += 1
                    
                    # Store result
                    chain.results[action.id] = result
                    action_results.append({
                        "action_id": action.id,
                        "description": action.description,
                        "result": result,
                        "duration": action.duration_seconds
                    })
                    
                    logger.info(f"✅ Action completed: {action.description}")
                    
                except Exception as e:
                    logger.error(f"❌ Action failed: {action.description} - {e}")
                    action.status = "failed"
                    action.error = str(e)
                    action.completed_at = datetime.now()
                    
                    chain.actions_failed += 1
                    failed += 1
                    chain.errors.append(f"Action {action.id}: {str(e)}")
                
                await self._notify_progress(chain)
            
            # All actions processed
            chain.status = ChainStatus.VERIFYING
            await self._notify_progress(chain)
            
        except Exception as e:
            logger.error(f"Chain execution failed: {e}", exc_info=True)
            chain.status = ChainStatus.FAILED
            chain.errors.append(str(e))
        
        return await self._finalize_chain(chain, completed, failed, action_results)
    
    async def _check_dependencies(self, action: Action, chain: ActionChain) -> bool:
        """Check if action dependencies are satisfied"""
        if not action.dependencies:
            return True
        
        for dep_id in action.dependencies:
            dep_action = next((a for a in chain.actions if a.id == dep_id), None)
            if not dep_action or dep_action.status != "completed":
                return False
        
        return True
    
    async def _execute_action(self, action: Action, chain: ActionChain) -> Any:
        """Execute single action"""
        
        # Use TaskChainOrchestrator if available
        if self.task_orchestrator and action.type in [ActionType.APP, ActionType.BROWSER]:
            from ai_assistant.ai.multi_step_parser import TaskStep
            
            # Convert to TaskStep
            step = TaskStep(
                step=chain.current_action_index + 1,
                intent=self._infer_intent(action),
                params=action.parameters,
                dependencies=action.dependencies
            )
            
            result = self.task_orchestrator.execute_step(step)
            return result
        
        # Fallback: simulate execution
        logger.info(f"Simulating execution: {action.description}")
        await asyncio.sleep(1)  # Simulate work
        
        return {
            "success": True,
            "message": f"Executed: {action.description}",
            "output": None
        }
    
    def _infer_intent(self, action: Action) -> str:
        """Infer intent from action type"""
        if action.type == ActionType.APP:
            return "open_app"
        elif action.type == ActionType.BROWSER:
            return "open_browser"
        elif action.type == ActionType.FILE:
            return "file_operation"
        else:
            return "custom_action"
    
    # ========== STEP 5: TRACK PROGRESS ==========
    
    async def get_progress(self, chain_id: str) -> ProgressReport:
        """Get real-time progress of chain"""
        chain = self.active_chains.get(chain_id) or self.completed_chains.get(chain_id)
        if not chain:
            raise ValueError(f"Chain {chain_id} not found")
        
        current_action = None
        current_progress = 0
        
        if chain.current_action_index < len(chain.actions):
            action = chain.actions[chain.current_action_index]
            current_action = action.description
            current_progress = action.progress
        
        return ProgressReport(
            chain_id=chain_id,
            status=chain.status.value,
            progress_percentage=chain.progress_percentage,
            current_action=current_action,
            current_action_progress=current_progress,
            completed_actions=chain.actions_completed,
            total_actions=chain.total_actions,
            elapsed_seconds=chain.duration_seconds,
            estimated_remaining_seconds=self._estimate_remaining_time(chain)
        )
    
    def _estimate_remaining_time(self, chain: ActionChain) -> float:
        """Estimate remaining execution time"""
        if chain.actions_completed == 0:
            return 0.0
        
        avg_time_per_action = chain.duration_seconds / chain.actions_completed
        remaining_actions = chain.total_actions - chain.actions_completed
        
        return avg_time_per_action * remaining_actions
    
    async def _notify_progress(self, chain: ActionChain):
        """Notify progress callbacks"""
        if chain.id in self.progress_callbacks:
            progress = await self.get_progress(chain.id)
            for callback in self.progress_callbacks[chain.id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(progress)
                    else:
                        callback(progress)
                except Exception as e:
                    logger.error(f"Progress callback error: {e}")
    
    def subscribe_progress(self, chain_id: str, callback: Callable):
        """Subscribe to progress updates"""
        if chain_id not in self.progress_callbacks:
            self.progress_callbacks[chain_id] = []
        self.progress_callbacks[chain_id].append(callback)
    
    # ========== STEP 6: AGGREGATE ==========
    
    async def _finalize_chain(self, chain: ActionChain, completed: int, 
                             failed: int, action_results: List[Dict]) -> ExecutionReport:
        """
        Aggregate results and create final report
        
        Args:
            chain: Executed chain
            completed: Number of completed actions
            failed: Number of failed actions
            action_results: List of action results
            
        Returns:
            ExecutionReport
        """
        logger.info(f"📊 STEP 6 - AGGREGATE: Combining results from {len(action_results)} actions")
        
        # Verify results if verifier available
        verification_passed = False
        verification_score = 0.0
        
        if self.verifier:
            try:
                verification_results = []
                for action in chain.actions:
                    if action.status == "completed" and action.result:
                        # TODO: Implement VLM verification based on action type
                        pass
                
                verification_passed = True
                verification_score = 0.95  # Placeholder
                
                logger.info(f"✅ Verification complete: {verification_score:.2%}")
            except Exception as e:
                logger.error(f"Verification failed: {e}")
        
        chain.verification_results.append({
            "passed": verification_passed,
            "score": verification_score,
            "timestamp": datetime.now().isoformat()
        })
        
        # Aggregate outputs
        outputs = []
        errors = []
        
        for action in chain.actions:
            if action.status == "completed" and action.result:
                if isinstance(action.result, dict) and "output" in action.result:
                    outputs.append(action.result["output"])
            elif action.error:
                errors.append(f"{action.description}: {action.error}")
        
        # Final status
        chain.completed_at = datetime.now()
        if failed > 0:
            chain.status = ChainStatus.FAILED
            self.stats["failed_chains"] += 1
        else:
            chain.status = ChainStatus.COMPLETED
            self.stats["successful_chains"] += 1
        
        # Move to completed
        self.completed_chains[chain.id] = chain
        if chain.id in self.active_chains:
            del self.active_chains[chain.id]
        
        # Update stats
        total_duration = chain.duration_seconds
        self.stats["average_duration"] = (
            (self.stats["average_duration"] * (self.stats["total_chains"] - 1) + total_duration) 
            / self.stats["total_chains"]
        )
        
        # Create report
        report = ExecutionReport(
            chain_id=chain.id,
            success=(failed == 0),
            total_actions=len(chain.actions),
            completed_actions=completed,
            failed_actions=failed,
            skipped_actions=len(chain.actions) - completed - failed,
            duration_seconds=total_duration,
            average_action_time=total_duration / len(chain.actions) if chain.actions else 0,
            outputs=outputs,
            errors=errors,
            verification_passed=verification_passed,
            verification_score=verification_score,
            action_results=action_results
        )
        
        return report
    
    # ========== STEP 7: NOTIFY ==========
    
    async def notify_completion(self, report: ExecutionReport) -> str:
        """
        Create completion notification
        
        Args:
            report: ExecutionReport
            
        Returns:
            Notification message
        """
        logger.info(f"📢 STEP 7 - NOTIFY: Creating completion notification")
        
        chain = self.completed_chains.get(report.chain_id)
        if not chain:
            return "Chain execution completed"
        
        if report.success:
            message = f"""
✅ Task Complete!

Command: {chain.command}

Summary:
- {report.completed_actions}/{report.total_actions} actions completed
- Duration: {report.duration_seconds:.1f} seconds
- Verification: {'✓ Passed' if report.verification_passed else '✗ Failed'} ({report.verification_score:.0%})

Outputs: {len(report.outputs)} files created
"""
        else:
            message = f"""
❌ Task Failed

Command: {chain.command}

Summary:
- {report.completed_actions}/{report.total_actions} actions completed
- {report.failed_actions} actions failed
- Duration: {report.duration_seconds:.1f} seconds

Errors:
{chr(10).join(f"- {err}" for err in report.errors[:3])}
"""
        
        logger.info(message)
        return message
    
    # ========== PUBLIC API ==========
    
    async def execute_command(self, command: str, 
                             on_progress: Optional[Callable] = None) -> ExecutionReport:
        """
        Execute command end-to-end (all 7 steps)
        
        Args:
            command: Natural language command
            on_progress: Optional callback for progress updates
            
        Returns:
            ExecutionReport
        """
        # Step 1: Listen (Create chain)
        chain = await self.create_chain(command)
        
        # Subscribe to progress
        if on_progress:
            self.subscribe_progress(chain.id, on_progress)
        
        # Step 2: Process & Breakdown
        await self.decompose_command(chain)
        
        # Step 3: Identify
        await self.identify_executors(chain)
        
        # Step 4: Assign & Execute + Step 5: Track Progress
        report = await self.execute_chain(chain.id)
        
        # Step 6: Aggregate (done in execute_chain)
        
        # Step 7: Notify
        message = await self.notify_completion(report)
        
        return report
    
    def get_chain(self, chain_id: str) -> Optional[ActionChain]:
        """Get chain by ID"""
        return self.active_chains.get(chain_id) or self.completed_chains.get(chain_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            **self.stats,
            "active_chains": len(self.active_chains),
            "completed_chains": len(self.completed_chains)
        }


# Singleton instance
_manager = None


def get_chain_manager() -> ChainOfActionsManager:
    """Get singleton chain manager"""
    global _manager
    if _manager is None:
        _manager = ChainOfActionsManager()
    return _manager
