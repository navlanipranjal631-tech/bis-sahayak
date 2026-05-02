"""
src/generator.py
================
Takes a user query + retrieved BIS standards and calls an LLM to produce
a clear, grounded rationale explaining why each standard applies.

Key design decisions
--------------------
1. GROUNDING: The system prompt explicitly tells the LLM to use ONLY the
   provided standards and never invent IS numbers. This prevents hallucination.

2. SYSTEM vs USER prompt:
   - System prompt = permanent instructions that shape the LLM's behaviour
     (role, rules, output format)
   - User prompt = the actual query + retrieved context for this request

3. Temperature = 0.1 (near-deterministic):
   Lower temperature → more focused, factual responses.
   We want the LLM to explain standards, not be creative.
   Higher temperature → more varied/creative but risks making things up.

4. Context truncation: full_text can be 500+ words per standard.
   We pass only the first 400 chars to stay within token limits while
   keeping the most important info (scope is always first).

What is "grounding" in RAG?
----------------------------
Without RAG, an LLM answering "what BIS standard covers OPC cement?" might:
  - Hallucinate: "IS 1234: 2022 covers this" (doesn't exist)
  - Be outdated: training data may have wrong year

With RAG, we first RETRIEVE real IS 269 text from our index, then tell the LLM:
  "Here is the actual standard text. Explain this to the user."
The LLM becomes an explainer, not a knowledge store. Much more reliable.
"""

import os
import json
import time
from groq import Groq

# ── Groq client — loaded once at import time ──────────────────────────────────
# Set your key:  export GROQ_API_KEY="your_key_here"
# Get free key:  https://console.groq.com
_groq_key = os.environ.get("GROQ_API_KEY", "")
_client   = Groq(api_key=_groq_key) if _groq_key else None

# Model: llama3-8b-8192
#   - 8B parameters: fast (< 1 second typically on Groq)
#   - 8192 token context window: enough for 5 standard summaries
#   - Free tier: 30 requests/minute, 14,400/day — more than enough
GROQ_MODEL   = "llama3-8b-8192"
TEMPERATURE  = 0.1          # near-zero = factual, consistent
MAX_TOKENS   = 900          # enough for a clear rationale for 3-5 standards
CONTEXT_TRIM = 400          # chars of full_text to include per standard


SYSTEM_PROMPT = """You are a BIS (Bureau of Indian Standards) compliance expert 
helping Indian Micro and Small Enterprises (MSEs) identify which standards 
apply to their products.

STRICT RULES — follow these exactly:
1. Only recommend standards from the CONTEXT provided below. 
2. Never invent, guess, or recall IS numbers from memory.
3. If a standard in the context is not relevant, do not mention it.
4. Be concise — one sentence of rationale per standard is enough.
5. Address the business owner directly in plain, simple English.
6. Format your response EXACTLY as shown in the example below.

OUTPUT FORMAT:
For each relevant standard, output:
**[IS Number: Year]** — [One sentence explaining why this applies to the product]

Example:
**IS 269: 1989** — This standard specifies the chemical and physical requirements for 33 Grade OPC, which is the exact grade your factory produces.
**IS 4031: 1988** — This covers the testing methods you must use to verify your cement meets IS 269 requirements."""


def build_user_prompt(query: str, retrieved: list[dict]) -> str:
    """
    Builds the user-turn prompt containing the query + retrieved context.

    Each standard gets a trimmed snippet so we stay within token limits.
    Including standard_id + title + snippet gives the LLM enough to work with.
    """
    context_parts = []
    for i, r in enumerate(retrieved, start=1):
        snippet = r["full_text"][:CONTEXT_TRIM].replace("\n", " ").strip()
        context_parts.append(
            f"[Standard {i}]\n"
            f"ID: {r['standard_id']}\n"
            f"Title: {r['title']}\n"
            f"Summary: {snippet}...\n"
        )
    context_block = "\n".join(context_parts)

    return (
        f"PRODUCT DESCRIPTION FROM BUSINESS OWNER:\n{query}\n\n"
        f"CONTEXT — RETRIEVED BIS STANDARDS (use ONLY these):\n"
        f"{'─'*50}\n"
        f"{context_block}"
        f"{'─'*50}\n\n"
        f"Which of the above standards apply to this product and why? "
        f"Be specific and practical. Only mention standards that are clearly relevant."
    )


def generate_rationale(query: str, retrieved: list[dict]) -> str:
    """
    Calls Groq LLM and returns a rationale string.

    Parameters
    ----------
    query     : the user's original product description
    retrieved : list of dicts from retriever.retrieve() — each has
                standard_id, title, full_text, score, rank

    Returns
    -------
    str : LLM-generated rationale (formatted as **IS XXX: YYYY** — reason)
    """
    if not retrieved:
        return "No relevant BIS standards found for this product description."

    user_prompt = build_user_prompt(query, retrieved)

    try:
        if not _client:
            raise RuntimeError("GROQ_API_KEY not set. Run: export GROQ_API_KEY=your_key")
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        # Never crash inference.py due to LLM errors — return a graceful fallback
        return (
            f"[LLM unavailable: {e}]\n\n"
            f"Retrieved standards: "
            + ", ".join(r["standard_id"] for r in retrieved)
        )


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Import retriever inline to test the full flow
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from src.retriever import retrieve

    test_queries = [
        "We manufacture 33 Grade OPC cement bags for the construction industry.",
        "Our plant produces Portland Pozzolana Cement using calcined clay as pozzolana.",
        "We make hollow lightweight concrete blocks for masonry walls.",
    ]

    for query in test_queries:
        print("\n" + "═"*65)
        print(f"QUERY: {query}")
        print("─"*65)

        # Retrieve top-5 standards
        retrieved = retrieve(query, top_k=5)
        print(f"Retrieved {len(retrieved)} standards:")
        for r in retrieved:
            print(f"  #{r['rank']} {r['standard_id']} (score={r['score']:.3f})")

        # Generate rationale
        print("\nGenerating rationale via Groq LLM...")
        t0 = time.time()
        rationale = generate_rationale(query, retrieved)
        latency = time.time() - t0

        print(f"\nRATIONALE (generated in {latency:.2f}s):\n")
        print(rationale)

    print("\n" + "═"*65)
