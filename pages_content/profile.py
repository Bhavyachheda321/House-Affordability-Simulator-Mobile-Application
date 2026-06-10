import streamlit as st

def render():
    st.title("👤 Your Profile")
    st.caption("Basic information to personalise your plan")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Personal details")
        st.session_state["age"] = st.number_input(
            "Your current age", min_value=18, max_value=70,
            value=st.session_state["age"], step=1)

        st.session_state["city"] = st.selectbox(
            "City", ["Mumbai", "Delhi NCR", "Bengaluru", "Pune",
                     "Hyderabad", "Chennai", "Kolkata", "Other"],
            index=["Mumbai", "Delhi NCR", "Bengaluru", "Pune",
                   "Hyderabad", "Chennai", "Kolkata", "Other"].index(
                st.session_state["city"]))

        st.session_state["marital_status"] = st.selectbox(
            "Marital status", ["Single", "Married", "Divorced", "Widowed"],
            index=["Single", "Married", "Divorced", "Widowed"].index(
                st.session_state["marital_status"]))

        st.session_state["has_kids"] = st.checkbox(
            "I have children", value=st.session_state["has_kids"])
        if st.session_state["has_kids"]:
            st.session_state["num_kids"] = st.number_input(
                "Number of children", min_value=1, max_value=5,
                value=max(st.session_state["num_kids"], 1), step=1)

    with col2:
        st.markdown("#### Living situation")
        st.session_state["living_situation"] = st.selectbox(
            "Current living situation",
            ["With parents (no rent)",
             "Renting",
             "Own home (no EMI)",
             "Own home (with EMI)"],
            index=["With parents (no rent)", "Renting",
                   "Own home (no EMI)", "Own home (with EMI)"].index(
                st.session_state["living_situation"]))

        if st.session_state["living_situation"] == "Renting":
            st.session_state["monthly_rent"] = st.number_input(
                "Monthly rent (₹)", min_value=0,
                value=st.session_state.get("monthly_rent", 0),
                step=1000, format="%d")
        elif st.session_state["living_situation"] == "Own home (with EMI)":
            st.session_state["home_emi"] = st.number_input(
                "Home loan EMI (₹/month)", min_value=0,
                value=st.session_state.get("home_emi", 0),
                step=1000, format="%d")
            st.session_state["home_loan_outstanding"] = st.number_input(
                "Loan outstanding (₹)", min_value=0,
                value=st.session_state.get("home_loan_outstanding", 0),
                step=100000, format="%d")

        st.markdown("#### Tax filing")
        st.session_state["tax_regime"] = st.selectbox(
            "Tax regime",
            ["New regime", "Old regime"],
            index=0 if st.session_state.get("tax_regime", "New regime") == "New regime" else 1)

        st.session_state["annual_income_bracket"] = st.selectbox(
            "Annual taxable income bracket",
            ["Up to ₹12L (no tax)", "₹12L–₹20L (10–15%)",
             "₹20L–₹50L (20–30%)", "₹50L–₹1Cr (30% + 10% surcharge)",
             "Above ₹1Cr (30% + 15% surcharge)"],
            index=3)

    st.divider()

    # derive effective tax rate
    bracket_rates = {
        "Up to ₹12L (no tax)": 0.0,
        "₹12L–₹20L (10–15%)": 0.1456,  # ~14% avg + cess
        "₹20L–₹50L (20–30%)": 0.2288,  # ~22% avg + cess
        "₹50L–₹1Cr (30% + 10% surcharge)": 0.3432,
        "Above ₹1Cr (30% + 15% surcharge)": 0.3588,
    }
    st.session_state["effective_slab_rate"] = bracket_rates[
        st.session_state["annual_income_bracket"]]

    # property appreciation by city
    city_appreciation = {
        "Mumbai": 7.0, "Delhi NCR": 6.0, "Bengaluru": 8.0,
        "Pune": 7.0, "Hyderabad": 7.5, "Chennai": 5.5,
        "Kolkata": 5.0, "Other": 6.0,
    }
    st.session_state["property_appreciation"] = city_appreciation[
        st.session_state["city"]]

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("Years to standard retirement (60)", 60 - st.session_state["age"])
    with col_info2:
        slab = st.session_state["effective_slab_rate"]
        st.metric("Effective tax rate (incl. cess)", f"{slab*100:.1f}%")
    with col_info3:
        st.metric("Assumed property appreciation", f"{st.session_state['property_appreciation']:.1f}% p.a.")

    st.divider()
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn2:
        if st.button("Next: Income & Expenses →", type="primary", use_container_width=True):
            st.session_state["profile_done"] = True
            st.session_state["page"] = "income"
            st.rerun()
