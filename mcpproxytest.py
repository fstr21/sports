import asyncio
import openai
import json
import os
from pathlib import Path
from mcp import ClientSession
from mcp.client.sse import sse_client
import httpx

def load_env_file(env_path):
    """Load environment variables from .env.local file"""
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

async def check_mcp_server_status():
    """Check if MCP server is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8080/status", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"Server returned status {response.status_code}"
    except Exception as e:
        return False, str(e)

def is_response_complete(response_text):
    """Check if the response seems complete"""
    if not response_text:
        return False
    
    # Check for incomplete sentences
    incomplete_indicators = [
        "I'm going to",
        "I will now",
        "Let me fetch",
        "I'll pull",
        "I'm about to"
    ]
    
    # If response ends with these phrases and is short, it's likely incomplete
    if len(response_text) < 200:
        for indicator in incomplete_indicators:
            if indicator.lower() in response_text.lower():
                return False
    
    # Check if response has substance (not just a statement of intent)
    if len(response_text.strip()) < 100:
        return False
    
    return True

async def ask_sports_question(question, openrouter_key, base_url, model, retry_incomplete=True):
    """Ask a sports question and get ESPN data - creates fresh connection each time"""
    print(f"\n[SPORTS] Question: {question}")
    
    # Enhanced system prompt
    system_prompt = """You are an expert sports analyst with access to ESPN's real-time data. 
When asked questions:
1. Use the ESPN API tools to fetch relevant current data
2. ALWAYS provide complete, detailed analysis based on the data you receive
3. For betting questions, provide data-driven insights (but remind users to gamble responsibly)
4. Structure your response with clear sections
5. Don't just say what you're going to do - actually analyze the data and provide complete answers

Important: After receiving ESPN data, provide a COMPLETE analysis. Don't end with statements like "I'm going to analyze" or "Let me look at" - actually perform the analysis."""
    
    # Setup OpenRouter client
    client = openai.OpenAI(
        base_url=base_url,
        api_key=openrouter_key
    )
    
    attempt = 0
    max_attempts = 2 if retry_incomplete else 1
    
    while attempt < max_attempts:
        attempt += 1
        if attempt > 1:
            print(f"   [RETRY] Retry attempt {attempt} (previous response was incomplete)")
        
        try:
            # Create fresh connection for each question
            print(f"   [CONNECT] Attempting connection to MCP server (attempt {attempt})")
            async with sse_client("http://127.0.0.1:8080/sse") as (read, write):
                print("   [SSE] SSE connection established")
                async with ClientSession(read, write) as session:
                    print("   [SESSION] Client session created")
                    await session.initialize()
                    print("   [SUCCESS] Connected to ESPN server")
                    
                    # Get ESPN tools
                    tools_response = await session.list_tools()
                    print(f"   [TOOLS] Using {len(tools_response.tools)} ESPN tool(s)")
                    
                    # Convert to OpenAI function format
                    openai_functions = [
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema
                            }
                        } for tool in tools_response.tools
                    ]
                    
                    # Add guidance for complex questions
                    enhanced_question = question
                    if "betting" in question.lower() or "stats" in question.lower():
                        enhanced_question += "\n\nPlease fetch team rosters, recent game results, player stats, and upcoming schedule as needed to provide a comprehensive analysis."
                    
                    # Ask LLM with ESPN tools available
                    print(f"   [AI] Asking {model}...")
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": enhanced_question}
                        ],
                        tools=openai_functions,
                        tool_choice="auto",
                        temperature=0.7,  # Add some variability
                        max_tokens=400000   # Ensure we have enough tokens for complete response
                    )
                    
                    message = response.choices[0].message
                    
                    # If LLM wants to call ESPN APIs
                    if message.tool_calls:
                        print(f"   [API] LLM is calling {len(message.tool_calls)} ESPN API(s)...")
                        
                        conversation = [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": enhanced_question},
                            {"role": "assistant", "content": message.content, "tool_calls": message.tool_calls}
                        ]
                        
                        total_data_received = 0
                        
                        # Execute each ESPN API call
                        for i, tool_call in enumerate(message.tool_calls, 1):
                            func_name = tool_call.function.name
                            func_args = json.loads(tool_call.function.arguments)
                            
                            print(f"      → Call {i}: {func_name}")
                            print(f"        Args: {func_args}")
                            
                            try:
                                print(f"        [CALL] Calling MCP tool: {func_name}")
                                result = await session.call_tool(func_name, func_args)
                                print(f"        [DONE] Tool call completed successfully")
                                espn_data = result.content[0].text if result.content else "No data"
                                data_size = len(espn_data)
                                total_data_received += data_size
                                print(f"        [SUCCESS] Got {data_size:,} characters from ESPN")
                                
                                # If we got a lot of data, truncate it intelligently
                                if data_size > 50000:
                                    print(f"        [WARNING] Large response, truncating to most relevant data")
                                    # Try to parse and extract relevant portions
                                    try:
                                        data_json = json.loads(espn_data)
                                        # Keep only essential fields for large responses
                                        if isinstance(data_json, dict):
                                            essential_keys = ['teams', 'athletes', 'statistics', 'events', 'competitions']
                                            filtered_data = {k: v for k, v in data_json.items() if k in essential_keys}
                                            espn_data = json.dumps(filtered_data)
                                    except:
                                        # If not JSON, truncate to first 30k characters
                                        espn_data = espn_data[:30000] + "... [truncated for length]"
                                
                                conversation.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": espn_data
                                })
                            except Exception as e:
                                print(f"        [ERROR] Error: {e}")
                                conversation.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": f"Error calling ESPN API: {str(e)}"
                                })
                        
                        print(f"   [DATA] Total data received: {total_data_received:,} characters")
                        
                        # Add a reminder to provide complete analysis
                        conversation.append({
                            "role": "system",
                            "content": "Now provide a COMPLETE analysis based on the ESPN data you just received. Include specific stats, insights, and if asked about betting, provide data-driven analysis (with responsible gambling reminder)."
                        })
                        
                        # Get final answer with ESPN data
                        print("   [GENERATE] Generating final answer...")
                        final_response = client.chat.completions.create(
                            model=model,
                            messages=conversation,
                            temperature=0.7,
                            max_tokens=4000
                        )
                        
                        final_answer = final_response.choices[0].message.content
                        
                        # Check if response is complete
                        if is_response_complete(final_answer):
                            return final_answer
                        elif attempt < max_attempts:
                            print("   [WARNING] Response seems incomplete, retrying...")
                            continue
                        else:
                            print("   [WARNING] Response may be incomplete but max attempts reached")
                            return final_answer
                    else:
                        print("   [INFO] LLM didn't need to call ESPN APIs")
                        return message.content
                        
        except Exception as e:
            if attempt < max_attempts:
                print(f"   [WARNING] Error on attempt {attempt}: {str(e)}")
                continue
            else:
                return f"[ERROR] Error connecting to ESPN server after {max_attempts} attempts: {str(e)}"
    
    return "[ERROR] Failed to get a complete response after all attempts"

