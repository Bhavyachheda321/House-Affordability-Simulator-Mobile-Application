"""FinPlan India v4 — Step 4: Assets & Investments
EPF is entered here (not Income page) with External Funding = True
so it's never double-counted against surplus.
"""
import streamlit as st


def render():
    s = st.session_state

    st.markdown("#### 📂 Your Current Savings & Investments")
    st.caption(
        "Enter your current balance in each bucket. Enter 0 if you don't have it. "
        "These grow year-by-year in the simulation."
    )

    # ── Equity ────────────────────────────────────────────────────────────────
    st.markdown("##### 📈 Equity")
    col1, col2 = st.columns(2)
    with col1:
        s["mf_value"] = st.number_input(
            "Mutual funds — current value (₹)", min_value=0,
            value=int(s.get("mf_value", 0)), step=10000, format="%d",
            help="Total value across all MF folios today. Check Groww / Zerodha / CAMS.",
        )
    with col2:
        s["stocks_value"] = st.number_input(
            "Stocks / direct equity — current value (₹)", min_value=0,
            value=int(s.get("stocks_value", 0)), step=10000, format="%d",
            help="Current market value of your equity portfolio.",
        )

    st.divider()

    # ── SIPs ─────────────────────────────────────────────────────────────────
    st.markdown("##### 💸 Monthly SIPs")
    col3, col4 = st.columns(2)
    with col3:
        s["sip_total_monthly"] = st.number_input(
            "Total monthly SIPs (₹)",
            min_value=0,
            value=int(s.get("sip_total_monthly", 0)),
            step=500, format="%d",
            help="Sum of all running SIPs across all funds and platforms.",
        )
    with col4:
        s["sip_stepup_pct"] = st.number_input(
            "SIP step-up every April (%/yr)",
            min_value=0.0, max_value=50.0,
            value=float(s.get("sip_stepup_pct", 10.0)),
            step=1.0, format="%.0f",
            help="Increase SIPs by this % every April. 10% is the default recommendation.",
        )

    st.divider()

    # ── EPF — External Funding ────────────────────────────────────────────────
    st.markdown("##### 🏦 EPF (Provident Fund)")
    st.markdown(
        '<div class="tip-box">'
        "💡 <strong>EPF is funded externally</strong> — your employer deducts it before "
        "the salary reaches you, so it never touches your monthly surplus. "
        "We model only the <em>employee share</em> going to your EPF corpus "
        "(the employer's 8.33% EPS portion has no lump-sum at retirement for most employees)."
        "<br>Find your balance: <strong>umang.gov.in → EPFO → Passbook</strong> or "
        "<strong>epfindia.gov.in</strong></div>",
        unsafe_allow_html=True,
    )
    col5, col6 = st.columns(2)
    with col5:
        has_epf = st.radio(
            "Does your employer deduct PF?",
            ["No / Not applicable", "Yes"],
            index=1 if s.get("epf_monthly", 0) > 0 or s.get("epf_value", 0) > 0 else 0,
            horizontal=True,
        )
    if has_epf == "Yes":
        c1, c2 = st.columns(2)
        with c1:
            s["epf_monthly"] = st.number_input(
                "Employee PF deduction per month (₹)",
                min_value=0,
                value=int(s.get("epf_monthly", 0)),
                step=500, format="%d",
                help=(
                    "The 'PF' line on your payslip — this is your (employee) share only. "
                    "Typically 12% of basic salary."
                ),
            )
        with c2:
            s["epf_value"] = st.number_input(
                "Current EPF balance (₹)",
                min_value=0,
                value=int(s.get("epf_value", 0)),
                step=10000, format="%d",
                help="Check on umang.gov.in or epfindia.gov.in → Member Passbook.",
            )
    else:
        s["epf_monthly"] = 0
        s["epf_value"]   = 0

    st.divider()

    # ── Tax-advantaged ────────────────────────────────────────────────────────
    st.markdown("##### 🏛 Tax-Advantaged Accounts")
    col7, col8 = st.columns(2)
    with col7:
        s["ppf_value"] = st.number_input(
            "PPF balance (₹)", min_value=0,
            value=int(s.get("ppf_value", 0)), step=10000, format="%d",
            help="Public Provident Fund balance. EEE — fully tax-free.",
        )
        s["ppf_contributing"] = st.checkbox(
            "I contribute ₹1,50,000/year to PPF",
            value=s.get("ppf_contributing", True),
            help="Tick if you deposit into PPF each year. Best done on April 1 for full interest.",
        )
    with col8:
        s["nps_value"] = st.number_input(
            "NPS balance (₹)", min_value=0,
            value=int(s.get("nps_value", 0)), step=10000, format="%d",
            help="NPS Tier-1 balance. At retirement: 60% tax-free lump sum, 40% goes to annuity.",
        )

    st.divider()

    # ── Other assets ──────────────────────────────────────────────────────────
    st.markdown("##### 🥇 Other Assets")
    col9, col10 = st.columns(2)
    with col9:
        s["gold_value"] = st.number_input(
            "Gold — current value (₹)", min_value=0,
            value=int(s.get("gold_value", 0)), step=5000, format="%d",
            help="Physical gold + SGBs + Gold ETFs. Use today's market value.",
        )
        s["fd_value"] = st.number_input(
            "Fixed Deposits — total (₹)", min_value=0,
            value=int(s.get("fd_value", 0)), step=10000, format="%d",
            help="Sum of all FDs across banks. Interest is taxed at slab rate.",
        )
    with col10:
        s["has_emergency_fund"] = st.checkbox(
            "I have a separate emergency fund",
            value=s.get("has_emergency_fund", False),
        )
        if s["has_emergency_fund"]:
            s["emergency_fund_value"] = st.number_input(
                "Emergency fund value (₹)", min_value=0,
                value=int(s.get("emergency_fund_value", 0)), step=5000, format="%d",
                help="Kept in liquid fund or savings account. Target: 6 months of expenses.",
            )
        else:
            s["emergency_fund_value"] = 0

    # ── Net worth summary ──────────────────────────────────────────────────────
    total = (
        s.get("mf_value", 0) + s.get("stocks_value", 0)
        + s.get("ppf_value", 0) + s.get("epf_value", 0)
        + s.get("nps_value", 0) + s.get("gold_value", 0)
        + s.get("fd_value", 0) + s.get("emergency_fund_value", 0)
    )
    loans = s.get("loans_outstanding", 0)
    net   = total - loans

    col_nw1, col_nw2, col_nw3 = st.columns(3)
    col_nw1.metric("Total Assets", f"₹{total:,.0f}")
    col_nw2.metric("Loans Outstanding", f"₹{loans:,.0f}")
    col_nw3.metric("Net Worth", f"₹{net:,.0f}")

    # ── Nav ───────────────────────────────────────────────────────────────────
    st.divider()
    col_a, _, col_b = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Back", use_container_width=True):
            s["step"] = 3
            st.rerun()
    with col_b:
        if st.button("Next →", type="primary", use_container_width=True):
            s["step"] = 5
            st.rerun()
