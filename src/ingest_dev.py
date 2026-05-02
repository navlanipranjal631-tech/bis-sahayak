"""
src/ingest_dev.py
=================
SANDBOX / OFFLINE FALLBACK — produces the exact same output files as ingest.py
(data/faiss_index.bin + data/metadata.json) but uses TF-IDF vectors instead
of sentence-transformer embeddings.

Use this when HuggingFace is not accessible.
Use src/ingest.py (the real one) on your local machine for the hackathon submission.

Why TF-IDF works here
---------------------
TF-IDF turns text into sparse vectors based on word frequency.
Not as powerful as neural embeddings for synonyms, but perfectly fine for:
  - BIS standards which use very consistent, domain-specific vocabulary
  - Development + testing of the retriever / pipeline / inference.py
  - Verifying eval metrics logic before switching to neural embeddings

The FAISS index and metadata.json format is IDENTICAL to what ingest.py produces,
so retriever.py, pipeline.py, and inference.py need ZERO changes.
"""

import json
import os
import time
import numpy as np
import faiss
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR         = "data"
STANDARDS_FILE   = os.path.join(DATA_DIR, "bis_standards.json")
FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_FILE    = os.path.join(DATA_DIR, "metadata.json")
VECTORIZER_FILE  = os.path.join(DATA_DIR, "tfidf_vectorizer.pkl")   # needed by retriever


def build_text_to_embed(record: dict) -> str:
    """
    Same function as in ingest.py — combine all fields into one string.
    Standard_id + title are repeated to boost their weight in TF-IDF.
    """
    sid   = record.get("standard_id", "")
    title = record.get("title", "")
    return "\n".join([
        sid,
        sid,        # repeat for weight
        title,
        title,      # repeat for weight
        record.get("section", ""),
        record.get("full_text", ""),
    ])


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Load standards
    with open(STANDARDS_FILE, encoding="utf-8") as f:
        standards = json.load(f)
    print(f"Loaded {len(standards)} standards from {STANDARDS_FILE}")

    # 2. Build texts
    texts = [build_text_to_embed(r) for r in standards]

    # 3. Fit TF-IDF vectorizer
    print("\nFitting TF-IDF vectorizer...")
    t0 = time.time()
    vectorizer = TfidfVectorizer(
        max_features=8192,      # vocabulary size cap
        ngram_range=(1, 2),     # unigrams + bigrams (catches "portland cement")
        sublinear_tf=True,      # log(tf+1) — reduces impact of very common words
        min_df=1,               # keep rare terms (standard numbers appear once)
    )
    tfidf_matrix = vectorizer.fit_transform(texts)   # shape: (568, 8192) sparse
    print(f"TF-IDF matrix: {tfidf_matrix.shape}  [{time.time()-t0:.1f}s]")

    # 4. Convert sparse → dense float32 and L2-normalise
    #    (normalise so dot product == cosine similarity, matching ingest.py behaviour)
    dense = tfidf_matrix.toarray().astype("float32")
    dense = normalize(dense, norm="l2")               # in-place unit normalisation
    print(f"Dense normalised matrix: {dense.shape}")

    # 5. Build FAISS IndexFlatIP (Inner Product == cosine on unit vectors)
    dim   = dense.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(dense)
    print(f"FAISS index built — {index.ntotal} vectors, dim={dim}")

    # 6. Save FAISS index
    faiss.write_index(index, FAISS_INDEX_FILE)
    print(f"Saved → {FAISS_INDEX_FILE}  ({os.path.getsize(FAISS_INDEX_FILE)/1024:.0f} KB)")

    # 7. Save metadata (position i ↔ standard i)
    metadata = [
        {
            "index":       i,
            "standard_id": r["standard_id"],
            "title":       r["title"],
            "section":     r["section"],
            "full_text":   r["full_text"],
        }
        for i, r in enumerate(standards)
    ]
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Saved → {METADATA_FILE}  ({os.path.getsize(METADATA_FILE)/1024:.0f} KB)")

    # 8. Save vectorizer (retriever.py needs it to embed new queries)
    with open(VECTORIZER_FILE, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"Saved → {VECTORIZER_FILE}  (vectorizer for query embedding)")

    # 9. Verification — run 3 test queries
    print("\n── VERIFICATION ─────────────────────────────────────────────")
    test_queries = [
        "Ordinary Portland Cement 33 grade chemical requirements",
        "coarse and fine aggregates for structural concrete",
        "hollow lightweight concrete masonry blocks dimensions",
    ]
    for query in test_queries:
        q_vec = vectorizer.transform([query]).toarray().astype("float32")
        q_vec = normalize(q_vec, norm="l2")
        scores, indices = index.search(q_vec, 3)
        print(f"\nQuery: \"{query}\"")
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
            m = metadata[idx]
            print(f"  #{rank}  score={score:.4f}  {m['standard_id']:<30} {m['title'][:55]}")

    print("\n" + "═"*55)
    print("  INGEST (DEV) COMPLETE")
    print("═"*55)
    print(f"  Standards indexed : {index.ntotal}")
    print(f"  Embedding dim     : {dim}  (TF-IDF)")
    print(f"  Index file        : {FAISS_INDEX_FILE}")
    print(f"  Metadata file     : {METADATA_FILE}")
    print(f"  Vectorizer file   : {VECTORIZER_FILE}")
    print("═"*55)
    print("\n  ✅  Same output format as ingest.py — retriever.py works unchanged.")
    print("  ⚠️   Switch to ingest.py (sentence-transformers) for final submission.\n")


if __name__ == "__main__":
    main()
