# Undetected ChromeDriver MCP Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server providing browser automation capabilities using **undetected-chromedriver** for enhanced anti-detection compared to standard Puppeteer implementations.

## 🚀 Features

- **🕵️ Enhanced Anti-Detection**: Uses undetected-chromedriver to bypass modern anti-bot protections
- **🔄 Drop-in Replacement**: 100% API compatible with server-puppeteer
- **⚡ High Performance**: Optimized session management and resource cleanup
- **🛡️ Production Ready**: Comprehensive error handling and logging
- **🎯 7 Core Tools**: Complete browser automation toolkit

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `chrome_navigate` | Navigate to URLs with anti-detection |
| `chrome_screenshot` | Capture page or element screenshots |
| `chrome_click` | Click page elements |
| `chrome_fill` | Fill input fields |
| `chrome_select` | Select dropdown options |
| `chrome_hover` | Hover over elements |
| `chrome_evaluate` | Execute JavaScript code |

## 📦 Installation

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser
- Git

### Install from Source

```bash
# Clone the repository
git clone https://github.com/andrewlwn77/undetected-chrome-mcp.git
cd undetected-chrome-mcp

# Install the package
pip install -e .
```

### Dependencies
- **mcp>=1.0.0** - Model Context Protocol
- **undetected-chromedriver>=3.5.0** - Anti-detection Chrome automation
- **selenium>=4.15.0** - WebDriver framework
- **Pillow>=10.0.0** - Image processing for screenshots

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROME_EXECUTABLE_PATH` | Path to Chrome executable | `/opt/google/chrome/google-chrome` |
| `CHROME_DRIVER_LOG_LEVEL` | Logging level | `INFO` |
| `CHROME_SESSION_TIMEOUT` | Session timeout (seconds) | `300` |
| `CHROME_MAX_SESSIONS` | Max concurrent sessions | `5` |

### MCP Configuration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "undetected-chrome": {
      "command": "python",
      "args": ["-m", "undetected_chrome_mcp.server"],
      "cwd": "/path/to/undetected-chrome-mcp",
      "transport": {
        "type": "stdio"
      },
      "env": {
        "CHROME_EXECUTABLE_PATH": "/opt/google/chrome/google-chrome",
        "CHROME_DRIVER_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## 🚀 Usage

### Command Line
```bash
# Run the MCP server
python -m undetected_chrome_mcp.server

# Or use the installed command
undetected-chrome-mcp-server
```

### Example Tool Calls

**Navigate to a webpage:**
```json
{
  "tool": "chrome_navigate",
  "arguments": {
    "url": "https://example.com",
    "timeout": 30000
  }
}
```

**Take a screenshot:**
```json
{
  "tool": "chrome_screenshot",
  "arguments": {
    "name": "example_page",
    "encoded": true,
    "fullPage": true
  }
}
```

**Execute JavaScript:**
```json
{
  "tool": "chrome_evaluate",
  "arguments": {
    "script": "return document.title;"
  }
}
```

## 🧪 Testing

The project includes comprehensive tests to validate functionality:

```bash
# Run basic function tests
python test_functions.py

# Run Reddit anti-detection tests
python test_reddit.py
```

### Test Results
- ✅ **Navigation**: Successfully loads protected pages
- ✅ **JavaScript Execution**: Full DOM access and data extraction
- ✅ **Screenshots**: High-quality image capture
- ✅ **Anti-Detection**: Bypasses modern bot protection (tested on Reddit)

## 🏗️ Architecture

The server follows a layered architecture:

1. **MCP Protocol Layer** - Handles MCP communication
2. **Browser Management Layer** - Manages Chrome sessions
3. **Anti-Detection Layer** - Implements stealth capabilities
4. **Operation Execution Layer** - Executes browser operations

## 🛡️ Anti-Detection Features

- **Undetected ChromeDriver**: Advanced stealth automation
- **User Agent Rotation**: Randomized browser fingerprints
- **Viewport Randomization**: Human-like window sizing
- **Human-like Delays**: Natural interaction timing
- **JavaScript Stealth**: Removes automation indicators
- **Session Isolation**: Clean state between operations

## 🎯 Comparison with server-puppeteer

| Feature | server-puppeteer | undetected-chrome-mcp |
|---------|------------------|----------------------|
| Anti-Detection | Basic | Advanced |
| Bot Protection Bypass | Limited | Excellent |
| API Compatibility | N/A | 100% Compatible |
| Performance | Good | Optimized |
| Resource Management | Basic | Advanced |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This project builds upon excellent open source work:

- **[server-puppeteer](https://github.com/modelcontextprotocol/servers)** - Original MCP Puppeteer server that inspired this implementation
- **[undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)** - The core anti-detection technology that powers this server
- **[Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk)** - The foundation protocol enabling AI-tool integration

Special thanks to the open source community for creating these foundational tools that make advanced browser automation accessible to everyone.

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/andrewlwn77/undetected-chrome-mcp/issues)
- **Documentation**: See `/docs` directory for detailed specifications
- **Examples**: Check `/tests` directory for usage examples

## 🔗 Related Projects

- [reddit-mcp](https://github.com/andrewlwn77/reddit-mcp) - Reddit research MCP server
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP documentation

---

**Built with ❤️ by [andrewlwn77](https://github.com/andrewlwn77)**