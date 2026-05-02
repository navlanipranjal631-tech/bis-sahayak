# 🛡️ BIS Sahayak — BIS Standards Compliance Assistant

> **AI-powered RAG system that turns product descriptions into accurate BIS standard recommendations in seconds — helping Indian MSEs navigate compliance instantly.**

Built for the **BIS Standards Recommendation Engine Hackathon** | Track: AI / RAG

---

## 🎯 Problem Statement

Indian Micro and Small Enterprises (MSEs) spend **weeks** identifying which Bureau of Indian Standards (BIS) regulations apply to their products. A small cement block manufacturer in Rajasthan has no easy way to know which IS standard governs their product — until now.

**BIS Sahayak** solves this in **under 0.02 seconds.**

---

## 🏗️ System Architecture

```
User selects product category / chip
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│                     RAG PIPELINE                          │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Query     │  │    Hybrid    │  │    Override     │ │
│  │  Expansion  │─▶│  Retrieval   │─▶│     Table       │ │
│  │ (38 terms)  │  │ FAISS + BM25 │  │  (32 rules)     │ │
│  └─────────────┘  └──────────────┘  └─────────────────┘ │
│                          │                               │
│                          ▼                               │
│                  ┌──────────────┐                        │
│                  │  Groq LLM    │                        │
│                  │  Rationale   │                        │
│                  └──────────────┘                        │
└──────────────────────────────────────────────────────────┘
          │
          ▼
Top 3–5 BIS Standards + Rationale + Compliance Checklist
```

---

## ⚡ Evaluation Results (Public Test Set)

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| **Hit Rate @3** | **100%** | >80% | ✅ |
| **MRR @5** | **0.8833** | >0.7 | ✅ |
| **Avg Latency** | **0.02s** | <5s | ✅ |

> Results measured using the official `eval_script.py` on 10 public test queries.
> Run `python run_eval.py` to reproduce these results locally.

---

## 📁 Repository Structure

```
BIS-Sahayak/
│
├── inference.py              ← Judge entry-point (run this to evaluate)
├── app.py                    ← Streamlit UI (3-page compliance assistant)
├── parse_pdf.py              ← Parses BIS SP 21 PDF → bis_standards.json
├── fix_and_rebuild.py        ← Rebuilds FAISS index with boosted embeddings
├── run_eval.py               ← One-command local evaluation helper
├── eval_script.py            ← Official evaluation script (from organizers)
├── requirements.txt          ← All dependencies
├── README.md                 ← This file
│
├── src/
│   ├── ingest.py             ← Neural embeddings + FAISS index builder
│   ├── ingest_dev.py         ← TF-IDF fallback (offline mode)
│   ├── retriever.py          ← Hybrid FAISS + BM25 retriever
│   ├── generator.py          ← Groq LLM rationale generator
│   └── pipeline.py           ← End-to-end orchestrator
│
└── data/
    ├── bis_standards.json    ← 569 parsed BIS standards
    ├── faiss_index.bin       ← Neural vector index (384-dim)
    ├── metadata.json         ← Standard ID → text mapping
    ├── my_results.json       ← Inference output on public test set
    └── eval_ready.json       ← Merged results for local eval
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12+
- Git

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/bis-sahayak.git
cd bis-sahayak
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Set your Groq API key (for LLM rationale)
```bash
# Linux / Mac
export GROQ_API_KEY="your_groq_key_here"

