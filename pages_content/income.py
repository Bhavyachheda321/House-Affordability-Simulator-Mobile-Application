import streamlit as st

def render():
    st.title("💰 Income & Expenses")
    st.caption("Your monthly cashflow — the foundation of the plan")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Salary & income")
        st.session_state["net_take_home"] = st.number_input(
            "Net take home salary / month (₹)  *(after EPF, tax deductions)*",
            min_value=0, value=st.session_state["net_take_home"],
            step=1000, format="%d")

        st.session_state["annual_bonus"] = st.number_input(
            "Annual bonus / variable pay (₹)  *(total per year)*",
            min_value=0, value=st.session_state["annual_bonus"],
            step=10000, format="%d")

        st.session_state["salary_growth_pct"] = st.slider(
            "Expected annual salary growth (%)",
            min_value=3.0, max_value=20.0,
            value=st.session_state["salary_growth_pct"], step=0.5)

        st.session_state["employer_nps_monthly"] = st.number_input(
            "Employer NPS contribution / month (₹)  *(Sec 80CCD(2), 0 if none)*",
            min_value=0, value=st.session_state["employer_nps_monthly"],
            step=500, format="%d")

        st.session_state["epf_monthly"] = st.number_input(
            "Your EPF deduction / month (₹)  *(already deducted from take home)*",
            min_value=0, value=st.session_state["epf_monthly"],
            step=500, format="%d")

    with col2:
        st.markdown("#### Monthly expenses")
        st.session_state["monthly_expenses"] = st.number_input(
            "Personal monthly expenses (₹)  *(food, transport, subscriptions, etc.)*",
            min_value=0, value=st.session_state["monthly_expenses"],
            step=1000, format="%d")

        st.session_state["family_contribution_annual"] = st.number_input(
            "Annual contribution to family (₹)  *(parents/siblings support)*",
            min_value=0, value=st.session_state["family_contribution_annual"],
            step=10000, format="%d")

        if st.session_state["marital_status"] == "Single":
            st.session_state["post_marriage_expenses"] = st.number_input(
                "Expected post-marriage monthly expenses (₹)",
                min_value=0, value=st.session_state["post_marriage_expenses"],
                step=1000, format="%d",
                help="Estimated combined household spending after marriage")

        st.session_state["lifestyle_inflation"] = st.slider(
            "Lifestyle / education inflation (%)",
            min_value=4.0, max_value=12.0,
            value=st.session_state["lifestyle_inflation"], step=0.5,
            help="Mumbai: 8%, Other metros: 6-7%, Smaller cities: 5-6%")

    st.divider()
    st.markdown("#### 📈 Current SIPs & recurring investments")
    st.caption("Add each SIP you currently run. You can edit them after adding.")

    if "sips" not in st.session_state or st.session_state["sips"] is None:
        st.session_state["sips"] = []

    # Add SIP form
    with st.expander("➕ Add a SIP / recurring investment", expanded=len(st.session_state["sips"]) == 0):
        sc1, sc2, sc3, sc4 = st.columns([3, 2, 2, 1])
        with sc1:
            new_fund = st.text_input("Fund / instrument name", key="new_fund_name",
                                     placeholder="e.g. Nifty 50 Index Fund")
        with sc2:
            new_cat = st.selectbox("Category", [
                "Large cap index", "Next 50 index", "Midcap index",
                "Smallcap index", "Flexi/multi cap", "ELSS",
                "Arbitrage", "Liquid / debt", "Gold ETF/SGB",
                "International", "Other"
            ], key="new_fund_cat")
        with sc3:
            new_amt = st.number_input("Monthly amount (₹)", min_value=0,
                                      value=0, step=500, format="%d", key="new_fund_amt")
        with sc4:
            st.write("")
            st.write("")
            if st.button("Add", type="primary", key="add_sip_btn"):
                if new_fund and new_amt > 0:
                    st.session_state["sips"].append({
                        "fund": new_fund,
                        "category": new_cat,
                        "monthly": new_amt,
                    })
                    st.rerun()

    if st.session_state["sips"]:
        st.markdown("**Current SIPs:**")
        to_remove = []
        for i, sip in enumerate(st.session_state["sips"]):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
            with c1:
                st.text(sip["fund"])
            with c2:
                st.caption(sip["category"])
            with c3:
                new_val = st.number_input(f"₹/mo", value=sip["monthly"],
                                          step=500, format="%d",
                                          key=f"sip_amt_{i}", label_visibility="collapsed")
                st.session_state["sips"][i]["monthly"] = new_val
            with c4:
                if st.button("🗑", key=f"del_sip_{i}"):
                    to_remove.append(i)
        for idx in reversed(to_remove):
            st.session_state["sips"].pop(idx)
        if to_remove:
            st.rerun()

        total_sip = sum(s["monthly"] for s in st.session_state["sips"])
        st.info(f"**Total monthly SIP: ₹{total_sip:,.0f}**")

    st.divider()

    # Live cashflow summary
    st.markdown("#### 📊 Live cashflow snapshot")
    income = st.session_state["net_take_home"] + st.session_state["annual_bonus"] / 12
    total_sips = sum(s["monthly"] for s in st.session_state["sips"])
    family = st.session_state["family_contribution_annual"] / 12
    expenses = st.session_state["monthly_expenses"]
    surplus = income - expenses - family - total_sips

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Monthly income", f"₹{income:,.0f}")
    col_m2.metric("Expenses + family", f"₹{expenses + family:,.0f}")
    col_m3.metric("Total SIPs", f"₹{total_sips:,.0f}")
    col_m4.metric("Undeployed surplus",
                  f"₹{surplus:,.0f}",
                  delta="Invest this!" if surplus > 0 else "Overextended",
                  delta_color="normal" if surplus > 0 else "inverse")

    if surplus < 0:
        st.error("⚠️ Your expenses + SIPs exceed your income. Reduce SIPs or expenses before proceeding.")
    elif surplus > 0:
        st.success(f"✅ You have ₹{surplus:,.0f}/month undeployed. The plan will suggest how to use it.")

    st.divider()
    cb1, cb2 = st.columns([3, 1])
    with cb2:
        if st.button("Next: Assets & Liabilities →", type="primary", use_container_width=True):
            st.session_state["income_done"] = True
            st.session_state["page"] = "assets"
            st.rerun()
