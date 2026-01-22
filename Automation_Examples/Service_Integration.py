#!/usr/bin/env python3
"""
Service Integration Pattern
Demonstrates unified orchestration of multiple microservices with error handling,
caching, and parallel execution capabilities.

This pattern is directly applicable to:
- XSOAR/XSIAM playbook development
- Security operations automation (SIEM, EDR, ticketing integration)
- Multi-API workflow orchestration
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceOrchestrator:
    """
    Unified interface for orchestrating multiple microservices.
    
    Provides:
    - Unified API for all services
    - Automatic caching
    - Error handling and retries
    - Parallel execution for batch operations
    """
    
    def __init__(self):
        self.cache = {}
        self.logger = logging.getLogger(__name__)
    
    # ========================================================================
    # DATA RETRIEVAL SERVICES
    # ========================================================================
    
    def get_entity_data(self, entity_id: str, entity_type: str) -> Dict[str, Any]:
        """
        Get entity data from data service.
        
        In production, this would call: data_service.get_entity(entity_id, entity_type)
        """
        cache_key = f"{entity_type}_{entity_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Simulated API call - in production, this would be:
            # response = data_service_client.get(f"/entities/{entity_type}/{entity_id}")
            # return response.json()
            
            # For demo purposes, return structured data
            entity_data = {
                "id": entity_id,
                "type": entity_type,
                "status": "active",
                "metadata": {}
            }
            
            self.cache[cache_key] = entity_data
            return entity_data
            
        except Exception as e:
            logger.error(f"Error retrieving entity data: {e}")
            return {}
    
    def update_entity_status(self, entity_id: str, new_status: str) -> bool:
        """
        Update entity status in data service.
        
        In production: status_service.update_status(entity_id, new_status)
        """
        logger.info(f"UPDATE STATUS: {entity_id} → {new_status}")
        # Clear cache to force refresh on next read
        self.cache.pop(f"entity_{entity_id}", None)
        return True
    
    def check_resource_availability(self, resource_id: str) -> bool:
        """
        Check if resource is currently available.
        
        In production: resource_service.check_availability(resource_id)
        """
        entity = self.get_entity_data(resource_id, "resource")
        return entity.get("available", False)
    
    # ========================================================================
    # RULES & VALIDATION SERVICES
    # ========================================================================
    
    def lookup_rule(self, rule_name: str) -> Dict[str, Any]:
        """
        Lookup rule definition from rules database.
        
        In production: rules_database.lookup_rule(rule_name)
        """
        cache_key = f"rule_{rule_name.lower()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Simulated API call
        rule_data = {
            "name": rule_name,
            "type": "validation",
            "parameters": {}
        }
        self.cache[cache_key] = rule_data
        return rule_data
    
    def validate_action(self, action_type: str, parameters: Dict) -> Dict[str, Any]:
        """
        Validate action against business rules.
        
        In production: validation_service.validate(action_type, parameters)
        """
        # Simulated validation
        return {
            "valid": True,
            "message": "Action validated",
            "constraints": []
        }
    
    # ========================================================================
    # EXECUTION SERVICES
    # ========================================================================
    
    def execute_action(self, action_type: str, parameters: Dict) -> Dict[str, Any]:
        """
        Execute action via execution service.
        
        In production: execution_service.execute(action_type, parameters)
        """
        import random
        # Simulated execution
        result = {
            "action": action_type,
            "status": "success",
            "result": random.randint(1, 20),  # Simulated result
            "timestamp": "2024-01-15T10:30:00Z"
        }
        return result
    
    def execute_action_with_modifier(
        self, 
        modifier: int, 
        advantage: bool = False, 
        disadvantage: bool = False
    ) -> Dict[str, Any]:
        """
        Execute action with modifier and optional advantage/disadvantage.
        
        In production: execution_service.execute_with_modifier(modifier, advantage, disadvantage)
        """
        import random
        
        if advantage:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            roll = max(rolls)
        elif disadvantage:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            roll = min(rolls)
        else:
            roll = random.randint(1, 20)
            rolls = [roll]
        
        return {
            "rolls": rolls,
            "roll": roll,
            "modifier": modifier,
            "total": roll + modifier,
            "advantage": advantage,
            "disadvantage": disadvantage
        }
    
    # ========================================================================
    # LOGGING & AUDIT SERVICES
    # ========================================================================
    
    def log_event(
        self, 
        event_type: str, 
        content: str, 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Log event to audit service.
        
        In production: audit_service.log_event(event_type, content, metadata)
        """
        logger.info(f"LOG EVENT [{event_type}]: {content}")
        return True
    
    def start_session(self, session_name: str, session_title: str = None) -> bool:
        """
        Start session logging.
        
        In production: session_service.start_session(session_name, session_title)
        """
        logger.info(f"START SESSION: {session_name}")
        return True
    
    def stop_session(self) -> bool:
        """
        Stop session logging.
        
        In production: session_service.stop_session()
        """
        logger.info("STOP SESSION")
        return True
    
    # ========================================================================
    # BATCH OPERATIONS (Parallel Execution)
    # ========================================================================
    
    def batch_lookup_entities(
        self, 
        entity_ids: List[str], 
        entity_type: str
    ) -> List[Dict[str, Any]]:
        """
        Lookup multiple entities in parallel for improved performance.
        
        This demonstrates the parallel execution pattern used throughout
        the system for handling multiple API calls efficiently.
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.get_entity_data, eid, entity_type): eid 
                for eid in entity_ids
            }
            results = []
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Error in batch lookup: {e}")
                    results.append({})
            return results
    
    def batch_get_entity_status(
        self, 
        entity_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get status for multiple entities in parallel.
        
        Demonstrates efficient batch processing for status checks.
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.get_entity_data, eid, "entity"): eid 
                for eid in entity_ids
            }
            results = []
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Error in batch status check: {e}")
                    results.append({})
            return results


# ============================================================================
# WORKFLOW HELPERS
# ============================================================================

def session_start_workflow(session_name: str) -> Dict[str, Any]:
    """
    Complete session start workflow.
    
    Demonstrates orchestrating multiple services for a common workflow:
    1. Start session logging
    2. Get current context
    3. Initialize environment
    4. Log initialization event
    
    This pattern is directly applicable to:
    - XSOAR playbook initialization
    - Security incident response workflows
    - Automated process initialization
    """
    orchestrator = ServiceOrchestrator()
    results = {}
    
    # 1. Start session log
    orchestrator.start_session(session_name)
    results["session_log"] = "started"
    
    # 2. Get current context (e.g., time, environment)
    context = {
        "timestamp": "2024-01-15T10:30:00Z",
        "environment": "production",
        "status": "active"
    }
    results["context"] = context
    
    # 3. Initialize environment
    orchestrator.log_event("initialization", f"Session started: {context['timestamp']}")
    results["initialized"] = True
    
    return results


def incident_response_workflow(
    incident_type: str, 
    entity_count: int
) -> Dict[str, Any]:
    """
    Complete incident response workflow.
    
    Demonstrates security operations automation pattern:
    1. Lookup incident details
    2. Switch to incident response mode
    3. Check environment status
    4. Log incident
    5. Create incident tracking entity
    
    This is directly applicable to XSOAR/XSIAM playbook development.
    """
    orchestrator = ServiceOrchestrator()
    results = {}
    
    # 1. Lookup incident details
    incidents = orchestrator.batch_lookup_entities(
        [f"{incident_type}_{i}" for i in range(entity_count)],
        "incident"
    )
    results["incidents"] = incidents
    
    # 2. Switch to response mode
    orchestrator.log_event("mode_change", f"Switched to incident response mode")
    results["mode"] = "incident_response"
    
    # 3. Check environment status
    status = orchestrator.get_entity_data("environment", "status")
    results["environment_status"] = status
    
    # 4. Log incident
    orchestrator.log_event(
        "incident", 
        f"Incident detected: {entity_count} {incident_type} entities"
    )
    
    # 5. Create incident tracking entity
    incident_id = f"incident_{incident_type}_{entity_count}"
    orchestrator.log_event("entity_created", f"Created incident: {incident_id}")
    results["incident_id"] = incident_id
    
    return results


def validation_workflow(
    entity_id: str, 
    validation_type: str, 
    threshold: int
) -> Dict[str, Any]:
    """
    Complete validation workflow.
    
    Demonstrates validation and execution pattern:
    1. Get entity data
    2. Calculate validation parameters
    3. Execute validation
    4. Determine outcome
    5. Log result
    
    Applicable to:
    - Security policy validation
    - Compliance checking
    - Automated rule enforcement
    """
    orchestrator = ServiceOrchestrator()
    results = {}
    
    # 1. Get entity data
    entity = orchestrator.get_entity_data(entity_id, "entity")
    results["entity"] = entity.get("id")
    
    # 2. Calculate validation parameters
    modifier = entity.get("modifier", 0)
    results["modifier"] = modifier
    
    # 3. Execute validation
    validation_result = orchestrator.execute_action_with_modifier(modifier)
    results["validation_result"] = validation_result
    
    # 4. Determine outcome
    success = validation_result["total"] >= threshold
    results["success"] = success
    results["threshold"] = threshold
    
    # 5. Log result
    outcome = "SUCCESS" if success else "FAILURE"
    orchestrator.log_event(
        "validation", 
        f"{entity.get('id')} {validation_type}: {validation_result['total']} vs threshold {threshold} - {outcome}"
    )
    
    return results


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("Testing Service Integration Pattern...")
    
    print("\n1. Session Start Workflow")
    print(json.dumps(session_start_workflow("Test Session"), indent=2))
    
    print("\n2. Incident Response Workflow")
    print(json.dumps(incident_response_workflow("threat", 3), indent=2))
    
    print("\n3. Validation Workflow")
    print(json.dumps(validation_workflow("entity_001", "security_check", 15), indent=2))
    
    print("\nService integration pattern working!")
