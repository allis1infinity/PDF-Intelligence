# PDF Intelligence — Extractor

A lightweight web tool for extracting structured data from business PDFs (company registers, official filings, annual reports). Upload a document, choose a template or write your own query, and get the relevant fields in seconds — displayed in the browser and downloadable as JSON.

## Quick start

```bash
git clone https://github.com/allis1infinity/PDF-Intelligence.git
cd PDF-Intelligence

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env        # add your API key or configure Ollama
python app.py               # open http://127.0.0.1:5000
```

**No API key needed** if you use [Ollama](https://ollama.com) (local, free, offline):
```bash
ollama pull llama3.1
```

## Supported providers

| Provider | Cost | Data privacy |
|---|---|---|
| Ollama (local) | Free | ✅ Stays on your machine |
| OpenAI | Pay per use | Sent to OpenAI |
| DeepSeek | Pay per use | Sent to DeepSeek |
| Gemini | Free tier | Sent to Google |

→ Full setup and configuration: [GUIDE.md](GUIDE.md)
