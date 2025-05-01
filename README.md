# Insomnia-Chatbot


Run Qdrant
```
docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
```


Run SearXNG:
```
docker run --rm -d -p 8080:8080 -v ./config/searxng-settings.yml:/etc/searxng/settings.yml -e "BASE_URL=http://localhost:8080/" -e "INSTANCE_NAME=my-instance" searxng/searxng
```


## Project Structure

```
multi-agent-system/
├── config/                          
│   ├── logging_dict_config.json     # Logging configuration settings
│   └── searxng-settings.yml        # SearXNG search engine configuration
│
├── src/
│   ├── agents/                      # Multi-agent system components
│   │   ├── base/                   # Base classes and shared components
│   │   │   └── models.py          # Common models like TaskHandlerOutput
│   │   │
│   │   ├── factor/                 # Factor analysis agent
│   │   │   ├── builder.py         # Factor subgraph construction
│   │   │   ├── nodes.py           # Factor agent implementation using Groq
│   │   │   └── states.py          # Factor agent state definitions
│   │   │
│   │   ├── harm/                   # Harm assessment agent
│   │   │   ├── builder.py         # Harm subgraph construction
│   │   │   ├── nodes.py           # Harm agent implementation using Groq
│   │   │   └── states.py          # Harm agent state definitions
│   │   │
│   │   ├── response/               # Response generation agent
│   │   │   └── nodes.py           # Response agent for final output
│   │   │
│   │   ├── suggestion/             # Suggestion generation agent
│   │   │   ├── builder.py         # Suggestion subgraph construction
│   │   │   ├── nodes.py           # Suggestion agent using Groq
│   │   │   └── states.py          # Suggestion agent state definitions
│   │   │
│   │   └── supervisor/             # Main supervisor agent
│   │       ├── models.py          # Supervisor models for delegation
│   │       └── nodes.py           # Supervisor implementation using Groq
│   │
│   ├── common/                      # Shared utilities
│   │   ├── llm/                    # LLM integration
│   │   │   └── agent.py           # LLM agent factory (Groq/Ollama support)
│   │   │
│   │   └── logging/                # Logging setup
│   │       └── setup.py           # Logging configuration
│   │
│   ├── graph/                      # LangGraph workflow
│   │   ├── builder.py             # Main graph construction
│   │   └── states.py              # Graph state definitions
│   │
│   ├── lmchunker/                  # Language model chunking
│   │   ├── chunker.py             # Main chunking logic
│   │   └── modules/               # Chunking modules
│   │
│   └── tools/                      # External integrations
│       ├── rag/                    # RAG (Retrieval-Augmented Generation)
│       │   ├── utils.py           # RAG utilities
│       │   └── vectorstore.py     # Vector store operations
│       │
│       ├── utils/                  # Utility functions
│       │   ├── chunking/          # Text chunking utilities
│       │   │   ├── markdown.py    # Markdown-specific chunking
│       │   │   └── perplexity_chunking.py  # Perplexity-based chunking
│       │   │
│       │   └── embeddings/        # Embedding utilities
│       │       ├── api.py         # Embedding API integration
│       │       └── late_chunking.py  # Late chunking implementation
│       │
│       └── web/                    # Web-related tools
│           ├── scraper/           # Web scraping functionality
│           └── search/            # SearXNG search integration
│
├── pyproject.toml                  # Project metadata and dependencies
├── README.md                       # Project documentation
└── uv.lock                         # Dependency lock file
```
