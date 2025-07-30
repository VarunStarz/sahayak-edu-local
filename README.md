# Multi-Agent Educational Platform

A sophisticated educational platform that uses multiple AI agents to provide personalized learning experiences through multimodal interactions.

## Project Structure

```
├── src/                          # Main source code
│   ├── agents/                   # Agent implementations
│   │   ├── router/               # Agent router implementation
│   │   ├── analytics/            # Analytics agent
│   │   ├── curriculum/           # Curriculum agent
│   │   ├── response/             # Response agent
│   │   └── planning/             # Planning agent
│   ├── models/                   # ObjectBox data models
│   ├── flows/                    # PocketFlow flow definitions
│   ├── database/                 # Database utilities
│   └── main.py                   # Application entry point
├── tests/                        # Test suite
├── data/                         # Data storage (created at runtime)
├── logs/                         # Application logs (created at runtime)
├── credentials/                  # API credentials (created at runtime)
├── config.py                     # Configuration settings
├── utils.py                      # Utility functions
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── pytest.ini                   # Test configuration
└── .env.template                 # Environment template
```

## Core Dependencies

- **PocketFlow**: Node-Flow architecture for agent orchestration
- **ObjectBox**: High-performance database with vector search
- **MCP Python SDK**: Model Context Protocol for external integrations
- **Plotly**: Interactive analytics dashboards
- **Google API Client**: Calendar integration

## Getting Started

1. Copy `.env.template` to `.env` and configure your settings
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest tests/`
4. Start the platform: `python -m src.main`

## Architecture

The platform uses PocketFlow's Node-Flow architecture where each agent is implemented as a Node with:
- **prep()**: Input validation and preprocessing
- **exec()**: Core agent logic and processing
- **post()**: Output generation and action routing

Agents communicate through PocketFlow's shared store mechanism and persist data using ObjectBox database.
