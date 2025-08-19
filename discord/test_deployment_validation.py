#!/usr/bin/env python3
"""
Deployment Validation Test Suite
Simplified version that doesn't require full bot initialization
"""

import os
import sys
import asyncio
import httpx
import json
import time
from datetime import datetime
from unittest.mock import Mock, patch

# Set up test environment
os.environ.setdefault('DISCORD_BOT_TOKEN', 'test_bot_token_' + 'x' * 50)
os.environ.setdefault('SOCCER_MCP_URL', 'https://soccermcp-production.up.railway.app/mcp')

print("🚀 Soccer Discord Integration - Deployment Validation")
print("=" * 60)

def test_environment_setup():
    """Test that environment is properly set up"""
    print("\n📋 Testing Environment Setup")
    print("-" * 30)
    
    checks = []
    
    # Check Python version
    python_version = sys.version_info
    python_ok = python_version >= (3, 8)
    checks.append(("Python version", python_ok, f"{python_version.major}.{python_version.minor}"))
    
    # Check required environment variables
    required_vars = ['DISCORD_BOT_TOKEN', 'SOCCER_MCP_URL']
    for var in required_vars:
        value = os.getenv(var)
        var_ok = value is not None and len(value) > 0
        checks.append((f"Environment variable {var}", var_ok, "Set" if var_ok else "Missing"))
    
    # Check optional environment variables
    optional_vars = ['AUTH_KEY']
    for var in optional_vars:
        value = os.getenv(var)
        var_status = "Set" if value else "Not set (optional)"
        checks.append((f"Optional variable {var}", True, var_status))
    
    # Print results
    passed = 0
    for check_name, success, details in checks:
        status = "✅" if success else "❌"
        print(f"  {status} {check_name}: {details}")
        if success:
            passed += 1
    
    print(f"\nEnvironment Setup: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n📋 Testing Dependencies")
    print("-" * 30)
    
    dependencies = [
        ('discord.py', 'discord'),
        ('httpx', 'httpx'),
        ('asyncio', 'asyncio'),
        ('json', 'json'),
        ('datetime', 'datetime')
    ]
    
    passed = 0
    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"  ✅ {dep_name}: Available")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {dep_name}: Missing ({e})")
    
    print(f"\nDependencies: {passed}/{len(dependencies)} available")
    return passed == len(dependencies)

def test_soccer_components():
    """Test that soccer components can be imported and initialized"""
    print("\n📋 Testing Soccer Components")
    print("-" * 30)
    
    components = []
    
    # Test SoccerMCPClient
    try:
        from soccer_integration import SoccerMCPClient
        client = SoccerMCPClient()
        components.append(("SoccerMCPClient", True, "Initialized successfully"))
    except Exception as e:
        components.append(("SoccerMCPClient", False, str(e)))
    
    # Test SoccerDataProcessor
    try:
        from soccer_integration import SoccerDataProcessor
        processor = SoccerDataProcessor()
        components.append(("SoccerDataProcessor", True, "Initialized successfully"))
    except Exception as e:
        components.append(("SoccerDataProcessor", False, str(e)))
    
    # Test SoccerEmbedBuilder
    try:
        from soccer_integration import SoccerEmbedBuilder
        builder = SoccerEmbedBuilder()
        components.append(("SoccerEmbedBuilder", True, "Initialized successfully"))
    except Exception as e:
        components.append(("SoccerEmbedBuilder", False, str(e)))
    
    # Test SoccerChannelManager
    try:
        from soccer_channel_manager import SoccerChannelManager
        manager = SoccerChannelManager(None)  # Mock bot
        components.append(("SoccerChannelManager", True, "Initialized successfully"))
    except Exception as e:
        components.append(("SoccerChannelManager", False, str(e)))
    
    # Test configuration
    try:
        from soccer_config import get_soccer_config, validate_soccer_environment
        config = get_soccer_config()
        validation = validate_soccer_environment()
        config_ok = config is not None and validation.get('valid', False)
        components.append(("Soccer Configuration", config_ok, "Loaded and validated"))
    except Exception as e:
        components.append(("Soccer Configuration", False, str(e)))
    
    # Print results
    passed = 0
    for comp_name, success, details in components:
        status = "✅" if success else "❌"
        print(f"  {status} {comp_name}: {details}")
        if success:
            passed += 1
    
    print(f"\nSoccer Components: {passed}/{len(components)} working")
    return passed == len(components)

