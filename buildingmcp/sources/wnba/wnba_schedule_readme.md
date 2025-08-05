# WNBA Game Data Checklist

This checklist outlines every piece of data you can reliably get for a single WNBA game based on the provided JSON source. Use this as a guide for designing queries for your MCP.

---

### **Data Source Details**

* **Method**: `GET`
* **Source URL**: `http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard`
* **Parameters**: `{"dates": "20250805"}`

---

### **Game Information**
- [ ] **Game ID**: "401736296"
- [ ] **Full Game Name**: "Dallas Wings at New York Liberty"
- [ ] **Game Date (UTC)**: "2025-08-05T23:00Z"
- [ ] **Game Status**: "Scheduled"
- [ ] **Venue Name**: "Barclays Center"
- [ ] **Venue City**: "Brooklyn"
- [ ] **Venue State**: "NY"
- [ ] **Broadcast Details**: "NBA TV, WNBA League Pass"

### **Betting Odds**
- [ ] **Odds Provider**: "ESPN BET"
- [ ] **Betting Line Summary**: "NY -9.5"
- [ ] **Point Spread**: -9.5
- [ ] **Over/Under Total**: 173.5

---

### **Home Team Details (New York Liberty)**
- [ ] **Team ID**: "9"
- [ ] **Team Name**: "New York Liberty"
- [ ] **Overall Record**: "18-10"
- [ ] **Moneyline Odds**: -450
- [ ] **Spread Odds**: -115.0
- [ ] **Team Statistics**:
    - [ ] Total Rebounds: "959"
    - [ ] Average Rebounds: "34.3"
    - [ ] Total Assists: "611"
    - [ ] Field Goals Attempted: "1865"
    - [ ] Field Goals Made: "845"
    - [ ] Field Goal Percentage: "45.3"
    - [ ] Free Throw Percentage: "83.9"
    - [ ] Free Throws Attempted: "565"
    - [ ] Free Throws Made: "474"
    - [ ] Total Points: "2434"
    - [ ] Three Point Percentage: "34.7"
    - [ ] Three Point Field Goals Attempted: "778"
    - [ ] Three Point Field Goals Made: "270"
    - [ ] Average Points: "86.9"
    - [ ] Average Assists: "21.8"
- [ ] **Team Leaders**:
    - [ ] **Points Per Game**:
        - Player Name: "Sabrina Ionescu"
        - Value: "20.4"
    - [ ] **Rebounds Per Game**:
        - Player Name: "Sabrina Ionescu"
        - Value: "4.9"
    - [ ] **Assists Per Game**:
        - Player Name: "Natasha Cloud"
        - Value: "5.8"
    - [ ] **Overall Rating**:
        - Player Name: "Sabrina Ionescu"
        - Value: "20.4 PPG, 4.9 RPG, 5.6 APG, 1.5 SPG, 0.4 BPG"

---

### **Away Team Details (Dallas Wings)**
- [ ] **Team ID**: "3"
- [ ] **Team Name**: "Dallas Wings"
- [ ] **Overall Record**: "8-21"
- [ ] **Moneyline Odds**: 340
- [ ] **Spread Odds**: -105.0
- [ ] **Team Statistics**:
    - [ ] Total Rebounds: "1048"
    - [ ] Average Rebounds: "36.1"
    - [ ] Total Assists: "579"
    - [ ] Field Goals Attempted: "2064"
    - [ ] Field Goals Made: "866"
    - [ ] Field Goal Percentage: "42.0"
    - [ ] Free Throw Percentage: "80.4"
    - [ ] Free Throws Attempted: "562"
    - [ ] Free Throws Made: "452"
    - [ ] Total Points: "2380"
    - [ ] Three Point Percentage: "32.2"
    - [ ] Three Point Field Goals Attempted: "608"
    - [ ] Three Point Field Goals Made: "196"
    - [ ] Average Points: "82.1"
    - [ ] Average Assists: "20.0"
- [ ] **Team Leaders**:
    - [ ] **Points Per Game**:
        - Player Name: "Paige Bueckers"
        - Value: "18.5"
    - [ ] **Rebounds Per Game**:
        - Player Name: "Myisha Hines-Allen"
        - Value: "5.1"
    - [ ] **Assists Per Game**:
        - Player Name: "Paige Bueckers"
        - Value: "5.5"
    - [ ] **Overall Rating**:
        - Player Name: "Paige Bueckers"
        - Value: "18.5 PPG, 3.9 RPG, 5.5 APG, 1.8 SPG, 0.6 BPG"