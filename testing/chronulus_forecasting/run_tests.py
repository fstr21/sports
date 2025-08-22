#!/usr/bin/env python3
"""
Chronulus MCP Test Runner
Orchestrates all testing and evaluation of Chronulus MCP for sports forecasting
"""
import asyncio
import subprocess
import sys
import os
from datetime import datetime
import json

def run_command(command, description):
    """Run a command and capture output"""
    print(f"\n🔄 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print("✅ Success")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, "", str(e)

def check_requirements():
    """Check if required packages are available"""
    print("📋 Checking requirements...")
    
    required_packages = ['httpx', 'asyncio']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r setup/requirements.txt")
        return False
    
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🌍 Checking environment...")
    
    env_vars = {
        'CHRONULUS_API_KEY': os.getenv('CHRONULUS_API_KEY'),
        'MLB_MCP_URL': 'https://mlbmcp-production.up.railway.app/mcp',
        'ODDS_MCP_URL': 'https://odds-mcp-v2-production.up.railway.app/mcp'
    }
    
    all_good = True
    for var, value in env_vars.items():
        if value:
            if 'API_KEY' in var:
                print(f"✅ {var}: {'SET' if value else 'NOT SET'}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            if var == 'CHRONULUS_API_KEY':
                print("   ⚠️  This will limit testing capabilities")
            all_good = False
    
    return all_good

async def main():
    """Main test orchestration"""
    print("🧪 CHRONULUS MCP TESTING SUITE")
    print("=" * 60)
    print(f"⏰ Started: {datetime.now()}")
    print(f"📁 Working Directory: {os.path.dirname(__file__)}")
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "requirements_check": False,
        "environment_check": False,
        "basic_test": {"success": False, "output": ""},
        "real_data_test": {"success": False, "output": ""},
        "overall_assessment": "Not Run"
    }
    
    # Step 1: Check requirements
    print("\n" + "="*30)
    print("📋 STEP 1: REQUIREMENTS CHECK")
    print("="*30)
    
    requirements_ok = check_requirements()
    test_results["requirements_check"] = requirements_ok
    
    if not requirements_ok:
        print("\n❌ Requirements check failed. Please install missing packages first.")
        print("💡 Run: pip install -r setup/requirements.txt")
        return test_results
    
    # Step 2: Check environment
    print("\n" + "="*30)
    print("🌍 STEP 2: ENVIRONMENT CHECK") 
    print("="*30)
    
    env_ok = check_environment()
    test_results["environment_check"] = env_ok
    
    # Step 3: Run basic tests
    print("\n" + "="*30)
    print("🧪 STEP 3: BASIC FUNCTIONALITY TEST")
    print("="*30)
    
    basic_success, basic_output, basic_error = run_command(
        f'python "{os.path.join("tests", "test_chronulus_basic.py")}"',
        "Running basic Chronulus MCP functionality tests"
    )
    
    test_results["basic_test"] = {
        "success": basic_success,
        "output": basic_output,
        "error": basic_error
    }
    
    # Step 4: Run real data tests
    print("\n" + "="*30)
    print("🏟️  STEP 4: REAL DATA INTEGRATION TEST")
    print("="*30)
    
    real_data_success, real_data_output, real_data_error = run_command(
        f'python "{os.path.join("tests", "test_with_real_data.py")}"',
        "Testing Chronulus MCP with real sports data"
    )
    
    test_results["real_data_test"] = {
        "success": real_data_success,
        "output": real_data_output,
        "error": real_data_error
    }
    
    # Step 5: Overall assessment
    print("\n" + "="*40)
    print("📊 STEP 5: OVERALL ASSESSMENT")
    print("="*40)
    
    success_count = sum([
        test_results["requirements_check"],
        test_results["environment_check"], 
        test_results["basic_test"]["success"],
        test_results["real_data_test"]["success"]
    ])
    
    total_tests = 4
    success_rate = success_count / total_tests
    
    if success_rate >= 0.75:
        assessment = "✅ EXCELLENT - Ready for production consideration"
        test_results["overall_assessment"] = "EXCELLENT"
    elif success_rate >= 0.5:
        assessment = "⚠️  GOOD - Promising but needs refinement"
        test_results["overall_assessment"] = "GOOD"
    elif success_rate >= 0.25:
        assessment = "⚠️  FAIR - Significant issues need addressing"
        test_results["overall_assessment"] = "FAIR"
    else:
        assessment = "❌ POOR - Not recommended for integration"
        test_results["overall_assessment"] = "POOR"
    
    print(f"📈 Success Rate: {success_rate:.1%} ({success_count}/{total_tests})")
    print(f"🎯 Assessment: {assessment}")
    
    # Specific recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if test_results["requirements_check"]:
        print("   ✅ Requirements satisfied")
    else:
        print("   ❌ Install missing Python packages first")
    
    if test_results["environment_check"]:
        print("   ✅ Environment properly configured")
    else:
        print("   ⚠️  Set CHRONULUS_API_KEY for full functionality")
    
    if test_results["basic_test"]["success"]:
        print("   ✅ Basic functionality working")
    else:
        print("   ❌ Basic tests failing - check installation")
    
    if test_results["real_data_test"]["success"]:
        print("   ✅ Real data integration successful")
        print("   🚀 Consider integrating with existing Discord bot")
    else:
        print("   ⚠️  Real data integration needs work")
    
    # Next steps
    print(f"\n🚀 NEXT STEPS:")
    if success_rate >= 0.75:
        print("   1. Obtain Chronulus API key if not already done")
        print("   2. Configure Chronulus MCP in Claude Desktop")
        print("   3. Create integration with Discord bot")
        print("   4. Test with live betting scenarios")
    elif success_rate >= 0.5:
        print("   1. Fix failing tests and configuration issues")
        print("   2. Obtain Chronulus API key")
        print("   3. Re-run tests to verify improvements")
        print("   4. Consider limited integration for testing")
    else:
        print("   1. Review installation and configuration")
        print("   2. Check Chronulus MCP documentation")
        print("   3. Resolve fundamental issues before proceeding")
    
    # Save comprehensive results
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    results_file = os.path.join(results_dir, f"chronulus_full_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n💾 Complete results saved: {results_file}")
    print(f"⏰ Completed: {datetime.now()}")
    
    return test_results

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Exit with appropriate code
    success_rate = sum([
        results["requirements_check"],
        results["environment_check"],
        results["basic_test"]["success"],
        results["real_data_test"]["success"]
    ]) / 4
    
    sys.exit(0 if success_rate >= 0.5 else 1)