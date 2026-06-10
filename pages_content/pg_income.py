import streamlit as st

def render():
    st.title("💰 Your income")
    st.write("We only need your take-home number — what actually lands in your bank account each month.")

    st.markdown('<div class="tip-box">💡 <b>Where to find this:</b> Check your salary slip or your bank statement — look for the credit from your employer each month. That is your take-home salary.</div>', unsafe_allow_html=True)

    st.session_state["monthly_salary"] = st.number_input(
        "Monthly salary — money credited to your bank after all deductions (₹)",
        min_value=0, value=st.session_state["monthly_salary"],
        step=1000, format="%d",
        placeholder="e.g. 85000"
    )

    st.session_state["annual_bonus"] = st.number_input(
        "Annual bonus or variable pay — total received in a year (₹)   *(put 0 if none)*",
        min_value=0, value=st.session_state["annual_bonus"],
        step=5000, format="%d"
    )

    st.divider()
    st.markdown("#### Does your employer invest money for you?")
    st.write("Many companies automatically invest in EPF and NPS on your behalf. Check your salary slip.")

    col1, col2 = st.columns(2)
    with col1:
        knows_epf = st.radio("Do you know your EPF deduction?",
            ["No / not sure — skip", "Yes, I know the amount"], key="knows_epf")
        if knows_epf == "Yes, I know the amount":
            st.session_state["epf_monthly"] = st.number_input(
                "EPF deducted per month (₹)", min_value=0,
                value=st.session_state["epf_monthly"], step=500, format="%d")
            st.markdown('<p class="skip-note">This is usually shown as "PF" on your salary slip</p>',
                        unsafe_allow_html=True)
        else:
            st.session_state["epf_monthly"] = 0

    with col2:
        knows_nps = st.radio("Does your employer contribute to NPS?",
            ["No / not sure — skip", "Yes, I know the amount"], key="knows_nps")
        if knows_nps == "Yes, I know the amount":
            st.session_state["employer_nps_monthly"] = st.number_input(
                "Employer NPS per month (₹)", min_value=0,
                value=st.session_state["employer_nps_monthly"], step=500, format="%d")
        else:
            st.session_state["employer_nps_monthly"] = 0

    st.divider()
    st.markdown("#### How fast does your salary grow?")
    st.session_state["salary_growth"] = st.select_slider(
        "Expected annual salary growth",
        options=[3, 5, 6, 7, 8, 10, 12, 15],
        value=st.session_state["salary_growth"],
        format_func=lambda x: f"{x}% per year"
    )

    g = st.session_state["salary_growth"] / 100
    sal = st.session_state["monthly_salary"]
    if sal > 0:
        st.markdown('<div class="tip-box">'
            f'At {st.session_state["salary_growth"]}% growth, your take-home will be approximately '
            f'<b>₹{sal*(1+g)**3:,.0f}/mo in 3 years</b> and '
            f'<b>₹{sal*(1+g)**5:,.0f}/mo in 5 years</b>.</div>',
            unsafe_allow_html=True)

    st.divider()
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Back", use_container_width=True):
            st.session_state["step"] = 0
            st.rerun()
    with col_c:
        if st.button("Next →", type="primary", use_container_width=True):
            if st.session_state["monthly_salary"] == 0:
                st.error("Please enter your monthly salary to continue.")
            else:
                st.session_state["step"] = 2
                st.rerun()
