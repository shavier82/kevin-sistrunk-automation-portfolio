"""
Parallel Processing Pattern
Demonstrates multi-agent parallel execution system for sub-5-second workflow processing.

This pattern is directly applicable to:
- XSOAR/XSIAM playbook execution
- Security incident response automation
- Multi-step workflow processing
- Real-time event processing
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class ParallelAgentSystem:
    """
    Parallel agent execution system for fast workflow processing.
    
    Architecture:
    - 4 specialized agents execute in parallel
    - Each agent handles a specific responsibility
    - Results are merged into final output
    - Sub-5-second execution time target
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete workflow using parallel agents.
        
        Returns merged results from all agents.
        """
        # Execute all agents in parallel
        results = await asyncio.gather(
            self._referee_agent(input_data),
            self._narrator_agent(input_data),
            self._state_patcher_agent(input_data),
            self._qa_compliance_agent(input_data),
            return_exceptions=True
        )
        
        # Unpack results
        referee_result, narrator_result, state_patcher_result, qa_result = results
        
        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                agent_names = ["REFEREE", "NARRATOR", "STATE_PATCHER", "QA_COMPLIANCE"]
                raise RuntimeError(f"{agent_names[i]} agent failed: {result}")
        
        # Merge results
        return self._merge_results(
            referee_result,
            narrator_result,
            state_patcher_result,
            qa_result
        )
    
    async def _referee_agent(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        REFEREE Agent: Validates rules and calculates outcomes.
        
        Responsibilities:
        - Validate business rules
        - Calculate outcomes
        - Determine success/failure
        - Request additional data if needed
        """
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Example: Validate action
        action = input_data.get("action", {})
        action_type = action.get("type", "unknown")
        
        # Calculate outcome
        outcome = {
            "valid": True,
            "result": 15,  # Simulated calculation
            "threshold": 10,
            "success": True
        }
        
        return {
            "agent_role": "REFEREE",
            "blocked": False,
            "outcome": outcome,
            "roll_request": None  # No roll needed if outcome calculated
        }
    
    async def _narrator_agent(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        NARRATOR Agent: Generates human-readable output.
        
        Responsibilities:
        - Generate descriptive text
        - Create user-facing messages
        - Suggest next actions
        """
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        action = input_data.get("action", {})
        action_type = action.get("type", "unknown")
        
        # Generate narration
        narration = (
            f"Processing {action_type} action. "
            f"The system validates the request and executes the workflow. "
            f"All checks passed successfully."
        )
        
        # Suggest actions
        suggested_actions = [
            "Review the results",
            "Proceed to next step",
            "Check system status"
        ]
        
        return {
            "agent_role": "NARRATOR",
            "blocked": False,
            "narration": narration,
            "suggested_actions": suggested_actions
        }
    
    async def _state_patcher_agent(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        STATE_PATCHER Agent: Updates system state atomically.
        
        Responsibilities:
        - Generate state patches
        - Track resource consumption
        - Update entity status
        - Ensure atomicity
        """
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        action = input_data.get("action", {})
        entity_id = action.get("entity_id", "unknown")
        
        # Generate state patches (JSON Patch format)
        patches = [
            {
                "op": "replace",
                "path": f"/entities/{entity_id}/status",
                "value": "processed"
            },
            {
                "op": "add",
                "path": f"/entities/{entity_id}/last_updated",
                "value": datetime.now().isoformat()
            }
        ]
        
        return {
            "agent_role": "STATE_PATCHER",
            "blocked": False,
            "patches": patches
        }
    
    async def _qa_compliance_agent(
        self, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        QA_COMPLIANCE Agent: Validates output format and compliance.
        
        Responsibilities:
        - Validate output schemas
        - Check guardrail compliance
        - Flag format issues
        - Ensure data integrity
        """
        # Simulate processing time
        await asyncio.sleep(0.05)  # QA is fastest
        
        # Validate input
        issues = []
        
        if "action" not in input_data:
            issues.append("Missing action in input")
        
        if issues:
            return {
                "agent_role": "QA_COMPLIANCE",
                "blocked": True,
                "status": "failed",
                "issues": issues
            }
        
        return {
            "agent_role": "QA_COMPLIANCE",
            "blocked": False,
            "status": "ok",
            "issues": []
        }
    
    def _merge_results(
        self,
        referee_result: Dict[str, Any],
        narrator_result: Dict[str, Any],
        state_patcher_result: Dict[str, Any],
        qa_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge results from all agents into final output.
        
        Handles:
        - Block propagation (if any agent blocks, output is blocked)
        - Format composition
        - Error handling
        """
        # Check for blocks
        if (referee_result.get("blocked") or 
            narrator_result.get("blocked") or 
            state_patcher_result.get("blocked") or 
            qa_result.get("blocked")):
            return {
                "blocked": True,
                "reason": "One or more agents blocked execution"
            }
        
        # Check QA status
        if qa_result.get("status") != "ok":
            return {
                "blocked": True,
                "reason": f"QA validation failed: {qa_result.get('issues', [])}"
            }
        
        # Compose final output
        return {
            "blocked": False,
            "final": {
                "NARRATION": narrator_result.get("narration", "(none)"),
                "ASK": self._build_ask(referee_result),
                "ACTIONS": narrator_result.get("suggested_actions", []),
                "PATCH": state_patcher_result.get("patches", [])
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "agents": ["REFEREE", "NARRATOR", "STATE_PATCHER", "QA_COMPLIANCE"]
            }
        }
    
    def _build_ask(self, referee_result: Dict[str, Any]) -> str:
        """Build ASK block from referee roll request."""
        roll_request = referee_result.get("roll_request")
        if not roll_request or not roll_request.get("required"):
            return "(none)"
        
        skill = roll_request.get("skill_or_check", "check")
        dc = roll_request.get("dc", 0)
        formula = roll_request.get("formula", "1d20")
        
        if dc > 0:
            return f"Roll {skill} vs DC {dc}. (Formula: {formula})"
        else:
            return f"Roll {skill}. (Formula: {formula})"
    
    def save_agent_outputs(
        self,
        referee_result: Dict[str, Any],
        narrator_result: Dict[str, Any],
        state_patcher_result: Dict[str, Any],
        qa_result: Dict[str, Any]
    ) -> None:
        """Save individual agent outputs to files (for debugging/audit)."""
        outputs = {
            "REFEREE": referee_result,
            "NARRATOR": narrator_result,
            "STATE_PATCHER": state_patcher_result,
            "QA_COMPLIANCE": qa_result
        }
        
        for agent_name, output in outputs.items():
            output_file = self.output_dir / f"output_{agent_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2)


# ============================================================================
# SYNCHRONOUS WRAPPER (for PowerShell/script integration)
# ============================================================================

def execute_workflow_sync(input_data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    Synchronous wrapper for parallel agent execution.
    
    Useful for integration with PowerShell scripts or other non-async contexts.
    """
    system = ParallelAgentSystem(output_dir)
    
    # Run async function in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(system.execute_workflow(input_data))
        return result
    finally:
        loop.close()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage of parallel agent system."""
    
    # Example input data
    input_data = {
        "action": {
            "type": "validate_entity",
            "entity_id": "entity_001",
            "parameters": {
                "threshold": 10
            }
        }
    }
    
    # Initialize system
    output_dir = Path("output")
    system = ParallelAgentSystem(output_dir)
    
    # Execute workflow
    print("Executing parallel workflow...")
    start_time = datetime.now()
    
    result = await system.execute_workflow(input_data)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\nWorkflow completed in {duration:.2f} seconds")
    print(f"Blocked: {result.get('blocked', False)}")
    
    if not result.get("blocked"):
        final = result.get("final", {})
        print(f"\nNARRATION:\n{final.get('NARRATION')}")
        print(f"\nASK:\n{final.get('ASK')}")
        print(f"\nACTIONS:")
        for action in final.get("ACTIONS", []):
            print(f"  - {action}")
        print(f"\nPATCH: {len(final.get('PATCH', []))} patches generated")


if __name__ == "__main__":
    asyncio.run(main())
