#!/usr/bin/env python3
"""
Humanize AI Analysis - Make Chronulus output sound more natural
Takes formal AI analysis and rewrites it in casual, experienced bettor tone
"""
import json
import re
from pathlib import Path

def humanize_text(ai_text):
    """
    Transform formal AI analysis into natural, conversational sports betting language
    """
    
    # Common AI phrases to replace
    ai_to_human_replacements = {
        # Formal -> Casual
        "Based on my analysis": "Look,",
        "Upon examination": "When I dig into",
        "It is important to note": "Here's the thing -",
        "In conclusion": "Bottom line:",
        "Furthermore": "Plus,",
        "Additionally": "Also,",
        "However": "But",
        "Nevertheless": "That said,",
        "Therefore": "So",
        "Consequently": "Which means",
        "Subsequently": "Then",
        "In summary": "To wrap it up:",
        
        # Academic -> Betting terms
        "probability assessment": "my read",
        "statistical analysis": "looking at the numbers",
        "empirical evidence": "what I'm seeing",
        "comprehensive evaluation": "breaking it down",
        "substantial deviation": "way off",
        "significant correlation": "strong connection",
        "marginal difference": "slight edge",
        "considerable variance": "big swings",
        
        # Formal confidence -> Casual confidence
        "high degree of confidence": "pretty damn sure",
        "moderate confidence": "somewhat confident",
        "low confidence": "not feeling great about it",
        "uncertainty": "it's a coin flip",
        
        # Sports betting specific
        "betting recommendation": "my play",
        "market inefficiency": "the books are off",
        "value proposition": "there's value here",
        "expected value": "long-term profit",
        "recent performance trend": "how they've been playing",
        "season-long metrics": "full-year numbers",
        "home field advantage": "playing at home",
        
        # Remove AI hedging
        "appears to": "",
        "seems to": "",
        "potentially": "",
        "possibly": "maybe",
        "arguably": "",
        "relatively": "",
        "somewhat": "",
        "tend to": "",
        "generally": "",
    }
    
    # Apply replacements
    humanized = ai_text
    for ai_phrase, human_phrase in ai_to_human_replacements.items():
        humanized = re.sub(ai_phrase, human_phrase, humanized, flags=re.IGNORECASE)
    
    # Make it more conversational
    conversational_patterns = [
        # Add contractions
        (r"\bis not\b", "isn't"),
        (r"\bdo not\b", "don't"),
        (r"\bcannot\b", "can't"),
        (r"\bwill not\b", "won't"),
        (r"\bwould not\b", "wouldn't"),
        (r"\bshould not\b", "shouldn't"),
        (r"\bhave not\b", "haven't"),
        (r"\bhas not\b", "hasn't"),
        (r"\bdid not\b", "didn't"),
        (r"\bwere not\b", "weren't"),
        (r"\bwas not\b", "wasn't"),
        (r"\bare not\b", "aren't"),
        (r"\bthey are\b", "they're"),
        (r"\bthat is\b", "that's"),
        (r"\bit is\b", "it's"),
        
        # More natural phrasing
        (r"The Colorado Rockies", "The Rockies"),
        (r"Pittsburgh Pirates", "Pirates"),
        (r"the aforementioned", "this"),
        (r"the previously mentioned", "the"),
        (r"as previously stated", "like I said"),
        (r"in order to", "to"),
        (r"due to the fact that", "because"),
        (r"for the reason that", "because"),
        (r"in the event that", "if"),
        (r"at this point in time", "right now"),
        (r"in the near future", "soon"),
        
        # Betting slang
        (r"positive expected value", "profitable long-term"),
        (r"negative expected value", "losing bet long-term"),
        (r"significant edge", "solid edge"),
        (r"minimal edge", "tiny edge"),
        (r"substantial risk", "risky as hell"),
        (r"moderate risk", "some risk"),
        (r"low risk", "safe bet"),
    ]
    
    for pattern, replacement in conversational_patterns:
        humanized = re.sub(pattern, replacement, humanized, flags=re.IGNORECASE)
    
    # Add some betting personality
    personality_additions = [
        # Start with confidence
        (r"^(I predict|My prediction)", "I'm thinking"),
        (r"^(The analysis shows|Analysis indicates)", "What I'm seeing is"),
        (r"^(The data suggests)", "The numbers tell me"),
        
        # Add emphasis
        (r"very important", "crucial"),
        (r"extremely significant", "huge factor"),
        (r"highly unlikely", "not happening"),
        (r"very likely", "almost certain"),
        
        # More natural transitions
        (r"Moving on to", "Now,"),
        (r"Turning our attention to", "Looking at"),
        (r"With regard to", "As for"),
    ]
    
    for pattern, replacement in personality_additions:
        humanized = re.sub(pattern, replacement, humanized, flags=re.IGNORECASE)
    
    # Clean up extra spaces and formatting
    humanized = re.sub(r'\s+', ' ', humanized)
    humanized = re.sub(r'\s*,\s*', ', ', humanized)
    humanized = re.sub(r'\s*\.\s*', '. ', humanized)
    
    return humanized.strip()

