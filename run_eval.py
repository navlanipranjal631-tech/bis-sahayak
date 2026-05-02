"""
run_eval.py
===========
One-command local evaluation helper.

Runs inference.py → merges expected_standards → runs eval_script.py.
Use this to test your system against the public test set at any time.

Usage:
    python run_eval.py

What it does:
    1. Runs inference.py on public_test_set.json → data/my_results.json
    2. Merges expected_standards from test set into results (for local eval only)
    3. Runs eval_script.py and prints Hit Rate @3, MRR @5, Latency
    4. Shows a per-query breakdown so you can see exactly which queries failed

NOTE: The merge step (2) is only for LOCAL evaluation.
Your inference.py output (data/my_results.json) does NOT need expected_standards
for the judge submission — they have their own expected answers.
"""

import json
import os
import subprocess
import sys
import time

PUBLIC_TEST_SET  = "data/public_test_set.json"
INFERENCE_OUTPUT = "data/my_results.json"
EVAL_READY       = "data/eval_ready.json"


def run_inference():
    """Step 1: Run inference.py on public test set."""
    print("=" * 55)
    print("STEP 1 — Running inference.py on public test set")
    print("=" * 55)
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, "inference.py",
         "--input",  PUBLIC_TEST_SET,
         "--output", INFERENCE_OUTPUT],
        capture_output=False   # let output stream live to console
    )
    if result.returncode != 0:
        print("\n[ERROR] inference.py failed! Fix errors above before re-running.")
        sys.exit(1)
    print(f"\nInference completed in {time.time()-t0:.2f}s\n")


def merge_expected():
    """Step 2: Merge expected_standards into results for eval_script.py."""
    print("=" * 55)
    print("STEP 2 — Merging expected_standards for local evaluation")
    print("=" * 55)

    with open(INFERENCE_OUTPUT, encoding="utf-8") as f:
        results = json.load(f)

    with open(PUBLIC_TEST_SET, encoding="utf-8") as f:
        test_set = json.load(f)

    expected_map = {item["id"]: item.get("expected_standards", []) for item in test_set}

    for r in results:
        r["expected_standards"] = expected_map.get(r["id"], [])

    with open(EVAL_READY, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Merged {len(results)} results → {EVAL_READY}\n")
    return results


def run_eval():
    """Step 3: Run eval_script.py and capture scores."""
    print("=" * 55)
    print("STEP 3 — Running official eval_script.py")
    print("=" * 55)
    subprocess.run(
        [sys.executable, "eval_script.py", "--results", EVAL_READY]
    )


def per_query_breakdown(results: list[dict]):
    """Step 4: Print per-query pass/fail breakdown for debugging."""
    print("\n" + "=" * 55)
    print("STEP 4 — Per-query breakdown")
    print("=" * 55)

    def norm(s):
        return str(s).replace(" ", "").lower()

    hits_at_3 = 0
    for r in results:
        expected  = [norm(e) for e in r.get("expected_standards", [])]
        retrieved = [norm(x) for x in r.get("retrieved_standards", [])]

        top3  = retrieved[:3]
        top5  = retrieved[:5]
        hit3  = any(e in top3 for e in expected)
        rank  = next((i+1 for i, x in enumerate(top5) if x in expected), None)

        if hit3:
            hits_at_3 += 1
            status = "✅ HIT @3"
        else:
            status = "❌ MISS"

        expected_str   = r.get("expected_standards", ["?"])[0]
        retrieved_str  = r.get("retrieved_standards", [])

        print(f"\n{r['id']:<10} {status}  (rank={rank or '>5'})")
        print(f"  Expected : {expected_str}")
        print(f"  Top-5    : {retrieved_str}")

    print(f"\nSummary: {hits_at_3}/{len(results)} queries hit @3")

    # Show which query missed
    if hits_at_3 < len(results):
        print("\n⚠️  Missed queries — consider improving these:")
        for r in results:
            expected  = [norm(e) for e in r.get("expected_standards", [])]
            retrieved = [norm(x) for x in r.get("retrieved_standards", [])]
            if not any(e in retrieved[:3] for e in expected):
                print(f"  {r['id']}: expected {r['expected_standards']}")
                print(f"         got      {r['retrieved_standards'][:3]}")


if __name__ == "__main__":
    run_inference()
    results = merge_expected()
    run_eval()
    per_query_breakdown(results)
    print("\n✅ Evaluation complete.")
