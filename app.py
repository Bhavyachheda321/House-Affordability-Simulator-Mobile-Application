"""
FinPlan India v4
Welcome screen → three entry modes → guided form → plan
"""
import sys
import os
import streamlit as st

# Ensure the app directory is on sys.path so pages_content imports work
# on both Streamlit Cloud and local dev regardless of working directory.
_app_dir = os.path.dirname(os.path.abspath(__file__))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

st.set_page_config(
    page_title="FinPlan India",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CSS
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp { background: #F7F9FC !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 1rem 3rem; max-width: 700px; }

/* ── Welcome card ── */
.welcome-card {
    background: linear-gradient(135deg, #1a56db 0%, #1e3a8a 100%);
    border-radius: 16px;
    padding: 2rem 2rem 1.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.welcome-card::after {
    content: '₹';
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 8rem;
    font-weight: 800;
    color: rgba(255,255,255,.06);
    line-height: 1;
}
.welcome-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.02em;
    margin: 0 0 .4rem;
}
.welcome-sub {
    font-size: .92rem;
    color: rgba(255,255,255,.82);
    font-weight: 500;
    line-height: 1.6;
    max-width: 480px;
    margin: 0;
}
.welcome-badges {
    display: flex;
    gap: .5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,.14);
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 20px;
    padding: .25rem .75rem;
    font-size: .75rem;
    font-weight: 600;
    color: #fff;
}

/* ── Mode cards ── */
.mode-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: .85rem;
    margin-bottom: 1.2rem;
}
.mode-card {
    background: #fff;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    cursor: pointer;
    transition: border-color .15s, box-shadow .15s;
    text-align: center;
}
.mode-card:hover {
    border-color: #1a56db;
    box-shadow: 0 4px 14px rgba(26,86,219,.12);
}
.mode-card.active {
    border-color: #1a56db;
    background: #EFF6FF;
}
.mode-icon { font-size: 1.8rem; margin-bottom: .5rem; }
.mode-title {
    font-size: .88rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: .3rem;
}
.mode-desc {
    font-size: .76rem;
    color: #64748b;
    line-height: 1.5;
    font-weight: 500;
}
.mode-default-tag {
    display: inline-block;
    background: #1a56db;
    color: #fff;
    font-size: .67rem;
    font-weight: 700;
    padding: .15rem .5rem;
    border-radius: 10px;
    margin-bottom: .4rem;
    letter-spacing: .04em;
    text-transform: uppercase;
}

/* ── Progress bar ── */
.prog-bar {
    display: flex;
    gap: .35rem;
    align-items: flex-end;
    margin-bottom: 1rem;
}
.prog-seg {
    flex: 1;
    height: 5px;
    border-radius: 3px;
    transition: background .2s;
}
.prog-label {
    display: flex;
    gap: .35rem;
    margin-bottom: .55rem;
}
.prog-label-item {
    flex: 1;
    font-size: .68rem;
    font-weight: 600;
    text-align: center;
    letter-spacing: .04em;
    text-transform: uppercase;
}

/* ── Tip / warn / ok boxes ── */
.tip-box {
    background: #EFF6FF;
    border: 1.5px solid #93c5fd;
    border-radius: 8px;
    padding: .7rem 1rem;
    font-size: .83rem;
    color: #334155;
    margin-bottom: .8rem;
    line-height: 1.65;
    font-weight: 500;
}
.warn-box {
    background: #FAEEDA;
    border-left: 3px solid #EF9F27;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: .85rem;
    color: #633806;
    margin: 8px 0 16px;
    line-height: 1.5;
}
.ok-box {
    background: #EAF3DE;
    border-left: 3px solid #3B6D11;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: .85rem;
    color: #27500A;
    margin: 8px 0 16px;
    line-height: 1.5;
}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1a56db, #1e3a8a) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: .92rem !important;
    padding: .6rem 1.6rem !important;
    box-shadow: 0 3px 10px rgba(26,86,219,.25) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px rgba(26,86,219,.4) !important;
}
.stButton > button:not([kind="primary"]) {
    background: #fff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #334155 !important;
    font-weight: 600 !important;
}

