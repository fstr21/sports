# Chronulus MCP Testing Environment

This folder contains all testing and experimentation with the Chronulus MCP server for sports betting forecasting. Everything is contained here for easy cleanup if needed.

## Overview

**Chronulus MCP**: AI forecasting and prediction server that integrates with Claude for advanced analytical capabilities.

**Purpose**: Test forecasting capabilities for sports betting predictions without affecting production systems.

## Setup Instructions

### 1. Installation Options

```bash
# Option A: PyPI Installation
pip install chronulus-mcp

# Option B: uvx (Automated)
uvx chronulus-mcp

# Option C: Docker (Custom build)
# See docker setup in this folder
```

### 2. Configuration Requirements

- **API Key**: Chronulus API key required
- **Config File**: 
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

### 3. Integration Points

**Potential Use Cases**:
- MLB game outcome predictions
- Player performance forecasting
- Betting odds trend analysis
- Value bet identification

## Testing Structure

```
chronulus_forecasting/
├── README.md                 # This file
├── setup/                    # Installation scripts
├── config/                   # Configuration files
├── tests/                    # Test scripts
├── data/                     # Sample data for testing
└── results/                  # Test results and analysis
```

## Goals

1. **Evaluate Forecasting Quality**: Test accuracy of sports predictions
2. **Integration Feasibility**: Check compatibility with existing MCP infrastructure
3. **Performance Assessment**: Measure speed and reliability
4. **Value Analysis**: Determine if it improves betting insights

## Status

- [ ] Initial setup and installation
- [ ] Configuration with existing sports data
- [ ] Test forecasting capabilities
- [ ] Evaluate integration potential
- [ ] Decision on production integration

## Cleanup

If testing doesn't meet expectations, simply delete this entire `chronulus_forecasting` folder - no impact on production systems.