import streamlit as st

def render():
    st.title("👋 Welcome to FinPlan India")
    st.write("Answer a few simple questions — we'll build your personalised money plan in under 10 minutes.")
    st.markdown('<div class="tip-box">No jargon. No sign-up. No data stored anywhere. Everything stays on your screen.</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### About you")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["age"] = st.number_input("Your age", 18, 65, st.session_state["age"], step=1)
    with col2:
        cities = ["Mumbai","Delhi NCR","Bengaluru","Pune","Hyderabad","Chennai","Kolkata","Other"]
        st.session_state["city"] = st.selectbox("City", cities,
            index=cities.index(st.session_state["city"]))

    city_appr  = {"Mumbai":7,"Delhi NCR":6,"Bengaluru":8,"Pune":7,
                  "Hyderabad":7.5,"Chennai":5.5,"Kolkata":5,"Other":6}
    city_infl  = {"Mumbai":8,"Delhi NCR":7,"Bengaluru":7,"Pune":7,
                  "Hyderabad":7,"Chennai":6,"Kolkata":6,"Other":6}
    st.session_state["property_appr_rate"] = city_appr[st.session_state["city"]]
    st.session_state["lifestyle_inflation"] = city_infl[st.session_state["city"]]

    col3, col4 = st.columns(2)
    with col3:
        st.session_state["married"] = st.radio(
            "Marital status", ["Single","Married"],
            index=1 if st.session_state["married"] else 0) == "Married"
    with col4:
        living_opts = ["With parents (no rent)","I pay rent","I own my home"]
        curr_living = st.session_state.get("living_situation","With parents (no rent)")
        if curr_living not in living_opts: curr_living = living_opts[0]
        st.session_state["living_situation"] = st.radio("Where do you live?", living_opts,
            index=living_opts.index(curr_living))
        st.session_state["living_with_parents"] = (st.session_state["living_situation"] == "With parents (no rent)")

    if st.session_state["living_with_parents"]:
        st.markdown('<div class="ok-box">Living with parents = saving ₹40,000–80,000/month in rent. Your plan will use this window to build wealth faster.</div>', unsafe_allow_html=True)

    # ── Spouse income ──────────────────────────────────────────────────────────
    if st.session_state["married"]:
        st.divider()
        st.markdown("#### Spouse income")
        has_spouse_income = st.checkbox("My spouse also earns income",
            value=st.session_state.get("has_spouse_income", False))
        st.session_state["has_spouse_income"] = has_spouse_income
        if has_spouse_income:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.session_state["spouse_monthly_salary"] = st.number_input(
                    "Spouse monthly take-home (₹)", min_value=0,
                    value=st.session_state.get("spouse_monthly_salary", 0),
                    step=1000, format="%d")
            with col_s2:
                st.session_state["spouse_sip_monthly"] = st.number_input(
                    "Spouse existing SIPs/month (₹)", min_value=0,
                    value=st.session_state.get("spouse_sip_monthly", 0),
                    step=500, format="%d")

    # ── Tax regime ─────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### Tax details")
    st.markdown('<p class="skip-note">This affects which investments we recommend. Check your last ITR or ask your CA.</p>', unsafe_allow_html=True)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        regime = st.radio("Which tax regime do you file under?",
            ["New regime (default from FY24-25)", "Old regime (with deductions)"],
            index=0 if not st.session_state.get("old_regime", False) else 1)
        st.session_state["old_regime"] = (regime == "Old regime (with deductions)")
        if st.session_state["old_regime"]:
            st.markdown('<div class="tip-box">Old regime: your PPF, ELSS, and insurance premiums reduce your tax. We\'ll factor this in.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="tip-box">New regime: lower rates but no deductions. PPF and ELSS still earn well — just no tax deduction on contributions.</div>', unsafe_allow_html=True)

    with col_t2:
        bracket_opts = ["Under ₹7L","₹7L–₹12L","₹12L–₹20L","₹20L–₹50L","Above ₹50L"]
        curr_bracket = st.session_state.get("bracket_label","₹20L–₹50L")
        if curr_bracket not in bracket_opts: curr_bracket = "₹20L–₹50L"
        bracket = st.selectbox("Your approximate annual taxable income",
            bracket_opts, index=bracket_opts.index(curr_bracket),
            help="Include salary, bonus, other income. This is gross income, not take-home.")
        st.session_state["bracket_label"] = bracket

    from pages_content.calculations import effective_slab_rate
    slab = effective_slab_rate(bracket)
    st.session_state["effective_slab_rate"] = slab

    if slab > 0:
        st.caption(f"Effective tax rate (after surcharge + cess): {slab*100:.1f}%")

    # ── Existing loan rate (for debt priority module) ──────────────────────────
    st.divider()
    st.markdown("#### Do you have any loans?")
    has_loans = st.radio("Current loans", ["No loans", "Yes, I have loans"],
        index=1 if st.session_state.get("has_loans_flag", False) else 0)
    st.session_state["has_loans_flag"] = (has_loans == "Yes, I have loans")
    if st.session_state["has_loans_flag"]:
        col_l1, col_l2, col_l3 = st.columns(3)
        with col_l1:
            st.session_state["loans_outstanding"] = st.number_input(
                "Total loan pending (₹)", min_value=0,
                value=st.session_state.get("loans_outstanding", 0),
                step=10000, format="%d")
        with col_l2:
            st.session_state["loan_emi_monthly"] = st.number_input(
                "Monthly EMI (₹)", min_value=0,
                value=st.session_state.get("loan_emi_monthly", 0),
                step=500, format="%d")
        with col_l3:
            st.session_state["loan_interest_rate"] = st.number_input(
                "Loan interest rate (%)", min_value=1.0, max_value=36.0,
                value=st.session_state.get("loan_interest_rate", 10.0),
                step=0.5, format="%.1f",
                help="Check your loan statement. Personal loan: 11-18%, Home loan: 8-9%, Car: 8-10%")
    else:
        st.session_state["loans_outstanding"] = 0
        st.session_state["loan_emi_monthly"] = 0
        st.session_state["loan_interest_rate"] = 0.0

    st.divider()
    _, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("Next →", type="primary", use_container_width=True):
            st.session_state["step"] = 1
            st.rerun()
