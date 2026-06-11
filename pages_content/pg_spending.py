import streamlit as st

def render():
    st.title("🛒 Your monthly spending")
    st.write("Be honest here — this is the most important page. Underestimating expenses is the #1 reason financial plans fail.")

    sal = st.session_state["monthly_salary"]

    # Smart default for expenses based on city
    city_expense_pct = {"Mumbai": 0.22, "Delhi NCR": 0.20, "Bengaluru": 0.20,
                        "Pune": 0.18, "Hyderabad": 0.18, "Chennai": 0.17,
                        "Kolkata": 0.16, "Other": 0.18}
    default_exp = int(sal * city_expense_pct.get(st.session_state["city"], 0.20))
    if st.session_state["monthly_expenses"] == 0 and default_exp > 0:
        st.session_state["monthly_expenses"] = default_exp

    st.markdown("#### What do you spend every month?")
    st.markdown('<p class="skip-note">Include food, transport, phone, subscriptions, clothes, eating out, petrol, gym, everything</p>', unsafe_allow_html=True)

    st.session_state["monthly_expenses"] = st.number_input(
        "My personal monthly expenses (₹)",
        min_value=0, value=st.session_state["monthly_expenses"],
        step=1000, format="%d"
    )

    if sal > 0 and st.session_state["monthly_expenses"] > 0:
        pct = st.session_state["monthly_expenses"] / sal * 100
        if pct < 15:
            st.markdown('<div class="warn-box">⚠️ This seems low. Most professionals in your city spend 20–35% of salary on personal expenses. Double-check — a wrong number here will make the whole plan unreliable.</div>', unsafe_allow_html=True)
        elif pct > 60:
            st.markdown('<div class="warn-box">⚠️ Spending 60%+ of take-home on personal expenses leaves very little to invest. The plan will show you how to fix this.</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Do you support your family financially?")
    family_support = st.radio("Do you give money to parents or siblings regularly?",
        ["No", "Yes"])
    if family_support == "Yes":
        st.session_state["family_support_annual"] = st.number_input(
            "How much do you give them per year? (₹)",
            min_value=0, value=st.session_state["family_support_annual"],
            step=10000, format="%d",
            help="e.g. if you give ₹15,000/month, enter 1,80,000"
        )
    else:
        st.session_state["family_support_annual"] = 0

    st.divider()
    st.markdown("#### Do you invest via SIP or mutual funds?")
    st.markdown('<p class="skip-note">SIP = a fixed amount auto-deducted from your bank every month into mutual funds</p>', unsafe_allow_html=True)

    has_sip = st.radio("Are you already running any SIPs or recurring investments?",
        ["No, not yet", "Yes, I invest monthly"])
    if has_sip == "Yes, I invest monthly":
        st.session_state["sip_total_monthly"] = st.number_input(
            "Total amount invested per month across all SIPs and mutual funds (₹)",
            min_value=0, value=st.session_state["sip_total_monthly"],
            step=500, format="%d"
        )
        st.markdown('<div class="tip-box">💡 Check your Groww, Zerodha, or CAMS app to see your total monthly SIP amount.</div>', unsafe_allow_html=True)
    else:
        st.session_state["sip_total_monthly"] = 0

    st.divider()
    st.markdown("#### Any existing loan EMIs?")
    has_loan = st.radio("Do you have any loans running right now?",
        ["No loans at all", "Yes, I have EMIs"])
    if has_loan == "Yes, I have EMIs":
        col1, col2 = st.columns(2)
        with col1:
            st.session_state["loan_emi_monthly"] = st.number_input(
                "Total EMIs per month (₹)",
                min_value=0, value=st.session_state["loan_emi_monthly"],
                step=500, format="%d"
            )
        with col2:
            st.session_state["loans_outstanding"] = st.number_input(
                "Total loan amount still pending (₹)",
                min_value=0, value=st.session_state["loans_outstanding"],
                step=10000, format="%d"
            )
    else:
        st.session_state["loan_emi_monthly"] = 0
        st.session_state["loans_outstanding"] = 0

    # Live surplus display
    if sal > 0:
        st.divider()
        monthly_income = sal + st.session_state["annual_bonus"] / 12
        total_out = (st.session_state["monthly_expenses"] +
                     st.session_state["family_support_annual"] / 12 +
                     st.session_state["sip_total_monthly"] +
                     st.session_state["loan_emi_monthly"])
        surplus = monthly_income - total_out

        col1, col2, col3 = st.columns(3)
        col1.metric("Monthly income", f"₹{monthly_income:,.0f}")
        col2.metric("Total going out", f"₹{total_out:,.0f}")
        col3.metric("Left over", f"₹{max(0,surplus):,.0f}",
                    delta="to invest!" if surplus > 0 else "overspent",
                    delta_color="normal" if surplus > 0 else "inverse")

        if surplus < 0:
            st.error("⚠️ Your outflows exceed your income. Please check your numbers — something doesn't add up.")
        elif surplus > 0:
            st.markdown(f'<div class="ok-box">You have <b>₹{surplus:,.0f}/month</b> that isn\'t going anywhere yet. Your plan will put this to work.</div>', unsafe_allow_html=True)

    st.divider()
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Back", use_container_width=True):
            st.session_state["step"] = 1
            st.rerun()
    with col_c:
        if st.button("Next →", type="primary", use_container_width=True):
            st.session_state["step"] = 3
            st.rerun()
