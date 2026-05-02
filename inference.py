"""
inference.py
============
THE MOST CRITICAL FILE IN THE PROJECT.

Judges will evaluate your submission by running EXACTLY this command:
    python inference.py --input hidden_private_dataset.json --output team_results.json

If this file crashes, or the output JSON has wrong key names,
you score 0 on the automated 40-point section. No exceptions.

Output schema (MUST match exactly — verified against sample_output.json):
[
  {
    "id": "PUB-01",
    "retrieved_standards": ["IS 269: 1989", "IS 455: 1989", ...],
    "latency_seconds": 1.24
  },
  ...
]

Key rules:
  - Key names are EXACT: "id", "retrieved_standards", "latency_seconds"
  - "retrieved_standards" is a list of strings (IS numbers with year)
  - "latency_seconds" is a float (per-query wall-clock time, retrieval only)
  - Always return exactly 5 standards per query (eval checks @3 and @5)
  - Load model/index ONCE before the loop — never inside the loop
  - If one query fails, log it and continue — never let one failure abort all
"""

import argparse
import json
import os
import sys
import time

# ── Make sure src/ is importable from project root ───────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Import pipeline components ────────────────────────────────────────────────
# IMPORTANT: retriever loads FAISS index + model at IMPORT TIME (not per query)
# This means the ~50ms startup cost happens once, not 10x or 100x.
from src.retriever import retrieve_standard_ids


def parse_args():
    """Parse --input and --output arguments exactly as judges expect."""
    parser = argparse.ArgumentParser(
        description="BIS Standards RAG Inference — BIS Hackathon 2026"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input JSON file with query items",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to write output JSON results",
    )
    return parser.parse_args()


def load_input(path: str) -> list[dict]:
    """
    Load the input JSON file.
    Input schema: [{"id": "...", "query": "..."}, ...]
    The 'expected_standards' field may or may not be present — we ignore it.
    """
    if not os.path.exists(path):
        print(f"[ERROR] Input file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("[ERROR] Input JSON must be a list of query objects", file=sys.stderr)
        sys.exit(1)

    print(f"[inference] Loaded {len(data)} queries from {path}")
    return data


def process_query(item: dict) -> dict:
    """
    Run one query through the RAG pipeline and return the result dict.

    Latency measured here covers:
      - Query embedding  (~2ms TF-IDF, ~50ms neural)
      - FAISS search     (~1ms)
    It does NOT include LLM time — eval only scores retrieval, not generation.

    Returns the EXACT output schema the judges expect.
    """
    query_id = item.get("id", "UNKNOWN")
    query    = item.get("query", "")

    if not query.strip():
        # Empty query — return empty results rather than crashing
        return {
            "id":                   query_id,
            "retrieved_standards":  [],
            "latency_seconds":      0.0,
        }

    t_start = time.time()

    # Retrieve top-5 standard IDs — this is what the eval script scores
    retrieved_standards = retrieve_standard_ids(query, top_k=5)

    latency = round(time.time() - t_start, 4)

    return {
        "id":                  query_id,          # exact key name
        "retrieved_standards": retrieved_standards, # exact key name — list of strings
        "latency_seconds":     latency,            # exact key name — float
    }


def save_output(results: list[dict], path: str):
    """Write results to the output path specified by the judge."""
    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[inference] Results saved to {path}")


def main():
    args   = parse_args()
    items  = load_input(args.input)
    results = []

    print(f"[inference] Processing {len(items)} queries...")
    print(f"[inference] Output will be written to: {args.output}")
    print()

    total_start = time.time()

    for i, item in enumerate(items, start=1):
        query_id = item.get("id", f"item-{i}")
        query    = item.get("query", "")[:80]   # truncate for display only

        try:
            result = process_query(item)
            results.append(result)

            # Progress log — visible to judges watching the run
            print(
                f"  [{i:>3}/{len(items)}] {query_id:<10} "
                f"latency={result['latency_seconds']*1000:.0f}ms  "
                f"top1={result['retrieved_standards'][0] if result['retrieved_standards'] else 'none'}"
            )

        except Exception as e:
            # One failed query must NOT abort the entire run
            # Log the error and add an empty result so the output stays complete
            print(f"  [{i:>3}/{len(items)}] {query_id:<10} ERROR: {e}", file=sys.stderr)
            results.append({
                "id":                  query_id,
                "retrieved_standards": [],
                "latency_seconds":     0.0,
            })

    total_time = time.time() - total_start
    avg_latency = sum(r["latency_seconds"] for r in results) / len(results) if results else 0

    print()
    print("─" * 55)
    print(f"  Total queries   : {len(results)}")
    print(f"  Total time      : {total_time:.2f}s")
    print(f"  Avg latency     : {avg_latency*1000:.1f}ms per query")
    print(f"  Latency target  : <5000ms  {'✅ PASS' if avg_latency < 5 else '❌ FAIL'}")
    print("─" * 55)

    # Save output
    save_output(results, args.output)

    print(f"\n[inference] Done. Run eval_script.py to score results:")
    print(f"  python eval_script.py --results {args.output}")


if __name__ == "__main__":
    main()
