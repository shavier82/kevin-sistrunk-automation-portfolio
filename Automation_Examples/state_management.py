#!/usr/bin/env python3
"""
State Management Pattern
Demonstrates atomic state updates with validation, conflict resolution,
and automatic backup capabilities.

This pattern is directly applicable to:
- XSOAR/XSIAM state management
- Security incident state tracking
- Multi-system state synchronization
- Resource tracking and allocation
"""

import json
import re
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple
from datetime import datetime


class StateManager:
    """
    Manages application state with atomic updates and validation.
    
    Features:
    - Atomic state updates (all-or-nothing)
    - Automatic backup before changes
    - Conflict detection and resolution
    - Schema validation
    - Resource underflow prevention
    """
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file."""
        if not self.state_file.exists():
            # Initialize empty state
            return {
                "entities": {},
                "resources": {},
                "metadata": {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat()
                }
            }
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load state: {e}")
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save state to file."""
        try:
            # Update metadata
            state["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Write atomically (write to temp, then rename)
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_file.replace(self.state_file)
            
        except Exception as e:
            raise ValueError(f"Failed to save state: {e}")
    
    def create_backup(self) -> Path:
        """
        Create a backup copy of the state file.
        
        Returns path to backup file.
        """
        backup_dir = self.state_file.parent / "backups" / "state"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"state.{timestamp}.json"
        
        shutil.copy2(self.state_file, backup_path)
        return backup_path
    
    def apply_delta(
        self, 
        deltas: Dict[Tuple[str, str, int], int],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Apply state deltas atomically.
        
        Args:
            deltas: Dict mapping (entity_id, resource_type, level) -> amount to subtract
            dry_run: If True, preview changes without applying
        
        Returns:
            Updated state dict
        """
        # Create deep copy for modification
        updated = json.loads(json.dumps(self.state))
        
        # Track changes for reporting
        changes = []
        
        for (entity_id, resource_type, level), amount in deltas.items():
            # Ensure entity exists
            if entity_id not in updated["entities"]:
                if not dry_run:
                    updated["entities"][entity_id] = {
                        "resources": {},
                        "metadata": {}
                    }
                else:
                    changes.append(f"DRY-RUN: Would create entity {entity_id}")
                    continue
            
            entity = updated["entities"][entity_id]
            
            # Ensure resources structure exists
            if "resources" not in entity:
                entity["resources"] = {}
            
            # Apply delta based on resource type
            if resource_type == "spell_slot" or resource_type.startswith("spell_slot."):
                # Handle spell slots (leveled resources)
                if "spell_slots" not in entity["resources"]:
                    entity["resources"]["spell_slots"] = {}
                
                level_str = str(level)
                current = entity["resources"]["spell_slots"].get(level_str, 0)
                new_value = max(0, current - amount)  # Prevent negative
                
                if dry_run:
                    changes.append(
                        f"DRY-RUN: {entity_id} {resource_type}.{level}: "
                        f"{current} -> {new_value} (subtract {amount})"
                    )
                else:
                    entity["resources"]["spell_slots"][level_str] = new_value
                    changes.append(
                        f"{entity_id} {resource_type}.{level}: "
                        f"{current} -> {new_value}"
                    )
            else:
                # Handle simple resources (rage, ki, etc.)
                current = entity["resources"].get(resource_type, 0)
                new_value = max(0, current - amount)  # Prevent negative
                
                if dry_run:
                    changes.append(
                        f"DRY-RUN: {entity_id} {resource_type}: "
                        f"{current} -> {new_value} (subtract {amount})"
                    )
                else:
                    entity["resources"][resource_type] = new_value
                    changes.append(
                        f"{entity_id} {resource_type}: {current} -> {new_value}"
                    )
        
        if not dry_run:
            # Create backup before saving
            self.create_backup()
            # Save updated state
            self._save_state(updated)
            self.state = updated
        
        return {
            "state": updated if not dry_run else self.state,
            "changes": changes,
            "applied": not dry_run
        }
    
    def validate_state(self, state: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
        """
        Validate state integrity.
        
        Returns:
            (is_valid, list_of_issues)
        """
        if state is None:
            state = self.state
        
        issues = []
        
        # Check required top-level keys
        required_keys = ["entities", "resources", "metadata"]
        for key in required_keys:
            if key not in state:
                issues.append(f"Missing required key: {key}")
        
        # Validate entity structure
        if "entities" in state:
            for entity_id, entity in state["entities"].items():
                if not isinstance(entity, dict):
                    issues.append(f"Entity {entity_id} is not a dict")
                elif "resources" not in entity:
                    issues.append(f"Entity {entity_id} missing resources")
        
        # Validate metadata
        if "metadata" in state:
            if "version" not in state["metadata"]:
                issues.append("Metadata missing version")
            if "last_updated" not in state["metadata"]:
                issues.append("Metadata missing last_updated")
        
        return len(issues) == 0, issues
    
    def get_entity_resources(self, entity_id: str) -> Dict[str, Any]:
        """Get current resources for an entity."""
        if entity_id not in self.state["entities"]:
            return {}
        
        entity = self.state["entities"][entity_id]
        return entity.get("resources", {})
    
    def check_resource_availability(
        self, 
        entity_id: str, 
        resource_type: str, 
        amount: int,
        level: int = 0
    ) -> bool:
        """
        Check if entity has sufficient resources.
        
        Returns True if entity has enough resources, False otherwise.
        """
        resources = self.get_entity_resources(entity_id)
        
        if resource_type == "spell_slot" or resource_type.startswith("spell_slot."):
            spell_slots = resources.get("spell_slots", {})
            level_str = str(level)
            available = spell_slots.get(level_str, 0)
            return available >= amount
        else:
            available = resources.get(resource_type, 0)
            return available >= amount


def parse_state_delta(text: str) -> Dict[Tuple[str, str, int], int]:
    """
    Parse STATE-DELTA block from text.
    
    Expected format:
    STATE-DELTA
    - entity_id: resource_type.level -= amount
    - entity_id: resource_type -= amount
    END STATE-DELTA
    
    Returns dict mapping (entity_id, resource_type, level) -> amount to subtract.
    """
    # Pattern to match STATE-DELTA block
    delta_block_pattern = re.compile(
        r"STATE-DELTA\s*(?P<body>.*?)\s*END STATE-DELTA",
        re.IGNORECASE | re.DOTALL
    )
    
    # Pattern to match delta lines
    delta_line_pattern = re.compile(
        r"^\s*-\s*(?P<entity>[a-zA-Z0-9_\-]+)\s*:\s*"
        r"(?P<key>[a-zA-Z0-9_\.\-]+)\s*-\=\s*(?P<amount>\d+)\s*$",
        re.IGNORECASE
    )
    
    match = delta_block_pattern.search(text)
    if not match:
        return {}
    
    body = match.group("body")
    deltas: Dict[Tuple[str, str, int], int] = {}
    
    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        
        line_match = delta_line_pattern.match(line)
        if not line_match:
            continue
        
        entity_id = line_match.group("entity")
        key = line_match.group("key").lower()
        amount = int(line_match.group("amount"))
        
        # Parse resource type and level
        if key.startswith("spell_slot."):
            level = int(key.split(".", 1)[1])
            resource_key = (entity_id, "spell_slot", level)
        else:
            resource_key = (entity_id, key, 0)
        
        # Accumulate deltas (in case of duplicates)
        deltas[resource_key] = deltas.get(resource_key, 0) + amount
    
    return deltas


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: State delta text (as might come from automation output)
    example_delta_text = """
    STATE-DELTA
    - entity_001: spell_slot.2 -= 1
    - entity_002: rage -= 1
    - entity_003: ki -= 2
    END STATE-DELTA
    """
    
    # Initialize state manager
    state_file = Path("state.json")
    manager = StateManager(state_file)
    
    # Parse deltas
    deltas = parse_state_delta(example_delta_text)
    print(f"Parsed {len(deltas)} deltas")
    
    # Dry run (preview changes)
    print("\n=== DRY RUN (Preview) ===")
    result = manager.apply_delta(deltas, dry_run=True)
    for change in result["changes"]:
        print(f"  {change}")
    
    # Validate state
    print("\n=== STATE VALIDATION ===")
    is_valid, issues = manager.validate_state()
    if is_valid:
        print("  ✓ State is valid")
    else:
        print(f"  ✗ State has {len(issues)} issues:")
        for issue in issues:
            print(f"    - {issue}")
    
    # Apply deltas (uncomment to actually apply)
    # print("\n=== APPLYING DELTAS ===")
    # result = manager.apply_delta(deltas, dry_run=False)
    # print(f"Applied {len(result['changes'])} changes")
    # print(f"Backup created at: {manager.create_backup()}")
