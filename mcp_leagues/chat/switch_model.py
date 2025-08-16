#!/usr/bin/env python3
"""
Model Switching Utility
Easily change the DEFAULT_MODEL in your .env file
"""

import os
import re

ENV_FILE = "../../.env"  # Use main project .env file

MODELS = {
    "1": ("anthropic/claude-3.5-haiku", "Fast & Cheap - Good for testing"),
    "2": ("anthropic/claude-3.5-sonnet", "Balanced - Best overall"),
    "3": ("openai/gpt-4-turbo", "Creative - Good for complex tasks"),
    "4": ("meta-llama/llama-3.1-8b-instruct", "Budget - Cheapest option"),
    "5": ("openai/gpt-oss-20b:free", "Free model - No cost"),
    "6": ("anthropic/claude-3-opus", "Premium - Most powerful (expensive)")
}

def read_env_file():
    """Read current .env file"""
    if not os.path.exists(ENV_FILE):
        print(f"❌ {ENV_FILE} file not found!")
        return None
    
    with open(ENV_FILE, 'r') as f:
        return f.read()

def get_current_model(content):
    """Extract current model from .env content"""
    match = re.search(r'^OPENROUTER_MODEL=(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Not found"

def update_model(content, new_model):
    """Update the OPENROUTER_MODEL in .env content"""
    # Replace the active OPENROUTER_MODEL line
    pattern = r'^OPENROUTER_MODEL=.+$'
    replacement = f'OPENROUTER_MODEL={new_model}'
    
    updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    return updated_content

def save_env_file(content):
    """Save updated content to .env file"""
    with open(ENV_FILE, 'w') as f:
        f.write(content)

def main():
    print("OpenRouter Model Switcher")
    print("=" * 40)
    
    # Read current .env
    content = read_env_file()
    if not content:
        return
    
    # Show current model
    current_model = get_current_model(content)
    print(f"Current model: {current_model}")
    print()
    
    # Show available models
    print("Available models:")
    for key, (model, description) in MODELS.items():
        current_marker = " (CURRENT)" if model == current_model else ""
        print(f"{key}. {model}")
        print(f"   {description}{current_marker}")
        print()
    
    # Get user choice
    choice = input("Choose model (1-6) or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        print("Cancelled")
        return
    
    if choice not in MODELS:
        print("Invalid choice")
        return
    
    # Update model
    new_model, description = MODELS[choice]
    
    if new_model == current_model:
        print(f"Model {new_model} is already active")
        return
    
    # Confirm change
    print(f"\nChanging model to: {new_model}")
    print(f"Description: {description}")
    confirm = input("Confirm? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    # Update .env file
    try:
        updated_content = update_model(content, new_model)
        save_env_file(updated_content)
        print(f"SUCCESS: Model updated to: {new_model}")
        print("NOTE: Restart any running scripts to use the new model")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()