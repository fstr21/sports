import asyncio
import os
import re
from dotenv import load_dotenv
from openrouter_discord_bridge import OpenRouterDiscordBridge

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..', '..')
env_file = os.path.join(project_root, '.env.local')

if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

def clean_unicode(text):
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()

async def main():
    print('Quick test...')
    bridge = OpenRouterDiscordBridge()
    
    async with bridge:
        messages = await bridge.read_discord_messages('mcp-testing', limit=2)
        for i, msg in enumerate(messages):
            print(f'{i+1}. {clean_unicode(msg.author)}: {clean_unicode(msg.content[:30])}')
        
        result = await bridge.send_discord_message('mcp-testing', 'Test working!')
        print('SUCCESS' if result['success'] else f'FAILED: {result.get("error")}')

asyncio.run(main())
