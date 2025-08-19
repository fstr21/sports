#!/usr/bin/env python3
# Configuration Validation Script
"""
Standalone script to validate soccer Discord bot configuration
Run this script to check your environment setup before deployment
"""

import sys
import os
from typing import Dict, Any

def main():
    """Main validation function"""
    print("🔍 Soccer Discord Bot - Configuration Validation")
    print("=" * 50)
    
    try:
        # Import configuration modules
        from soccer_config import (
            validate_soccer_environment, 
            perform_soccer_startup_checks,
            get_soccer_config,
            get_active_soccer_leagues
        )
        
        print("✅ Configuration modules loaded successfully")
        
        # Validate environment
        print("\n📋 Validating Environment Variables...")
        env_validation = validate_soccer_environment()
        
        if env_validation["valid"]:
            print("✅ Environment validation passed")
        else:
            print("❌ Environment validation failed:")
            for error in env_validation["errors"]:
                print(f"   - {error}")
        
        # Show warnings
        if env_validation["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in env_validation["warnings"]:
                print(f"   - {warning}")
        
        # Show missing optional variables
        if env_validation["missing_optional"]:
            print(f"\nℹ️  Optional variables not set: {', '.join(env_validation['missing_optional'])}")
        
        # Perform startup checks
        print("\n🚀 Performing Startup Checks...")
        startup_success = perform_soccer_startup_checks()
        
        if startup_success:
            print("✅ Startup checks passed")
        else:
            print("❌ Startup checks failed")
        
        # Show configuration summary
        if env_validation["valid"] and startup_success:
            print("\n📊 Configuration Summary:")
            config = get_soccer_config()
            active_leagues = get_active_soccer_leagues()
            
            print(f"   Soccer MCP URL: {config.mcp_url}")
            print(f"   Authentication: {'Enabled' if config.auth_key else 'Disabled'}")
            print(f"   Active Leagues: {', '.join(active_leagues)}")
            print(f"   Max Matches/Day: {config.max_matches_per_day}")
            print(f"   Channel Retention: {config.channel_retention_days} days")
            print(f"   H2H Analysis: {'Enabled' if config.enable_h2h_analysis else 'Disabled'}")
            print(f"   Betting Recommendations: {'Enabled' if config.enable_betting_recommendations else 'Disabled'}")
            print(f"   League Standings: {'Enabled' if config.enable_standings else 'Disabled'}")
        
        # Final result
        print("\n" + "=" * 50)
        if env_validation["valid"] and startup_success:
            print("🎉 Configuration validation completed successfully!")
            print("   Your bot is ready for deployment.")
            return 0
        else:
            print("💥 Configuration validation failed!")
            print("   Please fix the issues above before deployment.")
            return 1
            
    except ImportError as e:
        print(f"❌ Failed to import configuration modules: {e}")
        print("   Make sure you're running this from the correct directory.")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error during validation: {e}")
        return 1

def show_help():
    """Show help information"""
    print("Soccer Discord Bot - Configuration Validation")
    print()
    print("Usage: python validate_config.py [options]")
    print()
    print("Options:")
    print("  -h, --help     Show this help message")
    print("  -v, --verbose  Show detailed configuration information")
    print()
    print("Environment Variables:")
    print("  Required:")
    print("    DISCORD_BOT_TOKEN    Discord bot token")
    print()
    print("  Optional:")
    print("    SOCCER_MCP_URL       Soccer MCP server URL")
    print("    AUTH_KEY             Soccer MCP authentication key")
    print("    SOCCER_LEAGUES_CONFIG Custom league configuration (JSON)")
    print()
    print("Examples:")
    print("  python validate_config.py")
    print("  python validate_config.py --verbose")

if __name__ == "__main__":
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        show_help()
        sys.exit(0)
    
    # Check for verbose flag
    verbose = len(sys.argv) > 1 and sys.argv[1] in ["-v", "--verbose"]
    
    if verbose:
        # Enable debug logging for verbose output
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Run validation
    exit_code = main()
    sys.exit(exit_code)