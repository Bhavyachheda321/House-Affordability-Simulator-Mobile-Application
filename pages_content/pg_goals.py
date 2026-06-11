"""FinPlan India v4 — Step 5: Goals"""
import streamlit as st


def render():
    from pages_content.calculations import (
        CITY_PROPERTY_APPRECIATION, CITY_STAMP_DUTY,
        goal_corpus_needed, goal_monthly_sip, emi_amount,
    )

    s = st.session_state
    infl = s.get("lifestyle_inflation", 7) / 100

    st.markdown("#### 🎯 Your Financial Goals")
    st.caption("Tell us what you're working towards. Only tick what applies to you.")

    # ── Retirement (always shown) ─────────────────────────────────────────────
    st.markdown("##### 🏖 Retirement")
    col1, col2 = st.columns(2)
    with col1:
        s["retirement_age"] = st.number_input(
            "Target retirement age", min_value=int(s.get("age", 28)) + 1,
            max_value=75,
            value=int(s.get("retirement_age", 55)), step=1,
            help="The age at which you want to stop working (or have the option to).",
        )
    with col2:
        s["retirement_monthly_spend"] = st.number_input(
            "Monthly spending at retirement (₹, in today's money)",
            min_value=10000,
            value=int(s.get("retirement_monthly_spend", 100000)),
            step=5000, format="%d",
            help=(
                "How much you'd spend per month in retirement — in today's rupees. "
                "The simulator inflates this to the year you retire."
            ),
        )

    years_to_ret = max(1, s["retirement_age"] - s.get("age", 28))
    future_spend = s["retirement_monthly_spend"] * (1 + infl) ** years_to_ret
    st.caption(
        f"In {years_to_ret} years at {int(infl*100)}% inflation: "
        f"₹{future_spend:,.0f}/month"
    )

    st.divider()

    # ── House ─────────────────────────────────────────────────────────────────
    s["want_house"] = st.checkbox(
        "🏠 I want to buy a house",
        value=s.get("want_house", True),
    )
    if s["want_house"]:
        city  = s.get("city", "Other")
        appr  = CITY_PROPERTY_APPRECIATION.get(city, 6.0)
        stamp = CITY_STAMP_DUTY.get(city, 0.06)

        col3, col4 = st.columns(2)
        with col3:
            s["house_budget"] = st.number_input(
                "Target home price today (₹)", min_value=0,
                value=int(s.get("house_budget", 5000000)),
                step=500000, format="%d",
                help="Current market price of the home you want. We'll inflate it forward.",
            )
            s["home_loan_tenure"] = st.number_input(
                "Preferred loan tenure (years)", min_value=5, max_value=30,
                value=int(s.get("home_loan_tenure", 20)), step=1,
            )
        with col4:
            s["parents_house_contribution"] = st.number_input(
                "Family contribution to down payment (₹)  *(0 if none)*",
                min_value=0,
                value=int(s.get("parents_house_contribution", 0)),
                step=100000, format="%d",
            )
            s["home_loan_rate"] = st.number_input(
                "Expected home loan rate (%)", min_value=6.0, max_value=15.0,
                value=float(s.get("home_loan_rate", 8.5)),
                step=0.25, format="%.2f",
                help="Current home loan rates: 8.5–9.5% for most banks.",
            )

        # City info
        st.markdown(
            f'<div class="tip-box">📍 {city}: property appreciation ~{appr:.1f}%/yr, '
            f"stamp duty ~{stamp*100:.0f}%. "
            f"At {appr:.0f}% appreciation, ₹{s['house_budget']/1e5:.0f}L today → "
            f"₹{s['house_budget']*(1+appr/100)**5/1e7:.1f} Cr in 5 years.</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Marriage ──────────────────────────────────────────────────────────────
    s["want_marriage_savings"] = st.checkbox(
        "💍 I want to save for a wedding",
        value=s.get("want_marriage_savings", False),
    )
    if s["want_marriage_savings"]:
        col5, col6 = st.columns(2)
        with col5:
            s["marriage_cost"] = st.number_input(
                "Estimated wedding cost today (₹)", min_value=0,
                value=int(s.get("marriage_cost", 1500000)),
                step=100000, format="%d",
            )
        with col6:
            s["marriage_years"] = st.number_input(
                "Years from now", min_value=1, max_value=20,
                value=int(s.get("marriage_years", 3)), step=1,
            )
        m_fv = goal_corpus_needed(s["marriage_cost"], s["marriage_years"], infl)
        sip_m = goal_monthly_sip(m_fv, s["marriage_years"])
        st.caption(
            f"Inflation-adjusted cost in {s['marriage_years']} years: ₹{m_fv:,.0f} — "
            f"needs ₹{sip_m:,.0f}/mo SIP to reach it."
        )

    st.divider()

    # ── Child education ────────────────────────────────────────────────────────
    s["want_child_education"] = st.checkbox(
        "🎓 I want to plan for my child's education",
        value=s.get("want_child_education", False),
    )
    if s["want_child_education"]:
        col7, col8 = st.columns(2)
        with col7:
            s["child_education_cost"] = st.number_input(
                "Estimated education cost today (₹)", min_value=0,
                value=int(s.get("child_education_cost", 2500000)),
                step=100000, format="%d",
                help="Total cost of graduation/post-grad in today's money.",
            )
        with col8:
            s["child_education_years"] = st.number_input(
                "Years until education begins", min_value=1, max_value=25,
                value=int(s.get("child_education_years", 18)), step=1,
            )
        edu_infl = 0.10   # Education inflation ~10%
        e_fv = goal_corpus_needed(s["child_education_cost"], s["child_education_years"], edu_infl)
        sip_e = goal_monthly_sip(e_fv, s["child_education_years"])
        st.caption(
            f"Education inflation ~10%/yr: corpus needed ₹{e_fv:,.0f} in "
            f"{s['child_education_years']} years — needs ₹{sip_e:,.0f}/mo SIP."
        )

    # ── Nav ───────────────────────────────────────────────────────────────────
    st.divider()
    col_a, _, col_b = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Back", use_container_width=True):
            s["step"] = 4
            st.rerun()
    with col_b:
        if st.button("Build my plan →", type="primary", use_container_width=True):
            s["step"] = 6
            st.rerun()
