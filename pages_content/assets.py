import streamlit as st

def render():
    st.title("🏦 Assets & Liabilities")
    st.caption("Your current financial position — be as accurate as possible")
    st.divider()

    st.markdown("#### Equity & market investments")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["equity_mf_invested"] = st.number_input(
            "Equity MF — amount invested (₹)", min_value=0,
            value=st.session_state["equity_mf_invested"], step=10000, format="%d")
        st.session_state["equity_mf_value"] = st.number_input(
            "Equity MF — current value (₹)", min_value=0,
            value=st.session_state["equity_mf_value"], step=10000, format="%d")
    with col2:
        st.session_state["direct_equity_invested"] = st.number_input(
            "Direct stocks — amount invested (₹)", min_value=0,
            value=st.session_state["direct_equity_invested"], step=10000, format="%d")
        st.session_state["direct_equity_value"] = st.number_input(
            "Direct stocks — current value (₹)", min_value=0,
            value=st.session_state["direct_equity_value"], step=10000, format="%d")

    st.divider()
    st.markdown("#### Government & retirement instruments")
    col3, col4 = st.columns(2)
    with col3:
        st.session_state["ppf_value"] = st.number_input(
            "PPF — current balance (₹)", min_value=0,
            value=st.session_state["ppf_value"], step=10000, format="%d")
        st.session_state["ppf_active"] = st.checkbox(
            "PPF account is active (contributing every year)",
            value=st.session_state.get("ppf_active", True))
        st.session_state["ppf_annual_contribution"] = st.number_input(
            "PPF — annual contribution (₹, max ₹1,50,000)",
            min_value=0, max_value=150000,
            value=st.session_state.get("ppf_annual_contribution", 150000),
            step=10000, format="%d")

        st.session_state["epf_value"] = st.number_input(
            "EPF — current balance (₹)", min_value=0,
            value=st.session_state["epf_value"], step=10000, format="%d")
        st.session_state["nps_value"] = st.number_input(
            "NPS — current balance (₹)", min_value=0,
            value=st.session_state["nps_value"], step=10000, format="%d")

    with col4:
        st.session_state["rbi_bond_value"] = st.number_input(
            "RBI Floating Rate Bonds — invested amount (₹)", min_value=0,
            value=st.session_state["rbi_bond_value"], step=10000, format="%d")
        if st.session_state["rbi_bond_value"] > 0:
            import datetime
            st.session_state["rbi_bond_date"] = st.date_input(
                "RBI Bond — investment date",
                value=st.session_state["rbi_bond_date"] or datetime.date(2021, 5, 25),
                min_value=datetime.date(2020, 7, 1))
            import datetime as dt
            if st.session_state["rbi_bond_date"]:
                maturity = st.session_state["rbi_bond_date"].replace(
                    year=st.session_state["rbi_bond_date"].year + 7)
                months_left = max(0, (maturity - dt.date.today()).days // 30)
                st.caption(f"📅 Matures: {maturity.strftime('%b %Y')} ({months_left} months away)")
                st.session_state["rbi_bond_months_left"] = months_left

        st.session_state["fd_value"] = st.number_input(
            "Fixed Deposits — total value (₹)", min_value=0,
            value=st.session_state["fd_value"], step=10000, format="%d")

    st.divider()
    st.markdown("#### Other assets")
    col5, col6 = st.columns(2)
    with col5:
        st.session_state["gold_value"] = st.number_input(
            "Gold — current value (₹)  *(physical + SGB + ETF)*",
            min_value=0, value=st.session_state["gold_value"],
            step=10000, format="%d")
        st.session_state["other_assets"] = st.number_input(
            "Other assets (₹)  *(business, crypto, etc.)*",
            min_value=0, value=st.session_state["other_assets"],
            step=10000, format="%d")
    with col6:
        st.session_state["has_emergency_fund"] = st.checkbox(
            "I have a dedicated emergency fund",
            value=st.session_state["has_emergency_fund"])
        if st.session_state["has_emergency_fund"]:
            st.session_state["emergency_fund_value"] = st.number_input(
                "Emergency fund value (₹)",
                min_value=0,
                value=st.session_state.get("emergency_fund_value", 0),
                step=10000, format="%d")

    st.divider()
    st.markdown("#### Liabilities")
    col7, col8 = st.columns(2)
    with col7:
        st.session_state["personal_loan"] = st.number_input(
            "Personal loan outstanding (₹)", min_value=0,
            value=st.session_state.get("personal_loan", 0),
            step=10000, format="%d")
        st.session_state["personal_loan_emi"] = st.number_input(
            "Personal loan EMI / month (₹)", min_value=0,
            value=st.session_state.get("personal_loan_emi", 0),
            step=1000, format="%d")
    with col8:
        st.session_state["other_liabilities"] = st.number_input(
            "Other liabilities (₹)  *(credit card, vehicle loan, etc.)*",
            min_value=0, value=st.session_state.get("other_liabilities", 0),
            step=10000, format="%d")
        st.session_state["other_emis"] = st.number_input(
            "Other EMIs / month (₹)", min_value=0,
            value=st.session_state.get("other_emis", 0),
            step=1000, format="%d")

    st.divider()

    # Net worth summary
    gross_assets = (
        st.session_state["equity_mf_value"] +
        st.session_state["direct_equity_value"] +
        st.session_state["ppf_value"] +
        st.session_state["epf_value"] +
        st.session_state["nps_value"] +
        st.session_state["rbi_bond_value"] +
        st.session_state["fd_value"] +
        st.session_state["gold_value"] +
        st.session_state.get("emergency_fund_value", 0) +
        st.session_state["other_assets"]
    )
    total_liabilities = (
        st.session_state.get("personal_loan", 0) +
        st.session_state.get("other_liabilities", 0) +
        st.session_state.get("home_loan_outstanding", 0)
    )
    net_worth = gross_assets - total_liabilities

    liquid = (
        st.session_state["equity_mf_value"] +
        st.session_state["direct_equity_value"] +
        st.session_state["fd_value"] +
        st.session_state.get("emergency_fund_value", 0)
    )
    locked = (
        st.session_state["ppf_value"] +
        st.session_state["epf_value"] +
        st.session_state["nps_value"] +
        st.session_state["rbi_bond_value"]
    )

    st.markdown("#### 💼 Net worth snapshot")
    col_n1, col_n2, col_n3, col_n4 = st.columns(4)
    col_n1.metric("Gross assets", f"₹{gross_assets/1e5:.1f}L")
    col_n2.metric("Liabilities", f"₹{total_liabilities/1e5:.1f}L")
    col_n3.metric("Net worth", f"₹{net_worth/1e5:.1f}L")
    col_n4.metric("Liquid / investable", f"₹{liquid/1e5:.1f}L")

    # Gold check
    if gross_assets > 0:
        gold_pct = st.session_state["gold_value"] / gross_assets * 100
        if gold_pct < 5:
            st.warning(f"⚠️ Gold is only {gold_pct:.1f}% of your portfolio. Recommended: 8–10%. Consider Sovereign Gold Bonds.")

    if not st.session_state["has_emergency_fund"]:
        monthly_need = (st.session_state["monthly_expenses"] +
                        st.session_state["family_contribution_annual"] / 12)
        st.warning(f"⚠️ No emergency fund detected. You need ₹{monthly_need * 6:,.0f} (6 months of expenses = ₹{monthly_need:,.0f}/mo).")

    st.divider()
    cb1, cb2 = st.columns([3, 1])
    with cb2:
        if st.button("Next: Goals →", type="primary", use_container_width=True):
            st.session_state["assets_done"] = True
            st.session_state["page"] = "goals"
            st.rerun()
