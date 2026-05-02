"""
parse_pdf.py
============
Parses the BIS SP 21 PDF and extracts each standard summary
as a separate structured record saved to data/bis_standards.json.

Uses pdfplumber — works on Windows, Mac, and Linux.
No external tools needed.
"""

import re
import json
import os
import pdfplumber

# ── Config ───────────────────────────────────────────────────────────────────
PDF_PATH = "dataset.pdf"
OUT_PATH = "data/bis_standards.json"


def extract_text_from_pdf(pdf_path: str) -> str:
    print(f"Opening PDF: {pdf_path}")
    print("Extracting text page by page (this takes ~30 seconds)...")
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            if i % 50 == 0:
                print(f"  Processing page {i+1}/{total}...")
            text = page.extract_text()
            if text:
                all_text.append(text)
    full_text = "\n".join(all_text)
    print(f"Extraction complete. Total characters: {len(full_text):,}")
    return full_text


def clean_text(text: str) -> str:
    text = re.sub(r'SP\s*21\s*:\s*2005', '', text)
    text = text.replace('\f', ' ')
    text = re.sub(r'\n\s*\d{1,2}\.\d{1,3}\s*\n', '\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def infer_section(title: str, full_text: str) -> str:
    t = (title + " " + full_text[:200]).upper()
    if any(k in t for k in ["CEMENT", "CONCRETE", "AGGREGATE", "MORTAR", "POZZOLANA", "CLINKER", "SLAG CEMENT"]):
        return "CEMENT AND CONCRETE"
    if any(k in t for k in ["LIME ", "LIMES", "LIMEWASH", "HYDRATED LIME"]):
        return "BUILDING LIMES"
    if any(k in t for k in ["STONE", "MARBLE", "GRANITE", "SLATE"]):
        return "STONES"
    if any(k in t for k in ["PLYWOOD", "FIBREBOARD", "PARTICLE BOARD"]):
        return "WOOD PRODUCTS FOR BUILDING"
    if any(k in t for k in ["GYPSUM", "PLASTER OF PARIS"]):
        return "GYPSUM BUILDING MATERIALS"
    if any(k in t for k in ["TIMBER", "BAMBOO"]):
        return "TIMBER"
    if any(k in t for k in ["BITUMEN", "TAR ", "ASPHALT", "PITCH"]):
        return "BITUMEN AND TAR PRODUCTS"
    if any(k in t for k in ["TILE", "FLOORING", "ROOFING", "MOSAIC", "CERAMIC"]):
        return "FLOOR WALL ROOF COVERINGS AND FINISHES"
    if any(k in t for k in ["WATERPROOF", "DAMP PROOF", "SEALANT"]):
        return "WATER PROOFING AND DAMP PROOFING MATERIALS"
    if any(k in t for k in ["PIPE", "FITTING", "VALVE", "SANITARY", "TAP "]):
        return "SANITARY APPLIANCES AND WATER FITTINGS"
    if any(k in t for k in ["HINGE", "LOCK", "BOLT ", "HANDLE", "HARDWARE"]):
        return "BUILDERS HARDWARE"
    if any(k in t for k in ["DOOR", "WINDOW", "SHUTTER"]):
        return "DOORS WINDOWS AND SHUTTERS"
    if any(k in t for k in ["REINFORCEMENT", "REBAR", "PRESTRESS", "STRAND"]):
        return "CONCRETE REINFORCEMENT"
    if any(k in t for k in ["STRUCTURAL STEEL", "MILD STEEL", "ROLLED STEEL"]):
        return "STRUCTURAL STEELS"
    if any(k in t for k in ["ALUMINIUM", "ALUMINUM", "COPPER ", "BRASS "]):
        return "LIGHT METAL AND THEIR ALLOYS"
    if any(k in t for k in ["GLASS", "GLAZING"]):
        return "GLASS"
    if any(k in t for k in ["INSULATION", "INSULATING"]):
        return "THERMAL INSULATION MATERIALS"
    if any(k in t for k in ["PLASTIC", "PVC", "POLYETHYLENE"]):
        return "PLASTICS"
    if any(k in t for k in ["CABLE", "CONDUCTOR", "WIRING"]):
        return "CONDUCTORS AND CABLES"
    if any(k in t for k in ["WELDING", "ELECTRODE"]):
        return "WELDING ELECTRODES AND WIRES"
    if any(k in t for k in ["BOLT", "NUT ", "SCREW", "RIVET", "FASTENER"]):
        return "THREADED FASTENERS AND RIVETS"
    return "GENERAL"


def extract_standard_id_and_title(header_text: str):
    h = re.sub(r'[ \t]+', ' ', header_text).strip()
    h = re.sub(r'\((?:First|Second|Third|Fourth|Fifth)\s+Revision\)', '', h, flags=re.IGNORECASE).strip()
    pattern = re.compile(r'(IS\s+\d+(?:\s*\([^)]+\))?)\s*:?\s*(\d{4})\s*(.*)', re.IGNORECASE | re.DOTALL)
    m = pattern.match(h)
    if m:
        is_num = re.sub(r'\s+', ' ', m.group(1)).strip()
        year   = m.group(2).strip()
        title  = re.sub(r'\s+', ' ', m.group(3)).strip()
        return f"{is_num}: {year}", title.upper()
    return "UNKNOWN", h.upper()


def split_into_blocks(full_text: str) -> list:
    parts = re.split(r'\s*SUMMARY\s+OF\s*\n', full_text)
    return parts[1:]


def parse_block(block: str):
    lines = [l for l in block.split('\n') if l.strip()]
    if not lines:
        return None
    header_lines = []
    body_start   = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^\d+[\.\)]', stripped) or stripped.lower().startswith('scope'):
            body_start = i
            break
        header_lines.append(stripped)
    else:
        body_start = len(lines)
    header_text = ' '.join(header_lines)
    body_text   = ' '.join(lines[body_start:])
    if not re.match(r'IS\s+\d+', header_text, re.IGNORECASE):
        return None
    standard_id, title = extract_standard_id_and_title(header_text)
    if standard_id == "UNKNOWN" and not title:
        return None
    full_text = clean_text(header_text + "\n" + body_text)
    section   = infer_section(title, full_text)
    return {"standard_id": standard_id, "title": title, "section": section, "full_text": full_text}


