Directory Structure
bash
Copy
Edit
your_project/
├── data/
│   └── team_aliases.json     # <-- You maintain this file
├── modules/
│   └── normalization/
│       └── team_normalizer.py
🧱 1. team_normalizer.py
📁 modules/normalization/team_normalizer.py

python
Copy
Edit
import json
from pathlib import Path
from rapidfuzz import process

class TeamNormalizer:
    def __init__(self, league: str = "NFL", fuzzy: bool = True):
        self.league = league.upper()
        self.fuzzy = fuzzy
        self.mapping = self._load_mapping()
        self.reverse_map = self._build_reverse_map()

    def _load_mapping(self) -> dict:
        path = Path("data/team_aliases.json")
        with path.open() as f:
            all_data = json.load(f)
        return all_data.get(self.league, {})

    def _build_reverse_map(self) -> dict:
        reverse = {}
        for canonical_name, aliases in self.mapping.items():
            for alias in aliases:
                reverse[alias.strip().lower()] = canonical_name
        return reverse

    def normalize(self, name: str) -> str:
        key = name.strip().lower()
        if key in self.reverse_map:
            return self.reverse_map[key]
        elif self.fuzzy:
            return self._fuzzy_match(key)
        else:
            return name

    def _fuzzy_match(self, raw_name: str) -> str:
        candidates = list(self.reverse_map.keys())
        match, score, _ = process.extractOne(raw_name, candidates)
        if score > 85:
            return self.reverse_map[match]
        return raw_name
📄 2. team_aliases.json
📁 data/team_aliases.json

json
Copy
Edit
{
  "NFL": {
    "San Francisco 49ers": ["49ers", "SF", "S.F.", "San Fran"],
    "Kansas City Chiefs": ["KC", "Chiefs", "K.C.", "Kansas City"]
  },
  "NBA": {
    "Los Angeles Lakers": ["LAL", "Lakers", "LA Lakers"],
    "Boston Celtics": ["BOS", "Celtics", "Boston"]
  }
}
✍️ You maintain this file — add aliases as needed when new teams or bad data shows up.

🧪 3. Usage Example
python
Copy
Edit
from modules.normalization.team_normalizer import TeamNormalizer

normalizer = TeamNormalizer(league="NFL")

print(normalizer.normalize("KC"))         # ➝ "Kansas City Chiefs"
print(normalizer.normalize("s.f."))       # ➝ "San Francisco 49ers"
print(normalizer.normalize("Kansas City"))# ➝ "Kansas City Chiefs"
print(normalizer.normalize("Chicago"))    # ➝ "Chicago" (fallback if not in list)
📋 Instructions for You to Add to Your Project Doc
You can copy-paste this or adapt it for your checklist:

✅ Team Name Normalization MCP
Module: team_normalizer.py
Location: modules/normalization/
Data Source: data/team_aliases.json

Purpose:
Convert messy or inconsistent team names into a standardized format.

Works across leagues (NFL, NBA, etc.).

Supports fuzzy matching (e.g., “s.f.” → “San Francisco 49ers”).

Setup Steps:
Place team_normalizer.py in your codebase under modules/normalization/.

Create and maintain data/team_aliases.json with all known canonical names and aliases.

Anywhere in your pipeline, call:

python
Copy
Edit
TeamNormalizer(league="NFL").normalize("KC")
Update the alias file any time you discover new data inconsistencies.

Future Improvements:
Add team_id fields for database integration.

Include player name normalization.

Link to external data providers (like ESPN IDs).