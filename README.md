<h1 align="center"><b>Multi-Agent Chatbot System for Insomnia</b></h1>



## Quick Start
### Video Demo
https://github.com/user-attachments/assets/db788493-a2be-4e55-ba4a-d38b8152e51d

**Notes:**
- The UI is heavily based on Perplexica's interface, adapted to work with this project's backend.
- The UX currently appears slow due to two main reasons:
  1. Streaming tokens functionality is still under active development
  2. Display of intermediate reasoning steps is not yet implemented
- Further system-wide optimizations are needed and in progress

## Introduction

This project is a multi-agent chatbot system specifically designed to assist users with insomnia-related queries. Built using LangGraph for orchestrating complex agent workflows and PydanticAI for type-safe LLM interactions, the system leverages a sophisticated multi-agent architecture to provide comprehensive responses.

Key features:
- **Multi-agent architecture**: Specialized agents (Supervisor, Suggestion, Harm, Factor, and Response) work together to analyze queries and generate helpful responses
- **RAG capabilities**: Retrieval-augmented generation for accessing relevant information from local knowledge bases
- **Web search integration**: Real-time web search via SearXNG to supplement knowledge with up-to-date information
- **Contextual understanding**: Agents collaborate to understand user queries in context and provide well-rounded responses
- **FastAPI backend**: Robust API server with streaming response capabilities
- **Next.js frontend**: Modern, responsive user interface

The system demonstrates how complex agent-based workflows can be implemented to create specialized, context-aware conversational AI applications.

## Usage

### Prerequisites
1. Docker installed for running Qdrant and SearXNG
2. Python 3.12+ for the backend
3. Node.js for the frontend

### Setup

1. Start the Qdrant vector database:
```bash
docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
```

2. Start the SearXNG search engine:
```bash
docker run --rm -d -p 8080:8080 -v ./config/searxng-settings.yml:/etc/searxng/settings.yml -e "BASE_URL=http://localhost:8080/" -e "INSTANCE_NAME=my-instance" searxng/searxng
```

3. Install backend dependencies:
```bash
uv sync
```

4. Start the FastAPI backend server:
```bash
source .venv/bin/activate
python main.py
```

5. In a separate terminal, navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm install
```

6. Start the Next.js frontend:
```bash
npm run dev
```

7. Open your browser and navigate to http://localhost:3000 to use the chatbot

## Project Structure

```
multi-agent-chatbot-system-for-insomnia/
├── config/                          # Configuration files
├── src/
│   ├── agents/                      # Multi-agent system components
│   │   ├── base/                    # Base classes and shared models
│   │   ├── factor/                  # Factor analysis agent
│   │   ├── harm/                    # Harm assessment agent
│   │   ├── response/                # Response generation agent
│   │   ├── suggestion/              # Suggestion generation agent
│   │   └── supervisor/              # Main supervisor agent
│   ├── common/                      # Shared utilities
│   │   ├── llm/                     # LLM integration
│   │   └── logging/                 # Logging setup
│   ├── graph/                       # LangGraph workflow
│   ├── lmchunker/                   # Language model chunking
│   └── tools/                       # Various tools
│       ├── utils/                   # Utility functions
│       ├── rag/                     # Retrieval-augmented generation
│       └── web/                     # Web-related tools
│           ├── scraper/             # Web scraping functionality
│           └── search/              # Web search functionality
├── main.py                          # FastAPI server entry point
└── vectorstore.py                   # Vector store operations
```
