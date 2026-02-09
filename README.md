# Self-DeepResearch

<p align="center">
  <img src="frontend/public/favicon.svg" alt="DeepResearch Logo" width="80" height="80">
</p>

<p align="center">
  <strong>An autonomous deep research agent powered by LangGraph & Tavily</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#license">License</a>
</p>

---

## Overview

Self-DeepResearch is an AI-powered autonomous research assistant that can plan, search, reflect, and generate comprehensive research reports on any topic. It uses a multi-agent workflow with iterative refinement to ensure high-quality, well-sourced outputs.

## Features

- **Autonomous Research Workflow** - Multi-agent system that plans queries, searches the web, reviews findings, and iterates until satisfied
- **Real-time Streaming** - Watch the research process unfold in real-time with a beautiful thought chain visualization
- **Iterative Refinement** - Built-in reviewer agent that evaluates findings and requests additional research when needed
- **Source Attribution** - All research notes include source URLs for verification and further reading
- **Research History** - Save and revisit past research sessions with full context
- **Dark Mode** - Easy on the eyes with automatic theme detection
- **Export Options** - Download reports as Markdown or print to PDF

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Planner Agent                               │
│              Decomposes task into sub-queries                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Researcher Agent                              │
│         Searches web via Tavily, extracts key notes              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Reviewer Agent                               │
│     Evaluates completeness, requests more research if needed     │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              Need more?               Satisfied?
                    │                       │
                    ▼                       ▼
            Back to Researcher      ┌─────────────────┐
                                    │  Reporter Agent │
                                    │ Generates final │
                                    │     report      │
                                    └─────────────────┘
```

## Quick Start

### Prerequisites

- **Node.js** >= 18
- **Python** >= 3.10
- **OpenAI API Key** (or compatible endpoint)
- **Tavily API Key** ([Get one here](https://tavily.com/))

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Self-DeepResearch.git
cd Self-DeepResearch
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn src.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 4. Open the App

Navigate to `http://localhost:5173` in your browser.

## Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key
OPENAI_MODEL_NAME=gpt-4o
OPENAI_API_BASE=https://api.openai.com/v1  # Optional: for custom endpoints

# Tavily Search API
TAVILY_API_KEY=your-tavily-key

# Application Settings
LOG_LEVEL=INFO
```

### Frontend Environment Variables

The frontend uses Vite environment variables:

- `.env` - Development settings
- `.env.production` - Production settings

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance async web framework
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Multi-agent workflow orchestration
- **[LangChain](https://langchain.com/)** - LLM application framework
- **[Tavily](https://tavily.com/)** - AI-optimized search API
- **[SQLModel](https://sqlmodel.tiangolo.com/)** - SQL database with Pydantic models

### Frontend
- **[Vue 3](https://vuejs.org/)** - Progressive JavaScript framework
- **[Vite](https://vitejs.dev/)** - Next-generation frontend tooling
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Lucide Icons](https://lucide.dev/)** - Beautiful open-source icons

## Project Structure

```
Self-DeepResearch/
├── backend/
│   ├── src/
│   │   ├── agents/          # LangGraph agent nodes
│   │   │   ├── planner.py   # Query decomposition
│   │   │   ├── researcher.py # Web search & note-taking
│   │   │   ├── reviewer.py  # Quality evaluation
│   │   │   └── reporter.py  # Report generation
│   │   ├── core/            # Configuration & LLM setup
│   │   ├── tools/           # Tavily search integration
│   │   ├── graph.py         # LangGraph workflow definition
│   │   ├── main.py          # FastAPI application
│   │   └── models.py        # Pydantic/State models
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue components
│   │   │   ├── ResearchForm.vue
│   │   │   ├── ThoughtChain.vue
│   │   │   ├── ReportView.vue
│   │   │   └── HistorySidebar.vue
│   │   ├── composables/     # Vue composables
│   │   ├── App.vue          # Main application
│   │   └── types.ts         # TypeScript definitions
│   └── package.json
│
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/research/stream` | Start a new research session (SSE) |
| `GET` | `/history` | List all research sessions |
| `GET` | `/history/:id` | Get a specific session |
| `DELETE` | `/history/:id` | Delete a session |
| `GET` | `/health` | Health check |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/excelius">Excelius</a>
</p>
