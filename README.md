# 🤖 Chatbot

A simple conversational chatbot powered by [LangChain](https://www.langchain.com/) and Google's **Gemini 2.5 Flash** model.

## Features

- Interactive terminal chat with conversation history
- **Gradio web UI** with drag-and-drop file upload
- Powered by `gemini-2.5-flash` via the Google Generative AI API
- Configuration managed through environment variables using **pydantic-settings**
- Packaged with [uv](https://docs.astral.sh/uv/) for fast, reproducible dependency management

## Prerequisites

- **Python 3.12+**
- **uv** — install it from [docs.astral.sh/uv](https://docs.astral.sh/uv/)
- A **Google AI API key** — get one at [aistudio.google.com](https://aistudio.google.com/)

## Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd chatbot
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Set up your API key

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your-api-key-here
```

### 4. Run the chatbot

**Terminal UI:**

```bash
uv run chatbot
```

**Web UI (Gradio):**

```bash
uv run chatbot-web
```

This opens a browser at `http://localhost:7860` where you can chat and drag-and-drop images or PDFs.

### Multimodal Commands

| Command | Description |
|---|---|
| `/image <path> [prompt]` | Send a local image (png, jpg, gif, webp, bmp) with an optional prompt |
| `/pdf <path> [prompt]` | Send a local PDF with an optional prompt |
| `/reset` | Clear conversation history |
| `/help` | Show available commands |

**Examples:**

```
You: /image photo.png What is in this photo?
You: /pdf report.pdf Summarise the key findings
You: /image "C:\Users\me\My Photos\cat.jpg"
```

## Project Structure

```
chatbot/
├── src/chatbot/
│   ├── __init__.py
│   ├── config.py        # Settings loaded from .env via pydantic-settings
│   ├── main.py           # Terminal chat loop with slash-command router
│   ├── multimodal.py     # MultimodalChatbot class (text, image, PDF)
│   └── webui.py          # Gradio web interface
├── .env                   # API key (not committed)
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Development

Install dev dependencies (includes **ruff** for linting and **ty** for type-checking):

```bash
uv sync --group dev
```

Lint:

```bash
uv run ruff check .
```

## License

This project is unlicensed — use it however you like.