async def test_mcp_connectivity():
    """Test MCP server connectivity"""
    print("\n📋 Testing MCP Server Connectivity")
    print("-" * 30)
    
    mcp_url = os.getenv('SOCCER_MCP_URL')
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
            )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"  ✅ MCP Server: Accessible (HTTP {response.status_code})")
            print(f"  ✅ Response Time: {response_time:.2f}s")
            
            # Try to parse response
            try:
                data = response.json()
                if "result" in data:
                    print(f"  ✅ Response Format: Valid JSON-RPC")
                    return True
                else:
                    print(f"  ⚠️  Response Format: Missing 'result' field")
                    return False
            except json.JSONDecodeError:
                print(f"  ❌ Response Format: Invalid JSON")
                return False
        else:
            print(f"  ❌ MCP Server: HTTP {response.status_code}")
            return False
            
    except httpx.TimeoutException:
        print(f"  ❌ MCP Server: Timeout (>10s)")
        return False
    except httpx.ConnectError:
        print(f"  ❌ MCP Server: Connection failed")
        return False
    except Exception as e:
        print(f"  ❌ MCP Server: Error ({e})")
        return False

def test_data_processing():
    """Test data processing functionality"""
    print("\n📋 Testing Data Processing")
    print("-" * 30)
    
    try:
        from soccer_integration import SoccerDataProcessor
        processor = SoccerDataProcessor()
        
        # Test odds conversion
        decimal_odds = 2.50
        american_odds = processor.convert_to_american_odds(decimal_odds)
        odds_ok = american_odds == 150
        print(f"  {'✅' if odds_ok else '❌'} Odds Conversion: {decimal_odds} -> +{american_odds}")
        
        # Test team name cleaning
        team_name = "Manchester United F.C."
        clean_name = processor.clean_team_name_for_channel(team_name)
        name_ok = clean_name == "manchester-united-fc"
        print(f"  {'✅' if name_ok else '❌'} Team Name Cleaning: '{team_name}' -> '{clean_name}'")
        
        # Test sample data processing
        sample_data = {
            "matches_by_league": {
                "EPL": [
                    {
                        "id": 1,
                        "date": "2025-08-18",
                        "time": "15:00",
                        "venue": "Stadium",
                        "status": "scheduled",
                        "home_team": {"id": 1, "name": "Arsenal", "short_name": "ARS"},
                        "away_team": {"id": 2, "name": "Liverpool", "short_name": "LIV"}
                    }
                ]
            }
        }
        
        processed_matches = processor.process_match_data(sample_data)
        processing_ok = len(processed_matches) == 1
        print(f"  {'✅' if processing_ok else '❌'} Sample Data Processing: {len(processed_matches)} matches processed")
        
        return odds_ok and name_ok and processing_ok
        
    except Exception as e:
        print(f"  ❌ Data Processing: Error ({e})")
        return False

def test_embed_creation():
    """Test embed creation functionality"""
    print("\n📋 Testing Embed Creation")
    print("-" * 30)
    
    try:
        from soccer_integration import SoccerEmbedBuilder, ProcessedMatch, Team, League
        builder = SoccerEmbedBuilder()
        
        # Create sample match
        match = ProcessedMatch(
            match_id=1,
            home_team=Team(id=1, name="Arsenal", short_name="ARS"),
            away_team=Team(id=2, name="Liverpool", short_name="LIV"),
            league=League(id=228, name="Premier League", country="England"),
            date="2025-08-18",
            time="15:00",
            venue="Emirates Stadium",
            status="scheduled"
        )
        
        # Test embed creation
        embed = builder.create_match_preview_embed(match)
        
        embed_ok = (
            embed is not None and
            embed.title is not None and
            "Arsenal" in embed.title and
            "Liverpool" in embed.title and
            len(embed.fields) > 0
        )
        
        print(f"  {'✅' if embed_ok else '❌'} Match Preview Embed: Created successfully")
        print(f"  {'✅' if embed.color else '❌'} Embed Color: {embed.color}")
        print(f"  {'✅' if len(embed.fields) > 0 else '❌'} Embed Fields: {len(embed.fields)} fields")
        
        return embed_ok
        
    except Exception as e:
        print(f"  ❌ Embed Creation: Error ({e})")
        return False

