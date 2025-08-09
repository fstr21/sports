# MCP Usage Guide

## Overview

This project contains two main MCP (Model Context Protocol) implementations:

1. **MagicTunnel** - A smart MCP proxy with intelligent tool discovery
2. **Sports AI MCP** - ESPN sports data and odds API integration

## MagicTunnel Usage

### Quick Start

#### Full Stack Setup (Recommended)
```bash
# Clone and build
cd magictunnel
make build-release-semantic && make pregenerate-embeddings-ollama MAGICTUNNEL_ENV=development

# Run MagicTunnel with Web Dashboard & Supervisor
./magictunnel-supervisor

# Access Web Dashboard
open http://localhost:5173/dashboard

# Test smart discovery via API
curl -X POST http://localhost:3001/v1/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"name": "smart_tool_discovery", "arguments": {"request": "ping google.com"}}'
```

#### Lightweight Setup (MCP Server Only)
```bash
# Run standalone MCP server (no web dashboard)
./magictunnel
```

#### Setup with Smart Discovery (Recommended)
```bash
# Install Ollama (for local semantic search)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull nomic-embed-text

# Build with semantic search support
make build-release-semantic

# Pre-generate embeddings for faster startup
make pregenerate-embeddings-ollama

# Run with smart discovery
make run-release-ollama
```

### Configuration

Create `magictunnel-config.yaml` (see template in the project):

```yaml
server:
  host: "127.0.0.1"
  port: 8080

registry:
  paths: ["./capabilities"]

smart_discovery:
  enabled: true
  tool_selection_mode: "hybrid"  # or "rule_based", "semantic", "llm_based"
  
external_mcp:
  enabled: true
  config_file: "external-mcp-servers.yaml"
```

### Smart Discovery System

MagicTunnel's key innovation is the Smart Tool Discovery system that provides **one intelligent tool** instead of exposing 50+ individual tools:

#### Usage Examples

Instead of knowing exact tool names:
```json
// ❌ Before: Need to know exact tool names
{"name": "network_ping", "arguments": {"host": "google.com"}}
{"name": "filesystem_read", "arguments": {"path": "/etc/hosts"}}
```

Just describe what you want:
```json
// ✅ After: Natural language requests
{"name": "smart_tool_discovery", "arguments": {"request": "ping google.com"}}
{"name": "smart_tool_discovery", "arguments": {"request": "read the hosts file"}}
```

#### Discovery Modes
- **hybrid** (recommended): Combines semantic search (30%), rule-based (15%), and LLM analysis (55%)
- **rule_based**: Fast keyword matching and pattern analysis
- **semantic**: Embedding-based similarity search (requires Ollama or OpenAI)
- **llm_based**: AI-powered tool selection with OpenAI/Anthropic/Ollama APIs

### Web Dashboard

Access the comprehensive web dashboard at `http://localhost:5173/dashboard` for:
- 📊 Real-time monitoring and system status
- 🔧 Tool management and testing
- 📈 Tool usage analytics and discovery rankings
- 📋 Configuration management with validation
- 📝 Live log viewer with filtering and search
- 🔍 Interactive JSON-RPC command testing
- ⚙️ Service control (start/stop/restart)

### Environment Variables

```bash
# Enable debug logging
export RUST_LOG=debug

# Custom config path
export MAGICTUNNEL_CONFIG=./my-config.yaml

# LLM API keys (for smart discovery)
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
export OLLAMA_BASE_URL=http://localhost:11434

# Semantic search configuration
export MAGICTUNNEL_SEMANTIC_ENABLED=true
export MAGICTUNNEL_EMBEDDING_MODEL=text-embedding-3-small
```

## Sports AI MCP Usage

### Setup

```bash
# Set required environment variables
export OPENROUTER_API_KEY=your_openrouter_key_here

# Optional configuration
export OPENROUTER_MODEL=openrouter/auto
export MAX_INPUT_BYTES=10000
export MAX_OUTPUT_TOKENS=700
```

### Running the Server

```bash
# Run the Sports AI MCP server
cd sports_mcp
python sports_ai_mcp.py
```

### Supported Leagues

The Sports AI MCP supports the following leagues:
- **MLB** (baseball/mlb)
- **NBA** (basketball/nba)
- **WNBA** (basketball/wnba)
- **NFL** (football/nfl)
- **College Football** (football/college-football)
- **College Basketball** (basketball/mens-college-basketball)
- **NHL** (hockey/nhl)
- **Premier League** (soccer/eng.1)
- **La Liga** (soccer/esp.1)
- **MLS** (soccer/usa.1)

## Wagyu Sports MCP Usage

### Setup

```bash
# Set API key
export ODDS_API_KEY=your_odds_api_key

# Run the server
cd sports_mcp/wagyu_sports/mcp_server
python odds_client_server.py
```

### Test Mode

For development without API keys:
```bash
# Run with mock data
python odds_client_server.py --test-mode
```

### Command Line Options

```bash
python odds_client_server.py --help

Options:
  --api-key API_KEY    API key for the Odds API
  --test-mode         Use mock data instead of real API calls
```

## Integration with MCP Clients

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "sports-ai": {
      "command": "python",
      "args": ["/path/to/sports_ai_mcp.py"],
      "env": {
        "OPENROUTER_API_KEY": "your_key_here"
      }
    },
    "wagyu-sports": {
      "command": "python", 
      "args": ["/path/to/odds_client_server.py"],
      "env": {
        "ODDS_API_KEY": "your_odds_key_here"
      }
    },
    "magictunnel": {
      "command": "./magictunnel",
      "args": ["--stdio", "--config", "magictunnel-config.yaml"]
    }
  }
}
```

### Using with Other MCP Clients

Both servers support stdio mode for integration with any MCP-compatible client:

```bash
# Direct stdio mode
python sports_ai_mcp.py
python odds_client_server.py
./magictunnel --stdio
```

## Common Troubleshooting

### MagicTunnel Issues
- **Smart discovery low confidence**: Check hybrid AI matching configuration
- **Semantic search not working**: Verify OpenAI API key and embedding generation
- **External MCP not starting**: Check file permissions and working directory
- **Tool visibility issues**: Use `magictunnel-visibility` CLI to check/modify tool visibility

### Sports AI MCP Issues
- **API key errors**: Ensure OPENROUTER_API_KEY is set correctly
- **Rate limiting**: Check API quota with probeLeagueSupport tool
- **Invalid league**: Verify sport/league combination is supported

### Wagyu Sports MCP Issues
- **Odds API errors**: Ensure ODDS_API_KEY is valid and has quota remaining
- **Mock data**: Use `--test-mode` for development without API calls
- **Connection issues**: Check network connectivity and API endpoints

## Performance Optimization

### MagicTunnel
- Use `hybrid` mode for best balance of speed and accuracy
- Pre-generate embeddings with `make pregenerate-embeddings-ollama`
- Enable caching in smart discovery configuration
- Use local Ollama for semantic search to avoid API costs

### Sports APIs
- Use `probeLeagueSupport` to validate league capabilities before making multiple calls
- Cache results where possible to avoid API rate limits
- Use `getQuotaInfo` to monitor API usage

## Security Considerations

- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- Enable TLS/SSL for production deployments
- Configure appropriate authentication for web dashboard access
- Use trusted proxy headers only in secure environments