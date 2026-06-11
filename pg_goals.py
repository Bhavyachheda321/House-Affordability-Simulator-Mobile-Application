import streamlit as st

def render():
    st.title("🎯 What are you saving for?")
    st.write("Pick your goals. You can have more than one — we'll prioritise them for you.")

    infl = st.session_state["lifestyle_inflation"] / 100

    # ── Retirement ────────────────────────────────────────────────────────────
    st.markdown("#### 🏖 When do you want to stop working?")
    st.session_state["retirement_age"] = st.select_slider(
        "I want to retire (or become financially free) at age",
        options=[45, 48, 50, 52, 55, 58, 60, 65],
        value=st.session_state["retirement_age"]
    )
    years_left = st.session_state["retirement_age"] - st.session_state["age"]
    st.caption(f"That's {years_left} years from now.")

    st.markdown("#### How much do you want to spend each month after you retire?")
    st.markdown('<p class="skip-note">Think about your comfortable lifestyle today — this is in today\'s money, not future money.</p>', unsafe_allow_html=True)
    st.session_state["retirement_monthly_spend"] = st.select_slider(
        "Monthly lifestyle after retirement (₹, today's value)",
        options=[50000, 75000, 100000, 125000, 150000, 200000, 250000, 300000],
        value=st.session_state["retirement_monthly_spend"],
        format_func=lambda x: f"₹{x:,.0f}/month"
    )

    future_monthly = st.session_state["retirement_monthly_spend"] * (1 + infl) ** years_left
    corpus_needed = (future_monthly * 12) / 0.045
    st.markdown(
        f'<div class="tip-box">With {st.session_state["lifestyle_inflation"]}% yearly price rises in {st.session_state["city"]}, '
        f'₹{st.session_state["retirement_monthly_spend"]:,.0f}/month today will become '
        f'<b>₹{future_monthly:,.0f}/month</b> when you retire. '
        f'To fund that comfortably, you need a corpus of approximately '
        f'<b>₹{corpus_needed/1e7:.1f} Crore</b>.</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # ── House ─────────────────────────────────────────────────────────────────
    st.markdown("#### 🏠 Do you want to buy a home?")
    st.session_state["want_house"] = st.radio(
        "Home purchase goal",
        ["Yes, buying a home is important to me", "No, I'm happy renting"],
        key="house_radio"
    ) == "Yes, buying a home is important to me"

    if st.session_state["want_house"]:
        st.session_state["house_budget"] = st.number_input(
            "What is your approximate budget for the home? (₹, today's prices)",
            min_value=0, value=st.session_state["house_budget"],
            step=500000, format="%d",
            help="e.g. 3,50,00,000 for a ₹3.5 Crore flat"
        )
        if st.session_state["house_budget"] > 0:
            parents_help = st.radio(
                "Will family / parents help financially with the home?",
                ["No family contribution", "Yes, they will contribute"]
            )
            if parents_help == "Yes, they will contribute":
                st.session_state["parents_house_contribution"] = st.number_input(
                    "How much will family contribute? (₹)",
                    min_value=0,
                    value=st.session_state["parents_house_contribution"],
                    step=500000, format="%d"
                )
            else:
                st.session_state["parents_house_contribution"] = 0

    st.divider()

    # ── Marriage ──────────────────────────────────────────────────────────────
    if not st.session_state["married"]:
        st.markdown("#### 💍 Are you planning for marriage expenses?")
        st.session_state["want_marriage_savings"] = st.radio(
            "Marriage savings goal",
            ["No, not planning for this now",
             "Yes, I want to save for my wedding"],
            key="marr_radio"
        ) == "Yes, I want to save for my wedding"

        if st.session_state["want_marriage_savings"]:
            col1, col2 = st.columns(2)
            with col1:
                st.session_state["marriage_cost"] = st.number_input(
                    "Estimated wedding cost (₹, today's prices)",
                    min_value=0, value=st.session_state["marriage_cost"],
                    step=100000, format="%d"
                )
            with col2:
                st.session_state["marriage_years"] = st.number_input(
                    "In how many years?",
                    min_value=0, max_value=10,
                    value=st.session_state["marriage_years"], step=1
                )
                if st.session_state["marriage_cost"] > 0:
                    fv = st.session_state["marriage_cost"] * (1 + infl) ** st.session_state["marriage_years"]
                    st.caption(f"Will cost ~₹{fv/1e5:.1f}L by then (at {st.session_state['lifestyle_inflation']}% inflation)")
        st.divider()

    # ── Child education ───────────────────────────────────────────────────────
    st.markdown("#### 🎓 Do you want to save for a child's education?")
    st.session_state["want_child_education"] = st.radio(
        "Child education goal",
        ["No / not applicable",
         "Yes, I want to build an education fund"],
        key="edu_radio"
    ) == "Yes, I want to build an education fund"

    if st.session_state["want_child_education"]:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state["child_education_cost"] = st.number_input(
                "Estimated education cost (₹, today's prices)",
                min_value=0,
                value=st.session_state.get("child_education_cost", 2500000),
                step=100000, format="%d",
                help="Good engineering/medical/MBA: ₹20–50L today"
            )
        with col2:
            st.session_state["child_education_years"] = st.number_input(
                "In how many years will they need the money?",
                min_value=3, max_value=25,
                value=st.session_state.get("child_education_years", 18), step=1
            )

    st.divider()
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Back", use_container_width=True):
            st.session_state["step"] = 3
            st.rerun()
    with col_c:
        if st.button("Show my plan →", type="primary", use_container_width=True):
            st.session_state["step"] = 5
            st.rerun()
