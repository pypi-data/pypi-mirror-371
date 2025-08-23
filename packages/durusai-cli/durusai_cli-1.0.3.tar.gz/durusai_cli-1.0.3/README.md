# DurusAI Native CLI

🤖 Native CLI client for DurusAI - AI-powered development assistant

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/durusai.svg)](https://badge.fury.io/py/durusai)

## Features

- 🔐 **Secure authentication** with JWT tokens and keyring storage
- 💬 **Interactive chat mode** with AI models (Claude, GPT-4, Gemini)
- 🚀 **Single command queries** for quick AI assistance  
- 📊 **Usage statistics** and token tracking
- 🔧 **Multiple AI models** support
- 🎨 **Rich terminal UI** with markdown rendering
- ⚙️ **Configurable profiles** for different environments
- 🌐 **Cross-platform** (Linux, macOS, Windows)

## Installation

### From PyPI (Recommended)

```bash
pip install durusai
```

### From source

```bash
git clone https://github.com/durusai/cli.git
cd cli/durusai_native_cli
pip install -e .
```

### Development installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Login to DurusAI

```bash
durusai login
```

### 2. Ask a question

```bash
durusai query "Explain Python decorators"
```

### 3. Start interactive chat

```bash
durusai chat
```

## Usage

### Authentication

```bash
# Login with username/password
durusai login

# Login with specific profile
durusai login --profile work

# Check current user
durusai whoami

# Logout
durusai logout
```

### Queries

```bash
# Single query
durusai query "How to implement binary search in Python?"

# Query with specific model
durusai query "Explain async/await" --model gpt-4

# Query with custom parameters  
durusai query "Write a FastAPI endpoint" --max-tokens 2000 --temperature 0.7
```

### Interactive Mode

```bash
# Start interactive chat
durusai chat

# Chat with specific model
durusai chat --model claude-3-sonnet
```

Interactive commands:
- `/help` - Show help
- `/model <name>` - Switch AI model
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/stats` - Show session statistics
- `/quit` - Exit chat mode

### Models and Statistics

```bash
# List available models
durusai models

# Show usage statistics
durusai stats

# Check API health
durusai health
```

### Configuration

```bash
# Show all settings
durusai config --list

# Set API endpoint
durusai config api_endpoint "https://api.durusai.com"

# Set default model
durusai config settings.default_model "claude-3-sonnet"

# Enable streaming responses
durusai config settings.stream_responses true
```

## Configuration

DurusAI CLI stores configuration in `~/.durusai/`:

```
~/.durusai/
├── config.json         # Main configuration
├── profiles/           # User profiles  
│   ├── default.json
│   └── work.json
├── cache/             # Response cache
├── history/           # Command history
└── logs/             # Application logs
```

### Configuration Options

```json
{
  "api_endpoint": "https://api.durusai.com",
  "default_profile": "default",
  "settings": {
    "timeout": 30,
    "retry_count": 3,
    "stream_responses": true,
    "cache_ttl": 3600,
    "auto_update": true,
    "show_token_usage": true,
    "default_model": "claude-3-sonnet-20240229",
    "max_history_size": 1000
  },
  "display": {
    "use_colors": true,
    "show_timestamps": false,
    "markdown_rendering": true,
    "pager_enabled": true
  }
}
```

## API Models

DurusAI supports multiple AI providers:

| Model | Provider | Context Length | Status |
|-------|----------|----------------|---------|
| claude-3-sonnet-20240229 | Anthropic | 200K | ✅ |
| claude-3-haiku-20240307 | Anthropic | 200K | ✅ |
| gpt-4 | OpenAI | 8K | ✅ |
| gpt-4-turbo | OpenAI | 128K | ✅ |
| gemini-pro | Google | 32K | ✅ |

## Examples

### Code Generation

```bash
durusai query "Create a REST API endpoint for user registration with FastAPI"
```

### Code Explanation

```bash  
durusai query "Explain this Python code" < my_script.py
```

### Interactive Debugging

```bash
durusai chat
# Then in chat:
# User: I'm getting a TypeError in my Python code
# AI: I'd be happy to help! Please share the error and the relevant code...
```

### Batch Processing

```bash
# Process multiple files
for file in *.py; do
  durusai query "Review this code for bugs: $(cat $file)" > "${file%.py}_review.md"
done
```

## Environment Variables

- `DURUSAI_API_ENDPOINT` - API endpoint URL
- `DURUSAI_API_TOKEN` - API authentication token  
- `DURUSAI_CONFIG_DIR` - Configuration directory (default: ~/.durusai)
- `DURUSAI_PROFILE` - Default profile name

## Security

- **Tokens** are stored securely using system keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service)
- **Fallback encryption** using Fernet for systems without keyring
- **No plaintext passwords** stored locally
- **JWT tokens** with automatic refresh
- **TLS/SSL** for all API communications

## Development

### Setup

```bash
git clone https://github.com/durusai/cli.git
cd cli/durusai_native_cli
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Code formatting

```bash
black durusai/
flake8 durusai/
mypy durusai/
```

### Building

```bash
python -m build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Create a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- 📧 Email: support@durusai.com
- 💬 GitHub Issues: [durusai/cli/issues](https://github.com/durusai/cli/issues)
- 📖 Documentation: [docs.durusai.com](https://docs.durusai.com)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

---

Made with ❤️ by the DurusAI team