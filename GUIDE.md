# PDF Intelligence — Full Guide

## How it works

```
PDF upload → text extraction (pdfplumber) → LLM answers your query → result in browser + JSON download
```

1. **Text extraction** — `pdfplumber` reads the PDF and pulls all text. Fully deterministic, no AI at this step.
2. **Query** — choose a built-in template (General Information, Directors, Financials…) or write your own question in plain English.
3. **LLM** — the extracted text is sent to the model with a strict prompt: return only what is explicitly in the document, never guess.

---

## Setup

**Requirements:** Python 3.11+

```bash
# 1. Clone the repository
git clone https://github.com/allis1infinity/PDF-Intelligence.git
cd PDF-Intelligence

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your provider
cp .env.example .env
# Open .env and set PROVIDER and the corresponding key or model

# 5. Run
python app.py
# Open http://127.0.0.1:5000
```

---

## Provider configuration

Set your provider in `.env`:

```env
PROVIDER=ollama   # ollama | openai | deepseek | gemini
```

### Ollama — local, free, no internet required

```bash
# Install from https://ollama.com, then pull a model:
ollama pull llama3.1
```

```env
PROVIDER=ollama
OLLAMA_MODEL=llama3.1
```

No API key needed. Documents never leave your machine.

### OpenAI

```env
PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Get a key at [platform.openai.com](https://platform.openai.com/api-keys). Recommended model: `gpt-4o-mini`.

### DeepSeek

```env
PROVIDER=deepseek
DEEPSEEK_API_KEY=...
```

Get a key at [platform.deepseek.com](https://platform.deepseek.com/api-keys). Default model: `deepseek-chat`.

### Gemini

```env
PROVIDER=gemini
GEMINI_API_KEY=...
```

Get a key at [aistudio.google.com](https://aistudio.google.com/apikey). Free tier: 1,500 requests/day.

---

## File structure

```
PDF-Intelligence/
├── app.py               ← Flask backend
├── templates/
│   └── index.html       ← web interface
├── static/
│   └── style.css        ← styles
├── results/             ← auto-saved JSON results (gitignored)
├── .env                 ← your keys (gitignored)
├── .env.example         ← configuration template
├── requirements.txt
├── README.md
└── GUIDE.md
```

---

## Privacy

- Uploaded PDFs are processed in memory and immediately deleted — never stored on disk permanently.
- With Ollama: no data leaves your machine.
- With cloud providers: only the extracted text is transmitted, not the original PDF file.
- API keys are stored in `.env` which is excluded from git.