def main():
    os.makedirs("data", exist_ok=True)
    raw_text  = extract_text_from_pdf(PDF_PATH)
    blocks    = split_into_blocks(raw_text)
    print(f"\nFound {len(blocks)} 'SUMMARY OF' blocks in the PDF.")
    standards = []
    skipped   = 0
    for block in blocks:
        record = parse_block(block)
        if record:
            standards.append(record)
        else:
            skipped += 1
    print(f"Successfully parsed : {len(standards)} standards")
    print(f"Skipped (malformed) : {skipped} blocks")
    from collections import Counter
    section_counts = Counter(r["section"] for r in standards)
    print("\nStandards per section:")
    for section, count in sorted(section_counts.items(), key=lambda x: -x[1]):
        print(f"  {count:3d}  {section}")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(standards, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(standards)} records to {OUT_PATH}")
    print("\n── VERIFICATION ─────────────────────────────────────────────")
    expected_ids = [
        "IS 269: 1989", "IS 383: 1970", "IS 458: 2003",
        "IS 2185 (Part 2): 1983", "IS 459: 1992", "IS 455: 1989",
        "IS 1489 (Part 2): 1991", "IS 3466: 1988", "IS 6909: 1990",
        "IS 8042: 1989"
    ]
    found_ids  = {r["standard_id"] for r in standards}
    def normalize(s): return s.replace(" ", "").lower()
    norm_found = {normalize(s): s for s in found_ids}
    all_found  = True
    for eid in expected_ids:
        if normalize(eid) in norm_found:
            print(f"  ✅  {eid}")
        else:
            print(f"  ❌  {eid}  <- NOT FOUND")
            all_found = False
    if all_found:
        print("\n✅ All 10 test standards found! Ready for next step.")
    else:
        print("\n⚠️  Some standards missing.")

if __name__ == "__main__":
    main()
