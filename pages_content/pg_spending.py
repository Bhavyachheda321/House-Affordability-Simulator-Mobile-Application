"""FinPlan India v4 — Step 3: Spending"""
import streamlit as st


def render():
    s = st.session_state
    sal = s.get("monthly_salary", 0)

    st.markdown("#### 🛒 Monthly Spending")
    st.caption("How much you spend each month. Be honest — this drives your entire surplus calculation.")

    col1, col2 = st.columns(2)
    with col1:
        s["monthly_expenses"] = st.number_input(
            "Monthly expenses — excluding rent (₹)",
            min_value=0,
            value=int(s.get("monthly_expenses", 0)),
            step=1000, format="%d",
            help=(
                "All monthly costs: groceries, utilities, transport, subscriptions, "
                "dining, clothes, personal care. EXCLUDE rent — that's below."
            ),
            placeholder=f"e.g. {int(sal * 0.45):,}" if sal > 0 else "e.g. 35000",
        )
        if sal > 0 and s.get("monthly_expenses", 0) > 0:
            exp_pct = s["monthly_expenses"] / sal * 100
            colour  = "#3B6D11" if exp_pct < 50 else "#EF9F27" if exp_pct < 65 else "#A32D2D"
            st.markdown(
                f'<span style="font-size:.82rem;color:{colour};font-weight:600;">'
                f"{exp_pct:.0f}% of take-home on expenses</span>",
                unsafe_allow_html=True,
            )

    with col2:
        s["expense_inflation"] = st.number_input(
            "Expense inflation (%/yr)",
            min_value=0.0, max_value=20.0,
            value=float(s.get("expense_inflation", 6.0)),
            step=0.5, format="%.1f",
            help="How fast your living costs rise. Typically 5–7% for urban India.",
        )

    st.divider()
    st.markdown("#### 🏠 Rent")

    col3, col4 = st.columns(2)
    with col3:
        living = s.get("living_situation", "With parents (no rent)")
        rent_disabled = living == "With parents (no rent)" or living == "I own my home"

        if rent_disabled:
            st.number_input(
                "Monthly rent (₹)", value=0, disabled=True,
                help="Not applicable — you're not renting.",
            )
            s["rent_monthly"] = 0
        else:
            s["rent_monthly"] = st.number_input(
                "Monthly rent (₹)",
                min_value=0,
                value=int(s.get("rent_monthly", 0)),
                step=500, format="%d",
                placeholder="e.g. 25000",
            )
    with col4:
        s["rent_inflation"] = st.number_input(
            "Rent inflation (%/yr)",
            min_value=0.0, max_value=20.0,
            value=float(s.get("rent_inflation", 8.0)),
            step=0.5, format="%.1f",
            help="Rental contracts in Indian cities typically escalate 8–10% per year.",
        )

    # ── Family support ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 👨‍👩‍👦 Family Support")
    st.caption("Money you send to parents or dependents — treated as a fixed annual outflow.")

    s["family_support_annual"] = st.number_input(
        "Annual family support (₹)  *(0 if none)*",
        min_value=0,
        value=int(s.get("family_support_annual", 0)),
        step=5000, format="%d",
        help="Total annual amount sent to parents or other dependents.",
    )

    # ── Surplus preview ────────────────────────────────────────────────────────
    if sal > 0:
        st.divider()
        exp     = s.get("monthly_expenses", 0)
        rent    = s.get("rent_monthly", 0)
        family  = s.get("family_support_annual", 0) / 12
        sip     = s.get("sip_total_monthly", 0)
        surplus = sal - exp - rent - family - sip
        col = "#3B6D11" if surplus > 0 else "#A32D2D"
        st.markdown(
            f'<div class="tip-box">'
            f"Monthly surplus (after expenses, rent, family): "
            f'<strong style="color:{col};">₹{surplus:,.0f}/mo</strong>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Nav ───────────────────────────────────────────────────────────────────
    st.divider()
    col_a, _, col_b = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Back", use_container_width=True):
            s["step"] = 2
            st.rerun()
    with col_b:
        if st.button("Next →", type="primary", use_container_width=True):
            s["step"] = 4
            st.rerun()
