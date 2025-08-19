"""
Demonstration of the Soccer Discord Integration Error Handling System
Shows various error scenarios and how they are handled gracefully
"""

import asyncio
import logging
from datetime import datetime
from soccer_error_handling import (
    SoccerBotError, MCPConnectionError, MCPTimeoutError, MCPDataError,
    DiscordAPIError, ValidationError, ErrorContext, ErrorSeverity,
    retry_with_backoff, GracefulDegradation, error_handler, bot_logger
)

# Configure logging for demo
logging.basicConfig(level=logging.INFO)

async def demo_error_handling():
    """Demonstrate various error handling scenarios"""
    
    print("🚀 Soccer Discord Integration - Error Handling Demo")
    print("=" * 60)
    
    # 1. Error Context Creation
    print("\n1. Creating Error Context")
    context = ErrorContext(
        "demo_operation",
        user_id=12345,
        guild_id=67890,
        additional_data={"demo": True}
    )
    print(f"   ✓ Context created: {context.operation} at {context.timestamp}")
    
    # 2. Different Error Types
    print("\n2. Different Error Types and User Messages")
    
    # MCP Connection Error
    mcp_error = MCPConnectionError(
        "Failed to connect to MCP server",
        status_code=503,
        context=context
    )
    print(f"   🔌 MCP Connection Error:")
    print(f"      Technical: {mcp_error}")
    print(f"      User Message: {mcp_error.user_message}")
    
    # MCP Timeout Error
    timeout_error = MCPTimeoutError(
        "Request timed out",
        30.0,
        context
    )
    print(f"   ⏱️  MCP Timeout Error:")
    print(f"      Technical: {timeout_error}")
    print(f"      User Message: {timeout_error.user_message}")
    
    # Validation Error
    validation_error = ValidationError(
        "Invalid date format",
        "date",
        "invalid-date",
        "YYYY-MM-DD"
    )
    print(f"   ❌ Validation Error:")
    print(f"      Technical: {validation_error}")
    print(f"      User Message: {validation_error.user_message}")
    
    # Discord API Error
    discord_error = DiscordAPIError(
        "Permission denied",
        error_code=403,
        context=context
    )
    print(f"   🔒 Discord API Error:")
    print(f"      Technical: {discord_error}")
    print(f"      User Message: {discord_error.user_message}")
    
    # 3. Graceful Degradation
    print("\n3. Graceful Degradation Example")
    
    # Simulate partial match data
    incomplete_match_data = {
        "home_team": "Liverpool",
        "away_team": "Arsenal",
        "date": "2025-08-17"
        # Missing: odds, venue, time
    }
    
    missing_fields = ["odds", "venue", "time"]
    degraded_data = GracefulDegradation.create_partial_match_data(
        incomplete_match_data, 
        missing_fields
    )
    
    print(f"   📊 Original data: {list(incomplete_match_data.keys())}")
    print(f"   📊 After degradation: {list(degraded_data.keys())}")
    print(f"   📊 Partial data flag: {degraded_data.get('_partial_data')}")
    print(f"   📊 Missing fields: {degraded_data.get('_missing_fields')}")
    
    # 4. Retry Logic Demo
    print("\n4. Retry Logic Demonstration")
    
    attempt_count = 0
    
    @retry_with_backoff(max_retries=2, base_delay=0.1)
    async def flaky_operation():
        nonlocal attempt_count
        attempt_count += 1
        print(f"   🔄 Attempt {attempt_count}")
        
        if attempt_count < 3:
            raise ConnectionError("Simulated connection failure")
        return "Success!"
    
    try:
        result = await flaky_operation()
        print(f"   ✅ Operation succeeded: {result}")
    except Exception as e:
        print(f"   ❌ Operation failed after retries: {e}")
    
    # 5. Error Handler Usage
    print("\n5. Error Handler Integration")
    
    # Create error embed
    embed = error_handler.create_error_embed(
        mcp_error,
        suggestions=[
            "Try again in a few minutes",
            "Check your internet connection",
            "Contact an administrator if the issue persists"
        ]
    )
    
    print(f"   📋 Error embed created:")
    print(f"      Title: {embed.title}")
    print(f"      Description: {embed.description}")
    print(f"      Color: {embed.color}")
    print(f"      Fields: {len(embed.fields)}")
    
    # 6. Logging Demo
    print("\n6. Enhanced Logging System")
    
    # Log operation lifecycle
    bot_logger.log_operation_start("demo_operation", context)
    
    # Simulate some work
    await asyncio.sleep(0.1)
    
    bot_logger.log_operation_success(
        "demo_operation", 
        context, 
        duration=0.1, 
        result_summary="Demo completed successfully"
    )
    
    # Log an error scenario
    demo_error = SoccerBotError(
        "Demo error for logging",
        ErrorSeverity.LOW,
        context
    )
    bot_logger.log_operation_error("demo_error_operation", demo_error, context)
    
    # Log graceful degradation
    bot_logger.log_graceful_degradation(
        "demo_degradation",
        ["missing_odds", "missing_venue"],
        ["team_names", "date", "time"],
        context
    )
    
    print("   📝 Logging operations completed (check log files)")
    
    print("\n" + "=" * 60)
    print("✅ Error Handling Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• Comprehensive error types with user-friendly messages")
    print("• Graceful degradation for partial data")
    print("• Retry logic with exponential backoff")
    print("• Enhanced logging with context")
    print("• Discord embed creation for errors")
    print("• Input validation with helpful feedback")

if __name__ == "__main__":
    asyncio.run(demo_error_handling())