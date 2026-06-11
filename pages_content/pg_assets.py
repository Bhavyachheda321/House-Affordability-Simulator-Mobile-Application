import streamlit as st

def render():
    st.title("🏦 What you already own")
    st.write("Skip anything you don't have or aren't sure about — we'll still build your plan.")

    st.markdown('<div class="tip-box">💡 You can find most of these numbers in your bank app, Zerodha/Groww app, or your salary slip. Rough estimates are fine — don\'t stress about exact figures.</div>', unsafe_allow_html=True)

    # ── Mutual funds ──────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">Mutual funds</p>', unsafe_allow_html=True)
    has_mf = st.checkbox("I have mutual fund investments", value=st.session_state["mf_value"] > 0)
    if has_mf:
        st.session_state["mf_value"] = st.number_input(
            "Current value of all your mutual funds today (₹)",
            min_value=0, value=st.session_state["mf_value"], step=10000, format="%d",
            help="Open Groww or CAMS app → see 'Current Value'"
        )
    else:
        st.session_state["mf_value"] = 0

    # ── Direct stocks ─────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">Direct stocks (shares)</p>', unsafe_allow_html=True)
    has_stocks = st.checkbox("I own shares directly (Zerodha, Upstox, etc.)",
                             value=st.session_state["stocks_value"] > 0)
    if has_stocks:
        st.session_state["stocks_value"] = st.number_input(
            "Current value of your stock portfolio today (₹)",
            min_value=0, value=st.session_state["stocks_value"], step=10000, format="%d",
            help="Open Zerodha Kite or your broker app → see Portfolio value"
        )
    else:
        st.session_state["stocks_value"] = 0

    # ── PPF ───────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">PPF (Public Provident Fund)</p>', unsafe_allow_html=True)
    st.markdown('<p class="skip-note">A government savings scheme — usually opened at SBI or Post Office. Earns ~7.1% tax-free.</p>', unsafe_allow_html=True)
    has_ppf = st.checkbox("I have a PPF account", value=st.session_state["ppf_value"] > 0)
    if has_ppf:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state["ppf_value"] = st.number_input(
                "PPF balance today (₹)",
                min_value=0, value=st.session_state["ppf_value"], step=10000, format="%d"
            )
        with col2:
            st.session_state["ppf_contributing"] = st.radio(
                "Are you putting money in every year?",
                ["Yes, contributing", "No, just holding"],
                key="ppf_contrib"
            ) == "Yes, contributing"
    else:
        st.session_state["ppf_value"] = 0

    # ── EPF ───────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">EPF (Employee Provident Fund)</p>', unsafe_allow_html=True)
    st.markdown('<p class="skip-note">Your company deducts PF from salary and saves it for you. You can check the balance on the EPFO app.</p>', unsafe_allow_html=True)
    has_epf = st.checkbox("I have an EPF/PF account", value=st.session_state["epf_value"] > 0)
    if has_epf:
        st.session_state["epf_value"] = st.number_input(
            "EPF balance today (₹)  *(check EPFO Umang app or ask HR)*",
            min_value=0, value=st.session_state["epf_value"], step=10000, format="%d"
        )
    else:
        st.session_state["epf_value"] = 0

    # ── NPS ───────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">NPS (National Pension System)</p>', unsafe_allow_html=True)
    st.markdown('<p class="skip-note">A retirement savings account — check NPS CRA website or ask HR if your employer contributes.</p>', unsafe_allow_html=True)
    has_nps = st.checkbox("I have an NPS account", value=st.session_state["nps_value"] > 0)
    if has_nps:
        st.session_state["nps_value"] = st.number_input(
            "NPS balance today (₹)",
            min_value=0, value=st.session_state["nps_value"], step=10000, format="%d"
        )
    else:
        st.session_state["nps_value"] = 0

    # ── FD ────────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">Fixed Deposits (FDs)</p>', unsafe_allow_html=True)
    has_fd = st.checkbox("I have Fixed Deposits in a bank", value=st.session_state["fd_value"] > 0)
    if has_fd:
        st.session_state["fd_value"] = st.number_input(
            "Total FD value today (₹)",
            min_value=0, value=st.session_state["fd_value"], step=10000, format="%d"
        )
    else:
        st.session_state["fd_value"] = 0

    # ── Gold ──────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">Gold</p>', unsafe_allow_html=True)
    st.markdown('<p class="skip-note">Include physical gold jewellery (at market rate), Sovereign Gold Bonds (SGBs), or Gold ETFs</p>', unsafe_allow_html=True)
    has_gold = st.checkbox("I own gold (jewellery, SGB, or Gold ETF)",
                           value=st.session_state["gold_value"] > 0)
    if has_gold:
        st.session_state["gold_value"] = st.number_input(
            "Approximate total gold value today (₹)",
            min_value=0, value=st.session_state["gold_value"], step=5000, format="%d"
        )
    else:
        st.session_state["gold_value"] = 0

    # ── RBI Bonds ─────────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">RBI Government Bonds</p>', unsafe_allow_html=True)
    st.markdown('<p class="skip-note">7-year bonds issued by RBI. Earns 8.05% and pays interest every 6 months to your bank. Most people don\'t have these — skip if unsure.</p>', unsafe_allow_html=True)
    has_rbi = st.checkbox("I have RBI Floating Rate Bonds",
                          value=st.session_state["rbi_bond_value"] > 0)
    if has_rbi:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state["rbi_bond_value"] = st.number_input(
                "Amount invested in RBI Bonds (₹)",
                min_value=0, value=st.session_state["rbi_bond_value"],
                step=10000, format="%d"
            )
        with col2:
            import datetime
            invest_date = st.date_input(
                "When did you buy them?",
                value=datetime.date(2021, 5, 25),
                min_value=datetime.date(2020, 7, 1)
            )
            maturity = invest_date.replace(year=invest_date.year + 7)
            months_left = max(0, (maturity - datetime.date.today()).days // 30)
            st.session_state["rbi_bond_months_left"] = months_left
            st.caption(f"Matures: {maturity.strftime('%b %Y')} ({months_left} months away)")
    else:
        st.session_state["rbi_bond_value"] = 0
        st.session_state["rbi_bond_months_left"] = 0

    # ── Emergency fund ────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">Emergency savings</p>', unsafe_allow_html=True)
    st.markdown('<p class="skip-note">Money kept specifically for emergencies — separate from investments, easily accessible</p>', unsafe_allow_html=True)
    st.session_state["has_emergency_fund"] = st.radio(
        "Do you have money set aside for emergencies?",
        ["No, I don't have a dedicated emergency fund",
         "Yes, I have emergency savings"],
        key="ef_radio"
    ) == "Yes, I have emergency savings"

    if st.session_state["has_emergency_fund"]:
        st.session_state["emergency_fund_value"] = st.number_input(
            "How much is in your emergency fund? (₹)",
            min_value=0, value=st.session_state.get("emergency_fund_value", 0),
            step=10000, format="%d"
        )
    else:
        st.session_state["emergency_fund_value"] = 0
        monthly_expenses = st.session_state["monthly_expenses"] + st.session_state["family_support_annual"] / 12
        st.markdown(f'<div class="warn-box">⚠️ No emergency fund. If you lose your job tomorrow, you have no safety net. Your plan will fix this first — you need about <b>₹{monthly_expenses*6:,.0f}</b> (6 months of expenses) in a liquid fund.</div>', unsafe_allow_html=True)

    # Net worth summary
    st.divider()
    total_assets = (st.session_state["mf_value"] + st.session_state["stocks_value"] +
                    st.session_state["ppf_value"] + st.session_state["epf_value"] +
                    st.session_state["nps_value"] + st.session_state["fd_value"] +
                    st.session_state["gold_value"] + st.session_state["rbi_bond_value"] +
                    st.session_state.get("emergency_fund_value", 0))
    net_worth = total_assets - st.session_state["loans_outstanding"]

    if total_assets > 0:
        col1, col2 = st.columns(2)
        col1.metric("Total assets", f"₹{total_assets/1e5:.1f}L")
        col2.metric("Net worth (assets − loans)", f"₹{net_worth/1e5:.1f}L",
                    delta_color="normal" if net_worth >= 0 else "inverse")

    st.divider()
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Back", use_container_width=True):
            st.session_state["step"] = 2
            st.rerun()
    with col_c:
        if st.button("Next →", type="primary", use_container_width=True):
            st.session_state["step"] = 4
            st.rerun()
