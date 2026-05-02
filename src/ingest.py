"""
src/ingest.py
=============
Reads bis_standards.json, generates a vector embedding for every standard,
and stores them in a FAISS index for fast similarity search.

What this script produces
--------------------------
data/faiss_index.bin  — the vector index (fast nearest-neighbour lookup)
data/metadata.json    — maps each FAISS position → standard_id, title, full_text

Why we need two files
---------------------
FAISS stores only numbers (vectors). It has no idea what IS 269 or "cement" is.
metadata.json is the "label" file — once FAISS tells us "position 42 is the
nearest vector", we look up position 42 in metadata to get the actual standard.

What is an embedding (plain English)
-------------------------------------
Imagine a 384-dimensional coordinate. Every sentence in the world gets mapped
to a point in that 384-D space such that sentences with similar *meaning* land
close together — even if they use completely different words.

Example:
  "Portland cement for structural use"     →  [0.12, -0.34, 0.87, ...]
  "OPC binding material for construction"  →  [0.11, -0.31, 0.85, ...]  ← very close!
  "Corrugated asbestos roofing sheet"      →  [-0.72, 0.55, -0.19, ...] ← far away

FAISS finds the closest points in O(log n) time — that's the magic.
"""

import json
import os
import time
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR        = "data"
STANDARDS_FILE  = os.path.join(DATA_DIR, "bis_standards.json")
FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_FILE   = os.path.join(DATA_DIR, "metadata.json")

# ── Model ────────────────────────────────────────────────────────────────────
# all-MiniLM-L6-v2:
#   - 384-dimensional embeddings (small = fast)
#   - Trained on 1B+ sentence pairs for semantic similarity
#   - ~80 MB download, runs on CPU in ~50ms per sentence
#   - Consistently top performer for retrieval tasks at this size
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ── NOTE FOR LOCAL SETUP ─────────────────────────────────────────────────────
# First run will download ~80 MB from HuggingFace automatically.
# Make sure you have internet access when running for the first time.
# Subsequent runs use the local cache (~/.cache/huggingface/).
# ─────────────────────────────────────────────────────────────────────────────


def build_text_to_embed(record: dict) -> str:
    """
    Constructs the text we actually embed for each standard.

    We concatenate multiple fields so the embedding captures:
      - The IS number (for exact-ish matches like "IS 269")
      - The title (short, keyword-rich)
      - The section (category context)
      - The full_text (scope + requirements — the most semantically rich part)

    Putting the most important info first (title before full_text) gives it
    slightly more weight since transformer attention favours earlier tokens.
    """
    parts = [
        record.get("standard_id", ""),    # e.g. "IS 269: 1989"
        record.get("title", ""),           # e.g. "ORDINARY PORTLAND CEMENT, 33 GRADE"
        record.get("section", ""),         # e.g. "CEMENT AND CONCRETE"
        record.get("full_text", ""),       # Full scope + requirements text
    ]
    # Join with newlines so the model sees natural boundaries between fields
    return "\n".join(p for p in parts if p.strip())


def load_standards(path: str) -> list[dict]:
    """Loads the parsed standards from JSON."""
    with open(path, "r", encoding="utf-8") as f:
        standards = json.load(f)
    print(f"Loaded {len(standards)} standards from {path}")
    return standards


