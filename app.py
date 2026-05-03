"""
PDF Intelligence Search — Flask backend
Run:  python app.py   →  http://127.0.0.1:5000

Provider priority: Ollama (local) → DeepSeek → Gemini
Every analysis is also saved to results/<filename>_<timestamp>.json
"""

import json
import os
import re
import tempfile
from datetime import datetime

import pdfplumber
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

INSOLVENCY_KEYWORDS = [
    "Insolvenzverfahren", "Insolvenzantrag", "Insolvenzverwalter",
    "Gläubigerausschuss", "aufgelöst", "Liquidation",
]

PROMPT = """You are a German business document analyst.

USER QUESTION: {question}

STRICT RULES:
- Base your answer ONLY on what is explicitly written in the document below.
- If something is not present, set its value to null. Never guess.
- Return a single JSON object:
  {{
    "summary": "one clear sentence answering the question",
    "findings": [
      {{"label": "field name", "value": "found value or null"}}
    ],
    "confidence": "high" | "medium" | "low",
    "source_quotes": ["exact short quote from the document"]
  }}
- Return ONLY the JSON. No markdown fences, no extra text.

DOCUMENT:
---
{document}
---"""


# ── PDF helpers ───────────────────────────────────────────────────────────────

def read_pdf(path: str) -> tuple[str, int]:
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
    return "\n\n".join(pages), len(pages)


def keyword_scan(text: str) -> list[str]:
    return [kw for kw in INSOLVENCY_KEYWORDS if kw in text]


def parse_llm(raw: str) -> dict:
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"summary": clean[:400], "findings": [], "confidence": "low", "source_quotes": []}


# ── LLM backends ──────────────────────────────────────────────────────────────

# One config dict — add/remove providers here, nowhere else
PROVIDERS = {
    #  name       base_url (None = Gemini SDK)           env key for fallback    default model
    "ollama":   ("http://localhost:11434/v1",             None,                   "llama3.1"),
    "openai":   ("https://api.openai.com/v1",            "OPENAI_API_KEY",       "gpt-4o-mini"),
    "deepseek": ("https://api.deepseek.com",             "DEEPSEEK_API_KEY",     "deepseek-chat"),
    "gemini":   (None,                                   "GEMINI_API_KEY",       "gemini-2.0-flash"),
}


def run_llm(provider: str, api_key: str, model: str, prompt: str) -> tuple[dict, str]:
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")

    base_url, env_key, default_model = PROVIDERS[provider]
    model   = model   or os.getenv("OLLAMA_MODEL", default_model)
    api_key = api_key or (os.getenv(env_key, "") if env_key else "nokey")

    if base_url:                                          # OpenAI-compatible (Ollama, OpenAI, DeepSeek)
        from openai import OpenAI
        r = OpenAI(api_key=api_key, base_url=base_url).chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], temperature=0.1,
        )
        return parse_llm(r.choices[0].message.content), f"{provider.capitalize()} · {model}"

    else:                                                 # Gemini
        from google import genai
        r = genai.Client(api_key=api_key).models.generate_content(model=model, contents=prompt)
        return parse_llm(r.text), f"Gemini · {model}"


# ── result saving ─────────────────────────────────────────────────────────────

def save_result(filename: str, question: str, result: dict, model: str, keywords: list) -> str:
    safe_name = re.sub(r"[^\w\-.]", "_", filename.replace(".pdf", ""))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path  = os.path.join(RESULTS_DIR, f"{safe_name}_{timestamp}.json")
    payload   = {
        "timestamp": datetime.now().isoformat(),
        "source_file": filename,
        "question": question,
        "model": model,
        "insolvency_keywords_found": keywords,
        **result,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return out_path


# ── routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/analyze", methods=["POST"])
def analyze():
    pdf_file = request.files.get("pdf")
    question = request.form.get("question", "").strip()
    provider = request.form.get("provider", os.getenv("PROVIDER", "ollama")).strip()
    api_key  = request.form.get("api_key",  "").strip()
    model    = request.form.get("model",    "").strip()

    if not pdf_file or not pdf_file.filename:
        return jsonify({"error": "No PDF uploaded."}), 400
    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        doc_text, n_pages = read_pdf(tmp_path)
    finally:
        os.unlink(tmp_path)

    if not doc_text.strip():
        return jsonify({"error": "Could not extract text. The PDF may be a scanned image."}), 422

    kw_hits = keyword_scan(doc_text)
    prompt  = PROMPT.format(question=question, document=doc_text[:25_000])

    try:
        result, model_label = run_llm(provider, api_key, model, prompt)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    save_result(pdf_file.filename, question, result, model_label, kw_hits)
    return jsonify({"model": model_label, "pages": n_pages, "keywords": kw_hits, **result})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
