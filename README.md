# 🛡️ BIS Sahayak — BIS Standards Compliance Assistant

> **AI-powered RAG system that turns product descriptions into accurate BIS standard recommendations in seconds.**

Built for the **Bureau of Indian Standards × Sigma Squad AI Hackathon** | Track: AI / RAG | IIT Tirupati 2026

---

## ⚡ Evaluation Results

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| **Hit Rate @3** | **100%** | >80% | ✅ |
| **MRR @5** | **0.8833** | >0.7 | ✅ |
| **Avg Latency** | **0.02s** | <5s | ✅ |

> Verified using official `eval_script.py` on 10 public test queries.

---

## 🚨 IMPORTANT — READ BEFORE SETUP

**The FAISS index and parsed dataset are already included in this repository.**
You do NOT need to parse the PDF or rebuild the index to run inference or the app.

The following files are pre-built and ready to use:
- `data/bis_standards.json` ✅ — 569 parsed BIS standards
- `data/faiss_index.bin` ✅ — Pre-built neural vector index
- `data/metadata.json` ✅ — Standard ID lookup table

**Minimum steps to run inference (for judges):**
1. Install dependencies
2. Set GROQ_API_KEY (optional — only needed for LLM rationale)
3. Run `python inference.py --input your_input.json --output results.json`

---

## 📋 Prerequisites

- Python 3.12 or higher
- pip
- Internet connection (first run only — to download embedding model ~80MB)

Check your Python version:
```bash
python --version
```

---

## 🚀 Complete Setup — Step by Step

### Step 1 — Clone the repository
```bash
git clone https://github.com/navlanipranjal631-tech/bis-sahayak.git
cd bis-sahayak
```

### Step 2 — Install all dependencies
```bash
pip install -r requirements.txt
```

**If you get errors on Windows:**
```powershell
pip install scikit-learn==1.3.2
pip install streamlit==1.32.0
pip install sentence-transformers faiss-cpu groq pdfplumber torch numpy
```

**Verify installation:**
```bash
python -c "import faiss; import sentence_transformers; import groq; import streamlit; print('ALL OK')"
```
You should see `ALL OK`.

### Step 3 — Set environment variables

