# PDF Intelligence — Extractor

A web tool for extracting structured data from business documents (company registers, official filings, annual reports). Upload a PDF, choose a template or write your own query, and get the relevant fields instantly — displayed in the browser and downloadable as JSON.

**Ein Web-Tool zur strukturierten Datenextraktion aus Geschäftsdokumenten** (Unternehmensregister, offizielle Meldungen, Jahresabschlüsse). PDF hochladen, Vorlage auswählen oder eigene Abfrage eingeben — die relevanten Felder werden sofort extrahiert und als JSON ausgegeben.

**Простий веб-інструмент для витягання структурованих даних з бізнес-документів** (реєстри компаній, офіційні звіти, річна звітність). Завантажте PDF, оберіть шаблон або напишіть власний запит — потрібні поля витягуються миттєво і доступні для завантаження у форматі JSON.

---

## How it works

```
PDF upload → text extraction (pdfplumber) → LLM answers your query → result in browser + JSON download
```

1. **Text extraction** — `pdfplumber` reads the PDF and pulls all text. Fully deterministic, no AI involved at this step.
2. **Query** — you choose a built-in template (General Information, Directors, Financials…) or write your own question in plain language.
3. **LLM** — the extracted text is sent to the language model with a strict prompt: return only what is explicitly in the document, never guess.

---

## Supported LLM providers

| Provider | Cost | Privacy | How to get |
|---|---|---|---|
| **Ollama (local)** | **Free** | ✅ Data never leaves your machine | [ollama.com](https://ollama.com) |
| OpenAI | Pay per use | ⚠ Data sent to OpenAI | [platform.openai.com](https://platform.openai.com/api-keys) |
| DeepSeek | Pay per use | ⚠ Data sent to DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/api-keys) |
| Gemini | Free tier (1,500 req/day) | ⚠ Data sent to Google | [aistudio.google.com](https://aistudio.google.com/apikey) |

---

## Setup

**Requirements:** Python 3.11+

```bash
# 1. Clone the repository
git clone <repo-url>
cd pdf_intelligence

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your provider
cp .env.example .env
# Open .env and set PROVIDER and the corresponding key/model

# 5. Start the app
python app.py
```

Open your browser at **http://127.0.0.1:5000**

---

## Ollama quick start (recommended — free, local)

```bash
# Install Ollama from https://ollama.com, then:
ollama pull llama3.1

# In .env:
PROVIDER=ollama
OLLAMA_MODEL=llama3.1
```

No API key needed. Works fully offline.

---

## File structure

```
pdf_intelligence/
├── app.py               ← Flask backend
├── templates/
│   └── index.html       ← web interface
├── static/
│   └── style.css        ← styles
├── results/             ← auto-saved JSON results
├── .env                 ← your keys (never committed)
├── .env.example         ← template for setup
├── requirements.txt
└── GUIDE.md
```

---

## Privacy

- Uploaded PDFs are processed in memory and immediately deleted — never stored permanently.
- With Ollama: no data leaves your machine.
- With cloud providers: only the extracted text is transmitted, not the original PDF.
- API keys are stored in `.env` which is excluded from git.
