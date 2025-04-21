# Insomnia-Chatbot


Run SearXNG:
```
docker run --rm -d -p 8080:8080 -v ./config/searxng-settings.yml:/etc/searxng/settings.yml -e "BASE_URL=http://localhost:8080/" -e "INSTANCE_NAME=my-instance" searxng/searxng
```



Code Structure:

# Project Structure

```
multi-agent-system/
├── config/                          # Configuration
│   ├── logging_dict_config.json     # Logging configuration
│   └── searxng-settings.yml        # SearXNG search engine settings
│
├── src/
│   ├── agents/                      # Multi-agent system components
│   │   ├── base/                   # Base classes and shared components
│   │   ├── factor/                 # Factor agent implementation
│   │   ├── harm/                   # Harm agent implementation
│   │   ├── response/               # Response agent
│   │   ├── suggestion/             # Suggestion agent
│   │   └── supervisor/             # Supervisor agent
│   │
│   ├── common/                      # Shared utilities
│   │   ├── chunking/               # Text chunking utilities
│   │   │   ├── jina_api.py        # Jina AI embeddings integration
│   │   │   └── late_chunking.py   # Late chunking implementation
│   │   │
│   │   ├── logging/               # Logging setup and utilities
│   │   │   ├── formatters.py      # Custom log formatters
│   │   │   ├── handlers.py        # Custom log handlers
│   │   │   └── setup.py           # Logging initialization
│   │   │
│   │   └── llm/                 # LLM integration utilities
│   │
│   ├── graph/                      # LangGraph workflow definitions
│   │   ├── builder.py             # Main graph construction
│   │   └── states.py              # Graph state definitions
│   │
│   └── tools/                      # External tool integrations
│       └── web/                    # Web-related tools
│           ├── scraper/           # Web scraping functionality
│           └── search/            # Search engine integration
│
├── pyproject.toml                 
├── README.md                       
└── uv.lock                        
