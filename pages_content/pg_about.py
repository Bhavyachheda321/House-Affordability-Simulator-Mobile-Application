"""FinPlan India v4 — Step 1: About You"""
import streamlit as st


def render():
    from pages_content.calculations import (
        CITY_PROPERTY_APPRECIATION, CITY_LIFESTYLE_INFLATION, CITY_STAMP_DUTY,
    )
    from pages_content.tax_engine import effective_slab_rate_from_bracket

    s = st.session_state

    st.markdown("#### 👤 About You")
    st.caption("Basic details that shape your entire plan. Take 2 minutes to get these right.")

    col1, col2 = st.columns(2)
    with col1:
        s["age"] = st.number_input(
            "Your age", min_value=18, max_value=70,
            value=int(s.get("age", 28)), step=1,
            help="Your age today. The plan runs until retirement.",
        )
    with col2:
        cities = ["Mumbai", "Delhi NCR", "Bengaluru", "Pune",
                  "Hyderabad", "Chennai", "Kolkata", "Ahmedabad", "Other"]
        curr_city = s.get("city", "Mumbai")
        if curr_city not in cities:
            curr_city = "Mumbai"
        s["city"] = st.selectbox("City you live in", cities,
                                  index=cities.index(curr_city))

    # Auto-fill city defaults
    s["property_appr_rate"] = CITY_PROPERTY_APPRECIATION.get(s["city"], 6.0)
    s["lifestyle_inflation"] = CITY_LIFESTYLE_INFLATION.get(s["city"], 7)

    col3, col4 = st.columns(2)
    with col3:
        s["married"] = st.radio(
            "Marital status", ["Single", "Married"],
            index=1 if s.get("married") else 0,
        ) == "Married"
    with col4:
        living_opts = ["With parents (no rent)", "I pay rent", "I own my home"]
        curr = s.get("living_situation", "With parents (no rent)")
        if curr not in living_opts:
            curr = living_opts[0]
        s["living_situation"] = st.radio("Living situation", living_opts,
                                          index=living_opts.index(curr))
        s["living_with_parents"] = (s["living_situation"] == "With parents (no rent)")

    if s["living_with_parents"]:
        st.markdown(
            '<div class="tip-box">💡 Living with parents saves you ₹25K–₹80K/month in rent. '
            "Your plan will use this window to build wealth faster.</div>",
            unsafe_allow_html=True,
        )

    # ── Spouse ────────────────────────────────────────────────────────────────
    if s["married"]:
        st.divider()
        st.markdown("#### 👫 Spouse Income")
        s["has_spouse_income"] = st.checkbox(
            "My spouse also earns income",
            value=s.get("has_spouse_income", False),
        )
        if s["has_spouse_income"]:
            c1, c2, c3 = st.columns(3)
            with c1:
                s["spouse_monthly_salary"] = st.number_input(
                    "Spouse monthly take-home (₹)", min_value=0,
                    value=int(s.get("spouse_monthly_salary", 0)),
                    step=1000, format="%d",
                )
            with c2:
                s["spouse_salary_growth"] = st.number_input(
                    "Spouse salary growth (%/yr)", min_value=0.0, max_value=30.0,
                    value=float(s.get("spouse_salary_growth", 8.0)),
                    step=0.5, format="%.1f",
                    help="Expected annual increment for spouse. Can differ from yours.",
                )
            with c3:
                s["spouse_sip_monthly"] = st.number_input(
                    "Spouse monthly SIP (₹)", min_value=0,
                    value=int(s.get("spouse_sip_monthly", 0)),
                    step=500, format="%d",
                )

    # ── Tax details ───────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 🧾 Tax Details")
    st.caption("This affects which investments we recommend and how much tax we deduct in projections.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        regime = st.radio(
            "Tax regime",
            ["New regime (default from FY 2024-25)", "Old regime (with deductions)"],
            index=0 if not s.get("old_regime", False) else 1,
        )
        s["old_regime"] = ("Old regime" in regime)
        if s["old_regime"]:
            st.markdown(
                '<div class="tip-box">Old regime: PPF, ELSS, insurance premiums reduce your tax. '
                "We'll factor 80C, HRA, and NPS deductions in.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="tip-box">New regime: lower rates, no deductions (except NPS employer). '
                "Simpler tax — recommended if you don't claim many deductions.</div>",
                unsafe_allow_html=True,
            )

    with col_t2:
        bracket_opts = [
            "Under ₹7L", "₹7L–₹12L", "₹12L–₹20L",
            "₹20L–₹50L", "₹50L–₹1Cr", "₹1Cr–₹2Cr", "Above ₹2Cr",
        ]
        curr_b = s.get("bracket_label", "₹20L–₹50L")
        if curr_b not in bracket_opts:
            curr_b = "₹20L–₹50L"
        s["bracket_label"] = st.selectbox(
            "Annual taxable income (approx.)",
            bracket_opts,
            index=bracket_opts.index(curr_b),
            help="Include salary + bonus. This is gross income before deductions.",
        )
        s["effective_slab_rate"] = effective_slab_rate_from_bracket(s["bracket_label"])
        if s["effective_slab_rate"] > 0:
            st.caption(
                f"Effective rate (surcharge + cess included): "
                f"{s['effective_slab_rate']*100:.1f}%"
            )

    # Old-regime specific fields
    if s["old_regime"]:
        with st.expander("⚙️ Old Regime: HRA & Deduction Details", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                s["basic_monthly"] = st.number_input(
                    "Basic salary (₹/mo)", min_value=0,
                    value=int(s.get("basic_monthly", 0)), step=1000,
                    help="'Basic' on your payslip. Typically 40–50% of gross.",
                )
                s["hra_monthly"] = st.number_input(
                    "HRA received (₹/mo)", min_value=0,
                    value=int(s.get("hra_monthly", 0)), step=500,
                )
            with c2:
                s["metro_city"] = st.checkbox(
                    "Metro city? (Mumbai / Delhi / Kolkata / Chennai)",
                    value=s.get("metro_city", True),
                    help="Affects HRA exemption: 50% for metro, 40% for non-metro.",
                )
                s["other_80c"] = st.number_input(
                    "Other 80C deductions (₹/yr)",
                    min_value=0,
                    value=int(s.get("other_80c", 0)),
                    step=5000,
                    help="ELSS + LIC + PPF contribution. Max ₹1.5L. EPF is auto-included.",
                )
            with c3:
                s["employer_nps_annual"] = st.number_input(
                    "Employer NPS (₹/yr)", min_value=0,
                    value=int(s.get("employer_nps_annual", 0)), step=5000,
                    help="Company NPS contribution. Deductible under 80CCD(2) in both regimes.",
                )

    # ── Loans ─────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 💳 Existing Loans")
    has_loans = st.radio(
        "Do you have any active loans?",
        ["No loans", "Yes, I have loans"],
        index=1 if s.get("has_loans_flag", False) else 0,
        horizontal=True,
    )
    s["has_loans_flag"] = has_loans == "Yes, I have loans"
    if s["has_loans_flag"]:
        c1, c2, c3 = st.columns(3)
        with c1:
            s["loans_outstanding"] = st.number_input(
                "Total loan outstanding (₹)", min_value=0,
                value=int(s.get("loans_outstanding", 0)),
                step=10000, format="%d",
            )
        with c2:
            s["loan_emi_monthly"] = st.number_input(
                "Monthly EMI (₹)", min_value=0,
                value=int(s.get("loan_emi_monthly", 0)),
                step=500, format="%d",
            )
        with c3:
            s["loan_interest_rate"] = st.number_input(
                "Loan interest rate (%)", min_value=1.0, max_value=36.0,
                value=float(s.get("loan_interest_rate", 10.0)),
                step=0.5, format="%.1f",
                help="Check your loan statement. Home loan: 8–9%, Personal: 11–18%",
            )
    else:
        s["loans_outstanding"] = 0
        s["loan_emi_monthly"]  = 0
        s["loan_interest_rate"]= 0.0

    # ── Nav ───────────────────────────────────────────────────────────────────
    st.divider()
    _, col_btn = st.columns([3, 1])
    with col_btn:
        if st.button("Next →", type="primary", use_container_width=True):
            s["step"] = 2
            st.rerun()
