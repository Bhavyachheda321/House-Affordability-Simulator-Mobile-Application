import streamlit as st

def render():
    st.title("🎯 Your Financial Goals")
    st.caption("Define what you're working toward — be realistic, not optimistic")
    st.divider()

    # ── Retirement ────────────────────────────────────────────────────────────
    st.markdown("#### 🏖 Retirement / Financial independence")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state["retirement_age"] = st.number_input(
            "Target retirement age", min_value=40, max_value=70,
            value=st.session_state["retirement_age"], step=1)
        years_to_retire = st.session_state["retirement_age"] - st.session_state["age"]
        st.caption(f"⏱ {years_to_retire} years away")
    with col2:
        st.session_state["retirement_monthly_today"] = st.number_input(
            "Monthly lifestyle needed (₹, today's value)",
            min_value=10000, value=st.session_state["retirement_monthly_today"],
            step=5000, format="%d")
    with col3:
        infl = st.session_state["lifestyle_inflation"] / 100
        future_monthly = st.session_state["retirement_monthly_today"] * (1 + infl) ** years_to_retire
        corpus_needed = (future_monthly * 12) / 0.045  # 4.5% SWR
        st.metric("Corpus needed (4.5% SWR)", f"₹{corpus_needed/1e7:.2f} Cr")
        st.caption(f"Monthly need at retirement: ₹{future_monthly:,.0f}")

    st.divider()

    # ── House ─────────────────────────────────────────────────────────────────
    st.markdown("#### 🏠 Home purchase")
    wants_house = st.checkbox("I plan to buy a home",
                              value=st.session_state.get("wants_house", True))
    st.session_state["wants_house"] = wants_house

    if wants_house:
        col4, col5 = st.columns(2)
        with col4:
            st.session_state["house_budget_today"] = st.number_input(
                "Target property budget (₹, today's value)",
                min_value=0, value=st.session_state["house_budget_today"],
                step=500000, format="%d")
            st.session_state["house_parents_contribution"] = st.number_input(
                "Family / parental contribution (₹, interest-free)",
                min_value=0, value=st.session_state["house_parents_contribution"],
                step=100000, format="%d")
        with col5:
            st.session_state["house_loan_rate"] = st.slider(
                "Home loan rate (%)", min_value=7.0, max_value=12.0,
                value=st.session_state["house_loan_rate"], step=0.25)
            st.session_state["house_loan_tenure"] = st.selectbox(
                "Loan tenure (years)", [10, 15, 20, 25, 30],
                index=[10, 15, 20, 25, 30].index(st.session_state["house_loan_tenure"]))

        # EMI feasibility calc
        net_salary = st.session_state["net_take_home"]
        max_emi = net_salary * 0.40
        r = st.session_state["house_loan_rate"] / 100 / 12
        n = st.session_state["house_loan_tenure"] * 12
        if r > 0:
            emi_per_lakh = r * (1 + r)**n / ((1 + r)**n - 1) * 100000
            max_loan = (max_emi / emi_per_lakh) * 100000
        else:
            max_loan = max_emi * n

        st.session_state["max_home_loan"] = max_loan
        col_h1, col_h2, col_h3 = st.columns(3)
        col_h1.metric("Max loan (40% EMI rule)", f"₹{max_loan/1e5:.1f}L")
        col_h2.metric("Max EMI allowed", f"₹{max_emi:,.0f}/mo")
        col_h3.metric("EMI per ₹1L at current rate/tenure", f"₹{emi_per_lakh:,.0f}")

        if st.session_state["house_budget_today"] > 0:
            prop_appr = st.session_state.get("property_appreciation", 7.0) / 100
            own_needed_now = (st.session_state["house_budget_today"]
                              - st.session_state["house_parents_contribution"]
                              - max_loan)
            if own_needed_now > 0:
                st.info(f"💡 Own corpus needed (at today's prices): **₹{own_needed_now/1e5:.1f}L** "
                        f"(total - parents - max loan)")
            else:
                st.success("✅ Parents contribution + max loan covers the full budget at today's prices.")

    st.divider()

    # ── Marriage ──────────────────────────────────────────────────────────────
    if st.session_state["marital_status"] == "Single":
        st.markdown("#### 💍 Marriage")
        wants_marriage_corpus = st.checkbox("Plan for marriage expenses",
                                            value=st.session_state.get("wants_marriage_corpus", True))
        st.session_state["wants_marriage_corpus"] = wants_marriage_corpus
        if wants_marriage_corpus:
            col6, col7 = st.columns(2)
            with col6:
                st.session_state["marriage_pv"] = st.number_input(
                    "Expected marriage expenses (₹, today's value)",
                    min_value=0, value=st.session_state["marriage_pv"],
                    step=100000, format="%d")
            with col7:
                st.session_state["marriage_years"] = st.number_input(
                    "Years until marriage", min_value=0, max_value=15,
                    value=st.session_state["marriage_years"], step=1)
                if st.session_state["marriage_pv"] > 0:
                    infl = st.session_state["lifestyle_inflation"] / 100
                    marriage_fv = st.session_state["marriage_pv"] * (1 + infl) ** st.session_state["marriage_years"]
                    st.caption(f"Future value in {st.session_state['marriage_years']} yrs: **₹{marriage_fv/1e5:.2f}L**")

        st.divider()

    # ── Children ──────────────────────────────────────────────────────────────
    st.markdown("#### 👶 Children's education")
    wants_child = st.checkbox("Plan for child's education",
                              value=st.session_state.get("wants_child_education", False))
    st.session_state["wants_child_education"] = wants_child
    if wants_child:
        col8, col9 = st.columns(2)
        with col8:
            st.session_state["child_education_pv"] = st.number_input(
                "Education corpus needed (₹, today's value)",
                min_value=0,
                value=st.session_state.get("child_education_pv", 2500000),
                step=100000, format="%d")
        with col9:
            st.session_state["child_education_years"] = st.number_input(
                "Years until education expenses", min_value=5, max_value=25,
                value=st.session_state.get("child_education_years", 18), step=1)
            if st.session_state["child_education_pv"] > 0:
                infl = st.session_state["lifestyle_inflation"] / 100
                edu_fv = st.session_state["child_education_pv"] * (1 + infl) ** st.session_state["child_education_years"]
                r_m = 0.12 / 12
                n_m = st.session_state["child_education_years"] * 12
                sip_needed = edu_fv * r_m / ((1 + r_m)**n_m - 1)
                st.caption(f"Future value: **₹{edu_fv/1e5:.1f}L** | SIP needed: **₹{sip_needed:,.0f}/mo** at 12%")

    st.divider()

    # ── Emergency fund ────────────────────────────────────────────────────────
    st.markdown("#### 🛡 Emergency fund")
    col10, col11 = st.columns(2)
    with col10:
        st.session_state["emergency_fund_months"] = st.selectbox(
            "Emergency fund target (months of expenses)",
            [3, 6, 9, 12], index=1)
    with col11:
        monthly_need = (st.session_state["monthly_expenses"] +
                        st.session_state["family_contribution_annual"] / 12 +
                        st.session_state.get("personal_loan_emi", 0) +
                        st.session_state.get("other_emis", 0))
        ef_target = monthly_need * st.session_state["emergency_fund_months"]
        current_ef = st.session_state.get("emergency_fund_value", 0)
        ef_gap = max(0, ef_target - current_ef)
        st.metric("Emergency fund target", f"₹{ef_target:,.0f}")
        if ef_gap > 0:
            st.caption(f"Gap: ₹{ef_gap:,.0f} — build over {max(1, int(ef_gap/25000))} months at ₹25,000/mo")

    st.divider()
    cb1, cb2 = st.columns([3, 1])
    with cb2:
        if st.button("Generate My Plan →", type="primary", use_container_width=True):
            st.session_state["goals_done"] = True
            st.session_state["page"] = "plan"
            st.rerun()