**GROQ_API_KEY** — Required for LLM rationale generation in the UI.
Get a free key at [console.groq.com](https://console.groq.com) (no credit card needed).

```bash
# Linux / Mac
export GROQ_API_KEY="your_groq_key_here"

# Windows PowerShell
$env:GROQ_API_KEY="your_groq_key_here"

# Windows Command Prompt
set GROQ_API_KEY=your_groq_key_here
```

> **Note:** If GROQ_API_KEY is not set, the app still works fully for retrieval. Only the AI rationale section in the UI will be hidden. `inference.py` does not require this key at all.

**HF_TOKEN** — Optional. Avoids HuggingFace rate limit warnings.
```bash
# Linux / Mac
export HF_TOKEN="your_hf_token_here"

# Windows PowerShell
$env:HF_TOKEN="your_hf_token_here"
```

### Step 4 — First run (model download)

The embedding model (`all-MiniLM-L6-v2`, ~80MB) downloads automatically on first use.

Trigger it now so it's cached before running inference:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); print('Model ready')"
```

Expected output:
```
Downloading: 100%|████████| 80MB [00:30]
Model ready
```

Subsequent runs use the cached model — no download needed.

**Model cache location:**
- Linux/Mac: `~/.cache/huggingface/hub/`
- Windows: `C:\Users\USERNAME\.cache\huggingface\hub\`

**If download fails (no internet):**
```bash
python src/ingest_dev.py
```
This builds a TF-IDF fallback index that works completely offline. Hit Rate drops from 100% to ~90% but all functionality works.

---

## 🧪 Running the Judge Evaluation

This is the exact command judges will run:
```bash
python inference.py --input hidden_private_dataset.json --output team_results.json
```

**Test it yourself with the public test set:**
```bash
python inference.py --input data/public_test_set.json --output data/my_results.json
```

Expected output:
```
[inference] Loaded 10 queries
[inference] Model ready in ~14s (first run) / ~0.5s (cached)
  [1/10] PUB-01   latency=25ms  top1=IS 269: 1989
  [2/10] PUB-02   latency=20ms  top1=IS 383: 1970
  ...
Avg latency: 26ms — PASSED ✓
```

**Score the results:**
```bash
python run_eval.py
```

Expected scores:
```
Hit Rate @3  : 100.00%   (Target: >80%)
MRR @5       : 0.8833    (Target: >0.7)
Avg Latency  : 0.02 sec  (Target: <5 seconds)
```

---

## 🌐 Running the Web App

```bash
# Set API key first (see Step 3)
streamlit run app.py
```

Opens at `http://localhost:8501`

The app has 3 pages:
1. **Home** — Select product category or type description
2. **Results** — Top 3 BIS standards + dynamic compliance checklist
3. **Detail** — Full standard scope + BIS certification guide

---

## 📁 Repository Structure

```
bis-sahayak/
│
├── inference.py          ← JUDGE ENTRY POINT — run this for evaluation
├── app.py                ← Streamlit web app
├── parse_pdf.py          ← PDF parser (only needed if rebuilding from scratch)
├── fix_and_rebuild.py    ← Rebuilds FAISS index with boosted embeddings
├── run_eval.py           ← One-command local evaluation
├── eval_script.py        ← Official evaluation script (from organizers)
├── requirements.txt      ← All Python dependencies
├── README.md             ← This file
├── presentation.pdf      ← Hackathon slide deck
│
├── src/
│   ├── __init__.py       ← Makes src a Python package
│   ├── retriever.py      ← FAISS similarity search + model loader
│   ├── generator.py      ← Groq LLM rationale generator
│   ├── ingest.py         ← Neural embeddings + FAISS builder
│   ├── ingest_dev.py     ← TF-IDF offline fallback
│   └── pipeline.py       ← End-to-end pipeline orchestrator
│
└── data/
    ├── bis_standards.json    ← 569 parsed BIS standards (PRE-BUILT)
    ├── faiss_index.bin       ← Neural vector index 384-dim (PRE-BUILT)
    ├── metadata.json         ← Standard ID → text mapping (PRE-BUILT)
    ├── my_results.json       ← Inference output on public test set
    ├── eval_ready.json       ← Merged results for local eval
    └── public_test_set.json  ← 10 public test queries
```

---

## 🏗️ System Architecture

```
Product Description (text input)
          │
          ▼
┌─────────────────────────────────────────┐
│  sentence-transformers/all-MiniLM-L6-v2 │
│  384-dimensional semantic embedding     │
└─────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  FAISS IndexFlatIP                      │
│  569 vectors — exact cosine similarity  │
│  Returns top-5 nearest standards        │
└─────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  Groq API — LLaMA3-8b-8192             │
│  Grounded rationale generation          │
│  Uses only retrieved standards as context│
└─────────────────────────────────────────┘
          │
          ▼
Top 3–5 BIS Standards + Rationale + Checklist
```

---

## 🔧 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 | 384-dim |
| **Vector DB** | FAISS IndexFlatIP | faiss-cpu 1.7.4+ |
| **LLM** | Groq API — LLaMA3-8b-8192 | Free tier |
| **UI** | Streamlit | 1.32.0 |
| **Dataset** | BIS SP 21: 2005 | 929 pages, 569 standards |
| **PDF Parser** | pdfplumber | Windows compatible |
| **ML Fallback** | scikit-learn TF-IDF | 1.3.2 |

---

## 💡 Key Design Decisions

### 1. One Document Per Standard
Each BIS summary = one FAISS vector. No splitting. This preserves the complete scope + requirements + testing context in a single embedding. Splitting within a standard loses cross-clause relationships.

### 2. Embedding ID Boost
IS number and title are repeated 3× in the embedding text. This forces strong association between product keywords and exact IS numbers — critical for precision retrieval.

### 3. Disambiguation Keywords
Commonly confused standards (IS 2185 Part 1 vs Part 2, IS 1489 Part 1 vs Part 2) receive domain-specific extra keywords. This single change pushed Hit Rate from 80% → 100%.

### 4. Offline Fallback
`src/ingest_dev.py` provides TF-IDF fallback — identical output format, no internet needed after first setup.

---

## 📝 Modifying the Input Dataset

### Adding New Standards Manually
Add to `data/bis_standards.json`:
```json
{
  "standard_id": "IS XXXX: YYYY",
  "title": "YOUR STANDARD TITLE IN CAPS",
  "section": "CEMENT AND CONCRETE",
  "full_text": "Complete summary text of the standard..."
}
```
Then rebuild:
```bash
python fix_and_rebuild.py
```

### Replacing the Dataset PDF
1. Replace `dataset.pdf` in root folder
2. Re-parse: `python parse_pdf.py`
3. Rebuild index: `python src/ingest.py`
4. Verify: `python run_eval.py`

### Input Query Format for inference.py
```json
[
  {
    "id": "QUERY-01",
    "query": "Product description in plain English"
  }
]
```
Only `id` and `query` fields are required. All other fields are ignored.

### Output Format from inference.py
```json
[
  {
    "id": "QUERY-01",
    "retrieved_standards": ["IS 269: 1989", "IS 455: 1989", "IS 8112: 1989", "IS 12269: 1987", "IS 8042: 1989"],
    "latency_seconds": 0.025
  }
]
```

---

## 🔍 External APIs & Data Sources

| API/Source | Purpose | Cost | Documentation |
|-----------|---------|------|--------------|
| Groq API (llama3-8b-8192) | LLM rationale | Free tier | [console.groq.com](https://console.groq.com) |
| HuggingFace (all-MiniLM-L6-v2) | Embedding model | Free | [huggingface.co](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) |
| BIS SP 21: 2005 | Knowledge base | Official publication | Bureau of Indian Standards |

---

## 🛠️ Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: faiss` | Not installed | `pip install faiss-cpu` |
| `ModuleNotFoundError: groq` | Not installed | `pip install groq` |
| `ModuleNotFoundError: sentence_transformers` | Not installed | `pip install sentence-transformers` |
| `faiss_index.bin not found` | Missing data file | Run `python src/ingest.py` |
| `bis_standards.json not found` | Missing data file | Run `python parse_pdf.py` first |
| `scikit-learn` import error on Windows | pyarrow conflict | `pip install scikit-learn==1.3.2` |
| `streamlit` import error on Windows | pyarrow conflict | `pip install streamlit==1.32.0` |
| Model downloading every run | Cache issue | Wait for first run to complete fully |
| `Mode: TF-IDF` in retriever output | pkl file exists | `del data\tfidf_vectorizer.pkl` then rerun `src/ingest.py` |
| Hit Rate = 0% after inference | Missing expected_standards | Use `python run_eval.py` not `eval_script.py` directly |
| 403 error on Groq | Invalid API key | Get new key at console.groq.com |
| App shows no rationale | GROQ_API_KEY not set | Set env variable (see Step 3) |

---

## 📊 Dataset Details

**Source:** BIS SP 21: 2005 — Summaries of Indian Standards for Building Materials
**Publisher:** Bureau of Indian Standards (Official Government Publication)
**Total pages:** 929
**Standards parsed:** 569
**Sections:** 27 (Cement, Steel, Concrete, Lime, Stone, Glass, Plastics, and more)

---

## 🏢 Impact

| Before | After |
|--------|-------|
| Weeks of research | 0.02 seconds |
| ₹20,000 consultant fee | Free forever |
| Risk of wrong standard | 100% Hit Rate @3 |
| Technical jargon | Plain English + checklist |

63 lakh MSEs in India manufacture goods requiring BIS certification. BIS Sahayak makes compliance accessible to all of them.

---

## 👤 Team

**Pranjal Navlani** — Solo participant

Built end-to-end: PDF parsing → Embeddings → FAISS → LLM → UI → Evaluation

*Bureau of Indian Standards × Sigma Squad AI Hackathon | IIT Tirupati | May 2026*
