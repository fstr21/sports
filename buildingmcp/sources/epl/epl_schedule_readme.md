# EPL Schedule Data Checklist

This checklist outlines every piece of data you can reliably get for upcoming English Premier League fixtures by scraping ESPN's schedule page. Use this as a guide for designing queries for your MCP.

---

### **Data Source Details**

* **Method**: `GET` (Web Scraping)
* **Source URL**: `https://www.espn.com/soccer/schedule/_/league/eng.1`
* **League Code**: `eng.1` (English Premier League)
* **Data Format**: HTML parsing → structured output
* **Update Frequency**: Real-time updates as fixtures are scheduled/rescheduled
* **Headers Required**: User-Agent header to mimic browser request

---

### **Schedule Metadata**
- [ ] **League**: English Premier League
- [ ] **League Code**: "eng.1"
- [ ] **Source URL**: Full ESPN schedule page URL
- [ ] **Scraping Timestamp**: When the data was extracted
- [ ] **Total Fixtures Found**: Number of upcoming games discovered

---

### **Date Information**

#### **Date Headers**
- [ ] **Date Format**: "Friday, August 15, 2025"
- [ ] **Relative Dates**: "Today", "Tomorrow"
- [ ] **Day of Week**: Full day names (Monday, Tuesday, etc.)
- [ ] **Date Grouping**: Games grouped by date
- [ ] **Multiple Date Support**: Handles fixtures across multiple days

#### **Date Extraction Methods**
- [ ] **Primary Method**: Table__Title class elements
- [ ] **Fallback Method 1**: Previous sibling divs with date keywords
- [ ] **Fallback Method 2**: Header tags (h2, h3, h4) with date content
- [ ] **Keyword Detection**: Searches for date-related terms
- [ ] **Date Keywords**: today, tomorrow, jan-dec, monday-sunday

---

### **Fixture Information**

#### **Team Details (Per Match)**
- [ ] **Away Team Name**: "Liverpool" (extracted from team links)
- [ ] **Away Team ID**: "364" (unique ESPN identifier)
- [ ] **Home Team Name**: "AFC Bournemouth"
- [ ] **Home Team ID**: "349" (unique ESPN identifier)
- [ ] **Match Format**: "Away Team at Home Team"

#### **Game Scheduling**
- [ ] **Game Time**: "3:00 PM" (local time format)
- [ ] **Game ID**: "740596" (unique ESPN game identifier)
- [ ] **Game Links**: Direct links to ESPN game pages
- [ ] **Venue Information**: Stadium details when available

#### **Team ID Extraction**
- [ ] **URL Pattern**: `/soccer/team/_/id/{team_id}/`
- [ ] **Regex Matching**: Reliable extraction from href attributes
- [ ] **ID Reliability**: ~95% success rate for team identification
- [ ] **Fallback Handling**: "N/A" when ID extraction fails

---

### **Data Structure & Parsing**

#### **HTML Structure Analysis**
- [ ] **ResponsiveTable Elements**: Primary data containers
- [ ] **Generic Table Fallback**: Secondary parsing method
- [ ] **Team Link Analysis**: Tertiary extraction approach
- [ ] **Multiple Parsing Strategies**: Robust fallback system

#### **Table Structure**
- [ ] **Table Body**: `<tbody>` elements containing fixture rows
- [ ] **Table Rows**: `<tr>` elements for individual matches
- [ ] **Table Cells**: `<td>` elements with team and time data
- [ ] **Cell Structure**: Away team, Home team, Time/Game info

#### **Link Pattern Recognition**
- [ ] **Team Links**: `/soccer/team/_/id/\d+/` pattern
- [ ] **Game Links**: `gameId/\d+` pattern
- [ ] **Schedule Links**: Direct links to fixture details
- [ ] **Team Profile Links**: Links to team pages

---

### **Team Name Processing**

#### **Name Extraction Methods**
- [ ] **Primary**: team-name class elements
- [ ] **Secondary**: URL slug conversion
- [ ] **Tertiary**: Span text extraction
- [ ] **Fallback**: Cell text cleaning

#### **Team Name Mapping**
- [ ] **URL Slug Processing**: Convert kebab-case to proper names
- [ ] **Common Teams**: Liverpool, Chelsea, Manchester United, etc.
- [ ] **Name Standardization**: Consistent formatting across extractions
- [ ] **Special Characters**: Handle apostrophes and hyphens

---

### **Error Handling & Reliability**

#### **Robust Parsing**
- [ ] **Multiple Extraction Strategies**: 3-tier fallback system
- [ ] **Exception Handling**: Graceful failure for individual fixtures
- [ ] **Data Validation**: Verify extracted data quality
- [ ] **Debug Information**: Detailed logging for troubleshooting

#### **Common Issues & Solutions**
- [ ] **Page Structure Changes**: Multiple parsing approaches
- [ ] **Missing Data**: Fallback values ("N/A", "TBD")
- [ ] **Network Errors**: Request timeout and retry handling
- [ ] **Rate Limiting**: User-Agent headers to avoid blocking

---

### **Sample Output Format**

