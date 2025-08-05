# La Liga Team Stats & Standings Data Checklist

This checklist outlines every piece of data you can reliably get for Spanish La Liga team statistics and league standings using ESPN's API. Use this as a guide for designing queries for your MCP.

---

### **Data Source Details**

* **Method**: `GET` (REST API)
* **Base URL**: `https://site.api.espn.com/apis/v2/sports/soccer/`
* **League Code**: `esp.1` (Spanish La Liga)
* **Endpoint**: `/standings`
* **Parameters**: 
  - `season`: Season year (e.g., "2024" for 2024-25 season)
* **Full URL Example**: `https://site.api.espn.com/apis/v2/sports/soccer/esp.1/standings?season=2024`
* **Data Format**: JSON
* **Headers Required**: User-Agent header to mimic browser request
* **Update Frequency**: Updated after each matchday

---

### **Season Metadata**
- [ ] **Season Year**: "2024" (represents 2024-25 season)
- [ ] **League Name**: "Spanish La Liga" (LALIGA)
- [ ] **Total Teams**: 20 teams
- [ ] **Total Games**: 38 games per team (380 total matches)
- [ ] **Competition Format**: Round-robin, home and away
- [ ] **Points System**: 3 points for win, 1 for draw, 0 for loss

---

### **Team Information**

#### **Complete Team List (2024-25)**
- [ ] **Barcelona** (ID: 83) - Champions League
- [ ] **Real Madrid** (ID: 86) - Champions League
- [ ] **Atlético Madrid** (ID: 1068) - Champions League
- [ ] **Athletic Club** (ID: 93) - Champions League
- [ ] **Villarreal** (ID: 102) - Champions League
- [ ] **Real Betis** (ID: 244) - Europa League
- [ ] **Celta Vigo** (ID: 85) - Europa League
- [ ] **Rayo Vallecano** (ID: 101) - Conference League qualifying
- [ ] **Osasuna** (ID: 97)
- [ ] **Mallorca** (ID: 84)
- [ ] **Real Sociedad** (ID: 89)
- [ ] **Valencia** (ID: 94)
- [ ] **Getafe** (ID: 2922)
- [ ] **Espanyol** (ID: 88)
- [ ] **Alavés** (ID: 96)
- [ ] **Girona** (ID: 9812)
- [ ] **Sevilla** (ID: 243)
- [ ] **Leganés** (ID: 17534) - Relegation
- [ ] **Las Palmas** (ID: 98) - Relegation
- [ ] **Real Valladolid** (ID: 95) - Relegation

---

### **League Statistics (Per Team)**

#### **Core Statistics**
- [ ] **Position (#)**: League ranking (1-20)
- [ ] **Games Played (P)**: Total matches played (38)
- [ ] **Wins (W)**: Total victories
- [ ] **Draws (D)**: Total draws
- [ ] **Losses (L)**: Total defeats
- [ ] **Points (Pts)**: Total points accumulated
- [ ] **Goals For (GF)**: Total goals scored
- [ ] **Goals Against (GA)**: Total goals conceded
- [ ] **Goal Difference (GD)**: Goals for minus goals against

#### **Sample Team Record**
```
1   Barcelona                 83    38   28   4    6    102   39    +63   88    Champions League
```

---

### **Qualification & Competition Notes**

#### **European Competition Qualification**
- [ ] **Champions League**: Top 4 positions (1st-4th)
- [ ] **Europa League**: 5th-6th positions + cup winners
- [ ] **Conference League**: 7th position qualifying

#### **Relegation Information**
- [ ] **Relegation Zone**: Bottom 3 positions (18th-20th)
- [ ] **Segunda División**: Teams relegated to second tier

---

**Last Updated**: February 5, 2025  
**Data Source**: ESPN Soccer API  
**League**: Spanish La Liga (esp.1)  
**Endpoint**: `/standings` with season parameter