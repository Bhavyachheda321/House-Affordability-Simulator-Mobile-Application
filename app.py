import streamlit as st

st.set_page_config(
    page_title="FinPlan India",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container { padding: 1.5rem 1rem 3rem; max-width: 680px; }
    .stButton > button { border-radius: 10px; font-weight: 500; }
    .stButton > button[kind="primary"] {
        background: #185FA5; border: none; color: white; padding:.6rem 1.5rem;
    }
    .tip-box {
        background:#E6F1FB; border-left:3px solid #185FA5;
        border-radius:0 8px 8px 0; padding:10px 14px;
        font-size:.85rem; color:#0C447C; margin:8px 0 16px; line-height:1.5;
    }
    .warn-box {
        background:#FAEEDA; border-left:3px solid #EF9F27;
        border-radius:0 8px 8px 0; padding:10px 14px;
        font-size:.85rem; color:#633806; margin:8px 0 16px; line-height:1.5;
    }
    .ok-box {
        background:#EAF3DE; border-left:3px solid #3B6D11;
        border-radius:0 8px 8px 0; padding:10px 14px;
        font-size:.85rem; color:#27500A; margin:8px 0 16px; line-height:1.5;
    }
    .section-label {
        font-size:.75rem; font-weight:600; letter-spacing:.06em;
        text-transform:uppercase; color:#888; margin:1.5rem 0 .5rem;
    }
    .skip-note { font-size:.78rem; color:#aaa; margin-top:-10px; margin-bottom:8px; }
</style>
""", unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────────────────────
DEFAULTS = {
    "step": 0,
    "age": 28, "city": "Mumbai", "married": False,
    "living_with_parents": True, "living_situation": "With my parents (no rent)",
    "has_spouse_income": False, "spouse_monthly_salary": 0, "spouse_sip_monthly": 0,
    "old_regime": False, "bracket_label": "₹20L–₹50L", "effective_slab_rate": 0.2288,
    "property_appr_rate": 7.0, "lifestyle_inflation": 7,
    "has_loans_flag": False, "loans_outstanding": 0,
    "loan_emi_monthly": 0, "loan_interest_rate": 0.0,
    "monthly_salary": 0, "annual_bonus": 0, "salary_growth": 8,
    "epf_monthly": 0, "employer_nps_monthly": 0,
    "monthly_expenses": 0, "family_support_annual": 0,
    "post_marriage_expenses": 0, "sip_total_monthly": 0,
    "mf_value": 0, "stocks_value": 0,
    "ppf_value": 0, "ppf_contributing": True,
    "epf_value": 0, "nps_value": 0,
    "gold_value": 0, "fd_value": 0,
    "rbi_bond_value": 0, "rbi_bond_months_left": 0,
    "has_emergency_fund": False, "emergency_fund_value": 0,
    "want_house": True, "house_budget": 0, "parents_house_contribution": 0,
    "home_loan_rate": 8.5, "home_loan_tenure": 20,
    "want_marriage_savings": False, "marriage_cost": 0, "marriage_years": 2,
    "want_child_education": False, "child_education_cost": 2500000,
    "child_education_years": 18,
    "retirement_age": 55, "retirement_monthly_spend": 100000,
    "gemini_api_key": "", "gemini_question": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Progress bar ──────────────────────────────────────────────────────────────
STEP_LABELS = ["About you","Income","Spending","Assets","Goals","Your plan"]
step = st.session_state["step"]

if step > 0:
    cols = st.columns(len(STEP_LABELS))
    for i, label in enumerate(STEP_LABELS):
        with cols[i]:
            color = "#185FA5" if i <= step else "#ddd"
            txt_color = "#185FA5" if i == step else "#aaa" if i > step else "#555"
            st.markdown(
                f'<div style="height:4px;background:{color};border-radius:2px;margin-bottom:3px"></div>'
                f'<div style="font-size:10px;text-align:center;color:{txt_color}">{label}</div>',
                unsafe_allow_html=True)
    st.write("")

# ── PDF export (available on plan page) ──────────────────────────────────────
if step == 5:
    with st.sidebar:
        st.markdown("### 📄 Export your plan")
        if st.button("Download PDF summary", use_container_width=True):
            try:
                from fpdf import FPDF
                import io

                s = st.session_state
                from pages_content.calculations import (
                    project_retirement_corpus, monthly_cashflow, safe_withdrawal_rate
                )
                proj = project_retirement_corpus(s)
                cf   = monthly_cashflow(s)

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 16)
                pdf.cell(0, 10, "FinPlan India — Your Financial Plan", ln=True)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, f"Age: {s['age']}  |  City: {s['city']}  |  "
                         f"Bracket: {s.get('bracket_label','')}  |  "
                         f"{'Old' if s.get('old_regime') else 'New'} regime", ln=True)
                pdf.ln(4)

                pdf.set_font("Helvetica","B",12)
                pdf.cell(0,8,"Monthly Cashflow",ln=True)
                pdf.set_font("Helvetica","",10)
                pdf.cell(0,6,f"Take-home salary:  Rs.{cf['income']:,.0f}/month",ln=True)
                pdf.cell(0,6,f"Expenses + family: Rs.{cf['expenses']+cf['family']:,.0f}/month",ln=True)
                pdf.cell(0,6,f"Current SIPs:      Rs.{cf['sip']:,.0f}/month",ln=True)
                pdf.cell(0,6,f"Monthly surplus:   Rs.{cf['surplus']:,.0f}/month",ln=True)
                pdf.ln(4)

                total_assets = (s.get("mf_value",0)+s.get("stocks_value",0)+
                    s.get("ppf_value",0)+s.get("epf_value",0)+s.get("nps_value",0)+
                    s.get("gold_value",0)+s.get("rbi_bond_value",0)+s.get("fd_value",0))
                pdf.set_font("Helvetica","B",12)
                pdf.cell(0,8,"Net Worth Today",ln=True)
                pdf.set_font("Helvetica","",10)
                pdf.cell(0,6,f"Total assets: Rs.{total_assets:,.0f}",ln=True)
                pdf.cell(0,6,f"Loans outstanding: Rs.{s.get('loans_outstanding',0):,.0f}",ln=True)
                pdf.cell(0,6,f"Net worth: Rs.{total_assets - s.get('loans_outstanding',0):,.0f}",ln=True)
                pdf.ln(4)

                pdf.set_font("Helvetica","B",12)
                pdf.cell(0,8,"Retirement Projection",ln=True)
                pdf.set_font("Helvetica","",10)
                pdf.cell(0,6,f"Retirement age target: {s.get('retirement_age',55)}",ln=True)
                pdf.cell(0,6,f"Corpus needed: Rs.{proj['corpus_needed']:,.0f}",ln=True)
                pdf.cell(0,6,f"Projected (with 10% step-up): Rs.{proj['total_stepup']:,.0f}",ln=True)
                gap = proj['corpus_needed'] - proj['total_stepup']
                status = f"SURPLUS Rs.{-gap:,.0f}" if gap < 0 else f"SHORTFALL Rs.{gap:,.0f}"
                pdf.cell(0,6,f"Status: {status}",ln=True)
                pdf.ln(4)

                pdf.set_font("Helvetica","B",12)
                pdf.cell(0,8,"Top 3 Actions",ln=True)
                pdf.set_font("Helvetica","",10)
                actions = [
                    "1. Build emergency fund (6 months expenses) in a Liquid Mutual Fund",
                    "2. Buy Rs.2Cr term life + Rs.10L personal health insurance this week",
                    "3. Increase all SIPs by 10% every April and invest Rs.1.5L in PPF on April 1",
                ]
                for a in actions:
                    pdf.multi_cell(0,6,a)
                pdf.ln(4)

                pdf.set_font("Helvetica","I",8)
                pdf.multi_cell(0,5,
                    "DISCLAIMER: FinPlan India is a free educational calculator. Not SEBI-registered. "
                    "Not financial advice. All projections are estimates based on assumed returns. "
                    "Please consult a SEBI-registered investment adviser before making decisions.")

                buf = io.BytesIO()
                pdf_bytes = pdf.output()
                st.download_button("⬇ Click to download PDF",
                    data=bytes(pdf_bytes), file_name="finplan_india_plan.pdf",
                    mime="application/pdf", use_container_width=True)
            except ImportError:
                st.info("Install fpdf2 to enable PDF export: `pip install fpdf2`")
            except Exception as e:
                st.error(f"PDF generation error: {e}")

# ── Page routing ──────────────────────────────────────────────────────────────
from pages_content import (pg_about, pg_income, pg_spending,
                            pg_assets, pg_goals, pg_plan)
pages = [pg_about, pg_income, pg_spending, pg_assets, pg_goals, pg_plan]
pages[step].render()
