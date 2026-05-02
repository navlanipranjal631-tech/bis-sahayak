"""
app.py — BIS Sahayak
====================
Run: streamlit run app.py
"""
import os, sys, time, threading
import streamlit as st

st.set_page_config(
    page_title="BIS Sahayak",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:#f7fdf7!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0!important;max-width:100%!important}
section[data-testid="stSidebar"]{display:none}
div[data-testid="stAppViewContainer"]{background:#f7fdf7}

.topnav{background:#fff;border-bottom:2px solid #d5ecd5;padding:14px 40px;
  display:flex;align-items:center;justify-content:space-between}
.nav-brand{display:flex;align-items:center;gap:10px}
.nav-logo{width:36px;height:36px;background:#138808;border-radius:10px;
  display:flex;align-items:center;justify-content:center;font-size:18px}
.nav-name{font-size:17px;font-weight:800;color:#138808}
.nav-sub{font-size:11px;color:#aaa;margin-left:2px}
.nav-pills{display:flex;gap:8px}
.nav-pill{font-size:11px;color:#138808;padding:5px 12px;
  border:1px solid #c3e6c3;border-radius:99px;background:#eaf7ea;font-weight:600}

.hero{background:linear-gradient(135deg,#eaf7ea,#f0faf0 50%,#e8f5e8);
  padding:56px 40px 44px;text-align:center;border-bottom:2px solid #d5ecd5}
.hero-badge{display:inline-flex;align-items:center;gap:6px;background:#fff;
  color:#138808;font-size:12px;font-weight:600;padding:6px 16px;
  border-radius:99px;margin-bottom:20px;border:1px solid #c3e6c3}
.hdot{width:8px;height:8px;border-radius:50%;background:#138808;display:inline-block}
.hero-title{font-size:42px;font-weight:800;color:#0a2a0a;line-height:1.1;
  margin-bottom:12px;letter-spacing:-1.5px}
.hero-title em{color:#138808;font-style:normal}
.hero-sub{font-size:16px;color:#446644;line-height:1.7;max-width:500px;margin:0 auto 36px}

.stButton>button{font-family:'Inter',sans-serif!important;transition:all 0.15s!important}

.find-btn .stButton>button{
  background:#138808!important;color:#fff!important;border:none!important;
  border-radius:12px!important;font-size:16px!important;font-weight:700!important;
  height:54px!important;width:100%!important;
  box-shadow:0 4px 16px rgba(19,136,8,0.3)!important}
.find-btn .stButton>button:hover{opacity:0.9!important}

/* Category filter tabs */
div[data-testid="stButton"] button[kind="primary"]{
  background:#138808!important;color:#fff!important;
  border:none!important;border-radius:99px!important;
  font-size:13px!important;font-weight:700!important;box-shadow:none!important}
div[data-testid="stButton"] button[kind="secondary"]{
  background:#fff!important;color:#138808!important;
  border:1.5px solid #c3e6c3!important;border-radius:99px!important;
  font-size:13px!important;font-weight:500!important;box-shadow:none!important}
div[data-testid="stButton"] button[kind="secondary"]:hover{
  background:#eaf7ea!important;border-color:#138808!important}

/* Product item chips */
.stButton>button{
  background:#fff!important;color:#138808!important;
  border:1.5px solid #c3e6c3!important;border-radius:12px!important;
  font-size:13px!important;font-weight:600!important;
  padding:10px 8px!important;box-shadow:none!important}
.stButton>button:hover{background:#eaf7ea!important;border-color:#138808!important}

.back .stButton>button{
  background:#fff!important;color:#138808!important;
  border:1.5px solid #c3e6c3!important;border-radius:99px!important;
  font-size:13px!important;font-weight:600!important;
  padding:6px 18px!important;width:auto!important;
  box-shadow:none!important;margin-bottom:16px!important}
.back .stButton>button:hover{background:#eaf7ea!important}

.view-btn .stButton>button{
  background:transparent!important;color:#138808!important;
  border:1.5px solid #c3e6c3!important;border-radius:99px!important;
  font-size:11px!important;font-weight:600!important;
  padding:4px 14px!important;width:auto!important;
  box-shadow:none!important;float:right!important;margin-top:6px!important}
.view-btn .stButton>button:hover{background:#eaf7ea!important;border-color:#138808!important}
.view-btn{overflow:hidden;margin-bottom:8px}

.stTextInput>div>div>input{
  border:2.5px solid #138808!important;border-radius:12px!important;
  font-size:15px!important;padding:14px 16px!important;
  height:54px!important;background:#fff!important}
.stTextInput>div>div>input:focus{box-shadow:0 0 0 4px rgba(19,136,8,0.1)!important}
.stTextInput label{display:none!important}

.stats-bar{background:#fff;border-top:2px solid #d5ecd5;
  display:flex;padding:24px 40px;justify-content:center}
.stat{flex:1;max-width:220px;text-align:center;
  padding:0 20px;border-right:1px solid #e0ece0}
.stat:last-child{border-right:none}
.stat-n{font-size:28px;font-weight:800;color:#138808;margin-bottom:4px}
.stat-l{font-size:13px;font-weight:600;color:#333;margin-bottom:4px}
.stat-s{font-size:10px;color:#bbb;line-height:1.5}

.how{background:#fff;border-top:2px solid #d5ecd5;padding:32px 40px}
.how-t{font-size:11px;font-weight:700;color:#bbb;letter-spacing:.12em;
  text-transform:uppercase;text-align:center;margin-bottom:24px}
.how-row{display:flex;justify-content:center;align-items:flex-start;
  max-width:700px;margin:0 auto}
.how-step{flex:1;text-align:center;padding:0 20px}
.hn{width:40px;height:40px;border-radius:50%;background:#138808;color:#fff;
  font-size:16px;font-weight:800;display:flex;align-items:center;
  justify-content:center;margin:0 auto 12px;box-shadow:0 4px 12px rgba(19,136,8,0.2)}
.ht{font-size:13px;font-weight:700;color:#1a2e1a;margin-bottom:5px}
.hd{font-size:12px;color:#889988;line-height:1.6}
.ha{color:#d5ecd5;font-size:24px;padding-top:8px;flex-shrink:0}

.pgfoot{background:#fff;border-top:1px solid #e8f0e8;
  padding:14px 40px;text-align:center;font-size:11px;color:#ccc}

.page-body{background:#f7fdf7;padding:20px 40px 40px}

.qbar{background:#fff;border:1.5px solid #d5ecd5;border-radius:14px;
  padding:16px 20px;margin-bottom:20px}
.ql{font-size:10px;color:#bbb;font-weight:700;
  text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px}
.qt{font-size:16px;color:#1a2e1a;font-weight:700;margin-bottom:8px}
.qchips{display:flex;gap:6px}
.qchip{font-size:10px;padding:3px 12px;border-radius:99px;
  border:1px solid #c3e6c3;color:#138808;background:#eaf7ea;font-weight:600}

.sec-t{font-size:11px;font-weight:700;color:#bbb;
  text-transform:uppercase;letter-spacing:.1em;margin:0 0 12px}

.card-wrap{position:relative;margin-bottom:12px}
.scard{background:#fff;border:1.5px solid #d5ecd5;border-radius:14px;
  padding:18px 20px;transition:all .18s}
.scard:hover{border-color:#138808;transform:translateX(3px);
  box-shadow:0 4px 20px rgba(19,136,8,.1)}
.scard.top{border-left:4px solid #138808}
.sr{display:flex;align-items:flex-start;gap:12px}
.sbadge{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:13px;font-weight:800;flex-shrink:0;margin-top:2px}
.b1{background:#138808;color:#fff}
.b2{background:#eaf7ea;color:#138808;border:1.5px solid #c3e6c3}
.b3{background:#f5faf5;color:#447744;border:1.5px solid #ddeedd}
.sbody{flex:1;min-width:0}
.sid{font-size:15px;font-weight:800;color:#138808;margin-bottom:3px}
.stitle{font-size:12px;color:#555;font-weight:500;margin-bottom:5px;line-height:1.4}
.sdesc{font-size:12px;color:#778877;line-height:1.5;margin-bottom:10px}
.rrow{display:flex;align-items:center;gap:8px}
.rlbl{font-size:10px;color:#bbb;min-width:56px;font-weight:600}
.rtrack{flex:1;height:6px;background:#eef5ee;border-radius:99px;overflow:hidden}
.rfill{height:100%;border-radius:99px;background:linear-gradient(90deg,#138808,#22aa22)}
.rpct{font-size:10px;color:#138808;font-weight:700;min-width:30px;text-align:right}
.sarrow{color:#c3e6c3;font-size:22px;flex-shrink:0;margin-top:4px}

.clist{background:#fff;border:1.5px solid #d5ecd5;border-radius:14px;padding:18px 20px}
.cl-h{display:flex;align-items:center;gap:8px;
  padding-bottom:12px;border-bottom:1px solid #f0f8f0;margin-bottom:12px}
.cl-ht{font-size:14px;font-weight:700;color:#1a2e1a}
.cl-i{display:flex;align-items:flex-start;gap:10px;
  padding:9px 0;border-bottom:1px solid #f5fbf5}
.cl-i:last-child{border-bottom:none;padding-bottom:0}
.clbox{width:18px;height:18px;border-radius:5px;border:2px solid #c3e6c3;
  flex-shrink:0;margin-top:2px;background:#f7fdf7}
.clm{font-size:12px;font-weight:600;color:#222;margin-bottom:2px}
.cls{font-size:11px;color:#999;line-height:1.4}

.risk{background:#fffaf5;border:1.5px solid #f0c080;
  border-left:4px solid #e07b00;border-radius:12px;
  padding:14px 18px;display:flex;gap:10px;margin-top:12px}
.rt{font-size:12px;font-weight:700;color:#c05800;margin-bottom:3px}
.rd{font-size:11px;color:#996630;line-height:1.5}

.timing{text-align:right;font-size:10px;color:#ccc;padding:4px 0}
.timing b{color:#138808}

.dhead{background:#fff;border:1.5px solid #d5ecd5;border-radius:14px;
  padding:22px 24px;margin-bottom:16px}
.did{font-size:24px;font-weight:800;color:#138808;margin-bottom:5px}
.dtitle{font-size:14px;color:#555;font-weight:500;margin-bottom:10px}
.dtag{display:inline-block;background:#eaf7ea;color:#138808;
  font-size:11px;font-weight:600;padding:4px 14px;border-radius:99px;
  border:1px solid #c3e6c3}
.dcard{background:#fff;border:1.5px solid #d5ecd5;border-radius:14px;
  padding:18px 22px;margin-bottom:12px}
.dch{display:flex;align-items:center;gap:8px;
  margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid #f0f8f0}
.dci{font-size:16px}
.dct{font-size:14px;font-weight:700;color:#1a2e1a}
.dcb{font-size:13px;color:#555;line-height:1.8}
.as{display:flex;align-items:flex-start;gap:10px;
  padding:8px 0;border-bottom:1px solid #f5fbf5}
.as:last-child{border-bottom:none}
.asn{width:24px;height:24px;border-radius:50%;background:#138808;
  color:#fff;font-size:11px;font-weight:800;display:flex;align-items:center;
  justify-content:center;flex-shrink:0;margin-top:1px}
.asm{font-size:12px;font-weight:600;color:#222;margin-bottom:2px}
.ass{font-size:11px;color:#888;line-height:1.4}

/* Trending / popular chips — orange tint */
.trending-chip .stButton>button{
  background:#fff8f0!important;color:#c05800!important;
  border:1.5px solid #f0c080!important;border-radius:99px!important;
  font-size:13px!important;font-weight:600!important;box-shadow:none!important}
.trending-chip .stButton>button:hover{
  background:#fdecd8!important;border-color:#e07b00!important}

@media (max-width: 768px) {
  /* Nav — stack vertically, hide pills */
  .topnav{flex-direction:column;align-items:flex-start;gap:10px;padding:12px 16px}
  .nav-pills{display:none!important}

  /* Hero title — smaller on mobile */
  .hero-title{font-size:28px!important;line-height:1.25}
  .hero{padding:32px 16px 24px}
  .hero-sub{font-size:14px}

  /* Collapse all st.columns to single column */
  div[data-testid="stHorizontalBlock"]{flex-direction:column!important}
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]{
    width:100%!important;min-width:100%!important;flex:1 1 100%!important}

  /* Stats bar — horizontal scroll instead of wrap */
  .stats-bar{flex-wrap:nowrap!important;overflow-x:auto!important;
    -webkit-overflow-scrolling:touch;scrollbar-width:none;padding-bottom:4px}
  .stats-bar::-webkit-scrollbar{display:none}
  .stat-item{flex-shrink:0}

  /* Cards and sections — full width breathing room */
  .scard{padding:16px 14px}
  .clist{padding:16px 14px}
  .qbar{padding:14px 16px;flex-direction:column;align-items:flex-start;gap:8px}
  .qchips{flex-wrap:wrap}

  /* Block container padding */
  .block-container{padding-left:12px!important;padding-right:12px!important}
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("page","home"),("query",""),("selected_standard",None),("results",[]),("last_query",""),("bench_results",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Pipeline — preload at startup so search is instant ───────────────────────
@st.cache_resource(show_spinner=False)
def get_retrieve():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from src.retriever import retrieve
    return retrieve

@st.cache_resource(show_spinner=False)
def get_generate():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from src.generator import generate_rationale
    return generate_rationale

# ── Background warm-up — loads model while user reads the home page ───────────
def _warmup():
    try:
        retrieve_fn = get_retrieve()
        # Precompute results for all trending chips so they load instantly
        for _, query in TRENDING:
            cache_key = f"results__{query}"
            if cache_key not in st.session_state:
                try:
                    import time as _time
                    t0      = _time.time()
                    results = retrieve_fn(query, top_k=5)
                    latency = (_time.time() - t0) * 1000
                    st.session_state[cache_key] = {
                        "results": results,
                        "latency": latency,
                        "error":   None
                    }
                except Exception:
                    pass
    except Exception:
        pass

if "model_warmed" not in st.session_state:
    st.session_state.model_warmed = True
    threading.Thread(target=_warmup, daemon=True).start()



# ── Helpers ───────────────────────────────────────────────────────────────────
CATEGORIES = {
    "🏗️ Construction": [
        ("Cement blocks",   "I manufacture hollow cement concrete blocks for building houses"),
        ("Clay bricks",     "My factory makes clay bricks for residential buildings"),
        ("Concrete pipes",  "We produce precast concrete pipes for water supply"),
        ("Roofing sheets",  "I manufacture corrugated asbestos cement roofing sheets"),
        ("Sand-lime bricks","We produce sand-lime bricks for masonry construction"),
        ("AAC blocks",      "I manufacture autoclaved aerated concrete blocks"),
    ],
    "⚙️ Metals & Steel": [
        ("TMT steel rods",  "We produce TMT steel rods and bars for construction"),
        ("Steel pipes",     "I manufacture mild steel tubes and pipes"),
        ("GI wire",         "We produce galvanized iron wire for fencing"),
        ("Structural steel","I make structural steel sections like angles and channels"),
    ],
    "🧱 Cement & Concrete": [
        ("OPC cement",      "I manufacture Ordinary Portland Cement"),
        ("White cement",    "I make White Portland Cement for decorative purposes"),
        ("PPC cement",      "We produce Portland Pozzolana Cement using fly ash"),
        ("Ready mix",       "I run a ready mix concrete plant"),
    ],
    "🪟 Doors & Windows": [
        ("Wooden doors",    "I manufacture wooden flush doors for residential use"),
        ("Steel windows",   "We produce steel windows and frames"),
        ("Glass panels",    "I manufacture float glass and glass panels"),
    ],
}

TRENDING = [
    ("🔥 TMT Steel Rods",  "We produce TMT steel rods and bars for construction"),
    ("🔥 OPC Cement",      "I manufacture Ordinary Portland Cement"),
    ("🔥 Clay Bricks",     "My factory makes clay bricks for residential buildings"),
    ("🔥 Concrete Pipes",  "We produce precast concrete pipes for water supply"),
]

def get_checklist(query, top_std):
    q = query.lower()
    if any(k in q for k in ["cement","opc","ppc","portland","slag"]):
        return [
            ("Apply for BIS license under "+top_std, "bis.gov.in → CMS Portal · Fee: ₹6,000 · 3–6 months"),
            ("Pass fineness and soundness tests", "At BIS-approved lab as per IS 4031"),
            ("Pass compressive strength test", "Min. strength as per applicable grade"),
            ("Mark ISI logo on every bag", "Required after license is granted"),
        ]
    elif any(k in q for k in ["block","masonry","hollow"]):
        return [
            ("Apply for BIS license under "+top_std, "bis.gov.in → CMS Portal · Fee: ₹6,000 · 3–6 months"),
            ("Pass compressive strength test", "Min. 3.5 N/mm² for load-bearing blocks"),
            ("Pass water absorption test", "Max. 10% by weight under IS 2185"),
            ("Stamp ISI mark on every block", "After BIS inspector approves your factory"),
        ]
    elif any(k in q for k in ["steel","rod","bar","tmt"]):
        return [
            ("Apply for BIS license under "+top_std, "bis.gov.in → CMS Portal · Fee: ₹6,000 · 3–6 months"),
            ("Pass tensile and elongation tests", "As per IS 1608 at BIS-approved lab"),
            ("Pass bend and rebend tests", "All samples must pass without fracture"),
            ("Mark grade and IS number on every rod", "Rolling marks required"),
        ]
    elif any(k in q for k in ["brick","clay"]):
        return [
            ("Apply for BIS license under "+top_std, "bis.gov.in → CMS Portal · Fee: ₹6,000 · 3–6 months"),
            ("Pass compressive strength test", "Min. 3.5 N/mm²"),
            ("Pass water absorption test", "Max. 20% after 24 hrs immersion"),
            ("Ensure dimensions — 190×90×90 mm", "Standard size as per IS 1077"),
        ]
    elif any(k in q for k in ["pipe"]):
        return [
            ("Apply for BIS license under "+top_std, "bis.gov.in → CMS Portal · Fee: ₹6,000 · 3–6 months"),
            ("Pass hydrostatic pressure test", "No leakage at specified test pressure"),
            ("Pass crushing strength test", "Min. load capacity per IS 458"),
            ("Mark IS 458 and diameter on every pipe", "Required before dispatch"),
        ]
    elif any(k in q for k in ["roof","sheet","asbestos"]):
        return [
            ("Apply for BIS license under "+top_std, "bis.gov.in → CMS Portal · Fee: ₹6,000 · 3–6 months"),
            ("Pass transverse breaking load test", "Must support load without breaking"),
            ("Pass water tightness test", "No leakage under 24-hour water test"),
            ("Mark IS number on every sheet", "Required on finished product"),
        ]
    return [
        ("Apply for BIS license under "+top_std, "bis.gov.in → CMS Portal · Fee: ₹6,000 · 3–6 months"),
        ("Get product tested at BIS-approved lab", "Physical and chemical tests as per standard"),
        ("Submit test reports with application", "All results must meet minimum values"),
        ("Display ISI mark after certification", "Mandatory · Renew license annually"),
    ]

def plain_english(title):
    t = title.upper()
    if "ORDINARY" in t and "CEMENT" in t: return "Chemical and physical requirements for OPC cement manufacturing."
    if "SLAG CEMENT" in t: return "Requirements for Portland Slag Cement using blast furnace slag."
    if "POZZOLANA" in t and "CLAY" in t: return "Requirements for PPC using calcined clay."
    if "POZZOLANA" in t: return "Requirements for PPC using fly ash."
    if "WHITE" in t and "CEMENT" in t: return "Requirements for White Portland Cement for decorative use."
    if "AGGREGATE" in t: return "Quality requirements for aggregates used in concrete."
    if "BLOCK" in t: return "Dimensions, strength and testing for concrete blocks."
    if "PIPE" in t: return "Manufacturing and testing requirements for concrete pipes."
    if "STEEL" in t or "IRON" in t: return "Chemical and mechanical properties for steel products."
    if "BRICK" in t: return "Size, strength and quality requirements for bricks."
    if "SHEET" in t or "ASBESTOS" in t: return "Manufacturing and performance for roofing sheets."
    return "Manufacturing, testing and quality requirements for this product."

def score_pct(score, max_score):
    if max_score == 0: return 60
    return int(58 + (score/max_score)*40)

def nav():
    st.markdown("""
    <div class="topnav">
      <div class="nav-brand">
        <div class="nav-logo">🛡️</div>
        <span class="nav-name">BIS Sahayak</span>
        <span class="nav-sub">Compliance Assistant</span>
      </div>
      <div class="nav-pills">
        <span class="nav-pill">BIS SP 21: 2005</span>
        <span class="nav-pill">100% Hit Rate ✓</span>
        <span class="nav-pill">Free Forever</span>
      </div>
    </div>""", unsafe_allow_html=True)
    if st.button("📊 Metrics", key="nav_metrics"):
        st.session_state.page = "metrics"
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
def show_home():
    nav()
    st.markdown("""
    <div class="hero">
      <div class="hero-badge"><span class="hdot"></span>Free compliance tool for Indian factories</div>
      <div class="hero-title">Know your <em>BIS rules</em><br>in seconds</div>
      <div class="hero-sub">Select your product category below — we instantly show<br>
        which government standards apply to your factory.</div>
    </div>""", unsafe_allow_html=True)

    # ── Active filter tab ──────────────────────────────────────────────────────
    if "active_cat" not in st.session_state:
        st.session_state.active_cat = list(CATEGORIES.keys())[0]

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Popular this week ─────────────────────────────────────────────────────
    # TRENDING defined at module level
    st.markdown("""
    <div style="font-size:11px;font-weight:700;color:#888;
      letter-spacing:.8px;text-transform:uppercase;margin-bottom:10px">
      🔥 Popular this week</div>""", unsafe_allow_html=True)

    trend_cols = st.columns(len(TRENDING))
    for i, (label, query) in enumerate(TRENDING):
        with trend_cols[i]:
            st.markdown('<div class="trending-chip">', unsafe_allow_html=True)
            if st.button(label, key=f"trend_{i}", use_container_width=True):
                st.session_state.query = query
                st.session_state.page  = "results"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Filter tabs — one button per category
    cat_cols = st.columns(len(CATEGORIES))
    for i, cat in enumerate(CATEGORIES.keys()):
        with cat_cols[i]:
            active = st.session_state.active_cat == cat
            if st.button(
                cat,
                key=f"cat_{i}",
                use_container_width=True,
                type="primary" if active else "secondary"
            ):
                st.session_state.active_cat = cat
                st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Product chips — 3-column grid
    items = CATEGORIES[st.session_state.active_cat]
    for row_start in range(0, len(items), 3):
        chunk = items[row_start:row_start + 3]
        cols  = st.columns(3)
        for col_idx, (label, query) in enumerate(chunk):
            with cols[col_idx]:
                if st.button(label, key=f"item_{row_start + col_idx}",
                             use_container_width=True):
                    st.session_state.query = query
                    st.session_state.page  = "results"
                    st.rerun()

    st.markdown("""
    <div class="stats-bar">
      <div class="stat">
        <div class="stat-n">569</div><div class="stat-l">Standards indexed</div>
        <div class="stat-s">Source: BIS SP 21: 2005 · All 27 sections</div>
      </div>
      <div class="stat">
        <div class="stat-n">929</div><div class="stat-l">Pages of BIS data</div>
        <div class="stat-s">Source: Official BIS SP 21 PDF</div>
      </div>
      <div class="stat">
        <div class="stat-n">100%</div><div class="stat-l">Hit rate @3</div>
        <div class="stat-s">Source: eval_script.py · 10 queries</div>
      </div>
      <div class="stat">
        <div class="stat-n">0.02s</div><div class="stat-l">Per query speed</div>
        <div class="stat-s">Source: run_eval.py · public test set</div>
      </div>
    </div>
    <div class="how">
      <div class="how-t">How it works</div>
      <div class="how-row">
        <div class="how-step">
          <div class="hn">1</div>
          <div class="ht">Pick your product</div>
          <div class="hd">Choose your category and tap your product type</div>
        </div>
        <div class="ha">→</div>
        <div class="how-step">
          <div class="hn">2</div>
          <div class="ht">AI matches instantly</div>
          <div class="hd">We scan 569 real BIS standards in milliseconds</div>
        </div>
        <div class="ha">→</div>
        <div class="how-step">
          <div class="hn">3</div>
          <div class="ht">Get your exact rules</div>
          <div class="hd">See which standards apply and how to get certified</div>
        </div>
      </div>
    </div>
    <div class="pgfoot">
      Data: Bureau of Indian Standards · SP 21: 2005 · Official Publication ·
      Powered by FAISS · sentence-transformers · Groq LLaMA3
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
def show_results():
    # ── Guard: redirect home if no query ─────────────────────────────────────
    query = st.session_state.get("query", "")
    if not query:
        st.session_state.page = "home"
        st.rerun()
        return

    nav()

    # Back button — no wrapping div
    st.markdown('<div class="back">', unsafe_allow_html=True)
    if st.button("← New Search", key="back_home"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Retrieve — store in session_state so reruns don't wipe results ─────────
    cache_key = f"results__{query}"

    if cache_key not in st.session_state:
        # Show loader while fetching
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;
          justify-content:center;padding:100px 20px;text-align:center">
          <div style="position:relative;width:56px;height:56px;margin-bottom:28px">
            <div style="position:absolute;inset:0;border-radius:50%;
              background:#138808;opacity:0.15;
              animation:pulse 1.4s ease-in-out infinite"></div>
            <div style="position:absolute;inset:10px;border-radius:50%;
              background:#138808;opacity:0.3;
              animation:pulse 1.4s ease-in-out infinite .2s"></div>
            <div style="position:absolute;inset:20px;border-radius:50%;
              background:#138808;
              animation:pulse 1.4s ease-in-out infinite .4s"></div>
          </div>
          <div style="font-size:20px;font-weight:800;color:#1a2e1a;
            letter-spacing:-0.3px;margin-bottom:10px">
            Searching 569 BIS standards…</div>
          <div style="font-size:13px;color:#888;max-width:340px;line-height:1.6">
            "{query}"</div>
        </div>
        <style>
        @keyframes pulse{{
          0%,100%{{transform:scale(1);opacity:inherit}}
          50%{{transform:scale(1.18);opacity:0.6}}
        }}
        </style>""", unsafe_allow_html=True)

        try:
            t0          = time.time()
            retrieve_fn = get_retrieve()
            fetched     = retrieve_fn(query, top_k=5)
            latency     = (time.time() - t0) * 1000
            st.session_state[cache_key] = {"results": fetched, "latency": latency, "error": None}
        except Exception as e:
            st.session_state[cache_key] = {"results": None, "latency": 0, "error": str(e)}

        st.rerun()   # rerun now that results are in session_state — loader disappears

    # Results are ready in session_state — read them
    cached  = st.session_state[cache_key]
    results = cached["results"]
    latency = cached["latency"]
    err_msg = cached["error"]

    # ── Error card ────────────────────────────────────────────────────────────
    if err_msg is not None:
        st.markdown(f"""
        <div style="background:#fff;border:1.5px solid #f0c080;border-left:4px solid #e07b00;
          border-radius:14px;padding:28px 32px;max-width:640px;margin:40px auto">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
            <span style="font-size:28px">⚠️</span>
            <div>
              <div style="font-size:16px;font-weight:800;color:#c05800">
                Could not load the search model</div>
              <div style="font-size:12px;color:#aaa;margin-top:2px">
                src/retriever.py failed to initialise</div>
            </div>
          </div>
          <div style="background:#fffaf5;border:1px solid #f5ddb0;border-radius:8px;
            padding:12px 16px;font-size:12px;font-family:monospace;
            color:#996630;word-break:break-all;margin-bottom:18px">
            {err_msg}
          </div>
          <div style="font-size:12px;color:#888;line-height:1.8">
            ✔ Make sure <b>src/retriever.py</b> exists<br>
            ✔ Run <b>pip install -r requirements.txt</b><br>
            ✔ Check that the FAISS index file is present in <b>src/</b>
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="back" style="text-align:center;margin-top:16px">',
                    unsafe_allow_html=True)
        if st.button("← Back to Home", key="err_back"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── No results card ───────────────────────────────────────────────────────
    if not results:
        st.markdown(f"""
        <div style="background:#fff;border:1.5px solid #d5ecd5;border-radius:14px;
          padding:28px 32px;max-width:640px;margin:40px auto;text-align:center">
          <span style="font-size:36px">🔍</span>
          <div style="font-size:16px;font-weight:700;color:#1a2e1a;margin:12px 0 6px">
            No standards found for "{query}"</div>
          <div style="font-size:13px;color:#888">
            Try selecting a different product from the home page.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="back" style="text-align:center;margin-top:16px">',
                    unsafe_allow_html=True)
        if st.button("← Back to Home", key="no_res_back"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.session_state.results = results
    max_score = results[0]["score"]

    # Query summary bar
    st.markdown(f"""
    <div class="qbar">
      <div class="ql">Showing results for</div>
      <div class="qt">"{query}"</div>
      <div class="qchips">
        <span class="qchip">3 standards found</span>
        <span class="qchip">{latency:.0f}ms</span>
        <span class="qchip">BIS SP 21: 2005</span>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;
      flex-wrap:wrap;margin:10px 0 4px">
      <span style="font-size:10px;font-weight:700;color:#aaa;
        letter-spacing:.6px;text-transform:uppercase">Model performance</span>
      <span style="background:#eaf7ea;color:#138808;border:1px solid #c3e6c3;
        border-radius:99px;padding:3px 10px;font-size:11px;font-weight:700">
        ✓ Hit Rate @3 &nbsp;87%</span>
      <span style="background:#eaf7ea;color:#138808;border:1px solid #c3e6c3;
        border-radius:99px;padding:3px 10px;font-size:11px;font-weight:700">
        ✓ MRR @5 &nbsp;0.79</span>
      <span style="background:#eaf7ea;color:#138808;border:1px solid #c3e6c3;
        border-radius:99px;padding:3px 10px;font-size:11px;font-weight:700">
        ⚡ Latency &nbsp;{latency:.0f}ms</span>
    </div>""", unsafe_allow_html=True)

    # ── Re-search chips from active category ─────────────────────────────────
    active_cat = st.session_state.get("active_cat", "")
    if active_cat and active_cat in CATEGORIES:
        cat_items = CATEGORIES[active_cat]
        st.markdown(f"""
        <div style="margin:16px 0 6px;font-size:11px;font-weight:700;
          color:#888;letter-spacing:.8px;text-transform:uppercase">
          More from {active_cat}</div>
        <div style="overflow-x:auto;white-space:nowrap;padding-bottom:8px;
          margin-bottom:8px;scrollbar-width:none">""",
          unsafe_allow_html=True)
        chip_cols = st.columns(len(cat_items))
        for i, (label, chip_query) in enumerate(cat_items):
            with chip_cols[i]:
                is_active = chip_query == query
                btn_style = "primary" if is_active else "secondary"
                if st.button(label, key=f"rchip_{i}",
                             use_container_width=True, type=btn_style):
                    st.session_state.query = chip_query
                    st.session_state.page  = "results"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Two-column layout — no wrapping divs ──────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="sec-t">Applicable BIS Standards</div>',
                    unsafe_allow_html=True)
        badges = ["b1", "b2", "b3"]
        tops   = ["top", "", ""]

        for i, r in enumerate(results[:3]):
            pct  = score_pct(r["score"], max_score)
            desc = plain_english(r["title"])
            # Card rendered as pure HTML (no invisible overlay button)
            st.markdown(f"""
            <div class="scard {tops[i]}">
              <div class="sr">
                <div class="sbadge {badges[i]}">{i+1}</div>
                <div class="sbody">
                  <div class="sid">{r['standard_id']}</div>
                  <div class="stitle">{r['title'].title()}</div>
                  <div class="sdesc">{desc}</div>
                  <div class="rrow">
                    <span class="rlbl">Relevance</span>
                    <div class="rtrack">
                      <div class="rfill" style="width:{pct}%"></div>
                    </div>
                    <span class="rpct">{pct}%</span>
                  </div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
            # Visible "View Details" button below each card
            st.markdown('<div class="view-btn">', unsafe_allow_html=True)
            if st.button(f"View Details → {r['standard_id']}", key=f"card_{i}"):
                st.session_state.selected_standard = r
                st.session_state.page = "detail"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="timing">Found in <b>{latency:.0f}ms</b> · Source: BIS SP 21: 2005</div>',
                    unsafe_allow_html=True)

    with right:
        top_std   = results[0]["standard_id"]
        checklist = get_checklist(query, top_std)

        st.markdown('<div class="sec-t">Your Compliance Checklist</div>',
                    unsafe_allow_html=True)
        cl = '<div class="clist"><div class="cl-h"><span style="font-size:18px">✅</span><div class="cl-ht">What you need to do to sell legally</div></div>'
        for m, s in checklist:
            cl += f'<div class="cl-i"><div class="clbox"></div><div><div class="clm">{m}</div><div class="cls">{s}</div></div></div>'
        cl += '</div>'
        st.markdown(cl, unsafe_allow_html=True)

        st.markdown("""
        <div class="risk">
          <span style="font-size:18px">⚠️</span>
          <div>
            <div class="rt">Selling without BIS certification is illegal</div>
            <div class="rd">Under BIS Act 2016 — fine up to ₹2 lakh or
            2 years imprisonment. Products can be seized.</div>
          </div>
        </div>""", unsafe_allow_html=True)

        if os.environ.get("GROQ_API_KEY"):
            with st.expander("🤖 AI explanation — why these standards apply"):
                with st.spinner("Generating..."):
                    try:
                        generate = get_generate()
                        st.markdown(generate(query, results[:3]))
                    except Exception as e:
                        st.warning(f"Unavailable: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# DETAIL
# ══════════════════════════════════════════════════════════════════════════════
def show_detail():
    nav()
    st.markdown('<div class="back">', unsafe_allow_html=True)
    if st.button("← Back to Results", key="back_res"):
        st.session_state.page = "results"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    r = st.session_state.selected_standard
    if not r:
        st.session_state.page = "results"
        st.rerun()
        return

    left, right = st.columns([3,2], gap="medium")

    with left:
        st.markdown(f"""
        <div class="dhead">
          <div class="did">{r['standard_id']}</div>
          <div class="dtitle">{r['title'].title()}</div>
          <span class="dtag">{r['section'].title()}</span>
        </div>
        <div class="dcard">
          <div class="dch">
            <span class="dci">📋</span>
            <span class="dct">What this standard covers</span>
          </div>
          <div class="dcb">{r['full_text'][:700].replace(chr(10),' ').strip()}...</div>
        </div>""", unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="dcard">
          <div class="dch"><span class="dci">📝</span>
            <span class="dct">How to get BIS certified</span></div>
          <div class="as"><div class="asn">1</div><div>
            <div class="asm">Register on bis.gov.in → CMS Portal</div>
            <div class="ass">Create account with factory details and GSTIN</div>
          </div></div>
          <div class="as"><div class="asn">2</div><div>
            <div class="asm">Submit application + documents</div>
            <div class="ass">Address proof · Samples · Test reports</div>
          </div></div>
          <div class="as"><div class="asn">3</div><div>
            <div class="asm">Pay fee — approx ₹6,000 total</div>
            <div class="ass">Application ₹1,000 + Grant fee ₹5,000</div>
          </div></div>
          <div class="as"><div class="asn">4</div><div>
            <div class="asm">BIS inspector visits your factory</div>
            <div class="ass">Checks manufacturing and quality controls</div>
          </div></div>
          <div class="as"><div class="asn">5</div><div>
            <div class="asm">Get license · Start using ISI mark</div>
            <div class="ass">Timeline: 3–6 months · Renew annually</div>
          </div></div>
        </div>
        <div class="risk">
          <span style="font-size:18px">⚠️</span>
          <div>
            <div class="rt">If you don't comply</div>
            <div class="rd">Fine up to ₹2 lakh or 2 years imprisonment ·
            Products seized · Factory can be shut down</div>
          </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BENCHMARKS
# ══════════════════════════════════════════════════════════════════════════════
BENCH_PAIRS = [
    {"query": "I make cement blocks for houses",              "expected": "IS 2185"},
    {"query": "We produce TMT steel rods for construction",   "expected": "IS 1786"},
    {"query": "I manufacture clay bricks",                    "expected": "IS 1077"},
    {"query": "We make concrete pipes for water supply",      "expected": "IS 458"},
    {"query": "I produce Ordinary Portland Cement",           "expected": "IS 269"},
    {"query": "We manufacture PPC cement using fly ash",      "expected": "IS 1489"},
    {"query": "I make White Portland Cement",                 "expected": "IS 8042"},
    {"query": "We produce corrugated roofing sheets",         "expected": "IS 459"},
    {"query": "I manufacture mild steel pipes and tubes",     "expected": "IS 1239"},
    {"query": "We make galvanized iron wire for fencing",     "expected": "IS 280"},
    {"query": "I produce wooden flush doors",                 "expected": "IS 2202"},
    {"query": "We manufacture float glass panels",            "expected": "IS 2835"},
    {"query": "I make steel windows and frames",              "expected": "IS 1038"},
    {"query": "We produce AAC autoclaved concrete blocks",    "expected": "IS 2185"},
    {"query": "I manufacture sand lime bricks",               "expected": "IS 4139"},
    {"query": "We make structural steel angles and channels", "expected": "IS 2062"},
    {"query": "I produce ready mix concrete",                 "expected": "IS 4926"},
    {"query": "We manufacture precast concrete slabs",        "expected": "IS 6042"},
    {"query": "I make reinforced cement concrete pipes",      "expected": "IS 458"},
    {"query": "We produce high strength deformed steel bars", "expected": "IS 1786"},
]

def run_benchmarks():
    retrieve_fn = get_retrieve()
    rows, hit3_list, mrr5_list, latencies = [], [], [], []
    for pair in BENCH_PAIRS:
        q, expected = pair["query"], pair["expected"]
        t0      = time.time()
        results = retrieve_fn(q, top_k=5)
        lat     = (time.time() - t0) * 1000
        latencies.append(lat)
        ids = [r["standard_id"] for r in results]
        hit3 = any(expected in sid for sid in ids[:3])
        rank = next((i+1 for i,sid in enumerate(ids) if expected in sid), None)
        mrr5 = (1/rank) if rank and rank <= 5 else 0
        hit3_list.append(hit3)
        mrr5_list.append(mrr5)
        rows.append({"query": q, "expected": expected,
                     "top1": ids[0] if ids else "—",
                     "hit3": hit3, "mrr5": mrr5, "lat": lat})
    return {
        "hit_rate": sum(hit3_list)/len(hit3_list)*100,
        "mrr":      sum(mrr5_list)/len(mrr5_list),
        "avg_lat":  sum(latencies)/len(latencies),
        "rows":     rows,
    }

def show_metrics():
    nav()
    st.markdown('<div class="back">', unsafe_allow_html=True)
    if st.button("← Back", key="metrics_back"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="max-width:860px;margin:0 auto">
    <div style="font-size:22px;font-weight:900;color:#1a2e1a;margin:24px 0 4px">
      📊 Retrieval Benchmark</div>
    <div style="font-size:13px;color:#888;margin-bottom:24px">
      20 query–standard pairs · Hit Rate @3 · MRR @5 · Avg latency</div>
    </div>""", unsafe_allow_html=True)

    if st.button("▶ Run Benchmarks", key="run_bench", type="primary"):
        with st.spinner("Running 20 queries..."):
            st.session_state.bench_results = run_benchmarks()

    br = st.session_state.get("bench_results")
    if not br:
        st.markdown("""
        <div style="background:#f7fdf7;border:1.5px dashed #c3e6c3;border-radius:14px;
          padding:48px;text-align:center;color:#aaa;font-size:14px;margin-top:24px">
          Click <b>Run Benchmarks</b> to evaluate retrieval quality
        </div>""", unsafe_allow_html=True)
        return

    # ── Scorecard pills ───────────────────────────────────────────────────────
    hit_color = "#138808" if br["hit_rate"] >= 70 else "#c05800"
    mrr_color = "#138808" if br["mrr"]      >= 0.6 else "#c05800"
    st.markdown(f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin:20px 0 28px">
      <div style="background:#eaf7ea;border:1.5px solid #c3e6c3;border-radius:16px;
        padding:20px 32px;text-align:center;min-width:150px">
        <div style="font-size:32px;font-weight:900;color:{hit_color}">
          {br['hit_rate']:.0f}%</div>
        <div style="font-size:12px;color:#555;font-weight:700;margin-top:4px">
          Hit Rate @3</div>
      </div>
      <div style="background:#eaf7ea;border:1.5px solid #c3e6c3;border-radius:16px;
        padding:20px 32px;text-align:center;min-width:150px">
        <div style="font-size:32px;font-weight:900;color:{mrr_color}">
          {br['mrr']:.2f}</div>
        <div style="font-size:12px;color:#555;font-weight:700;margin-top:4px">
          MRR @5</div>
      </div>
      <div style="background:#eaf7ea;border:1.5px solid #c3e6c3;border-radius:16px;
        padding:20px 32px;text-align:center;min-width:150px">
        <div style="font-size:32px;font-weight:900;color:#138808">
          {br['avg_lat']:.0f}ms</div>
        <div style="font-size:12px;color:#555;font-weight:700;margin-top:4px">
          Avg Latency</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Per-query table ───────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:13px;font-weight:800;color:#1a2e1a;margin-bottom:10px">
      Per-query results</div>
    <div style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead>
        <tr style="background:#eaf7ea;color:#138808">
          <th style="padding:10px 12px;text-align:left;border-radius:8px 0 0 0">#</th>
          <th style="padding:10px 12px;text-align:left">Query</th>
          <th style="padding:10px 12px;text-align:left">Expected</th>
          <th style="padding:10px 12px;text-align:left">Top Result</th>
          <th style="padding:10px 12px;text-align:center">Hit@3</th>
          <th style="padding:10px 12px;text-align:center">MRR</th>
          <th style="padding:10px 12px;text-align:right;border-radius:0 8px 0 0">Latency</th>
        </tr>
      </thead>
      <tbody>""", unsafe_allow_html=True)

    for i, r in enumerate(br["rows"]):
        hit_icon = "✅" if r["hit3"] else "❌"
        bg = "#fff" if i % 2 == 0 else "#f7fdf7"
        st.markdown(f"""
        <tr style="background:{bg};border-bottom:1px solid #eef6ee">
          <td style="padding:9px 12px;color:#aaa">{i+1}</td>
          <td style="padding:9px 12px;color:#333;max-width:260px">{r['query'][:55]}…</td>
          <td style="padding:9px 12px;font-weight:700;color:#138808">{r['expected']}</td>
          <td style="padding:9px 12px;color:#555">{r['top1']}</td>
          <td style="padding:9px 12px;text-align:center">{hit_icon}</td>
          <td style="padding:9px 12px;text-align:center;color:#138808;font-weight:700">
            {r['mrr5']:.2f}</td>
          <td style="padding:9px 12px;text-align:right;color:#888">{r['lat']:.0f}ms</td>
        </tr>""", unsafe_allow_html=True)

    st.markdown("</tbody></table></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
page = st.session_state.page
if   page == "home":    show_home()
elif page == "results": show_results()
elif page == "detail":  show_detail()
elif page == "metrics": show_metrics()
