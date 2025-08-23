# 🧠 Chronulus Railway MCP Testing

This folder contains all testing scripts and results for the Railway-hosted Chronulus MCP server.

## 📁 Structure

```
testing_chronulus_railway/
├── README.md                    # This file
├── test_railway_chronulus.py    # Main testing script
└── results/                     # Test results with timestamps
    ├── health_check_TIMESTAMP.json
    ├── health_check_TIMESTAMP.md
    ├── hardcoded_dodgers_padres_TIMESTAMP.json
    └── hardcoded_dodgers_padres_TIMESTAMP.md
```

## 🚀 Usage

```bash
cd testing_chronulus_railway
python test_railway_chronulus.py
```

## 🎯 Tests

1. **Health Check**: Verifies Railway server is running and Chronulus SDK is available
2. **Hard-coded Analysis**: Tests with Dodgers @ Padres game data
   - Single expert analysis (cost ~$0.02-0.05)
   - Analyzes all betting markets (Moneyline, Run Line, Total)
   - Detailed explanations requested

## 📊 Results

Results are automatically saved with timestamps:
- **JSON files**: Raw API responses 
- **MD files**: Human-readable analysis with extracted insights

## 🌐 Server

- **URL**: https://chronulusmcp-production.up.railway.app/mcp
- **Protocol**: JSON-RPC 2.0 MCP
- **Tools**: `getChronulusHealth`, `testChronulusHardcoded`

## 🧹 Cleanup

To remove all testing files:
```bash
# From project root
rm -rf testing_chronulus_railway/
```