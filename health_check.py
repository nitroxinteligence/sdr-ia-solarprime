#!/usr/bin/env python3
"""
Health Check and Validation Script for AGNO v1.7.6
Validates Team and Agent initialization parameters
"""

import sys
import inspect
import traceback
from typing import Dict, Any, List

def check_agno_parameters() -> Dict[str, Any]:
    """Check AGNO Team and Agent parameter signatures"""
    results = {
        "status": "checking",
        "team_params": {},
        "agent_params": {},
        "errors": []
    }
    
    try:
        from agno.team import Team
        from agno.agent import Agent
        
        # Check Team parameters
        team_sig = inspect.signature(Team.__init__)
        team_params = []
        for param_name, param in team_sig.parameters.items():
            if param_name != 'self':
                team_params.append(param_name)
        
        results["team_params"] = {
            "available": team_params,
            "has_role": "role" in team_params,
            "has_description": "description" in team_params,
            "has_instructions": "instructions" in team_params
        }
        
        # Check Agent parameters
        agent_sig = inspect.signature(Agent.__init__)
        agent_params = []
        for param_name, param in agent_sig.parameters.items():
            if param_name != 'self':
                agent_params.append(param_name)
        
        results["agent_params"] = {
            "available": agent_params,
            "has_role": "role" in agent_params,
            "has_description": "description" in agent_params,
            "has_instructions": "instructions" in agent_params
        }
        
        results["status"] = "success"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(f"Parameter check failed: {str(e)}")
    
    return results

def validate_team_creation() -> Dict[str, Any]:
    """Validate Team creation with correct parameters"""
    results = {
        "status": "checking",
        "team_creation": None,
        "errors": []
    }
    
    try:
        from agno.team import Team
        from agno.agent import Agent
        from agno.models.google import Gemini
        from agno.memory import AgentMemory
        import os
        
        # Create test model
        model = Gemini(
            id="gemini-2.0-flash-exp",
            api_key=os.getenv("GOOGLE_API_KEY", "test-key")
        )
        
        # Create test memory
        memory = AgentMemory()
        
        # Create test agent
        agent = Agent(
            name="Test Agent",
            model=model,
            instructions="Test instructions"
        )
        
        # Try creating Team with different parameter combinations
        test_results = []
        
        # Test 1: With description (should work)
        try:
            team1 = Team(
                name="Test Team 1",
                members=[agent],
                mode="coordinate",
                model=model,
                description="Test description",
                instructions="Test instructions",
                memory=memory
            )
            test_results.append({"test": "description_param", "result": "success"})
        except TypeError as e:
            test_results.append({"test": "description_param", "result": f"failed: {e}"})
        
        # Test 2: With role (might fail)
        try:
            team2 = Team(
                name="Test Team 2",
                members=[agent],
                mode="coordinate",
                model=model,
                role="Test role",
                instructions="Test instructions",
                memory=memory
            )
            test_results.append({"test": "role_param", "result": "success"})
        except TypeError as e:
            test_results.append({"test": "role_param", "result": f"failed: {e}"})
        
        results["team_creation"] = test_results
        results["status"] = "success"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(f"Team creation validation failed: {str(e)}")
        results["traceback"] = traceback.format_exc()
    
    return results

def check_sdr_team_file() -> Dict[str, Any]:
    """Check the actual SDR Team file for issues"""
    results = {
        "status": "checking",
        "file_check": {},
        "errors": []
    }
    
    try:
        import os
        import re
        
        sdr_team_path = "app/teams/sdr_team.py"
        
        if os.path.exists(sdr_team_path):
            with open(sdr_team_path, 'r') as f:
                content = f.read()
            
            # Check for 'role=' usage in Team initialization
            team_init_pattern = r'Team\([^)]*role='
            role_matches = re.findall(team_init_pattern, content)
            
            # Check for 'description=' usage in Team initialization
            desc_pattern = r'Team\([^)]*description='
            desc_matches = re.findall(desc_pattern, content)
            
            # Find line number of Team initialization
            lines = content.split('\n')
            team_line = None
            for i, line in enumerate(lines):
                if 'self.team = Team(' in line:
                    team_line = i + 1
                    break
            
            results["file_check"] = {
                "file_exists": True,
                "uses_role": len(role_matches) > 0,
                "uses_description": len(desc_matches) > 0,
                "team_init_line": team_line,
                "role_occurrences": len(role_matches),
                "description_occurrences": len(desc_matches)
            }
        else:
            results["file_check"]["file_exists"] = False
        
        results["status"] = "success"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(f"File check failed: {str(e)}")
    
    return results

def main():
    """Run all health checks"""
    print("=" * 60)
    print("AGNO v1.7.6 Health Check")
    print("=" * 60)
    
    all_results = {}
    
    # Check 1: Parameter signatures
    print("\n1. Checking AGNO parameter signatures...")
    param_results = check_agno_parameters()
    all_results["parameters"] = param_results
    
    if param_results["status"] == "success":
        print(f"   ✅ Team has 'description': {param_results['team_params']['has_description']}")
        print(f"   ✅ Team has 'role': {param_results['team_params']['has_role']}")
        print(f"   ✅ Agent has 'instructions': {param_results['agent_params']['has_instructions']}")
    else:
        print(f"   ❌ Error: {param_results['errors']}")
    
    # Check 2: Team creation validation
    print("\n2. Validating Team creation...")
    creation_results = validate_team_creation()
    all_results["creation"] = creation_results
    
    if creation_results["status"] == "success":
        for test in creation_results.get("team_creation", []):
            status = "✅" if "success" in test["result"] else "❌"
            print(f"   {status} {test['test']}: {test['result']}")
    else:
        print(f"   ❌ Error: {creation_results['errors']}")
    
    # Check 3: SDR Team file check
    print("\n3. Checking SDR Team file...")
    file_results = check_sdr_team_file()
    all_results["file"] = file_results
    
    if file_results["status"] == "success":
        check = file_results["file_check"]
        if check.get("file_exists"):
            print(f"   ✅ File exists")
            print(f"   {'❌' if check['uses_role'] else '✅'} Uses 'role': {check['uses_role']}")
            print(f"   {'✅' if check['uses_description'] else '❌'} Uses 'description': {check['uses_description']}")
            print(f"   📍 Team init at line: {check['team_init_line']}")
        else:
            print(f"   ❌ File not found")
    else:
        print(f"   ❌ Error: {file_results['errors']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    has_errors = any(r["status"] == "error" for r in all_results.values())
    
    if has_errors:
        print("❌ Health check FAILED - Issues detected")
        sys.exit(1)
    else:
        print("✅ Health check PASSED - System ready")
        sys.exit(0)

if __name__ == "__main__":
    main()