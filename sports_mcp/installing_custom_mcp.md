# Custom MCP Server Installation Guide for Claude Code

**Version:** 1.0  
**Date:** August 2025  
**Platform:** Windows (Claude Code)

---

## **Prerequisites**

### **Required Software**
- **Claude Code** installed and working
- **Python 3.10+** installed and accessible via `python` command
- **MCP SDK** installed: `pip install "mcp[cli]" httpx`

### **Required Files**
- Your custom MCP server Python file (e.g., `wnba_mcp.py`)
- Server must use FastMCP format with proper async/await structure

---

## **Installation Process**

### **Step 1: Set Up MCP Servers Folder**

1. **Create dedicated MCP folder**:
   ```bash
   mkdir C:\Users\[USERNAME]\Desktop\sports\mcp
   ```

2. **Save your MCP server** in the MCP folder:
   ```
   C:\Users\[USERNAME]\Desktop\sports\mcp\wnba_mcp.py
   ```

3. **Test the server works standalone**:
   ```bash
   python "C:\Users\[USERNAME]\Desktop\sports\mcp\wnba_mcp.py"
   ```
   - Should start and wait (no errors)
   - Press `Ctrl+C` to stop
   - If errors appear, fix them before proceeding

### **Step 2: Add Server to Claude Code**

1. **Open Claude Code** (not Claude Desktop)

2. **Add the MCP server using bash command** (this is critical):
   ```bash
   claude mcp add [SERVER-NAME] python "[FULL-PATH-TO-MCP-FOLDER]\[SCRIPT-NAME].py"
   ```

   **Example:**
   ```bash
   claude mcp add wnba-stats python "C:\Users\fstr2\Desktop\sports\mcp\wnba_mcp.py"
   ```

### **Step 3: Critical Requirements**

**✅ MUST DO:**
- **Use quotes** around the file path: `"C:\Users\..."`
- **Use absolute paths** (not relative paths like `./mcp/wnba_mcp.py`)
- **Run as bash command** in Claude Code (let Claude execute it)
- **Use backslashes** in Windows paths: `C:\Users\...`
- **Put all MCP servers** in the dedicated `mcp\` folder

**❌ WILL FAIL:**
- No quotes: `C:\Users\fstr2\Desktop\sports\mcp\wnba_mcp.py`
- Relative paths: `./mcp/wnba_mcp.py` or `wnba_mcp.py`
- Forward slashes on Windows: `C:/Users/...`
- Mixing MCP servers with other files

### **Step 4: Restart Claude Code**

1. **Completely exit** Claude Code (`Ctrl+C` or close terminal)
2. **Restart** Claude Code: `claude`
3. **Wait for full startup** before testing

---

## **Verification & Testing**

### **Step 1: Check MCP Server Status**
```bash
/mcp
```

**Expected Result:**
```
❯ 1. [SERVER-NAME]  ✔ connected · Enter to view details
```

**If you see:** "No MCP servers configured" → See Troubleshooting section

### **Step 2: Test the Functionality**
Ask Claude a question that would use your tool:

**Example:**
```
What are the current WNBA standings?
```

**Expected Behavior:**
- Claude automatically calls your MCP tool
- Returns formatted results with natural language context
- Much better than raw Python script output

---

## **Recommended Folder Structure**

```
C:\Users\[USERNAME]\Desktop\sports\
├── mcp\                           # All MCP servers here
│   ├── wnba_mcp.py               # WNBA standings server
│   ├── betting_odds_mcp.py       # Future: betting odds server
│   └── team_stats_mcp.py         # Future: team statistics server
├── testing\                      # Regular Python test scripts
│   ├── nomcp.py                  # Non-MCP versions for comparison
│   └── other_tests.py
├── data\                         # Data files, databases
└── docs\                         # Documentation
```

---

## **Common Issues & Solutions**

### **Issue 1: "No MCP servers configured"**

**Causes:**
- Path not quoted properly
- Server script has errors
- Claude Code not restarted after installation

**Solutions:**
1. Check the bash command worked: Look for "Added stdio MCP server..." message
2. Test server directly: `python "C:\Users\[USERNAME]\Desktop\sports\mcp\[script].py"`
3. Restart Claude Code completely
4. Verify path exists: `dir "C:\Users\[USERNAME]\Desktop\sports\mcp\[script].py"`

### **Issue 2: Server shows "disconnected" or errors**

**Causes:**
- Missing Python dependencies
- Syntax errors in server code
- Incorrect FastMCP usage

**Solutions:**
1. Install dependencies: `pip install "mcp[cli]" httpx`
2. Test server standalone first
3. Check server logs for specific errors
4. Verify FastMCP format is correct

### **Issue 3: Tool not being called by Claude**

**Causes:**
- Tool name doesn't match what Claude expects
- Tool description unclear
- Server connected but tool registration failed

**Solutions:**
1. Check tool name and description are clear
2. Use `/mcp` → Select server → View tool details
3. Ask Claude explicitly to use the tool: "Use the get_wnba_standings tool"

---

## **Managing Multiple MCP Servers**

### **Adding New Servers:**
```bash
claude mcp add [new-server-name] python "C:\Users\[USERNAME]\Desktop\sports\mcp\[new-script].py"
```

### **Removing Servers:**
```bash
claude mcp remove [server-name]
```

### **Listing All Servers:**
```bash
claude mcp list
```

### **Checking Server Health:**
```bash
/mcp
```

---

## **Best Practices**

### **File Naming:**
- Use descriptive names: `wnba_mcp.py`, `nfl_odds_mcp.py`
- Keep `_mcp.py` suffix for clarity
- Avoid spaces in filenames

### **Server Organization:**
- One server per sport/data source
- Group related tools in same server
- Keep servers focused and lightweight

### **Testing Workflow:**
1. **Test Python script first:** `python script.py`
2. **Add to MCP:** `claude mcp add ...`
3. **Restart Claude Code**
4. **Verify connection:** `/mcp`
5. **Test with Claude:** Ask natural language questions

---

## **Example Commands Reference**

### **Full Installation Example:**
```bash
# 1. Create folder
mkdir C:\Users\fstr2\Desktop\sports\mcp

# 2. Test server
python "C:\Users\fstr2\Desktop\sports\mcp\wnba_mcp.py"

# 3. Add to Claude Code
claude mcp add wnba-stats python "C:\Users\fstr2\Desktop\sports\mcp\wnba_mcp.py"

# 4. Restart Claude Code
^C
claude

# 5. Verify
/mcp
```

### **For Your Sports Betting Platform:**
```bash
# Future MCP servers you might add:
claude mcp add nfl-odds python "C:\Users\fstr2\Desktop\sports\mcp\nfl_odds_mcp.py"
claude mcp add team-stats python "C:\Users\fstr2\Desktop\sports\mcp\team_stats_mcp.py"
claude mcp add betting-tips python "C:\Users\fstr2\Desktop\sports\mcp\betting_tips_mcp.py"
```

---

**Next Steps:** Use this process to add more MCP servers for your sports betting platform as you develop them!