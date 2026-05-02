"""
src/retriever.py
================
Loads the FAISS index + metadata ONCE at startup, then answers
retrieve(query) calls in milliseconds.

Two modes depending on what's available:
  1. Neural (production): sentence-transformers all-MiniLM-L6-v2
  2. TF-IDF (dev/offline): sklearn vectorizer from ingest_dev.py

The retriever auto-detects which mode to use based on whether
data/tfidf_vectorizer.pkl exists. No code changes needed.

What is cosine similarity (plain English)?
------------------------------------------
Imagine every standard as a direction in space (a unit vector).
When you type a query, it also becomes a direction.
Cosine similarity = how well those two directions "point the same way".
  1.0  = identical direction (perfect match)
  0.0  = perpendicular (no relation)
 -1.0  = opposite directions (can't happen with TF-IDF / positive embeddings)

A score of 0.35 is a strong match for TF-IDF on this dataset.
Neural embeddings typically give scores in 0.6–0.9 range.

Why load model at startup, not per query?
-----------------------------------------
Loading the model takes ~1–2 seconds.
If you loaded it inside retrieve(), every single query would take 2+ seconds
just for model loading — BEFORE any actual search.
By loading once at module import time, all queries after the first share
the already-loaded model, giving ~50ms per query.
This is critical for hitting the <5 second latency target.
"""

import json
import os
import pickle
import time
import numpy as np
import faiss

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR         = "data"
FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_FILE    = os.path.join(DATA_DIR, "metadata.json")
VECTORIZER_FILE  = os.path.join(DATA_DIR, "tfidf_vectorizer.pkl")

# ── Load index and metadata at MODULE IMPORT TIME ────────────────────────────
# These lines run once when Python first imports this file.
# Every call to retrieve() after that reuses the already-loaded objects.
print("[retriever] Loading FAISS index and metadata...")
_t0 = time.time()

_index    = faiss.read_index(FAISS_INDEX_FILE)
_metadata = json.load(open(METADATA_FILE, encoding="utf-8"))

print(f"[retriever] Index loaded: {_index.ntotal} vectors, dim={_index.d}  [{time.time()-_t0:.2f}s]")


# ── Load embedding model (auto-detect neural vs TF-IDF) ──────────────────────
def _load_embedder():
    """
    Returns an embed_fn: list[str] → np.ndarray (float32, L2-normalised).
    Tries neural (sentence-transformers) first, falls back to TF-IDF.
    """
    # Try TF-IDF first (works offline, always available after ingest_dev.py)
    if os.path.exists(VECTORIZER_FILE):
        from sklearn.preprocessing import normalize as sk_normalize
        with open(VECTORIZER_FILE, "rb") as f:
            vectorizer = pickle.load(f)
        print("[retriever] Mode: TF-IDF (dev)  — run ingest.py for neural embeddings")

        def tfidf_embed(texts: list[str]) -> np.ndarray:
            mat = vectorizer.transform(texts).toarray().astype("float32")
            return sk_normalize(mat, norm="l2")

        return tfidf_embed

    # Fall back to sentence-transformers (production)
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("[retriever] Mode: Neural (sentence-transformers all-MiniLM-L6-v2)")

        def neural_embed(texts: list[str]) -> np.ndarray:
            return model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
            ).astype("float32")

        return neural_embed

    except Exception as e:
        raise RuntimeError(
            "No embedding model found. Run src/ingest_dev.py (offline) "
            "or src/ingest.py (online) first."
        ) from e


_embed = _load_embedder()   # loaded once at import time


# ── Public API ────────────────────────────────────────────────────────────────

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Search the FAISS index for the top_k most relevant BIS standards.

    Parameters
    ----------
    query   : natural-language product description from the user
    top_k   : how many standards to return (default 5 for eval @5)

    Returns
    -------
    List of dicts, each containing:
        standard_id  : e.g. "IS 269: 1989"
        title        : e.g. "ORDINARY PORTLAND CEMENT, 33 GRADE"
        section      : e.g. "CEMENT AND CONCRETE"
        full_text    : complete summary text (used as LLM context)
        score        : cosine similarity score (higher = more relevant)
        rank         : 1-based position in results
    """
    # 1. Embed the query using the same model/vectorizer used for indexing
    #    Shape after embed: (1, dim)  — batch of 1
    q_vec = _embed([query])   # always pass as list

    # 2. Search FAISS for top_k nearest neighbours
    #    scores  shape: (1, top_k)  — similarity scores
    #    indices shape: (1, top_k)  — positions in the index
    scores, indices = _index.search(q_vec, top_k)

    # 3. Map FAISS positions back to standard metadata
    results = []
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        if idx == -1:   # FAISS returns -1 if not enough vectors exist
            continue
        meta = _metadata[idx]
        results.append({
            "standard_id": meta["standard_id"],
            "title":       meta["title"],
            "section":     meta["section"],
            "full_text":   meta["full_text"],
            "score":       float(score),
            "rank":        rank,
        })

    return results


def retrieve_standard_ids(query: str, top_k: int = 5) -> list[str]:
    """
    Convenience wrapper — returns only the list of standard IDs.
    Used by inference.py to build the output JSON.

    Example return: ["IS 269: 1989", "IS 8112: 1989", "IS 455: 1989", ...]
    """
    results = retrieve(query, top_k)
    return [r["standard_id"] for r in results]


# ── CLI test (run directly: python src/retriever.py) ─────────────────────────
if __name__ == "__main__":
    print("\n" + "═"*60)
    print("  RETRIEVER TEST — top-5 results per query")
    print("═"*60)

    test_queries = [
        # From public test set — expected answers in brackets
        ("We manufacture 33 Grade OPC cement",
         "IS 269: 1989"),
        ("Coarse and fine aggregates for structural concrete",
         "IS 383: 1970"),
        ("Portland pozzolana cement calcined clay based",
         "IS 1489 (Part 2): 1991"),
        ("Hollow and solid lightweight concrete masonry blocks",
         "IS 2185 (Part 2): 1983"),
        ("White Portland cement for architectural purposes",
         "IS 8042: 1989"),
    ]

    hit_count = 0
    for query, expected in test_queries:
        t0 = time.time()
        results = retrieve(query, top_k=5)
        latency = time.time() - t0

        retrieved_ids = [r["standard_id"] for r in results]

        # Check if expected standard is in top-3
        def norm(s): return s.replace(" ", "").lower()
        in_top3 = any(norm(expected) == norm(rid) for rid in retrieved_ids[:3])
        if in_top3:
            hit_count += 1
            hit_marker = "✅"
        else:
            hit_marker = "❌"

        print(f"\n{hit_marker} Query   : {query}")
        print(f"   Expected: {expected}")
        print(f"   Latency : {latency*1000:.0f}ms")
        for r in results:
            marker = "→" if norm(r["standard_id"]) == norm(expected) else " "
            print(f"   {marker} #{r['rank']}  score={r['score']:.4f}  "
                  f"{r['standard_id']:<30}  {r['title'][:45]}")

    print(f"\n{'═'*60}")
    print(f"  Hit Rate @3 on sample: {hit_count}/{len(test_queries)} "
          f"= {hit_count/len(test_queries)*100:.0f}%")
    print(f"{'═'*60}\n")