def process_json_analysis(json_file_path):
    """Process JSON file and humanize expert analyses"""
    
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Humanize expert reasoning
    if 'expert_analyses' in data:
        for expert in data['expert_analyses']:
            if 'detailed_reasoning' in expert and expert['detailed_reasoning']:
                expert['detailed_reasoning'] = humanize_text(expert['detailed_reasoning'])
                expert['humanized'] = True
    
    # Save humanized version
    output_path = json_file_path.replace('.json', '_humanized.json')
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return output_path

def process_markdown_analysis(md_file_path):
    """Process Markdown file and humanize content"""
    
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and humanize expert reasoning sections
    expert_pattern = r'(\*\*Detailed Expert Reasoning\*\*:\n\n)(.*?)(\n\n---)'
    
    def humanize_expert_section(match):
        prefix = match.group(1)
        expert_text = match.group(2)
        suffix = match.group(3)
        
        humanized_text = humanize_text(expert_text)
        return f"{prefix}{humanized_text}{suffix}"
    
    humanized_content = re.sub(expert_pattern, humanize_expert_section, content, flags=re.DOTALL)
    
    # Also humanize any other analysis sections
    analysis_sections = [
        'Key Insights',
        'Market Efficiency', 
        'Risk Factors'
    ]
    
    for section in analysis_sections:
        section_pattern = f'(### {section}.*?\n\n)(.*?)(\n\n###|\n\n---|\Z)'
        humanized_content = re.sub(
            section_pattern, 
            lambda m: m.group(1) + humanize_text(m.group(2)) + m.group(3),
            humanized_content,
            flags=re.DOTALL
        )
    
    # Save humanized version
    output_path = md_file_path.replace('.md', '_humanized.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(humanized_content)
    
    return output_path

def main():
    """Find latest analysis files and humanize them"""
    
    results_dir = Path(__file__).parent / 'results'
    
    if not results_dir.exists():
        print("No results directory found. Run an analysis first.")
        return
    
    # Find latest files
    json_files = list(results_dir.glob('comprehensive_analysis_*.json'))
    md_files = list(results_dir.glob('comprehensive_analysis_*.md'))
    
    if not json_files and not md_files:
        print("No analysis files found to humanize.")
        return
    
    # Get latest files
    if json_files:
        latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
        print(f"Humanizing JSON: {latest_json.name}")
        humanized_json = process_json_analysis(latest_json)
        print(f"Created: {Path(humanized_json).name}")
    
    if md_files:
        latest_md = max(md_files, key=lambda x: x.stat().st_mtime)
        print(f"Humanizing Markdown: {latest_md.name}")
        humanized_md = process_markdown_analysis(latest_md)
        print(f"Created: {Path(humanized_md).name}")
    
    print("\nHumanization complete! The '_humanized' versions should sound much more natural.")

if __name__ == "__main__":
    main()