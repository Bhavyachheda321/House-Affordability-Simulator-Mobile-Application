import streamlit as st
import plotly.graph_objects as go
from pages_content.calculations import (
    sip_future_value, step_up_sip_fv, lumpsum_fv,
    sip_needed_for_goal, max_loan_for_emi, emi_amount,
    rbi_bond_net_payout, retirement_corpus_needed,
    EQUITY_LONG_TERM_RETURN, ARBITRAGE_RETURN,
    LIQUID_RETURN, PPF_RATE, EPF_RATE, NPS_EQUITY_RETURN,
    GOLD_RETURN, RBI_BOND_RATE
)

def cr(x):
    if x >= 1e7: return f"₹{x/1e7:.1f} Cr"
    if x >= 1e5: return f"₹{x/1e5:.1f}L"
    return f"₹{x:,.0f}"

def render():
    s = st.session_state

    if s.get("monthly_salary", 0) == 0:
        st.warning("Please fill in your income details first.")
        if st.button("← Go back to start"):
            s["step"] = 1
            st.rerun()
        return

    # ── Core numbers ──────────────────────────────────────────────────────────
    sal = s["monthly_salary"]
    bonus_monthly = s["annual_bonus"] / 12
    income = sal + bonus_monthly
    expenses = s["monthly_expenses"]
    family = s["family_support_annual"] / 12
    sip_current = s["sip_total_monthly"]
    loan_emi = s["loan_emi_monthly"]
    surplus = income - expenses - family - sip_current - loan_emi

    infl = s["lifestyle_inflation"] / 100
    age = s["age"]
    ret_age = s["retirement_age"]
    yrs = ret_age - age
    slab = s["effective_slab_rate"]

    total_assets = (s["mf_value"] + s["stocks_value"] + s["ppf_value"] +
                    s["epf_value"] + s["nps_value"] + s["fd_value"] +
                    s["gold_value"] + s["rbi_bond_value"] +
                    s.get("emergency_fund_value", 0))

    # Retirement corpus
    corpus_needed = retirement_corpus_needed(s["retirement_monthly_spend"], infl, yrs)

    # Projected corpus at retirement (step-up SIPs)
    equity_base = s["mf_value"] + s["stocks_value"]
    equity_fv = lumpsum_fv(equity_base, EQUITY_LONG_TERM_RETURN, yrs)
    sip_stepup = step_up_sip_fv(sip_current, EQUITY_LONG_TERM_RETURN, yrs, 0.10)
    ppf_fv = (lumpsum_fv(s["ppf_value"], PPF_RATE, yrs) +
               sip_future_value(150000/12 if s["ppf_contributing"] else 0, PPF_RATE, yrs))
    epf_fv = (lumpsum_fv(s["epf_value"], EPF_RATE, yrs) +
               sip_future_value(s["epf_monthly"] * 2, EPF_RATE, yrs))
    nps_fv = (lumpsum_fv(s["nps_value"], NPS_EQUITY_RETURN, yrs) +
               sip_future_value(s["employer_nps_monthly"], NPS_EQUITY_RETURN, yrs))
    gold_fv = lumpsum_fv(s["gold_value"], GOLD_RETURN, yrs)
    rbi_months = s.get("rbi_bond_months_left", 0)
    rbi_reinvest_yrs = max(0, yrs - rbi_months / 12)
    rbi_net = rbi_bond_net_payout(s["rbi_bond_value"], RBI_BOND_RATE, slab)
    rbi_fv = lumpsum_fv(rbi_net["total_in_hand"], EQUITY_LONG_TERM_RETURN, rbi_reinvest_yrs) if s["rbi_bond_value"] > 0 else 0

    projected_stepup = equity_fv + sip_stepup + ppf_fv + epf_fv + nps_fv + gold_fv + rbi_fv
    projected_flat = equity_fv + sip_future_value(sip_current, EQUITY_LONG_TERM_RETURN, yrs) + ppf_fv + epf_fv + nps_fv + gold_fv + rbi_fv

    gap_stepup = corpus_needed - projected_stepup
    on_track = gap_stepup <= 0

    # ── Header ────────────────────────────────────────────────────────────────
    st.title("📊 Your financial plan")
    st.caption(f"Built for {age}-year-old in {s['city']} | Retirement target: age {ret_age}")

    st.markdown("---")

    # ── SECTION 1: WHAT TO DO THIS MONTH ─────────────────────────────────────
    st.markdown("## ✅ What to do this month")
    st.write("Do these in order. Each one builds on the last.")

    action_num = 0

    def action(title, detail, color="#185FA5"):
        nonlocal action_num
        action_num += 1
        bg = {"#185FA5": "#E6F1FB", "#A32D2D": "#FCEBEB",
              "#854F0B": "#FAEEDA", "#3B6D11": "#EAF3DE"}
        bg_color = bg.get(color, "#E6F1FB")
        text_color = color
        st.markdown(
            f'<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px;'
            f'background:var(--background-color);border:.5px solid #ddd;border-radius:10px;padding:14px 16px;">'
            f'<div style="width:28px;height:28px;border-radius:50%;background:{bg_color};'
            f'color:{text_color};display:flex;align-items:center;justify-content:center;'
            f'font-size:13px;font-weight:600;flex-shrink:0">{action_num}</div>'
            f'<div><div style="font-size:14px;font-weight:500;margin-bottom:4px">{title}</div>'
            f'<div style="font-size:13px;color:#666;line-height:1.6">{detail}</div></div></div>',
            unsafe_allow_html=True
        )

    # 1. Emergency fund
    ef_target = (expenses + family) * 6
    ef_current = s.get("emergency_fund_value", 0) if s["has_emergency_fund"] else 0
    if ef_current < ef_target:
        ef_gap = ef_target - ef_current
        months_to_build = max(1, int(ef_gap / 25000))
        action(
            f"🛡 Build your emergency fund — {cr(ef_target)} target",
            f"Open a Liquid Mutual Fund (try Parag Parikh Liquid Fund on Groww). "
            f"Invest ₹25,000/month. It will be ready in {months_to_build} months. "
            f"This is money you can withdraw any day if something goes wrong — job loss, medical emergency, etc. "
            f"Without this, one bad event can wipe out all your investments.",
            color="#A32D2D"
        )

    # 2. Insurance
    action(
        "❤️ Buy life insurance + health insurance",
        f"You need: (1) Term life cover of {cr(sal*12*20)} "
        f"— try LIC Tech Term or HDFC Click2Protect online, costs ~₹16,000–22,000/year. "
        f"(2) Personal health insurance of ₹10L — don't rely on office cover alone. "
        f"Buy this week. At age {age}, premiums are cheapest right now.",
        color="#A32D2D"
    )

    # 3. SIP increase if surplus
    if surplus > 10000:
        new_sip = int(surplus * 0.75 / 500) * 500
        action(
            f"📈 Increase your monthly investments by {cr(new_sip)}",
            f"You have {cr(surplus)}/month that isn't invested yet. "
            f"Add {cr(new_sip)}/month to your existing SIPs (or start new ones). "
            f"Suggested split: Nifty 50 Index Fund (40%) + Nifty Next 50 Index Fund (30%) + "
            f"Nifty Midcap 150 Index Fund (30%). Use Groww or Zerodha to set this up in 10 minutes.",
            color="#3B6D11"
        )
    elif surplus <= 0:
        action(
            "⚠️ Reduce expenses or increase income",
            f"Your expenses are consuming your full salary. You need at least ₹10,000/month free "
            f"to start investing. Look at what can be cut — subscriptions, eating out, impulse purchases.",
            color="#A32D2D"
        )

    # 4. Marriage corpus (if applicable)
    if s.get("want_marriage_savings") and s.get("marriage_cost", 0) > 0:
        m_fv = s["marriage_cost"] * (1 + infl) ** s["marriage_years"]
        action(
            f"💍 Start a separate marriage savings SIP — {cr(m_fv)} needed in {s['marriage_years']} years",
            f"Open Kotak or Nippon Arbitrage Fund separately. SIP ₹30,000/month. "
            f"This earns ~6.5% and is taxed much less than an FD for someone in your tax bracket. "
            f"Keep this money separate — do not mix with your long-term investments.",
            color="#854F0B"
        )

    # 5. Gold top-up
    gold_pct = s["gold_value"] / max(1, total_assets) * 100
    if gold_pct < 5 and total_assets > 100000:
        gold_target = total_assets * 0.08
        gold_needed = gold_target - s["gold_value"]
        action(
            f"🥇 Buy Sovereign Gold Bonds — target {cr(gold_needed)} more",
            f"Your gold is only {gold_pct:.0f}% of your savings (ideal: 8–10%). "
            f"Buy Sovereign Gold Bonds (SGBs) from RBI or NSE — NOT physical gold. "
            f"SGBs pay 2.5% interest per year plus gold price appreciation, and you pay zero tax when they mature. "
            f"Buy on Zerodha or Groww during the next RBI issuance window.",
            color="#854F0B"
        )

    # 6. PPF
    if s["ppf_value"] > 0 and s["ppf_contributing"]:
        action(
            "📗 Invest your full PPF quota (₹1,50,000) on April 1 every year",
            "Log into your bank app on April 1 and transfer ₹1,50,000 to PPF. "
            "If you do it on April 30 instead, you lose a full month's tax-free interest. "
            "PPF earns 7.1% with zero tax — it's the safest, best debt instrument available.",
            color="#3B6D11"
        )

    # 7. Step-up reminder
    action(
        "🔁 Increase all your SIPs by 10% every April — for life",
        "Set a phone reminder for April 1 every year. Log into Groww/Zerodha and increase "
        "every SIP by 10%. Also invest ₹1.5L in PPF the same day. "
        f"Doing this every year for {yrs} years adds over {cr(sip_stepup - sip_future_value(sip_current, EQUITY_LONG_TERM_RETURN, yrs))} "
        "extra to your retirement corpus compared to never increasing your SIP.",
        color="#3B6D11"
    )

    st.markdown("---")

    # ── SECTION 2: YOUR 10-YEAR PICTURE ──────────────────────────────────────
    st.markdown("## 📈 Your big picture")

    # Net worth card
    col1, col2, col3 = st.columns(3)
    col1.metric("Your savings today", cr(total_assets))
    col2.metric(f"Projected at age {ret_age}", cr(projected_stepup),
                help="With 10% annual SIP increase")
    col3.metric("Target at retirement", cr(corpus_needed))

    # On-track indicator
    if on_track:
        pct_funded = min(100, projected_stepup / corpus_needed * 100)
        st.markdown(
            f'<div class="ok-box"><b>✅ You are on track to retire at {ret_age}!</b><br>'
            f'With 10% annual SIP increases, your projected corpus is {cr(projected_stepup)} '
            f'vs the {cr(corpus_needed)} you need. You have a cushion of {cr(abs(gap_stepup))}.</div>',
            unsafe_allow_html=True
        )
    else:
        add_monthly = sip_needed_for_goal(abs(gap_stepup), EQUITY_LONG_TERM_RETURN, yrs)
        st.markdown(
            f'<div class="warn-box"><b>⚠️ You are {cr(abs(gap_stepup))} short of your retirement target.</b><br>'
            f'To close the gap, you need to invest an extra <b>₹{add_monthly:,.0f}/month</b> consistently. '
            f'Alternatively, retire at {ret_age + 3} instead — that gives your money 3 more years to grow.</div>',
            unsafe_allow_html=True
        )

    # Corpus growth chart
    ages_list = list(range(age, ret_age + 1))
    corpus_with = []
    corpus_without = []
    for a in ages_list:
        y = a - age
        su = step_up_sip_fv(sip_current, EQUITY_LONG_TERM_RETURN, y, 0.10)
        fl = sip_future_value(sip_current, EQUITY_LONG_TERM_RETURN, y)
        eq = lumpsum_fv(equity_base, EQUITY_LONG_TERM_RETURN, y)
        corpus_with.append((su + eq) / 1e7)
        corpus_without.append((fl + eq) / 1e7)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ages_list, y=corpus_with, mode="lines", fill="tozeroy",
        name="With 10% annual increase",
        line=dict(color="#185FA5", width=2.5),
        fillcolor="rgba(24,95,165,0.08)"
    ))
    fig.add_trace(go.Scatter(
        x=ages_list, y=corpus_without, mode="lines",
        name="No increase (flat SIPs)",
        line=dict(color="#aaa", width=1.5, dash="dot")
    ))
    fig.add_hline(
        y=corpus_needed / 1e7, line_dash="dash", line_color="#A32D2D",
        annotation_text=f"Target: {cr(corpus_needed)}",
        annotation_position="right"
    )
    fig.update_layout(
        height=260, margin=dict(t=20, b=20, l=10, r=70),
        xaxis_title="Your age", yaxis_title="₹ Crore",
        legend=dict(orientation="h", y=-0.25, font=dict(size=11)),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── House section ─────────────────────────────────────────────────────────
    if s.get("want_house") and s.get("house_budget", 0) > 0:
        st.markdown("#### 🏠 Your home purchase")
        max_emi_allowed = sal * 0.40
        max_loan = max_loan_for_emi(max_emi_allowed, 8.5, 20)
        parents = s.get("parents_house_contribution", 0)
        prop_appr = s.get("property_appr_rate", 7) / 100

        rows = []
        for yr in [3, 5, 7]:
            cost = s["house_budget"] * (1 + prop_appr) ** yr
            own = max(0, cost - parents - max_loan)
            rows.append((yr, age + yr, cost, own))

        st.markdown(
            f'With a max loan of {cr(max_loan)} (40% EMI rule at 8.5%) '
            f'and family contribution of {cr(parents)}, here\'s what you need from your own savings:'
        )

        col_y, col_a, col_c, col_o = st.columns(4)
        col_y.markdown("**Year**")
        col_a.markdown("**Your age**")
        col_c.markdown("**Property cost**")
        col_o.markdown("**You need from savings**")
        for yr, ag, cost, own in rows:
            c1, c2, c3, c4 = st.columns(4)
            c1.write(f"Year {yr}")
            c2.write(f"Age {ag}")
            c3.write(cr(cost))
            color = "🟢" if own < equity_base * 1.5 else "🟡" if own < equity_base * 3 else "🔴"
            c4.write(f"{color} {cr(own)}")

        st.markdown(
            f'<div class="tip-box">💡 The best time to buy is when your own savings cover the gap shown above. '
            f'Property in {s["city"]} appreciates ~{s["property_appr_rate"]:.0f}%/year — '
            f'waiting too long makes the gap bigger, not smaller.</div>',
            unsafe_allow_html=True
        )

    # ── Where your money is ───────────────────────────────────────────────────
    if total_assets > 0:
        st.markdown("#### 💼 Where your money is today")
        labels = ["Mutual funds & stocks", "PPF + EPF + NPS", "Gold",
                  "FD + RBI Bond", "Emergency fund"]
        values = [
            s["mf_value"] + s["stocks_value"],
            s["ppf_value"] + s["epf_value"] + s["nps_value"],
            s["gold_value"],
            s["fd_value"] + s["rbi_bond_value"],
            s.get("emergency_fund_value", 0)
        ]
        values = [max(0, v) for v in values]
        if sum(values) > 0:
            fig2 = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.5,
                marker_colors=["#185FA5", "#3B6D11", "#D4537E", "#EF9F27", "#888780"],
                textinfo="percent+label", textfont_size=11,
            ))
            fig2.update_layout(
                showlegend=False, height=260,
                margin=dict(t=10, b=10, l=10, r=10),
                annotations=[dict(text=f"{cr(total_assets)}<br>total",
                                  x=0.5, y=0.5, font_size=13, showarrow=False)],
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── Key habits summary ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📌 The 3 habits that determine everything")
    st.markdown(
        '<div style="display:grid;grid-template-columns:1fr;gap:10px">'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        '<div style="font-weight:500;margin-bottom:4px">1. Increase SIPs 10% every April</div>'
        '<div style="font-size:13px;color:#666">The single most powerful thing you can do. '
        'Set a phone alarm for April 1. Log in. Increase by 10%. Done.</div></div>'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        '<div style="font-weight:500;margin-bottom:4px">2. Never pause SIPs — even during tough months</div>'
        '<div style="font-size:13px;color:#666">When money is tight, cut expenses first. '
        'Pausing a SIP for 3 months costs more in compounding than it saves in cash.</div></div>'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        '<div style="font-weight:500;margin-bottom:4px">3. Spend your bonus on goals, not upgrades</div>'
        '<div style="font-size:13px;color:#666">Each year, put at least 80% of your bonus '
        'into your house fund, emergency fund, or SIP top-up — before you spend any of it.</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.caption(
        "⚠️ **Disclaimer:** FinPlan India is a free educational calculator. It is not registered with SEBI "
        "and does not constitute financial advice. All projections assume returns that may not be achieved. "
        "Please consult a SEBI-registered investment adviser before making financial decisions."
    )

    st.markdown("")
    col_x, col_y, col_z = st.columns([1, 2, 1])
    with col_y:
        if st.button("🔄 Start over with different numbers", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
