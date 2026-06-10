import streamlit as st

def render():
    st.title("📊 FinPlan India")
    st.subheader("Goal-based financial planning built for Indian investors")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🎯 Goal-linked")
        st.write("Plan for marriage, home, child education, and retirement — all in one place with accurate Indian tax calculations.")
    with col2:
        st.markdown("#### 🧮 Tax-aware")
        st.write("LTCG, STCG, slab rates, NPS, PPF, EPF — every calculation reflects current Indian tax law.")
    with col3:
        st.markdown("#### 📱 Your numbers")
        st.write("No generic advice. Enter your salary, assets and goals — get a personalised, actionable plan.")

    st.divider()
    st.markdown("### How it works")

    steps_col1, steps_col2 = st.columns(2)
    with steps_col1:
        st.markdown("""
**Step 1 — Profile** (2 min)
Age, city, family situation

**Step 2 — Income & Expenses** (3 min)
Salary, bonus, SIPs, monthly spend

**Step 3 — Assets & Liabilities** (3 min)
MF, stocks, PPF, EPF, NPS, gold, loans
        """)
    with steps_col2:
        st.markdown("""
**Step 4 — Goals** (3 min)
Marriage, house, retirement, kids

**Step 5 — Your Plan** (instant)
Full projection, tax computation,
actionable month-by-month steps
        """)

    st.divider()
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        if st.button("🚀 Start your plan →", use_container_width=True, type="primary"):
            st.session_state["page"] = "profile"
            st.rerun()

    st.divider()
    st.caption("""
⚠️ **Disclaimer:** FinPlan India is an educational financial calculator. It does not constitute financial advice.
All projections are based on assumptions that may not reflect actual market conditions.
Past returns are not indicative of future performance. Please consult a SEBI-registered investment advisor
before making financial decisions.
    """)
