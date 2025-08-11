import json

with open('espn ids/espn_team_ids.json') as f:
    data = json.load(f)
    
print("Keys:", list(data.keys()))
print("MLB keys:", list(data.get('MLB', {}).keys()) if 'MLB' in data else 'No MLB key')
if 'MLB' in data:
    print("MLB teams count:", data['MLB'].get('count', 0))
    print("MLB teams:", list(data['MLB'].get('teams', {}).keys())[:5])
