#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rules Manager for Desktop App
Handles CRUD operations for classification rules
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List
import shutil

# Get user data path from environment or use default
USER_DATA_PATH = os.environ.get('USER_DATA_PATH', str(Path.home() / '.90daychonhanh'))
RULES_OVERRIDE_FILE = Path(USER_DATA_PATH) / 'rules_overrides.json'

# Import default rules from rule_classifier
sys.path.insert(0, os.path.dirname(__file__))
from rule_classifier import DOCUMENT_RULES as DEFAULT_RULES


def ensure_user_data_dir():
    """Ensure user data directory exists"""
    Path(USER_DATA_PATH).mkdir(parents=True, exist_ok=True)


def get_rules() -> Dict:
    """
    Get merged rules (default + overrides)
    Returns combined rules with user overrides taking precedence
    """
    ensure_user_data_dir()
    
    # Start with default rules
    merged_rules = dict(DEFAULT_RULES)
    
    # Apply overrides if file exists
    if RULES_OVERRIDE_FILE.exists():
        try:
            with open(RULES_OVERRIDE_FILE, 'r', encoding='utf-8') as f:
                overrides = json.load(f)
                
            # Merge overrides into default rules
            for doc_type, rule_data in overrides.items():
                if doc_type in merged_rules:
                    # Update existing rule
                    merged_rules[doc_type].update(rule_data)
                else:
                    # Add new rule
                    merged_rules[doc_type] = rule_data
                    
        except Exception as e:
            print(f"Error loading rules overrides: {e}", file=sys.stderr)
    
    return merged_rules


def save_rule(doc_type: str, rule_data: Dict) -> dict:
    """
    Save or update a single rule
    
    Args:
        doc_type: Document type code (e.g. "GCNM")
        rule_data: Rule configuration
        
    Returns:
        Result dict with success status
    """
    ensure_user_data_dir()
    
    try:
        # Load existing overrides
        overrides = {}
        if RULES_OVERRIDE_FILE.exists():
            with open(RULES_OVERRIDE_FILE, 'r', encoding='utf-8') as f:
                overrides = json.load(f)
        
        # Update or add rule
        overrides[doc_type] = rule_data
        
        # Save back to file
        with open(RULES_OVERRIDE_FILE, 'w', encoding='utf-8') as f:
            json.dump(overrides, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"Rule '{doc_type}' saved successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def delete_rule(doc_type: str) -> dict:
    """
    Delete a rule override (reverts to default)
    
    Args:
        doc_type: Document type code to delete
        
    Returns:
        Result dict with success status
    """
    ensure_user_data_dir()
    
    try:
        if not RULES_OVERRIDE_FILE.exists():
            return {
                "success": True,
                "message": "No overrides to delete"
            }
        
        # Load existing overrides
        with open(RULES_OVERRIDE_FILE, 'r', encoding='utf-8') as f:
            overrides = json.load(f)
        
        # Remove rule if exists
        if doc_type in overrides:
            del overrides[doc_type]
            
            # Save back
            with open(RULES_OVERRIDE_FILE, 'w', encoding='utf-8') as f:
                json.dump(overrides, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "message": f"Rule '{doc_type}' deleted, reverted to default"
            }
        else:
            return {
                "success": True,
                "message": f"Rule '{doc_type}' not found in overrides"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def reset_all_rules() -> dict:
    """
    Delete all rule overrides (revert to defaults)
    
    Returns:
        Result dict with success status
    """
    try:
        if RULES_OVERRIDE_FILE.exists():
            RULES_OVERRIDE_FILE.unlink()
        
        return {
            "success": True,
            "message": "All rules reset to defaults"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def export_rules(export_path: str) -> dict:
    """
    Export current rules to JSON file
    
    Args:
        export_path: Path to export file
        
    Returns:
        Result dict with success status
    """
    try:
        rules = get_rules()
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"Rules exported to {export_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def import_rules(import_path: str, merge: bool = True) -> dict:
    """
    Import rules from JSON file
    
    Args:
        import_path: Path to import file
        merge: If True, merge with existing; if False, replace all
        
    Returns:
        Result dict with success status
    """
    ensure_user_data_dir()
    
    try:
        # Load import file
        with open(import_path, 'r', encoding='utf-8') as f:
            imported_rules = json.load(f)
        
        if merge:
            # Merge with existing overrides
            overrides = {}
            if RULES_OVERRIDE_FILE.exists():
                with open(RULES_OVERRIDE_FILE, 'r', encoding='utf-8') as f:
                    overrides = json.load(f)
            
            # Merge imported rules
            overrides.update(imported_rules)
            final_rules = overrides
        else:
            # Replace all
            final_rules = imported_rules
        
        # Save to overrides file
        with open(RULES_OVERRIDE_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_rules, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"Rules imported from {import_path}",
            "count": len(imported_rules)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_rules_folder_path() -> str:
    """Get the path to rules folder"""
    ensure_user_data_dir()
    return str(Path(USER_DATA_PATH))


def main():
    """Command-line interface for rules manager"""
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python rules_manager.py <command> [args]",
            "commands": ["get", "save", "delete", "reset", "export", "import", "folder"],
            "success": False
        }))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "get":
        rules = get_rules()
        print(json.dumps(rules, ensure_ascii=False, indent=2))
    
    elif command == "save":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: save <doc_type> <rule_json>", "success": False}))
            sys.exit(1)
        doc_type = sys.argv[2]
        rule_json = sys.argv[3]
        rule_data = json.loads(rule_json)
        result = save_rule(doc_type, rule_data)
        print(json.dumps(result))
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: delete <doc_type>", "success": False}))
            sys.exit(1)
        doc_type = sys.argv[2]
        result = delete_rule(doc_type)
        print(json.dumps(result))
    
    elif command == "reset":
        result = reset_all_rules()
        print(json.dumps(result))
    
    elif command == "export":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: export <file_path>", "success": False}))
            sys.exit(1)
        export_path = sys.argv[2]
        result = export_rules(export_path)
        print(json.dumps(result))
    
    elif command == "import":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: import <file_path> [merge]", "success": False}))
            sys.exit(1)
        import_path = sys.argv[2]
        merge = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True
        result = import_rules(import_path, merge)
        print(json.dumps(result))
    
    elif command == "folder":
        folder_path = get_rules_folder_path()
        print(json.dumps({"success": True, "path": folder_path}))
    
    else:
        print(json.dumps({
            "error": f"Unknown command: {command}",
            "success": False
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
