"""
src/pipeline.py
===============
Connects retriever → generator into a single run_pipeline() function.
This is the single entry-point used by both app.py (UI) and inference.py (eval).

Flow
----
  query (str)
    │
    ├─► retriever.retrieve()        ~5ms   — FAISS vector search
    │       returns top-5 standards
    │
    ├─► generator.generate_rationale()  ~800ms  — Groq LLM call
    │       returns explanation text
    │
    └─► package into result dict + record latency
"""

import time
import sys
import os

# Allow running from project root or src/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retriever import retrieve, retrieve_standard_ids
from src.generator import generate_rationale


def run_pipeline(query: str, top_k: int = 5, include_rationale: bool = True) -> dict:
    """
    Full RAG pipeline: query → retrieved standards + rationale.

    Parameters
    ----------
    query            : user's product description (free text)
    top_k            : number of standards to retrieve (default 5)
    include_rationale: set False to skip LLM call (faster, for eval-only runs)

    Returns
    -------
    {
      "query"               : str   — original query
      "retrieved_standards" : list  — standard IDs ["IS 269: 1989", ...]
      "retrieved_details"   : list  — full dicts with score, title, full_text
      "rationale"           : str   — LLM explanation (empty if include_rationale=False)
      "latency_seconds"     : float — total wall-clock time for this call
    }
    """
    t_start = time.time()

    # ── Step 1: Retrieve ──────────────────────────────────────────────────────
    retrieved_details = retrieve(query, top_k=top_k)
    retrieved_ids     = [r["standard_id"] for r in retrieved_details]

    # ── Step 2: Generate rationale (optional) ────────────────────────────────
    if include_rationale:
        rationale = generate_rationale(query, retrieved_details)
    else:
        rationale = ""

    # ── Step 3: Record latency ────────────────────────────────────────────────
    latency = round(time.time() - t_start, 4)

    return {
        "query":                query,
        "retrieved_standards":  retrieved_ids,
        "retrieved_details":    retrieved_details,
        "rationale":            rationale,
        "latency_seconds":      latency,
    }


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print("\n" + "═"*65)
    print("  PIPELINE END-TO-END TEST")
    print("═"*65)

    # Test with retrieval only (no LLM) to verify latency without API key
    test_queries = [
        "We manufacture 33 Grade OPC cement for construction",
        "Coarse aggregates from natural sources for structural concrete",
        "Hollow lightweight concrete masonry blocks",
        "Portland slag cement chemical requirements",
        "White Portland cement for architectural decoration",
    ]

    print("\n[1] RETRIEVAL-ONLY MODE (no LLM call)\n")
    total_latency = 0
    for q in test_queries:
        result = run_pipeline(q, include_rationale=False)
        total_latency += result["latency_seconds"]
        print(f"Query   : {q[:55]}")
        print(f"Top-3   : {result['retrieved_standards'][:3]}")
        print(f"Latency : {result['latency_seconds']*1000:.1f}ms\n")

    print(f"Avg retrieval latency: {total_latency/len(test_queries)*1000:.1f}ms")

    # Only run LLM test if GROQ_API_KEY is set
    if os.environ.get("GROQ_API_KEY"):
        print("\n[2] FULL PIPELINE (with LLM rationale)\n")
        result = run_pipeline(
            "We are a small enterprise manufacturing 33 Grade Ordinary Portland Cement",
            include_rationale=True
        )
        print(f"Query   : {result['query']}")
        print(f"Standards retrieved: {result['retrieved_standards']}")
        print(f"Latency : {result['latency_seconds']:.2f}s")
        print(f"\nRATIONALE:\n{result['rationale']}")
    else:
        print("\n[2] LLM TEST SKIPPED — set GROQ_API_KEY to enable")
        print("    export GROQ_API_KEY='your_key_here'")

    print("\n" + "═"*65)
    print("  Pipeline test complete.")
    print("═"*65)
