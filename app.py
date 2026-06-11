"""
FinPlan India v4
Welcome screen → three entry modes → guided form → plan
"""
import sys
import os
import streamlit as st

# Ensure pages_content is importable regardless of working directory
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
# MINIMAL CSS — no external font imports, no complex selectors
# =============================================================================
st.markdown("""
<style>
.stApp { background: #F7F9FC !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 1rem 3rem; max-width: 700px; }

.tip-box {
    background: #EFF6FF; border: 1.5px solid #93c5fd;
    border-radius: 8px; padding: .7rem 1rem;
    font-size: .85rem; color: #334155;
    margin-bottom: .8rem; line-height: 1.65;
}
.warn-box {
    background: #FAEEDA; border-left: 3px solid #EF9F27;
    border-radius: 0 8px 8px 0; padding: 10px 14px;
    font-size: .85rem; color: #633806;
    margin: 8px 0 16px; line-height: 1.5;
}
.ok-box {
    background: #EAF3DE; border-left: 3px solid #3B6D11;
    border-radius: 0 8px 8px 0; padding: 10px 14px;
    font-size: .85rem; color: #27500A;
    margin: 8px 0 16px; line-height: 1.5;
}
hr { border-color: #e2e8f0 !important; margin: 1.2rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE DEFAULTS
# =============================================================================
DEFAULTS = {
    "step": 0,
    "mode": "welcome",
    "age": 28, "city": "Mumbai", "married": False,
    "living_with_parents": True, "living_situation": "With parents (no rent)",
    "metro_city": True,
    "has_spouse_income": False, "spouse_monthly_salary": 0,
    "spouse_salary_growth": 8.0, "spouse_sip_monthly": 0,
    "old_regime": False, "bracket_label": "₹20L–₹50L",
    "effective_slab_rate": 0.2288,
    "basic_monthly": 0, "hra_monthly": 0, "other_80c": 0,
    "employer_nps_annual": 0,
    "monthly_salary": 0, "income_gross_monthly": 0,
    "annual_bonus": 0, "salary_growth": 8, "bonus_growth": 5,
    "monthly_expenses": 0, "expense_inflation": 6.0,
    "rent_monthly": 0, "rent_inflation": 8.0,
    "family_support_annual": 0,
    "mf_value": 0, "stocks_value": 0,
    "ppf_value": 0, "ppf_contributing": True,
    "epf_value": 0, "epf_monthly": 0,
    "nps_value": 0, "gold_value": 0, "fd_value": 0,
    "has_emergency_fund": False, "emergency_fund_value": 0,
    "sip_total_monthly": 0, "sip_stepup_pct": 10.0,
    "has_loans_flag": False, "loans_outstanding": 0,
    "loan_emi_monthly": 0, "loan_interest_rate": 0.0,
    "retirement_age": 55, "retirement_monthly_spend": 100000,
    "want_house": True, "house_budget": 0,
    "parents_house_contribution": 0, "home_loan_rate": 8.5,
    "home_loan_tenure": 20,
    "want_marriage_savings": False, "marriage_cost": 0, "marriage_years": 3,
    "want_child_education": False, "child_education_cost": 2500000,
    "child_education_years": 18,
    "property_appr_rate": 7.0, "lifestyle_inflation": 7,
    "gemini_q_text": "",
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =============================================================================
# PROGRESS BAR (native Streamlit columns)
# =============================================================================
STEPS = ["About", "Income", "Spending", "Assets", "Goals", "Plan"]

def progress_bar(current_step: int):
    cols = st.columns(len(STEPS))
    for i, (col, label) in enumerate(zip(cols, STEPS)):
        with col:
            if i < current_step:
                color = "#1a56db"
                st.markdown(
                    f'<div style="height:4px;background:{color};border-radius:2px;margin-bottom:3px"></div>'
                    f'<div style="font-size:10px;text-align:center;color:#555">{label}</div>',
                    unsafe_allow_html=True,
                )
            elif i == current_step:
                st.markdown(
                    '<div style="height:4px;background:#1a56db;border-radius:2px;margin-bottom:3px"></div>'
                    f'<div style="font-size:10px;text-align:center;color:#1a56db;font-weight:700">{label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="height:4px;background:#e2e8f0;border-radius:2px;margin-bottom:3px"></div>'
                    f'<div style="font-size:10px;text-align:center;color:#aaa">{label}</div>',
                    unsafe_allow_html=True,
                )
    st.write("")


# =============================================================================
# ROUTING
# =============================================================================
mode = st.session_state.get("mode", "welcome")
step = st.session_state.get("step", 0)

# ── Welcome screen ────────────────────────────────────────────────────────────
if mode == "welcome":
    st.title("📊 FinPlan India")
    st.markdown(
        "A personalised, year-by-year financial plan built around Indian tax laws, "
        "inflation, SIP step-ups, and your real life goals. **Free. No sign-up. Nothing stored.**"
    )
    st.markdown("---")
    st.markdown("#### How would you like to get started?")

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("##### 📋 Guided Form")
        st.caption("Step-by-step questions with helpful hints. Recommended for most people.")
        if st.button("Start Guided Form", type="primary", use_container_width=True, key="btn_form"):
            st.session_state["mode"] = "form"
            st.session_state["step"] = 1
            st.rerun()

    with col2:
        st.markdown("##### 🤖 Chat with AI")
        st.caption("Answer conversationally. Gemini fills in gaps you don't know.")
        if st.button("Start AI Chat", use_container_width=True, key="btn_chat"):
            st.session_state["mode"] = "chat"
            st.rerun()

    with col3:
        st.markdown("##### ⚙️ Expert Mode")
        st.caption("All fields visible at once. For users who know their exact numbers.")
        if st.button("Start Expert Mode", use_container_width=True, key="btn_expert"):
            st.session_state["mode"] = "expert"
            st.session_state["step"] = 1
            st.rerun()

    st.markdown("---")
    st.caption("🇮🇳 India-specific tax engine · 📅 FY-aligned simulation · 🔒 No data stored")


# ── Chat / Gemini onboarding ──────────────────────────────────────────────────
elif mode == "chat":
    st.markdown("#### 🤖 Chat with FinPlan AI")
    st.caption("Answer in your own words — the AI fills in the form for you.")
    if st.button("← Choose a different mode", key="chat_back"):
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

    if mode == "expert" and step < 6:
        st.info("⚙️ Expert Mode — all fields are visible. Navigate freely between steps.")

    if 1 <= step <= 5:
        progress_bar(step - 1)
    elif step == 6:
        progress_bar(5)

    if step <= 1:
        if st.button("← Back to mode selection", key="back_to_welcome"):
            st.session_state["mode"] = "welcome"
            st.session_state["step"] = 0
            st.rerun()

    try:
        if step == 1:
            from pages_content import pg_about
            pg_about.render()
        elif step == 2:
            from pages_content import pg_income
            pg_income.render()
        elif step == 3:
            from pages_content import pg_spending
            pg_spending.render()
        elif step == 4:
            from pages_content import pg_assets
            pg_assets.render()
        elif step == 5:
            from pages_content import pg_goals
            pg_goals.render()
        elif step == 6:
            from pages_content import pg_plan
            pg_plan.render()
        else:
            st.session_state["step"] = 1
            st.rerun()
    except Exception as _e:
        import traceback
        st.error(f"Error on step {step}: {_e}")
        st.code(traceback.format_exc())
        st.button("← Start over", on_click=lambda: st.session_state.update({"step": 1}))

else:
    # Unknown mode — reset to welcome
    st.session_state["mode"] = "welcome"
    st.rerun()