def generate_embeddings(
    texts: list[str],
    model: SentenceTransformer,
    batch_size: int = 64,
) -> np.ndarray:
    """
    Converts a list of text strings into a 2D numpy array of embeddings.

    Shape: (num_standards, 384)
    Each row is one standard's embedding vector.

    batch_size=64: process 64 texts at once. Bigger = faster but more RAM.
    show_progress_bar=True: shows a tqdm progress bar during encoding.
    normalize_embeddings=True: makes each vector unit length (L2 norm = 1).
        This is IMPORTANT — it lets us use dot product instead of cosine
        similarity, which is faster in FAISS (IndexFlatIP vs IndexFlatL2).
    """
    print(f"\nGenerating embeddings for {len(texts)} standards...")
    print(f"Model: {MODEL_NAME}")
    print(f"Batch size: {batch_size}")

    t0 = time.time()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,   # <-- unit vectors → use dot product
        convert_to_numpy=True,
    )
    elapsed = time.time() - t0

    print(f"\nEmbedding complete in {elapsed:.1f}s")
    print(f"Shape: {embeddings.shape}  (standards × dimensions)")
    print(f"dtype: {embeddings.dtype}")
    return embeddings.astype("float32")   # FAISS requires float32


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Builds a FAISS index from the embedding matrix.

    IndexFlatIP = Inner Product (dot product) similarity index.
    Because our vectors are L2-normalised, dot product == cosine similarity.
    'Flat' means we store every vector and do an exact search — no
    approximation. This is fine for 568 vectors (tiny). For millions of
    vectors you'd switch to IndexIVFFlat or HNSW.

    Why not IndexFlatL2?
    For normalised vectors, L2 distance and cosine similarity give identical
    rankings. IP is slightly more standard for semantic similarity tasks.
    """
    dim = embeddings.shape[1]   # 384 for MiniLM
    print(f"\nBuilding FAISS IndexFlatIP with dimension={dim}...")

    index = faiss.IndexFlatIP(dim)   # IP = Inner Product
    index.add(embeddings)            # Add all vectors at once

    print(f"FAISS index built. Total vectors stored: {index.ntotal}")
    return index


def save_index(index: faiss.Index, path: str):
    """Serialises the FAISS index to disk."""
    faiss.write_index(index, path)
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"Saved FAISS index → {path}  ({size_mb:.2f} MB)")


def save_metadata(standards: list[dict], path: str):
    """
    Saves a metadata list where position i corresponds to FAISS vector i.

    We deliberately strip full_text here to keep the file lightweight —
    we'll load full_text from this file at query time but we only need
    the essentials for fast lookup.

    Actually: we keep full_text here too so the retriever can return
    context to the LLM without re-reading the standards file.
    """
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
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(path) / 1024
    print(f"Saved metadata     → {path}  ({size_kb:.1f} KB, {len(metadata)} records)")


def verify_index(
    index: faiss.Index,
    metadata: list[dict],
    model: SentenceTransformer,
):
    """
    Sanity-check: run 3 test queries against the freshly built index
    and print the top-3 results for each.

    If the index is working correctly you should see:
      - "OPC cement" → IS 269, IS 8112, IS 12269 (OPC variants)
      - "steel reinforcement bars" → IS 1786, IS 432 (steel standards)
      - "aggregate for concrete" → IS 383, IS 9142 (aggregate standards)
    """
    test_queries = [
        "Ordinary Portland Cement 33 grade chemical requirements",
        "coarse and fine aggregates for structural concrete",
        "hollow lightweight concrete masonry blocks dimensions",
    ]

    print("\n── VERIFICATION QUERIES ────────────────────────────────────")
    for query in test_queries:
        q_vec = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype("float32")

        scores, indices = index.search(q_vec, 3)   # top-3

        print(f"\nQuery: \"{query}\"")
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
            m = metadata[idx]
            print(f"  #{rank}  score={score:.4f}  {m['standard_id']:<30} {m['title'][:55]}")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Load standards
    standards = load_standards(STANDARDS_FILE)

    # 2. Build the text to embed for each standard
    texts = [build_text_to_embed(r) for r in standards]

    # Quick preview of what we're embedding
    print(f"\nSample embed text for standards[3] ({standards[3]['standard_id']}):")
    print("─" * 60)
    print(texts[3][:300])
    print("─" * 60)

    # 3. Load the embedding model (downloads ~80 MB on first run)
    print(f"\nLoading model: {MODEL_NAME}")
    print("(First run downloads ~80 MB — subsequent runs use cache)")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}")

    # 4. Generate embeddings for all standards
    embeddings = generate_embeddings(texts, model)

    # 5. Build FAISS index
    index = build_faiss_index(embeddings)

    # 6. Save index and metadata
    save_index(index, FAISS_INDEX_FILE)
    save_metadata(standards, METADATA_FILE)

    # 7. Verify with test queries
    metadata = json.load(open(METADATA_FILE))
    verify_index(index, metadata, model)

    # 8. Final summary
    print("\n" + "═" * 55)
    print("  INGEST COMPLETE")
    print("═" * 55)
    print(f"  Standards indexed : {index.ntotal}")
    print(f"  Embedding dim     : {embeddings.shape[1]}")
    print(f"  Index file        : {FAISS_INDEX_FILE}")
    print(f"  Metadata file     : {METADATA_FILE}")
    print("═" * 55)
    print("\nYou can now run src/retriever.py to search the index.")


if __name__ == "__main__":
    main()
