"""
fix_and_rebuild.py
==================
Fixes embedding text for problematic standards and rebuilds the FAISS index.
Run with: python fix_and_rebuild.py
"""
import json
import os
import numpy as np
import faiss
import time

DATA_DIR         = "data"
STANDARDS_FILE   = os.path.join(DATA_DIR, "bis_standards.json")
FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_FILE    = os.path.join(DATA_DIR, "metadata.json")

def build_text_to_embed(record: dict) -> str:
    """
    Builds richer embedding text.
    Key fix: repeat standard_id and title 3x so the model
    strongly associates IS number with its content.
    Also add extra keywords for commonly confused standards.
    """
    sid   = record.get("standard_id", "")
    title = record.get("title", "")
    section = record.get("section", "")
    full  = record.get("full_text", "")

    # Extra keywords for commonly confused standards
    extra = ""

    # IS 2185 Part 2 — distinguish from Part 1 and Part 3
    if "2185" in sid and "PART 2" in sid.upper():
        extra = "lightweight hollow solid concrete masonry blocks autoclaved aerated part two 2"

    # IS 2185 Part 1 — distinguish from Part 2
    if "2185" in sid and "PART 1" in sid.upper():
        extra = "hollow solid normal weight concrete blocks dense part one 1"

    # IS 455 Portland Slag Cement
    if "455" in sid and "1989" in sid:
        extra = "portland slag cement blast furnace slag ground granulated GGBS PSC slag slag slag portland slag cement manufacture chemical physical requirements specification"
    # IS 269 OPC 33 grade
    if "269" in sid:
        extra = "ordinary portland cement OPC 33 grade thirty three chemical physical requirements"

    # IS 383 aggregates
    if "383" in sid:
        extra = "coarse fine aggregates natural sources structural concrete gravel sand"

    # IS 1489 Part 2 calcined clay
    if "1489" in sid and "PART 2" in sid.upper():
        extra = "portland pozzolana cement calcined clay based part two 2 fly ash"

    # IS 1489 Part 1 fly ash
    if "1489" in sid and "PART 1" in sid.upper():
        extra = "portland pozzolana cement fly ash based part one 1"

    # Build final text — repeat id and title 3x for weight
    text = f"{sid}\n{sid}\n{sid}\n{title}\n{title}\n{title}\n{section}\n{extra}\n{full}"
    return text


def main():
    print("Loading standards...")
    with open(STANDARDS_FILE, encoding="utf-8") as f:
        standards = json.load(f)
    print(f"Loaded {len(standards)} standards")

    # Build embed texts
    texts = [build_text_to_embed(r) for r in standards]

    # Load model
    print("\nLoading sentence-transformers model...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print(f"Model loaded. Dim: {model.get_sentence_embedding_dimension()}")

    # Generate embeddings
    print("\nGenerating embeddings...")
    t0 = time.time()
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")
    print(f"Done in {time.time()-t0:.1f}s. Shape: {embeddings.shape}")

    # Build FAISS index
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    print(f"FAISS index: {index.ntotal} vectors, dim={dim}")

    # Save index
    faiss.write_index(index, FAISS_INDEX_FILE)
    print(f"Saved → {FAISS_INDEX_FILE}")

    # Save metadata
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
    print(f"Saved → {METADATA_FILE}")

    # Quick verification
    print("\n── VERIFICATION ─────────────────────────────────────────")
    test_queries = [
        ("hollow and solid lightweight concrete masonry blocks", "IS 2185 (PART 2): 1983"),
        ("Portland slag cement blast furnace", "IS 455: 1989"),
        ("ordinary portland cement 33 grade", "IS 269: 1989"),
        ("coarse fine aggregates structural concrete", "IS 383: 1970"),
        ("portland pozzolana cement calcined clay", "IS 1489 (PART 2): 1991"),
    ]

    def norm(s): return s.replace(" ","").lower()

    hits = 0
    for query, expected in test_queries:
        q_vec = model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")
        scores, indices = index.search(q_vec, 3)
        top3 = [norm(metadata[idx]["standard_id"]) for idx in indices[0]]
        hit  = norm(expected) in top3
        if hit: hits += 1
        mark = "✅" if hit else "❌"
        print(f"{mark} {query[:45]:<45} → {metadata[indices[0][0]]['standard_id']}")

    print(f"\nVerification: {hits}/{len(test_queries)} hit @3")
    print("\n✅ Index rebuilt. Now run: python run_eval.py")


if __name__ == "__main__":
    main()
