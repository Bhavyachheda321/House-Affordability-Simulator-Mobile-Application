import streamlit as st

def render():
    st.title("👋 Welcome to FinPlan India")
    st.write("Answer a few simple questions and we'll build your personalised money plan in under 10 minutes.")

    st.markdown('<div class="tip-box">No jargon. No sign-up. No data stored anywhere. Everything stays on your screen.</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Tell us a little about yourself")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["age"] = st.number_input("How old are you?", 18, 65,
            st.session_state["age"], step=1)
    with col2:
        st.session_state["city"] = st.selectbox("Which city do you live in?",
            ["Mumbai", "Delhi NCR", "Bengaluru", "Pune", "Hyderabad",
             "Chennai", "Kolkata", "Other"],
            index=["Mumbai","Delhi NCR","Bengaluru","Pune","Hyderabad",
                   "Chennai","Kolkata","Other"].index(st.session_state["city"]))

    city_appr = {"Mumbai":7,"Delhi NCR":6,"Bengaluru":8,"Pune":7,
                 "Hyderabad":7.5,"Chennai":5.5,"Kolkata":5,"Other":6}
    st.session_state["property_appr_rate"] = city_appr[st.session_state["city"]]

    st.session_state["married"] = st.radio(
        "Are you married?", ["No, I'm single", "Yes, I'm married"],
        index=1 if st.session_state["married"] else 0
    ) == "Yes, I'm married"

    st.session_state["living_with_parents"] = st.radio(
        "Where do you currently live?",
        ["With my parents (paying no rent)", "I pay rent", "I own my home"],
        index=0 if st.session_state["living_with_parents"] else 1
    ) == "With my parents (paying no rent)"

    if st.session_state["living_with_parents"]:
        st.markdown('<div class="ok-box">Living with parents = saving ₹40,000–80,000/month in rent. This is a huge financial advantage — your plan will use this window to build wealth faster.</div>', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Tax bracket</p>', unsafe_allow_html=True)
    bracket = st.select_slider(
        "What is your approximate annual income?",
        options=["Under ₹7L", "₹7L–₹12L", "₹12L–₹20L", "₹20L–₹50L", "Above ₹50L"],
        value=st.session_state.get("bracket_label", "₹20L–₹50L")
    )
    st.session_state["bracket_label"] = bracket
    rates = {"Under ₹7L": 0.0, "₹7L–₹12L": 0.0,
             "₹12L–₹20L": 0.1456, "₹20L–₹50L": 0.2288,
             "Above ₹50L": 0.3432}
    st.session_state["effective_slab_rate"] = rates[bracket]

    infl_map = {"Mumbai": 8, "Delhi NCR": 7, "Bengaluru": 7,
                "Pune": 7, "Hyderabad": 7, "Chennai": 6,
                "Kolkata": 6, "Other": 6}
    st.session_state["lifestyle_inflation"] = infl_map[st.session_state["city"]]

    st.divider()
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("Next →", type="primary", use_container_width=True):
            st.session_state["step"] = 1
            st.rerun()
