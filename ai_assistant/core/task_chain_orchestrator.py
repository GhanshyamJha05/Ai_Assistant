"""
Task Chain Orchestrator
Executes multi-step task chains with state management, error handling, and context awareness.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ai_assistant.ai.multi_step_parser import TaskStep, MultiStepCommandParser
from ai_assistant.core.conversation_context import ContextManager, ExecutionState, get_context_manager
from ai_assistant.core.universal_app_controller import UniversalAppController, get_universal_controller

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of task chain execution."""
    success: bool
    steps_completed: int
    total_steps: int
    results: List[Dict[str, Any]]
    error: Optional[str] = None
    message: str = ""


class TaskChainOrchestrator:
    """
    Orchestrates execution of multi-step task chains.
    
    Features:
    - State machine (IDLE → PARSING → EXECUTING → COMPLETE)
    - Dependency resolution
    - Context passing between steps
    - Error handling and rollback
    - Mid-task override support
    
    Usage:
        orchestrator = TaskChainOrchestrator()
        
        result = orchestrator.execute_command(
            "WhatsApp खोलो, मॉम को message करो कि hello"
        )
    """
    
    def __init__(self,
                 context_manager: ContextManager = None,
                 app_controller: UniversalAppController = None,
                 parser: MultiStepCommandParser = None):
        """
        Initialize orchestrator.
        
        Args:
            context_manager: Context manager (optional, will create default)
            app_controller: App controller (optional, will create default)
            parser: Command parser (optional, will create default)
        """
        self.context_manager = context_manager or get_context_manager()
        self.app_controller = app_controller or get_universal_controller()
        self.parser = parser or MultiStepCommandParser()
        
        logger.info("Task Chain Orchestrator initialized")
    
    # ===== MAIN EXECUTION METHODS =====
    
    def execute_command(self, command: str) -> ExecutionResult:
        """
        Execute a command (single or multi-step).
        
        This is the MAIN entry point for command execution.
        
        Args:
            command: User command
        
        Returns:
            ExecutionResult with status and details
        """
        logger.info(f"Executing command: {command}")
        
        try:
            # Check for override
            if self.context_manager.is_override(command):
                self.context_manager.handle_override(command)
                logger.info("Override detected, handling...")
            
            # Parse command
            self.context_manager.set_state(ExecutionState.PARSING)
            steps = self.parser.parse_command(command)
            
            logger.info(f"Parsed {len(steps)} steps")
            
            # Execute task chain
            result = self.execute_chain(steps)
            
            # Add to history
            self.context_manager.add_command(
                command,
                intent=steps[0].intent if steps else 'unknown',
                completed=result.success
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Command execution failed: {e}", exc_info=True)
            self.context_manager.set_state(ExecutionState.ERROR)
            
            return ExecutionResult(
                success=False,
                steps_completed=0,
                total_steps=0,
                results=[],
                error=str(e),
                message=f"Failed to execute command: {e}"
            )
    
    def execute_chain(self, steps: List[TaskStep]) -> ExecutionResult:
        """
        Execute a chain of task steps.
        
        Args:
            steps: List of TaskStep objects
        
        Returns:
            ExecutionResult
        """
        logger.info(f"Executing chain of {len(steps)} steps")
        
        # Save task chain to context
        self.context_manager.set_task_chain([
            {
                'step': s.step,
                'intent': s.intent,
                'params': s.params,
                'dependencies': s.dependencies
            }
            for s in steps
        ])
        
        self.context_manager.set_state(ExecutionState.EXECUTING)
        
        results = []
        steps_completed = 0
        
        try:
            for step in steps:
                logger.info(f"Executing step {step.step}/{len(steps)}: {step.intent}")
                
                # Check dependencies
                if not self._check_dependencies(step, results):
                    error_msg = f"Dependencies not met for step {step.step}"
                    logger.error(error_msg)
                    return ExecutionResult(
                        success=False,
                        steps_completed=steps_completed,
                        total_steps=len(steps),
                        results=results,
                        error=error_msg
                    )
                
                # Execute step
                step_result = self.execute_step(step)
                results.append(step_result)
                
                if step_result['success']:
                    steps_completed += 1
                    self.context_manager.advance_step()
                else:
                    # Step failed
                    logger.error(f"Step {step.step} failed: {step_result.get('error')}")
                    
                    # Try to rollback
                    self._rollback_steps(results[:-1])
                    
                    return ExecutionResult(
                        success=False,
                        steps_completed=steps_completed,
                        total_steps=len(steps),
                        results=results,
                        error=step_result.get('error'),
                        message=f"Failed at step {step.step}: {step_result.get('error')}"
                    )
            
            # All steps completed successfully
            self.context_manager.set_state(ExecutionState.COMPLETE)
            self.context_manager.clear_task_chain()
            
            return ExecutionResult(
                success=True,
                steps_completed=steps_completed,
                total_steps=len(steps),
                results=results,
                message=f"Successfully completed {steps_completed} steps!"
            )
        
        except Exception as e:
            logger.error(f"Chain execution failed: {e}", exc_info=True)
            self.context_manager.set_state(ExecutionState.ERROR)
            
            return ExecutionResult(
                success=False,
                steps_completed=steps_completed,
                total_steps=len(steps),
                results=results,
                error=str(e)
            )
    
    def execute_step(self, step: TaskStep) -> Dict[str, Any]:
        """
        Execute a single task step.
        
        Args:
            step: TaskStep to execute
        
        Returns:
            Dict with execution result
        """
        logger.debug(f"Executing step: {step.intent} with params: {step.params}")
        
        try:
            # Infer missing parameters from context
            params = self.context_manager.infer_missing_params(step.intent, step.params)
            
            # Map intent to action
            if step.intent == 'open_app':
                app_name = params.get('app_name') or params.get('app')
                if not app_name:
                    return {
                        'success': False,
                        'step': step.step,
                        'intent': step.intent,
                        'error': 'No app name provided'
                    }
                
                result = self.app_controller.open_app(app_name)
                
                # Update context
                if result['success']:
                    self.context_manager.set_var('current_app', app_name.lower())
                    self.context_manager.set_var('last_action', 'opened_app')
                
                return {
                    'success': result['success'],
                    'step': step.step,
                    'intent': step.intent,
                    'result': result
                }
            
            elif step.intent == 'send_message':
                app_name = params.get('app_name', self.context_manager.get_var('current_app', 'WhatsApp'))
                contact = params.get('contact')
                message = params.get('message', '')
                
                if not contact:
                    return {
                        'success': False,
                        'step': step.step,
                        'intent': step.intent,
                        'error': 'No contact specified'
                    }
                
                result = self.app_controller.execute_action(app_name, 'send_message', {
                    'contact': contact,
                    'message': message
                })
                
                # Update context
                if result['success']:
                    self.context_manager.set_var('selected_contact', contact)
                    self.context_manager.set_var('last_message', message)
                    self.context_manager.set_var('last_action', 'sent_message')
                
                return {
                    'success': result.get('success', False),
                    'step': step.step,
                    'intent': step.intent,
                    'result': result
                }
            
            elif step.intent == 'type_text':
                app_name = params.get('app_name', self.context_manager.get_var('current_app'))
                text = params.get('text', '')
                
                if not app_name:
                    return {
                        'success': False,
                        'step': step.step,
                        'intent': step.intent,
                        'error': 'No app specified and no current app in context'
                    }
                
                result = self.app_controller.execute_action(app_name, 'type_text', {
                    'text': text
                })
                
                return {
                    'success': result.get('success', False),
                    'step': step.step,
                    'intent': step.intent,
                    'result': result
                }
            
            elif step.intent == 'play_video':
                app_name = params.get('app_name', 'YouTube')
                query = params.get('query', '')
                
                result = self.app_controller.execute_action(app_name, 'play_video', {
                    'query': query
                })
                
                return {
                    'success': result.get('success', False),
                    'step': step.step,
                    'intent': step.intent,
                    'result': result
                }
            
            elif step.intent == 'skip_time':
                app_name = params.get('app_name', self.context_manager.get_var('current_app', 'YouTube'))
                minutes = params.get('minutes', 0)
                
                result = self.app_controller.execute_action(app_name, 'skip_time', {
                    'minutes': minutes
                })
                
                return {
                    'success': result.get('success', False),
                    'step': step.step,
                    'intent': step.intent,
                    'result': result
                }
            
            else:
                # Unknown intent - try generic execution
                logger.warning(f"Unknown intent: {step.intent}, trying generic execution")
                
                return {
                    'success': False,
                    'step': step.step,
                    'intent': step.intent,
                    'error': f"Unknown intent: {step.intent}"
                }
        
        except Exception as e:
            logger.error(f"Step execution failed: {e}", exc_info=True)
            return {
                'success': False,
                'step': step.step,
                'intent': step.intent,
                'error': str(e)
            }
    
    # ===== DEPENDENCY MANAGEMENT =====
    
    def _check_dependencies(self, step: TaskStep, previous_results: List[Dict]) -> bool:
        """
        Check if step dependencies are met.
        
        Args:
            step: Step to check
            previous_results: Results from previous steps
        
        Returns:
            True if dependencies met, False otherwise
        """
        if not step.dependencies:
            return True
        
        for dep_step_num in step.dependencies:
            # Find result for this dependency
            dep_result = next((r for r in previous_results if r.get('step') == dep_step_num), None)
            
            if not dep_result or not dep_result.get('success'):
                logger.warning(f"Dependency step {dep_step_num} not successful")
                return False
        
        return True
    
    # ===== ERROR HANDLING =====
    
    def _rollback_steps(self, results: List[Dict]):
        """
        Attempt to rollback executed steps.
        
        Currently just logs - full rollback would require action-specific undo logic.
        """
        logger.info(f"Attempting rollback of {len(results)} steps")
        
        # For now, just clear context
        # Full rollback would require each action to support undo
        self.context_manager.set_var('last_action', 'rolled_back')
    
    # ===== OVERRIDE HANDLING =====
    
    def handle_override(self, new_command: str) -> ExecutionResult:
        """
        Handle a command override during execution.
        
        Args:
            new_command: New command that overrides current execution
        
        Returns:
            ExecutionResult for new command
        """
        logger.warning(f"Handling override: {new_command}")
        
        # Context manager already handled the override detection
        # Just execute the new command
        return self.execute_command(new_command)
    
    # ===== STATUS & MONITORING =====
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        context_summary = self.context_manager.get_summary()
        
        return {
            'state': context_summary['state'],
            'current_step': context_summary['current_step'],
            'active_apps': self.app_controller.get_active_apps(),
            'context_vars': context_summary['key_vars'],
        }
    
    def pause(self):
        """Pause current execution."""
        self.context_manager.set_state(ExecutionState.PAUSED)
        logger.info("Execution paused")
    
    def resume(self):
        """Resume paused execution."""
        if self.context_manager.get_state() == ExecutionState.PAUSED:
            self.context_manager.set_state(ExecutionState.EXECUTING)
            logger.info("Execution resumed")
    
    def cancel(self):
        """Cancel current execution."""
        self.context_manager.clear_task_chain()
        self.context_manager.set_state(ExecutionState.IDLE)
        logger.info("Execution cancelled")


# Singleton instance
_orchestrator = None

def get_orchestrator() -> TaskChainOrchestrator:
    """Get singleton orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TaskChainOrchestrator()
    return _orchestrator
