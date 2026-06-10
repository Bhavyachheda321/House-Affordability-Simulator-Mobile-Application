import streamlit as st

st.set_page_config(
    page_title="FinPlan India",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── shared session-state initialisation ──────────────────────────────────────
def init_state():
    defaults = {
        "profile_done": False,
        "income_done": False,
        "assets_done": False,
        "goals_done": False,
        # profile
        "age": 30,
        "city": "Mumbai",
        "marital_status": "Single",
        "has_kids": False,
        "num_kids": 0,
        "living_situation": "With parents (no rent)",
        # income
        "net_take_home": 0,
        "annual_bonus": 0,
        "salary_growth_pct": 8.0,
        "employer_nps_monthly": 0,
        "epf_monthly": 0,
        # expenses
        "monthly_expenses": 0,
        "family_contribution_annual": 0,
        "post_marriage_expenses": 0,
        # assets
        "equity_mf_value": 0,
        "equity_mf_invested": 0,
        "direct_equity_value": 0,
        "direct_equity_invested": 0,
        "ppf_value": 0,
        "epf_value": 0,
        "nps_value": 0,
        "gold_value": 0,
        "rbi_bond_value": 0,
        "rbi_bond_date": None,
        "fd_value": 0,
        "other_assets": 0,
        "existing_liabilities": 0,
        # SIPs
        "sips": [],
        # goals
        "marriage_pv": 0,
        "marriage_years": 2,
        "house_budget_today": 0,
        "house_parents_contribution": 0,
        "house_loan_tenure": 20,
        "house_loan_rate": 8.5,
        "retirement_age": 55,
        "retirement_monthly_today": 150000,
        "lifestyle_inflation": 8.0,
        "has_emergency_fund": False,
        "emergency_fund_months": 6,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 FinPlan India")
    st.markdown("*Free financial planning for every Indian*")
    st.divider()
    steps = {
        "🏠 Home": "home",
        "👤 Profile": "profile",
        "💰 Income & Expenses": "income",
        "🏦 Assets & Liabilities": "assets",
        "🎯 Goals": "goals",
        "📈 Your Plan": "plan",
    }
    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    for label, key in steps.items():
        is_active = st.session_state["page"] == key
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state["page"] = key
            st.rerun()

    st.divider()
    # completion tracker
    done = sum([
        st.session_state["profile_done"],
        st.session_state["income_done"],
        st.session_state["assets_done"],
        st.session_state["goals_done"],
    ])
    st.progress(done / 4, text=f"Setup: {done}/4 sections done")
    st.caption("⚠️ This tool is for educational purposes only. Not SEBI-registered financial advice.")

# ── page router ───────────────────────────────────────────────────────────────
page = st.session_state["page"]

if page == "home":
    from pages_content import home
    home.render()
elif page == "profile":
    from pages_content import profile
    profile.render()
elif page == "income":
    from pages_content import income
    income.render()
elif page == "assets":
    from pages_content import assets
    assets.render()
elif page == "goals":
    from pages_content import goals
    goals.render()
elif page == "plan":
    from pages_content import plan
    plan.render()