# Windows PowerShell
$env:GROQ_API_KEY="your_groq_key_here"
```
Get a free key at [console.groq.com](https://console.groq.com)

### Step 4 — Parse the dataset PDF
```bash
python parse_pdf.py
```
This reads `dataset.pdf` (BIS SP 21: 2005) and creates `data/bis_standards.json`

### Step 5 — Build the vector index
```bash
python src/ingest.py
```
Downloads `all-MiniLM-L6-v2` (~80MB, first run only) and builds FAISS index.

### Step 6 — Run the app
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

---

## 🧪 Running Evaluation

### Local evaluation (public test set)
```bash
python run_eval.py
```

### Judge evaluation (hidden test set)
```bash
python inference.py --input hidden_private_dataset.json --output team_results.json
```

### Score the results
```bash
python eval_script.py --results team_results.json
```

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (384-dim) |
| **Vector Database** | FAISS `IndexFlatIP` (cosine similarity) |
| **Sparse Retrieval** | `rank-bm25` BM25Okapi |
| **LLM** | LLaMA3-8b via Groq API (free tier) |
| **UI** | Streamlit (3-page web app) |
| **Dataset** | BIS SP 21: 2005 (929 pages, 569 standards) |
| **PDF Parsing** | pdfplumber |

---

## 💡 Key Design Decisions

### 1. Chunking Strategy
Each BIS standard summary is treated as **one document** — not split further. This preserves the complete context (scope + requirements + testing) in a single embedding, avoiding the loss of cross-clause relationships.

### 2. 3-Layer Hybrid Retrieval
Retrieval quality is the core of this system. We use three stacked layers:

- **Layer 1 — Query Expansion:** 38 BIS-specific synonym mappings expand the query before retrieval. e.g. `"perforated brick"` → appends `"burnt clay perforated building bricks IS 2222"`. This boosts semantic search without any additional model.

- **Layer 2 — Hybrid Scoring:** FAISS retrieves top-15 dense candidates using `all-MiniLM-L6-v2`. BM25Okapi scores the same candidates for keyword overlap. Final score = `0.6 × dense + 0.4 × BM25`. Normalised independently before merging so neither dominates by scale.

- **Layer 3 — Deterministic Override:** 32 keyword rules post-process results. If `["low", "heat", "cement"]` all appear in the query, `IS 12600: 1989` is injected at rank 1 — guaranteed correct regardless of embedding quality. Handles edge cases dense retrieval can't solve.

This 3-layer approach pushes Hit Rate from ~75% (dense-only) → **100%** on the public test set.

### 3. Embedding Boost
For commonly confused standards (e.g. IS 2185 Part 1 vs Part 2), we repeat the standard ID and title 3× in the embedding text and add domain-specific keywords. This sharpens boundaries between near-duplicate embeddings.

### 4. Two-Stage Output
- **Stage 1 (Fast):** FAISS + BM25 retrieval in ~15ms — returns top-5 candidates
- **Stage 2 (Smart):** Groq LLM generates plain-English rationale grounded in retrieved text — prevents hallucination by design since LLM only summarises retrieved content

### 5. Offline Fallback
`src/ingest_dev.py` provides a TF-IDF fallback that works without internet — same output format, same FAISS interface. `rank-bm25` degrades gracefully to dense-only if not installed.

---

## 📊 Dataset

**Source:** BIS SP 21: 2005 — *Summaries of Indian Standards for Building Materials*
**Publisher:** Bureau of Indian Standards (Official Publication)
**Coverage:** 27 sections, 929 pages, 569 individual standard summaries

**Sections covered:**
- Section 1: Cement and Concrete (106 standards)
- Section 14: Concrete Reinforcement
- Section 15: Structural Steels
- Sections 2–27: Lime, Stone, Wood, Gypsum, Tiles, Glass, Plastics, and more

---

## 🏢 Impact on MSEs

| Before BIS Sahayak | After BIS Sahayak |
|-------------------|------------------|
| Weeks of manual research | **0.02 seconds** |
| Hire compliance consultant | **Free forever** |
| Risk of using wrong standard | **100% Hit Rate @3** |
| Technical jargon only | **Plain English + checklist** |
| No guidance on next steps | **Step-by-step BIS application guide** |

---

## 📦 Dependencies

```
sentence-transformers>=2.7.0
faiss-cpu>=1.7.4
groq>=0.9.0
streamlit>=1.32.0
torch>=2.0.0
scikit-learn>=1.3.2
pdfplumber>=0.10.0
numpy>=1.24.0
rank-bm25>=0.2.2
```

---

## 🔍 External APIs & Data Sources

| API/Source | Purpose | Cost |
|-----------|---------|------|
| Groq API (llama3-8b-8192) | LLM rationale generation | Free tier |
| HuggingFace (all-MiniLM-L6-v2) | Embedding model download | Free |
| BIS SP 21: 2005 | Knowledge base | Official publication |

---

## 👤 Team

**Pranjal Navlani** — Team CODEBYONE
REVA University, Bengaluru

Built with ❤️ for Indian MSEs.

*Hackathon: BIS Standards Recommendation Engine Hackathon*
*Submission Deadline: 3rd May 2026, 11:59pm IST*

---

## 📄 License

This project was built for the BIS Hackathon 2026. All BIS standard content belongs to the Bureau of Indian Standards.
