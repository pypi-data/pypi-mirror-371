# Changelog

All notable changes to DurusAI Native CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-21

### Added
- 🎉 Initial release of DurusAI Native CLI
- 🔐 Secure JWT authentication with token refresh
- 🤖 Support for multiple AI models (Claude, GPT-4, Gemini)
- 💬 Interactive REPL chat mode with rich features
- 📊 Usage statistics and token tracking
- ⚙️ Configurable user profiles and settings
- 🔒 Secure credential storage using system keyring
- 🌐 REST API client with retry logic and error handling
- 📝 Markdown rendering for AI responses
- 🎨 Rich terminal UI with colors and formatting
- 📋 Command history and conversation export
- 🏥 Health check and API status monitoring
- 🚀 Cross-platform support (Linux, macOS, Windows)

### Commands
- `durusai login` - Authentication and session management
- `durusai query` - Single AI queries with parameters
- `durusai chat` - Interactive chat mode
- `durusai models` - List available AI models
- `durusai stats` - Usage statistics
- `durusai config` - Configuration management
- `durusai whoami` - User information
- `durusai health` - API health check
- `durusai logout` - Session termination

### Interactive Features
- `/help` - Show available commands
- `/model <name>` - Switch AI model
- `/models` - List available models
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/stats` - Session statistics
- `/export <file>` - Export conversation to file
- `/settings` - Show current settings
- `/quit` - Exit interactive mode

### Configuration
- `~/.durusai/config.json` - Main configuration file
- `~/.durusai/profiles/` - User profiles directory
- `~/.durusai/cache/` - Response cache
- `~/.durusai/history/` - Command history
- `~/.durusai/logs/` - Application logs

### Security
- JWT tokens with automatic refresh
- Secure storage using system keyring
- Fallback encryption for systems without keyring
- No plaintext password storage
- TLS/SSL for all API communications

### Installation
- PyPI package: `pip install durusai`
- Development install: `pip install -e ".[dev]"`
- Full features: `pip install -e ".[full]"`

### Dependencies
- typer[all] >= 0.9.0 - CLI framework
- rich >= 13.0.0 - Rich text and formatting
- httpx >= 0.24.0 - HTTP client
- prompt-toolkit >= 3.0.0 - Interactive prompts
- keyring >= 24.0.0 - Secure credential storage
- cryptography >= 40.0.0 - Encryption
- PyJWT >= 2.8.0 - JWT token handling
- markdown >= 3.4.0 - Markdown rendering

### API Compatibility
- DurusAI API v1.0.0
- Authentication endpoints
- Query and streaming endpoints
- Model management endpoints
- Statistics endpoints

---

## Development History

### Pre-release Development
- 📋 Project planning and architecture design
- 🏗️ Backend API development and testing
- 🔧 CLI client development and integration
- 🧪 Comprehensive testing and validation
- 📚 Documentation and demo creation

### Future Roadmap
- 📱 Mobile app integration
- 🔌 Plugin system for extensions
- 🌍 Multi-language support
- 📊 Advanced analytics and reporting
- 🤝 Team collaboration features
- 🔄 Automatic updates mechanism

---

*For the latest changes and updates, visit our [GitHub repository](https://github.com/durusai/cli).*