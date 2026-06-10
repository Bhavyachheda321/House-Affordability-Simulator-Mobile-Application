import streamlit as st

st.set_page_config(
    page_title="FinPlan India",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS — clean, mobile-first ─────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding: 1.5rem 1rem 3rem; max-width: 640px; }
    .stProgress > div > div { border-radius: 10px; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.15s;
    }
    .stButton > button[kind="primary"] {
        background: #185FA5;
        border: none;
        color: white;
        padding: .6rem 1.5rem;
    }
    .tip-box {
        background: #E6F1FB;
        border-left: 3px solid #185FA5;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #0C447C;
        margin: 8px 0 16px;
        line-height: 1.5;
    }
    .warn-box {
        background: #FAEEDA;
        border-left: 3px solid #EF9F27;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #633806;
        margin: 8px 0 16px;
        line-height: 1.5;
    }
    .ok-box {
        background: #EAF3DE;
        border-left: 3px solid #3B6D11;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #27500A;
        margin: 8px 0 16px;
        line-height: 1.5;
    }
    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #888;
        margin: 1.5rem 0 0.5rem;
    }
    .skip-note {
        font-size: 0.78rem;
        color: #aaa;
        margin-top: -10px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
DEFAULTS = {
    "step": 0,
    "age": 28,
    "city": "Mumbai",
    "married": False,
    "has_kids": False,
    "living_with_parents": True,
    "monthly_salary": 0,
    "annual_bonus": 0,
    "monthly_expenses": 0,
    "family_support_annual": 0,
    "post_marriage_expenses": 0,
    "epf_monthly": 0,
    "employer_nps_monthly": 0,
    "salary_growth": 8,
    "mf_value": 0,
    "stocks_value": 0,
    "ppf_value": 0,
    "ppf_contributing": True,
    "epf_value": 0,
    "nps_value": 0,
    "gold_value": 0,
    "fd_value": 0,
    "rbi_bond_value": 0,
    "rbi_bond_months_left": 0,
    "has_emergency_fund": False,
    "emergency_fund_value": 0,
    "loans_outstanding": 0,
    "loan_emi_monthly": 0,
    "sip_total_monthly": 0,
    "want_house": True,
    "house_budget": 0,
    "parents_house_contribution": 0,
    "want_marriage_savings": False,
    "marriage_cost": 0,
    "marriage_years": 2,
    "want_child_education": False,
    "child_education_cost": 0,
    "child_education_years": 18,
    "retirement_age": 55,
    "retirement_monthly_spend": 100000,
    "lifestyle_inflation": 7,
    "tax_bracket": "30%",
    "effective_slab_rate": 0.3432,
    "property_appr_rate": 7.0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Step routing ──────────────────────────────────────────────────────────────
STEPS = ["about_you", "money_in", "money_out", "what_you_own", "your_goals", "your_plan"]
STEP_LABELS = ["About you", "Income", "Spending", "What you own", "Goals", "Your plan"]

step = st.session_state["step"]

# Top progress bar
if step > 0:
    pct = step / (len(STEPS) - 1)
    cols = st.columns(len(STEPS))
    for i, label in enumerate(STEP_LABELS):
        with cols[i]:
            color = "#185FA5" if i <= step else "#ddd"
            st.markdown(
                f'<div style="height:4px;background:{color};border-radius:2px;margin-bottom:3px"></div>'
                f'<div style="font-size:10px;text-align:center;color:{"#185FA5" if i==step else "#aaa" if i>step else "#555"}">'
                f'{label}</div>',
                unsafe_allow_html=True
            )
    st.write("")

# ── Page import and render ────────────────────────────────────────────────────
from pages_content import (
    pg_about, pg_income, pg_spending,
    pg_assets, pg_goals, pg_plan
)

pages = [pg_about, pg_income, pg_spending, pg_assets, pg_goals, pg_plan]
pages[step].render()
