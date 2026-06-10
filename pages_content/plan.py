import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pages_content.calculations import (
    cashflow_analysis, projected_corpus_at_retirement,
    house_analysis, rent_vs_buy, sip_future_value,
    lumpsum_fv, sip_needed_for_goal, step_up_sip_fv,
    emi_amount, max_loan_for_emi, rbi_bond_net_payout,
    EQUITY_LONG_TERM_RETURN, ARBITRAGE_RETURN
)

COLORS = {
    "green": "#3B6D11", "green_light": "#EAF3DE",
    "amber": "#854F0B", "amber_light": "#FAEEDA",
    "red": "#A32D2D", "red_light": "#FCEBEB",
    "blue": "#185FA5", "blue_light": "#E6F1FB",
    "teal": "#0F6E56", "teal_light": "#E1F5EE",
}


def cr(x): return f"₹{x/1e7:.2f} Cr" if x >= 1e6 else f"₹{x:,.0f}"
def lakh(x): return f"₹{x/1e5:.1f}L"


def render():
    s = st.session_state

    # Guard: check if enough data entered
    if not s.get("income_done") or not s.get("assets_done"):
        st.warning("⚠️ Please complete Income and Assets sections before viewing your plan.")
        col_g1, col_g2 = st.columns([3, 1])
        with col_g2:
            if st.button("Go to Income →", type="primary"):
                s["page"] = "income"
                st.rerun()
        return

    st.title("📈 Your Financial Plan")
    st.caption(f"Plan for {s.get('age', 30)}-year-old in {s.get('city', 'India')} "
               f"| Retirement target: age {s.get('retirement_age', 55)}")
    st.divider()

    # ── TABS ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Net Worth",
        "💵 Cashflow",
        "🎯 Goal Tracker",
        "🏠 Rent vs Buy",
        "🏖 Retirement",
        "📋 Action Plan",
    ])

    # ── TAB 0: NET WORTH ──────────────────────────────────────────────────────
    with tabs[0]:
        st.subheader("Your net worth today")

        equity_total = s.get("equity_mf_value", 0) + s.get("direct_equity_value", 0)
        locked = s.get("ppf_value", 0) + s.get("epf_value", 0) + s.get("nps_value", 0)
        semi_locked = s.get("rbi_bond_value", 0) + s.get("fd_value", 0)
        gold = s.get("gold_value", 0)
        liquid = s.get("emergency_fund_value", 0)
        other = s.get("other_assets", 0)
        liabilities = (s.get("personal_loan", 0) + s.get("other_liabilities", 0) +
                       s.get("home_loan_outstanding", 0))
        gross = equity_total + locked + semi_locked + gold + liquid + other
        net_worth = gross - liabilities

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Gross assets", cr(gross))
        col2.metric("Liabilities", cr(liabilities), delta=f"-{cr(liabilities)}" if liabilities else None,
                    delta_color="inverse")
        col3.metric("Net worth", cr(net_worth))
        col4.metric("Liquid / investable", cr(equity_total + liquid))

        # Donut chart
        labels = ["Equity (MF+Stocks)", "PPF/EPF/NPS", "RBI Bond/FD", "Gold", "Liquid/Other"]
        values = [equity_total, locked, semi_locked, gold, liquid + other]
        values_clean = [max(0, v) for v in values]

        if sum(values_clean) > 0:
            fig = go.Figure(go.Pie(
                labels=labels, values=values_clean,
                hole=0.55,
                marker_colors=["#185FA5", "#3B6D11", "#EF9F27", "#D4537E", "#888780"],
                textinfo="label+percent",
                textfont_size=12,
            ))
            fig.update_layout(
                showlegend=False, height=320, margin=dict(t=10, b=10, l=10, r=10),
                annotations=[dict(text=f"₹{net_worth/1e5:.0f}L<br>Net worth",
                                  x=0.5, y=0.5, font_size=14, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)

        # Alerts
        if gross > 0:
            gold_pct = gold / gross * 100
            if gold_pct < 5:
                st.warning(f"⚠️ Gold is {gold_pct:.1f}% of assets. Target 8–10%. Buy Sovereign Gold Bonds.")
        if not s.get("has_emergency_fund"):
            monthly_need = s.get("monthly_expenses", 0) + s.get("family_contribution_annual", 0) / 12
            st.error(f"🔴 No emergency fund. Build ₹{monthly_need*6:,.0f} (6 months) in a liquid fund first.")

    # ── TAB 1: CASHFLOW ───────────────────────────────────────────────────────
    with tabs[1]:
        st.subheader("Monthly cashflow analysis")
        cf = cashflow_analysis(s)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Monthly income", cr(cf["income"]))
        col2.metric("Expenses + family", cr(cf["expenses"] + cf["family"]))
        col3.metric("Total SIPs", cr(cf["total_sip"]))
        surplus_color = "normal" if cf["surplus"] >= 0 else "inverse"
        col4.metric("Undeployed surplus", cr(cf["surplus"]),
                    delta="Available to invest" if cf["surplus"] > 0 else "OVEREXTENDED",
                    delta_color=surplus_color)

        if cf["surplus"] < 0:
            st.error("🔴 Your committed outflows exceed income. Reduce expenses or SIPs.")
        elif cf["surplus"] > 5000:
            st.success(f"✅ You have {cr(cf['surplus'])}/month unallocated. Suggested deployment below.")
            # Surplus allocation suggestion
            ef_gap = max(0, s.get("monthly_expenses", 0) * 6 -
                         s.get("emergency_fund_value", 0))
            ef_monthly = min(25000, cf["surplus"]) if ef_gap > 0 else 0
            remaining = cf["surplus"] - ef_monthly
            marriage_monthly = min(30000, remaining) if s.get("wants_marriage_corpus") else 0
            house_monthly = min(remaining - marriage_monthly, remaining - marriage_monthly)

            if ef_monthly > 0 or marriage_monthly > 0:
                st.markdown("**💡 Suggested surplus allocation:**")
                alloc_data = {}
                if ef_monthly > 0:
                    alloc_data[f"Emergency fund (Liquid Fund) — ₹{ef_monthly:,.0f}/mo"] = ef_monthly
                if marriage_monthly > 0:
                    alloc_data[f"Marriage corpus (Arbitrage Fund) — ₹{marriage_monthly:,.0f}/mo"] = marriage_monthly
                leftover = cf["surplus"] - ef_monthly - marriage_monthly
                if leftover > 0:
                    alloc_data[f"House/retirement SIP — ₹{leftover:,.0f}/mo"] = leftover

                fig2 = go.Figure(go.Bar(
                    x=list(alloc_data.values()),
                    y=list(alloc_data.keys()),
                    orientation="h",
                    marker_color=["#3B6D11", "#185FA5", "#854F0B"][:len(alloc_data)]
                ))
                fig2.update_layout(height=180, margin=dict(t=10, b=10, l=10, r=10),
                                   xaxis_title="₹/month")
                st.plotly_chart(fig2, use_container_width=True)

        # Salary growth projection
        st.markdown("**Salary trajectory (8% growth p.a.)**")
        growth = s.get("salary_growth_pct", 8) / 100
        sal_years = list(range(0, 11))
        salaries = [s.get("net_take_home", 0) * (1 + growth)**y for y in sal_years]
        fig3 = go.Figure(go.Scatter(
            x=[s.get("age", 30) + y for y in sal_years],
            y=salaries, mode="lines+markers",
            line=dict(color="#185FA5", width=2),
            marker=dict(size=6),
        ))
        fig3.update_layout(height=200, margin=dict(t=10, b=10, l=10, r=10),
                           xaxis_title="Age", yaxis_title="Net take home (₹)")
        st.plotly_chart(fig3, use_container_width=True)

    # ── TAB 2: GOAL TRACKER ───────────────────────────────────────────────────
    with tabs[2]:
        st.subheader("Goal-by-goal status")
        infl = s.get("lifestyle_inflation", 8.0) / 100

        # Emergency fund
        monthly_need = s.get("monthly_expenses", 0) + s.get("family_contribution_annual", 0) / 12
        ef_target = monthly_need * 6
        ef_current = s.get("emergency_fund_value", 0) if s.get("has_emergency_fund") else 0
        ef_pct = min(100, ef_current / ef_target * 100) if ef_target > 0 else 0
        with st.expander(f"🛡 Emergency Fund — {ef_pct:.0f}% funded", expanded=True):
            col_a, col_b = st.columns(2)
            col_a.metric("Target (6 months)", cr(ef_target))
            col_b.metric("Current", cr(ef_current))
            st.progress(ef_pct / 100)
            if ef_pct < 100:
                months_needed = int((ef_target - ef_current) / 25000) + 1
                st.info(f"💡 Invest ₹25,000/month in a Liquid Fund → fully funded in {months_needed} months")

        # Marriage
        if s.get("wants_marriage_corpus") and s.get("marriage_pv", 0) > 0:
            m_fv = s.get("marriage_pv", 0) * (1 + infl) ** s.get("marriage_years", 2)
            arb_monthly = 30000
            m_built = sip_future_value(arb_monthly, ARBITRAGE_RETURN, s.get("marriage_years", 2))
            m_pct = min(100, m_built / m_fv * 100)
            with st.expander(f"💍 Marriage — corpus buildable: {lakh(m_built)} of {lakh(m_fv)}"):
                col_ma, col_mb = st.columns(2)
                col_ma.metric(f"Needed in {s.get('marriage_years',2)} yrs", lakh(m_fv))
                col_mb.metric("Buildable via ₹30K/mo SIP", lakh(m_built))
                st.progress(m_pct / 100)
                gap = m_fv - m_built
                if gap > 0:
                    st.warning(f"Gap: {lakh(gap)} — bridge with annual bonus allocation or backstop from equity corpus.")

        # House
        if s.get("wants_house") and s.get("house_budget_today", 0) > 0:
            ha = house_analysis(s)
            with st.expander("🏠 House purchase — timeline analysis"):
                st.markdown("**Own corpus needed at different purchase years:**")
                for sc in ha["scenarios"]:
                    pct_feasible = "✅" if sc["own_corpus_needed"] < 15000000 else "⚠️"
                    st.markdown(
                        f"{pct_feasible} **Year {sc['year']} (Age {sc['age_at_purchase']})**: "
                        f"Property {lakh(sc['property_cost'])} → Own corpus needed {lakh(sc['own_corpus_needed'])} "
                        f"| EMI {cr(sc['emi'])}/mo | Interest {lakh(sc['total_interest'])}"
                    )
                st.info(f"Max loan at 40% EMI rule: {lakh(ha['max_loan'])} | Max EMI: ₹{ha['max_emi']:,.0f}/mo")

        # Child education
        if s.get("wants_child_education") and s.get("child_education_pv", 0) > 0:
            edu_yrs = s.get("child_education_years", 18)
            edu_fv = s.get("child_education_pv", 0) * (1 + infl) ** edu_yrs
            sip_req = sip_needed_for_goal(edu_fv, EQUITY_LONG_TERM_RETURN, edu_yrs)
            with st.expander(f"🎓 Child Education — {lakh(edu_fv)} needed in {edu_yrs} years"):
                col_ea, col_eb = st.columns(2)
                col_ea.metric("Future value needed", lakh(edu_fv))
                col_eb.metric("Monthly SIP required (12%)", f"₹{sip_req:,.0f}")
                st.info(f"Start a dedicated ₹{sip_req:,.0f}/month SIP the month your child is born. "
                        f"Use Nifty Next 50 + Midcap 150 blend.")

    # ── TAB 3: RENT VS BUY ────────────────────────────────────────────────────
    with tabs[3]:
        st.subheader("Rent vs buy — Mumbai analysis")

        if not s.get("wants_house") or s.get("house_budget_today", 0) == 0:
            st.info("Enter your house budget in the Goals section to see this analysis.")
        else:
            buy_yr = st.slider("Evaluate: buy at year…", 1, 10, 5, key="rvb_yr")
            rvb = rent_vs_buy(s, buy_yr)

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("#### 🏠 Buy path")
                st.metric("Property cost at purchase", cr(rvb["property_at_buy"]))
                st.metric("Monthly EMI", f"₹{rvb['monthly_emi']:,.0f}")
                st.metric(f"Property value {rvb['horizon']} yrs later", cr(rvb["property_at_horizon"]))
                st.metric("Net wealth (property equity)", cr(rvb["property_at_horizon"]))
            with col_r2:
                st.markdown("#### 📈 Rent + invest path")
                st.metric("Monthly rent at purchase year", f"₹{rvb['monthly_rent_at_buy']:,.0f}")
                st.metric("Down payment invested at 12%", cr(rvb["rent_corpus_at_horizon"]))
                st.metric(f"Rent cost after {rvb['horizon']} yrs", f"₹{rvb['rent_at_horizon']:,.0f}/mo")
                st.metric("Total financial wealth", cr(rvb["rent_corpus_at_horizon"]))

            if rvb["buy_wins"]:
                st.success(f"🏠 **Buy wins** by {cr(abs(rvb['difference']))} over {rvb['horizon']} years "
                           f"at {s.get('property_appreciation',7):.0f}% property appreciation.")
            else:
                st.info(f"📈 **Rent + invest wins** by {cr(abs(rvb['difference']))} purely on numbers. "
                        f"But rent escalation risk is real — ₹{rvb['rent_at_horizon']:,.0f}/mo at retirement is "
                        f"dangerous on a fixed corpus.")

            # Appreciation sensitivity
            st.markdown("#### Sensitivity: property appreciation rate")
            app_rates = [4, 5, 6, 7, 8, 10, 12, 15, 20]
            prop_vals, equity_vals = [], []
            budget = s.get("house_budget_today", 0)
            for ar in app_rates:
                prop_at_buy = budget * (1 + ar / 100) ** buy_yr
                prop_at_end = prop_at_buy * (1 + ar / 100) ** rvb["horizon"]
                prop_vals.append(prop_at_end / 1e7)
                equity_vals.append(rvb["rent_corpus_at_horizon"] / 1e7)

            fig_sens = go.Figure()
            fig_sens.add_trace(go.Scatter(x=app_rates, y=prop_vals, mode="lines+markers",
                                          name="Property value", line=dict(color="#185FA5")))
            fig_sens.add_trace(go.Scatter(x=app_rates, y=equity_vals, mode="lines",
                                          name="Equity corpus", line=dict(color="#3B6D11", dash="dash")))
            fig_sens.update_layout(height=260, xaxis_title="Property appreciation (%)",
                                   yaxis_title="Value (₹ Cr)",
                                   legend=dict(orientation="h", y=1.1),
                                   margin=dict(t=30, b=30, l=10, r=10))
            st.plotly_chart(fig_sens, use_container_width=True)
            st.caption(f"Mumbai recent YoY: 20% | Long-term average: 7–8% | Conservative: 5%")

    # ── TAB 4: RETIREMENT ─────────────────────────────────────────────────────
    with tabs[4]:
        st.subheader(f"Retirement corpus — target age {s.get('retirement_age', 55)}")
        proj = projected_corpus_at_retirement(s)

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Corpus needed", cr(proj["corpus_needed"]))
        col_r2.metric("With 10% SIP step-up", cr(proj["total_with_stepup"]),
                      delta=cr(proj["total_with_stepup"] - proj["corpus_needed"]),
                      delta_color="normal" if proj["gap_stepup"] <= 0 else "inverse")
        col_r3.metric("Flat SIPs (no step-up)", cr(proj["total_flat"]),
                      delta=cr(proj["total_flat"] - proj["corpus_needed"]),
                      delta_color="normal" if proj["gap_flat"] <= 0 else "inverse")

        if proj["gap_stepup"] > 0:
            st.error(f"🔴 Even with 10% step-up, gap of {cr(proj['gap_stepup'])}. "
                     f"Increase SIPs or delay retirement by 2–3 years.")
        elif proj["gap_flat"] > 0:
            st.warning(f"⚠️ Without SIP step-up, shortfall of {cr(proj['gap_flat'])}. "
                       f"Step-up by 10% every April is non-negotiable.")
        else:
            st.success(f"✅ On track! Surplus of {cr(abs(proj['gap_stepup']))} even with step-up.")

        # Corpus breakdown waterfall
        breakdown_labels = ["Equity SIPs\n(step-up)", "Existing\nEquity", "EPF", "NPS", "PPF",
                             "RBI Bond\n(reinvested)", "Gold"]
        breakdown_values = [
            proj["equity_sip_stepup"], proj["existing_equity_fv"],
            proj["epf_fv"], proj["nps_fv"], proj["ppf_fv"],
            proj["rbi_fv"], proj["gold_fv"]
        ]
        colors_bar = ["#185FA5", "#378ADD", "#3B6D11", "#639922",
                      "#97C459", "#EF9F27", "#D4537E"]

        fig_bar = go.Figure(go.Bar(
            x=breakdown_labels,
            y=[v / 1e7 for v in breakdown_values],
            marker_color=colors_bar,
            text=[f"₹{v/1e7:.1f}Cr" for v in breakdown_values],
            textposition="outside",
        ))
        fig_bar.add_hline(y=proj["corpus_needed"] / 1e7,
                          line_dash="dash", line_color="red",
                          annotation_text="Target", annotation_position="right")
        fig_bar.update_layout(height=320, yaxis_title="₹ Crore",
                              margin=dict(t=30, b=10, l=10, r=60))
        st.plotly_chart(fig_bar, use_container_width=True)

        # Corpus growth projection
        st.markdown("**Corpus growth over time (with vs without step-up)**")
        ages = list(range(s.get("age", 30), s.get("retirement_age", 55) + 1))
        corpus_stepup, corpus_flat = [], []
        total_sip = proj["total_sip_now"]
        base_equity = s.get("equity_mf_value", 0) + s.get("direct_equity_value", 0)
        for i, ag in enumerate(ages):
            yrs_so_far = ag - s.get("age", 30)
            su = step_up_sip_fv(total_sip, EQUITY_LONG_TERM_RETURN, yrs_so_far, 0.10)
            fl = sip_future_value(total_sip, EQUITY_LONG_TERM_RETURN, yrs_so_far)
            eq = lumpsum_fv(base_equity, EQUITY_LONG_TERM_RETURN, yrs_so_far)
            corpus_stepup.append((su + eq) / 1e7)
            corpus_flat.append((fl + eq) / 1e7)

        fig_growth = go.Figure()
        fig_growth.add_trace(go.Scatter(x=ages, y=corpus_stepup, mode="lines",
                                         name="With 10% annual step-up",
                                         line=dict(color="#3B6D11", width=2.5)))
        fig_growth.add_trace(go.Scatter(x=ages, y=corpus_flat, mode="lines",
                                         name="Flat SIPs",
                                         line=dict(color="#185FA5", width=1.5, dash="dot")))
        fig_growth.add_hline(y=proj["corpus_needed"] / 1e7,
                              line_dash="dash", line_color="#A32D2D",
                              annotation_text="Target corpus", annotation_position="right")
        fig_growth.update_layout(height=280, xaxis_title="Age", yaxis_title="₹ Crore",
                                  legend=dict(orientation="h", y=1.1),
                                  margin=dict(t=30, b=10, l=10, r=60))
        st.plotly_chart(fig_growth, use_container_width=True)

    # ── TAB 5: ACTION PLAN ────────────────────────────────────────────────────
    with tabs[5]:
        st.subheader("Your personalised action plan")
        st.caption("Prioritised steps — do them in order")

        actions_immediate = []
        actions_soon = []
        actions_ongoing = []

        # Emergency fund
        if not s.get("has_emergency_fund"):
            ef_target = (s.get("monthly_expenses", 0) +
                         s.get("family_contribution_annual", 0) / 12) * 6
            actions_immediate.append({
                "title": "🛡 Build emergency fund",
                "detail": f"Open Parag Parikh or HDFC Liquid Fund. "
                           f"Invest ₹25,000/month. Target: {cr(ef_target)} in "
                           f"{max(1,int(ef_target/25000))} months. Do this before anything else."
            })

        # Insurance
        actions_immediate.append({
            "title": "❤️ Buy term life + health insurance",
            "detail": "₹2Cr term cover (LIC Tech Term / HDFC Click2Protect) ≈ ₹16,000–22,000/yr. "
                      "Personal health floater ₹10L ≈ ₹12,000/yr. Buy this month — cheapest at your current age."
        })

        # SIP step up
        total_sip = sum(x["monthly"] for x in s.get("sips", []))
        surplus = cashflow_analysis(s)["surplus"]
        if surplus > 10000:
            actions_immediate.append({
                "title": f"📈 Increase SIPs by {cr(surplus * 0.7)}/month",
                "detail": f"You have {cr(surplus)}/month unallocated. Deploy 70% into existing SIPs "
                           f"(prioritise Nifty Next 50 and Midcap 150). Keep 30% as buffer."
            })

        # Marriage
        if s.get("wants_marriage_corpus") and s.get("marriage_pv", 0) > 0:
            actions_immediate.append({
                "title": "💍 Start marriage corpus SIP",
                "detail": f"Open Kotak/Nippon Arbitrage Fund. SIP ₹30,000/month. "
                           f"Do NOT use existing equity corpus — avoids tax event. "
                           f"Supplement with annual bonus."
            })

        # PPF top-up
        if s.get("ppf_value", 0) > 0:
            actions_soon.append({
                "title": "📗 Max out PPF on April 1 every year",
                "detail": "Invest full ₹1,50,000 on April 1 (not April 30) to earn full year's interest. "
                           "PPF at 7.1% tax-free EEE beats any taxable instrument on risk-adjusted basis."
            })

        # Gold
        gold_pct = s.get("gold_value", 0) / max(1, s.get("equity_mf_value", 0) +
                                                   s.get("direct_equity_value", 0) +
                                                   s.get("ppf_value", 0) + s.get("epf_value", 0) +
                                                   s.get("nps_value", 0)) * 100
        if gold_pct < 5:
            actions_soon.append({
                "title": "🥇 Buy Sovereign Gold Bonds to reach 8% allocation",
                "detail": f"Current gold is {gold_pct:.1f}% of portfolio. Buy SGBs via RBI issuance "
                           f"or NSE secondary market. 2.5% annual interest + appreciation + zero LTCG at maturity."
            })

        # RBI bond payout
        if s.get("rbi_bond_value", 0) > 0:
            actions_soon.append({
                "title": "💰 Reinvest every RBI Bond payout immediately",
                "detail": f"Every January 1 and July 1 you receive "
                           f"₹{s.get('rbi_bond_value',0) * 0.0805 / 2:,.0f} gross. "
                           f"Move to Arbitrage Fund the same day. Do not leave in savings account."
            })

        # SIP step-up reminder
        actions_ongoing.append({
            "title": "🔁 Step up all SIPs by 10% every April (24 years)",
            "detail": "Set a recurring calendar reminder for April 1. Log in and increase every SIP by 10%. "
                      "Also invest ₹1.5L in PPF on the same day. "
                      "This single habit is worth more than any investment advice."
        })

        # House
        if s.get("wants_house"):
            proj_local = projected_corpus_at_retirement(s)
            actions_ongoing.append({
                "title": "🏠 Discipline: never compromise SIPs for EMI",
                "detail": "When home loan EMI begins, reduce discretionary spending — not SIPs. "
                           "Pausing SIPs for 6 months during EMI years costs more in compounding "
                           "loss than any short-term relief."
            })

        # Render actions
        st.markdown("#### 🔴 Do immediately (this week)")
        for a in actions_immediate:
            with st.container(border=True):
                st.markdown(f"**{a['title']}**")
                st.caption(a["detail"])

        st.markdown("#### 🟡 Within 3 months")
        for a in actions_soon:
            with st.container(border=True):
                st.markdown(f"**{a['title']}**")
                st.caption(a["detail"])

        st.markdown("#### 🟢 Ongoing discipline (every year)")
        for a in actions_ongoing:
            with st.container(border=True):
                st.markdown(f"**{a['title']}**")
                st.caption(a["detail"])

        st.divider()
        st.caption("⚠️ FinPlan India is an educational calculator. Not SEBI-registered financial advice. "
                   "All projections assume consistent returns that may not be achieved. "
                   "Consult a SEBI-registered investment advisor for personalised advice.")