#### **Successful Extraction**
```
--- EPL Upcoming Fixtures ---

📅 Date information found on page:
   - Friday, August 15, 2025
   - Saturday, August 16, 2025

📅 Friday, August 15, 2025
--------------------------------------------------
⚽ Liverpool (ID: 364) at AFC Bournemouth (ID: 349)
   🕐 3:00 PM | Game ID: 740596

⚽ Aston Villa (ID: 362) at Newcastle United (ID: 361)
   🕐 7:30 AM | Game ID: 740597
```

#### **Data Structure Per Fixture**
```json
{
  "date": "Friday, August 15, 2025",
  "away_team": {
    "name": "Liverpool",
    "id": "364"
  },
  "home_team": {
    "name": "AFC Bournemouth", 
    "id": "349"
  },
  "game_time": "3:00 PM",
  "game_id": "740596"
}
```

---

### **Technical Implementation**

#### **Required Libraries**
- [ ] **requests**: HTTP requests to ESPN
- [ ] **BeautifulSoup**: HTML parsing and extraction
- [ ] **re**: Regular expression pattern matching
- [ ] **Standard Libraries**: Built-in Python modules

#### **Request Configuration**
- [ ] **User-Agent Header**: Required to avoid blocking
- [ ] **Timeout Settings**: 15-second request timeout
- [ ] **Error Handling**: HTTP status code validation
- [ ] **Response Processing**: HTML content parsing

#### **Parsing Strategy**
- [ ] **Primary**: ResponsiveTable class elements
- [ ] **Secondary**: Generic table elements
- [ ] **Tertiary**: Team link pattern analysis
- [ ] **Date Context**: Associate fixtures with dates

---

### **Data Quality & Reliability**

#### **Highly Reliable Data**
✅ **Team Names**: Consistent extraction from multiple sources  
✅ **Team IDs**: Reliable ESPN identifier extraction  
✅ **Game IDs**: Unique fixture identifiers  
✅ **Game Times**: Accurate scheduling information  

#### **Moderately Reliable Data**
⚠️ **Date Information**: Depends on ESPN page structure  
⚠️ **Venue Details**: Not always available in schedule view  
⚠️ **TV Coverage**: Limited information in basic schedule  

#### **Potential Issues**
❌ **Page Structure Changes**: ESPN may modify HTML structure  
❌ **Rate Limiting**: Too many requests may be blocked  
❌ **Regional Differences**: Time zones and formatting variations  

---

### **Use Cases for Sports Analysis**

#### **Fixture Planning**
- [ ] **Upcoming Matches**: Complete fixture list with dates
- [ ] **Team Scheduling**: When specific teams play next
- [ ] **Game ID Collection**: Identifiers for detailed match data
- [ ] **Venue Planning**: Home/away fixture identification

#### **Betting Applications**
- [ ] **Pre-Match Analysis**: Upcoming fixture identification
- [ ] **Odds Preparation**: Games requiring betting line setup
- [ ] **Schedule Monitoring**: Track fixture changes and updates
- [ ] **Multi-Game Parlays**: Identify same-day fixtures

#### **Fantasy Sports**
- [ ] **Lineup Planning**: Upcoming player availability
- [ ] **Captain Selection**: Home/away advantage consideration
- [ ] **Transfer Planning**: Fixture difficulty assessment
- [ ] **Gameweek Strategy**: Multiple fixture identification

#### **Database Integration**
- [ ] **Fixture Database**: Store upcoming match schedules
- [ ] **Team Tracking**: Monitor specific team fixtures
- [ ] **Historical Patterns**: Analyze scheduling trends
- [ ] **Cross-Reference**: Link with other ESPN APIs using IDs

---

### **Advanced Features**

#### **Multi-Day Support**
- [ ] **Date Range**: Handles fixtures across multiple days
- [ ] **Chronological Order**: Maintains proper date sequence
- [ ] **Date Grouping**: Organizes fixtures by date
- [ ] **Weekend Fixtures**: Special handling for match days

#### **Flexible Parsing**
- [ ] **Adaptive Structure**: Handles ESPN page changes
- [ ] **Multiple Formats**: Works with different table structures
- [ ] **Fallback Methods**: Ensures data extraction success
- [ ] **Debug Output**: Detailed parsing information

---

### **Integration Examples**

#### **MCP Tool Integration**
```python
def get_epl_fixtures():
    """Get upcoming EPL fixtures with team IDs and game IDs"""
    scraper = EPLScheduleScraper()
    fixtures = scraper.scrape_epl_schedule()
    return {
        "fixtures": fixtures,
        "last_updated": datetime.now().isoformat(),
        "source": "ESPN Schedule Page"
    }
```

#### **Database Storage**
```sql
CREATE TABLE epl_fixtures (
    game_id VARCHAR(20) PRIMARY KEY,
    game_date DATE,
    game_time TIME,
    home_team_id VARCHAR(10),
    away_team_id VARCHAR(10),
    home_team_name VARCHAR(100),
    away_team_name VARCHAR(100),
    scraped_at TIMESTAMP
);
```

---

**Last Updated**: February 5, 2025  
**Data Source**: ESPN Schedule Page (Web Scraping)  
**League**: English Premier League (eng.1)  
**Method**: HTML parsing with multiple fallback strategies  
**Reliability**: High for fixture identification, moderate for date extraction