async def interactive_chat():
    """Interactive chat with status display"""
    print("ESPN Sports Bot - Interactive Mode (Enhanced)")
    print("=" * 50)
    
    # Load environment variables from .env.local
    env_path = Path(r"C:\Users\fstr2\Desktop\sports\.env.local")
    env_vars = load_env_file(env_path)
    
    # Get configuration from .env.local
    openrouter_key = env_vars.get('OPENROUTER_API_KEY')
    base_url = env_vars.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    model = env_vars.get('OPENROUTER_MODEL', 'anthropic/claude-3-5-sonnet')
    
    if not openrouter_key:
        print("[ERROR] Error: OPENROUTER_API_KEY not found in .env.local file")
        print(f"Please check: {env_path}")
        return
    
    # Display configuration
    print(f"[KEY] API Key: {openrouter_key[:15]}...")
    print(f"[URL] Base URL: {base_url}")
    print(f"[MODEL] Model: {model}")
    
    # Check MCP server status
    print("\n[SERVER] Checking MCP Server Status...")
    server_ok, server_info = await check_mcp_server_status()
    
    if server_ok:
        print("   [SUCCESS] MCP Server is running")
        if isinstance(server_info, dict):
            instances = server_info.get('server_instances', {})
            print(f"   [INFO] Server instances: {list(instances.keys())}")
    else:
        print(f"   [ERROR] MCP Server issue: {server_info}")
        print("   [FIX] Make sure mcp-proxy is running:")
        print("      mcp-proxy --port 8080 --env REST_BASE_URL \"https://site.api.espn.com/apis/site/v2/sports\" npx dkmaker-mcp-rest-api")
        return
    
    print("\n" + "=" * 50)
    print("[READY] Ready to answer sports questions!")
    print("[INPUT] Type your questions (or 'quit'/'exit' to stop)")
    print("[EXAMPLES] Examples:")
    print("   - 'NBA games today'")
    print("   - 'Lakers vs Warriors analysis'")
    print("   - 'Sabrina Ionescu season stats'")
    print("   - 'WNBA Liberty vs Wings preview'")
    print("[ENHANCED] Enhanced: Now with better analysis and retry logic!")
    print("=" * 50)
    
    question_count = 0
    
    while True:
        try:
            # Prompt for question
            print(f"\n[Question #{question_count + 1}]")
            question = input("[SPORTS] Ask about sports: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n[GOODBYE] Thanks for using ESPN Sports Bot!")
                break
            
            question_count += 1
            
            # Get answer with retry logic for incomplete responses
            answer = await ask_sports_question(
                question, 
                openrouter_key, 
                base_url, 
                model,
                retry_incomplete=True
            )
            
            print(f"\n[ANSWER] Answer:")
            print("=" * 50)
            print(answer)
            print("=" * 50)
            
            # Quick quality check
            if len(answer) < 200 and "error" not in answer.lower():
                print("\n[NOTE] Note: Response seems short. You might want to ask a more specific question.")
            
        except KeyboardInterrupt:
            print("\n\n[GOODBYE] Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            print("Continuing...")

async def main():
    """Main entry point"""
    await interactive_chat()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[GOODBYE] Goodbye!")
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")