/* ── Inputs ── */
label[data-testid="stWidgetLabel"] > div,
label[data-testid="stWidgetLabel"] p {
    font-size: .78rem !important;
    font-weight: 700 !important;
    color: #475569 !important;
    letter-spacing: .04em !important;
    text-transform: uppercase !important;
}
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .9rem !important;
}
.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus {
    border-color: #1a56db !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,.12) !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    margin-bottom: .5rem !important;
}

/* ── Misc ── */
hr { border-color: #e2e8f0 !important; margin: 1.2rem 0 !important; }
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #94a3b8 !important;
    font-size: .8rem !important;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE DEFAULTS
# =============================================================================
DEFAULTS = {
    # Navigation
    "step": 0,
    "mode": "welcome",   # "welcome" | "chat" | "form" | "expert"

    # Profile
    "age": 28, "city": "Mumbai", "married": False,
    "living_with_parents": True, "living_situation": "With parents (no rent)",
    "metro_city": True,

    # Spouse
    "has_spouse_income": False, "spouse_monthly_salary": 0,
    "spouse_salary_growth": 8.0, "spouse_sip_monthly": 0,

    # Tax
    "old_regime": False, "bracket_label": "₹20L–₹50L",
    "effective_slab_rate": 0.2288,
    "basic_monthly": 0, "hra_monthly": 0, "other_80c": 0,
    "employer_nps_annual": 0,

    # Income
    "monthly_salary": 0, "income_gross_monthly": 0,
    "annual_bonus": 0, "salary_growth": 8, "bonus_growth": 5,

    # Spending
    "monthly_expenses": 0, "expense_inflation": 6.0,
    "rent_monthly": 0, "rent_inflation": 8.0,
    "family_support_annual": 0,

    # Assets
    "mf_value": 0, "stocks_value": 0,
    "ppf_value": 0, "ppf_contributing": True,
    "epf_value": 0, "epf_monthly": 0,
    "nps_value": 0,
    "gold_value": 0, "fd_value": 0,
    "has_emergency_fund": False, "emergency_fund_value": 0,
    "sip_total_monthly": 0, "sip_stepup_pct": 10.0,

    # Loans
    "has_loans_flag": False, "loans_outstanding": 0,
    "loan_emi_monthly": 0, "loan_interest_rate": 0.0,

    # Goals
    "retirement_age": 55, "retirement_monthly_spend": 100000,
    "want_house": True, "house_budget": 0,
    "parents_house_contribution": 0, "home_loan_rate": 8.5,
    "home_loan_tenure": 20,
    "want_marriage_savings": False, "marriage_cost": 0, "marriage_years": 3,
    "want_child_education": False, "child_education_cost": 2500000,
    "child_education_years": 18,

    # City-derived (overwritten on city select)
    "property_appr_rate": 7.0, "lifestyle_inflation": 7,

    # Gemini state
    "gemini_q_text": "",
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =============================================================================
# STEP LABELS FOR PROGRESS BAR
# =============================================================================
STEPS = ["About", "Income", "Spending", "Assets", "Goals", "Plan"]


def progress_bar(current_step: int):
    """Render coloured progress bar + labels."""
    segs, labels = "", ""
    for i, label in enumerate(STEPS):
        if i < current_step:
            col, txt = "#1a56db", "#1a56db"
        elif i == current_step:
            col, txt = "#1a56db", "#1a56db"
        else:
            col, txt = "#e2e8f0", "#94a3b8"
        segs  += f'<div class="prog-seg" style="background:{col}"></div>'
        weight = "700" if i == current_step else "500"
        labels += f'<div class="prog-label-item" style="color:{txt};font-weight:{weight}">{label}</div>'

    st.markdown(
        f'<div class="prog-bar">{segs}</div>'
        f'<div class="prog-label">{labels}</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# ROUTING
# =============================================================================
mode = st.session_state.get("mode", "welcome")
step = st.session_state.get("step", 0)

# ── Welcome screen ────────────────────────────────────────────────────────────
if mode == "welcome":
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-title">FinPlan India</div>
        <div class="welcome-sub">
            A personalised, year-by-year financial plan that accounts for
            Indian tax laws, inflation, SIP step-ups, and your real life goals.
            Free. No sign-up. Nothing stored.
        </div>
        <div class="welcome-badges">
            <span class="badge">🇮🇳 India-specific tax engine</span>
            <span class="badge">📅 FY-aligned simulation</span>
            <span class="badge">🔒 No data stored</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### How would you like to get started?")

    st.markdown("""
    <div class="mode-grid">
        <div class="mode-card">
            <div class="mode-icon">📋</div>
            <div class="mode-default-tag">Recommended</div>
            <div class="mode-title">Guided Form</div>
            <div class="mode-desc">Step-by-step questions with helpful hints. Best for most people.</div>
        </div>
        <div class="mode-card">
            <div class="mode-icon">🤖</div>
            <div class="mode-title">Chat with AI</div>
            <div class="mode-desc">Answer questions conversationally. Gemini fills in gaps you don't know.</div>
        </div>
        <div class="mode-card">
            <div class="mode-icon">⚙️</div>
            <div class="mode-title">Expert Mode</div>
            <div class="mode-desc">All fields visible at once. For users who know their exact numbers.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Guided Form", type="primary", use_container_width=True):
            st.session_state["mode"] = "form"
            st.session_state["step"] = 1
            st.rerun()
    with col2:
        if st.button("🤖 Chat with AI", use_container_width=True):
            st.session_state["mode"] = "chat"
            st.rerun()
    with col3:
        if st.button("⚙️ Expert Mode", use_container_width=True):
            st.session_state["mode"] = "expert"
            st.session_state["step"] = 1
            st.rerun()

# ── Chat / Gemini onboarding ──────────────────────────────────────────────────
elif mode == "chat":
    st.markdown("#### 🤖 Chat with FinPlan AI")
    st.caption("Answer in your own words — the AI fills in the form for you.")
    if st.button("← Choose a different mode"):
        st.session_state["mode"] = "welcome"
        st.rerun()
    try:
        from pages_content import gemini_onboarding
        gemini_onboarding.render()
    except Exception as _e:
        import traceback
        st.error(f"Chat error: {_e}")
        st.code(traceback.format_exc())

# ── Form / Expert mode ────────────────────────────────────────────────────────
elif mode in ("form", "expert"):
    from pages_content import pg_about, pg_income, pg_spending, pg_assets, pg_goals, pg_plan

    # Show expert-mode note
    if mode == "expert" and step < 6:
        st.markdown(
            '<div class="tip-box">⚙️ <strong>Expert Mode</strong> — all fields are visible. '
            "Navigate freely between steps using the Back / Next buttons.</div>",
            unsafe_allow_html=True,
        )

    # Progress bar (shown for steps 1–5)
    if 1 <= step <= 5:
        progress_bar(step - 1)
    elif step == 6:
        progress_bar(5)

    # Mode switch link (only before entering data)
    if step <= 1:
        if st.button("← Back to mode selection"):
            st.session_state["mode"] = "welcome"
            st.session_state["step"] = 0
            st.rerun()

    # Route to the right page — wrapped so errors show instead of blank screen
    page_map = {1: pg_about, 2: pg_income, 3: pg_spending,
                4: pg_assets, 5: pg_goals, 6: pg_plan}
    if step in page_map:
        try:
            page_map[step].render()
        except Exception as _e:
            import traceback
            st.error(f"Page error on step {step}: {_e}")
            st.code(traceback.format_exc())
    else:
        st.session_state["step"] = 1
        st.rerun()
