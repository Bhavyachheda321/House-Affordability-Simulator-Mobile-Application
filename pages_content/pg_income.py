"""FinPlan India v4 — Step 2: Income"""
import streamlit as st


def render():
    s = st.session_state

    st.markdown("#### 💰 Your Income")
    st.markdown(
        '<div class="tip-box">💡 Use the amount <strong>credited to your bank</strong> each month '
        "— after PF, tax, and other deductions. Check your salary slip or bank statement.</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        s["monthly_salary"] = st.number_input(
            "Monthly take-home salary (₹)",
            min_value=0,
            value=int(s.get("monthly_salary", 0)),
            step=1000, format="%d",
            placeholder="e.g. 85000",
            help="What lands in your bank after all deductions (TDS, PF, etc.)",
        )
    with col2:
        s["annual_bonus"] = st.number_input(
            "Annual bonus / variable pay — net of tax (₹)  *(0 if none)*",
            min_value=0,
            value=int(s.get("annual_bonus", 0)),
            step=5000, format="%d",
            help="Total bonus received in a year after TDS. Enter 0 if none.",
        )

    col3, col4 = st.columns(2)
    with col3:
        s["salary_growth"] = st.select_slider(
            "Your expected annual salary growth",
            options=[3, 5, 6, 7, 8, 10, 12, 15],
            value=int(s.get("salary_growth", 8)),
            format_func=lambda x: f"{x}% per year",
            help="Realistic growth including promotions. Use 8–10% for most IT/finance roles.",
        )
    with col4:
        s["bonus_growth"] = st.select_slider(
            "Expected bonus growth rate",
            options=[0, 3, 5, 8, 10],
            value=int(s.get("bonus_growth", 5)),
            format_func=lambda x: f"{x}% per year",
        )

    # Projection preview
    sal = s.get("monthly_salary", 0)
    g   = s.get("salary_growth", 8) / 100
    if sal > 0:
        st.markdown(
            f'<div class="tip-box">At {s["salary_growth"]}% growth, your take-home will be approximately '
            f"<strong>₹{sal*(1+g)**3:,.0f}/mo in 3 years</strong> and "
            f"<strong>₹{sal*(1+g)**5:,.0f}/mo in 5 years</strong>.</div>",
            unsafe_allow_html=True,
        )

    # ── Gross income (for tax engine) ─────────────────────────────────────────
    st.divider()
    st.markdown("#### 🧾 Gross Income (for accurate tax calculation)")
    st.caption(
        "Optional but recommended. This lets us compute your actual tax each year "
        "as your salary grows, rather than using a flat estimate."
    )

    s["income_gross_monthly"] = st.number_input(
        "Monthly gross salary (₹) — your CTC/12 before any deduction  *(leave 0 to skip)*",
        min_value=0,
        value=int(s.get("income_gross_monthly", 0)),
        step=1000, format="%d",
        help="CTC divided by 12, or your gross salary from your offer letter.",
    )

    # ── Nav ───────────────────────────────────────────────────────────────────
    st.divider()
    col_a, _, col_b = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Back", use_container_width=True):
            s["step"] = 1
            st.rerun()
    with col_b:
        if st.button("Next →", type="primary", use_container_width=True):
            if s.get("monthly_salary", 0) == 0:
                st.error("Please enter your monthly take-home salary.")
            else:
                s["step"] = 3
                st.rerun()