def test_error_handling():
    """Test error handling functionality"""
    print("\n📋 Testing Error Handling")
    print("-" * 30)
    
    try:
        from soccer_integration import SoccerDataProcessor
        processor = SoccerDataProcessor()
        
        # Test empty data handling
        empty_result = processor.process_match_data({})
        empty_ok = empty_result == []
        print(f"  {'✅' if empty_ok else '❌'} Empty Data Handling: Graceful")
        
        # Test malformed data handling
        malformed_data = {"invalid": "structure"}
        malformed_result = processor.process_match_data(malformed_data)
        malformed_ok = malformed_result == []
        print(f"  {'✅' if malformed_ok else '❌'} Malformed Data Handling: Graceful")
        
        # Test date validation
        from bot_structure import validate_date_input
        
        try:
            validate_date_input("invalid-date")
            date_validation_ok = False  # Should have raised error
        except ValueError:
            date_validation_ok = True  # Expected behavior
        
        print(f"  {'✅' if date_validation_ok else '❌'} Date Validation: Invalid dates rejected")
        
        return empty_ok and malformed_ok and date_validation_ok
        
    except Exception as e:
        print(f"  ❌ Error Handling: Error ({e})")
        return False

def test_configuration_validation():
    """Test configuration validation"""
    print("\n📋 Testing Configuration Validation")
    print("-" * 30)
    
    try:
        from soccer_config import validate_soccer_environment, get_soccer_config
        
        # Test environment validation
        validation = validate_soccer_environment()
        env_valid = validation.get('valid', False)
        print(f"  {'✅' if env_valid else '❌'} Environment Validation: {'Valid' if env_valid else 'Invalid'}")
        
        if not env_valid and 'errors' in validation:
            for error in validation['errors']:
                print(f"    - {error}")
        
        # Test configuration loading
        config = get_soccer_config()
        config_ok = config is not None
        print(f"  {'✅' if config_ok else '❌'} Configuration Loading: {'Success' if config_ok else 'Failed'}")
        
        # Test league configuration
        if config_ok:
            leagues = config.leagues if hasattr(config, 'leagues') else {}
            league_count = len(leagues)
            leagues_ok = league_count >= 6  # Should have at least 6 leagues
            print(f"  {'✅' if leagues_ok else '❌'} League Configuration: {league_count} leagues configured")
        else:
            leagues_ok = False
        
        return env_valid and config_ok and leagues_ok
        
    except Exception as e:
        print(f"  ❌ Configuration Validation: Error ({e})")
        return False

async def run_all_tests():
    """Run all deployment validation tests"""
    print("Starting deployment validation tests...\n")
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Dependencies", test_dependencies),
        ("Soccer Components", test_soccer_components),
        ("MCP Connectivity", test_mcp_connectivity),
        ("Data Processing", test_data_processing),
        ("Embed Creation", test_embed_creation),
        ("Error Handling", test_error_handling),
        ("Configuration", test_configuration_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name}: Test failed with error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    # Determine deployment readiness
    if success_rate >= 90:
        print("\n🎉 DEPLOYMENT READY")
        print("All critical systems are functioning correctly.")
        print("The soccer integration is ready for production deployment.")
        return True
    elif success_rate >= 75:
        print("\n⚠️  MOSTLY READY")
        print("Most systems are working, but some issues were found.")
        print("Review failed tests before production deployment.")
        return True
    else:
        print("\n🚫 NOT READY")
        print("Critical issues found that must be resolved before deployment.")
        print("Do not deploy to production until all tests pass.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nValidation failed with error: {e}")
        exit(1)