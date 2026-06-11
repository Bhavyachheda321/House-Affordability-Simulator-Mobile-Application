"""
FinPlan India v4 — Plan Page
Year-by-year simulation results, dynamic action plan, what-if scenarios, Gemini Q&A.
"""
import json
import streamlit as st
import plotly.graph_objects as go

from pages_content.calculations import (
    run_simulation, project_retirement, monthly_cashflow,
    house_scenarios, debt_priority, goal_corpus_needed, goal_monthly_sip,
    safe_withdrawal_rate, sip_needed,
    EQUITY_RETURN, CITY_STAMP_DUTY,
)
from pages_content.tax_engine import effective_slab_rate_from_bracket


# ── Formatting helpers ────────────────────────────────────────────────────────
def cr(x: float) -> str:
    if x >= 1e7:  return f"₹{x/1e7:.1f} Cr"
    if x >= 1e5:  return f"₹{x/1e5:.1f}L"
    if x >= 1e3:  return f"₹{x/1e3:.0f}K"
    return f"₹{x:,.0f}"


# ── Gemini plan Q&A ───────────────────────────────────────────────────────────
def ask_gemini_plan(question: str, plan_context: str) -> str:
    try:
        import urllib.request, json as _json
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            return "GEMINI_API_KEY not configured in Streamlit secrets."
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={api_key}"
        )
        prompt = (
            "You are a plain-language financial planning assistant for Indian investors. "
            "The user's computed financial plan data is below. "
            "Answer their question clearly in 3–5 sentences. "
            "Use only numbers from the plan data — do not invent figures. "
            "End with one practical action the user can take today.\n\n"
            f"PLAN DATA:\n{plan_context}\n\nUSER QUESTION: {question}"
        )
        payload = _json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400},
        }).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Could not reach Gemini: {e}"


# ── Main render ───────────────────────────────────────────────────────────────
def render():
    s = st.session_state

    if s.get("monthly_salary", 0) == 0:
        st.warning("Please fill in your income first.")
        if st.button("← Go to income"):
            s["step"] = 2
            st.rerun()
        return

    # ── Run simulation ────────────────────────────────────────────────────────
    snapshots = run_simulation(s)
    proj      = project_retirement(s, snapshots)
    cf        = monthly_cashflow(s)

    slab       = s.get("effective_slab_rate", 0.2288)
    old_reg    = s.get("old_regime", False)
    age        = s.get("age", 30)
    ret_age    = s.get("retirement_age", 55)
    yrs        = proj["years_to_retire"]
    infl       = s.get("lifestyle_inflation", 7) / 100
    city       = s.get("city", "Mumbai")
    sal        = s.get("monthly_salary", 0)

    total_assets = sum(snapshots[0]["assets"].values())

    st.title("📊 Your Financial Plan")
    st.caption(
        f"Age {age} · {city} · Retirement target: age {ret_age} · "
        f"{'Old' if old_reg else 'New'} regime · "
        f"Simulation: Indian FY aligned, {len(snapshots)} years"
    )

    # ── On-track banner ───────────────────────────────────────────────────────
    if proj["on_track"]:
        surplus_cr = -proj["gap"]
        st.markdown(
            f'<div style="background:#EAF3DE;border:2px solid #86efac;border-radius:12px;'
            f'padding:1.2rem 1.5rem;margin-bottom:1rem;">'
            f'<span style="font-size:1.4rem;font-weight:800;color:#166534">✅ On track for retirement</span><br>'
            f'<span style="color:#166534;font-size:.9rem;">Projected corpus {cr(proj["corpus_at_ret"])} '
            f'vs {cr(proj["corpus_needed"])} needed — surplus of {cr(surplus_cr)}</span></div>',
            unsafe_allow_html=True,
        )
    else:
        extra = sip_needed(proj["gap"], EQUITY_RETURN, yrs)
        st.markdown(
            f'<div style="background:#fee2e2;border:2px solid #fca5a5;border-radius:12px;'
            f'padding:1.2rem 1.5rem;margin-bottom:1rem;">'
            f'<span style="font-size:1.4rem;font-weight:800;color:#991b1b">⚠️ Retirement shortfall</span><br>'
            f'<span style="color:#991b1b;font-size:.9rem;">Gap: {cr(proj["gap"])} · '
            f'To close it: invest {cr(extra)}/mo extra, '
            f'or retire at {ret_age + 3}, or spend less in retirement.</span></div>',
            unsafe_allow_html=True,
        )

    # ── SECTION 1: ACTION PLAN ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## ✅ What to do right now")
    st.write("In priority order. Complete step 1 before moving to step 2.")

    actions_html = ""
    num = 0

    def act(title: str, detail: str, col: str = "#185FA5"):
        nonlocal num, actions_html
        num += 1
        bg = {"#185FA5": "#E6F1FB", "#A32D2D": "#FCEBEB",
              "#854F0B": "#FAEEDA", "#3B6D11": "#EAF3DE"}.get(col, "#E6F1FB")
        actions_html += (
            f'<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;'
            f'border:.5px solid #ddd;border-radius:10px;padding:14px 16px">'
            f'<div style="width:28px;height:28px;border-radius:50%;background:{bg};color:{col};'
            f'display:flex;align-items:center;justify-content:center;font-size:13px;'
            f'font-weight:600;flex-shrink:0">{num}</div>'
            f'<div><div style="font-size:14px;font-weight:500;margin-bottom:3px">{title}</div>'
            f'<div style="font-size:13px;color:#666;line-height:1.6">{detail}</div>'
            f'</div></div>'
        )

    # A. Emergency fund
    ef_target = (s.get("monthly_expenses", 0) + s.get("family_support_annual", 0) / 12) * 6
    ef_have   = s.get("emergency_fund_value", 0) if s.get("has_emergency_fund") else 0
    if ef_have < ef_target:
        months_to_build = max(1, int((ef_target - ef_have) / 25000))
        act(
            "🛡 Build your emergency fund first",
            f"Target: {cr(ef_target)} (6 months of expenses). You have {cr(ef_have)}. "
            f"Open Parag Parikh or HDFC Liquid Fund on Groww — invest ₹25,000/month. "
            f"Ready in ~{months_to_build} months. Withdraw any day without penalty.",
            "#A32D2D",
        )

    # B. Debt priority
    debt_rec = debt_priority(
        s.get("loan_interest_rate", 0),
        s.get("loans_outstanding", 0),
        s.get("loan_emi_monthly", 0),
    )
    if debt_rec.get("has_loan") and debt_rec.get("should_prepay"):
        act(
            "💳 Pay off your loan before investing in equity",
            debt_rec["reason"] + f" Use your monthly surplus of {cr(cf['surplus'])} "
            "for extra loan payments. Once the loan is gone, redirect everything to investments.",
            "#A32D2D",
        )

    # C. Insurance
    base_prem   = 10000 + age * 300
    health_prem = 8000 + (age - 25) * 200
    act(
        "❤️ Buy term life + personal health insurance",
        f"Term cover needed: {cr(sal * 12 * 20)} "
        f"(LIC Tech Term / HDFC Click2Protect / Max Life). "
        f"Estimated premium at age {age}: ~₹{base_prem:,.0f}–₹{base_prem+6000:,.0f}/yr. "
        f"Personal health: ₹10L cover ~₹{health_prem:,.0f}/yr. "
        "Do NOT rely on employer insurance — it stops when you change jobs.",
        "#A32D2D",
    )

    # D. ELSS for old-regime filers
    if old_reg and slab >= 0.15 and not debt_rec.get("should_prepay"):
        elss_saving = 150000 * slab
        act(
            f"📗 Start ELSS SIP — saves ₹{elss_saving:,.0f} in tax this FY",
            f"Old regime filers get ₹1,50,000 deduction under 80C by investing in ELSS. "
            f"Saves ₹{elss_saving:,.0f} in tax annually. SIP ₹12,500/month. "
            "Best ELSS: Mirae Asset Tax Saver, Quant ELSS (check Groww ratings). "
            "3-year lock-in, then treated as equity LTCG.",
            "#854F0B",
        )

    # E. SIP increase
    surplus = cf["surplus"]
    if not debt_rec.get("should_prepay") and surplus > 5000:
        new_sip = int(surplus * 0.75 / 500) * 500
        if slab >= 0.20:
            arb_note = (
                "For parking short-term money (12+ months), use Kotak/Nippon Arbitrage Fund — "
                "you pay only 12.5% LTCG vs 34%+ on FD interest at your tax bracket."
            )
        elif slab > 0:
            arb_note = "For 1–3 year goals, a short-duration debt fund works well at your bracket."
        else:
            arb_note = "For parking money, a liquid fund or bank FD is simplest."
        act(
            f"📈 Invest {cr(new_sip)} more per month",
            f"You have {cr(surplus)}/month unallocated after expenses and current SIPs. "
            f"Invest {cr(new_sip)}/month in equity index SIPs: "
            "Nifty 50 (40%) · Nifty Next 50 (30%) · Nifty Midcap 150 (30%). "
            f"{arb_note}",
            "#3B6D11",
        )

    # F. Marriage goal
    if s.get("want_marriage_savings") and s.get("marriage_cost", 0) > 0:
        m_fv  = goal_corpus_needed(s["marriage_cost"], s.get("marriage_years", 3), infl)
        sip_m = goal_monthly_sip(m_fv, s.get("marriage_years", 3))
        if slab >= 0.20:
            instr = "Kotak/Nippon Arbitrage Fund (equity tax rates — far better than FD at your bracket)"
        else:
            instr = "short-duration debt fund or bank FD"
        act(
            f"💍 Build wedding corpus — {cr(m_fv)} in {s.get('marriage_years', 3)} years",
            f"Open a dedicated SIP of {cr(sip_m)}/month in a {instr}. "
            "Keep this separate from your long-term investments.",
            "#854F0B",
        )

    # G. Child education goal
    if s.get("want_child_education") and s.get("child_education_cost", 0) > 0:
        edu_infl = 0.10
        e_yrs = s.get("child_education_years", 18)
        e_fv  = goal_corpus_needed(s["child_education_cost"], e_yrs, edu_infl)
        sip_e = goal_monthly_sip(e_fv, e_yrs)
        act(
            f"🎓 Start child education SIP — {cr(e_fv)} needed in {e_yrs} years",
            f"Education inflation runs ~10%/yr. Start {cr(sip_e)}/month now in a "
            "Nifty 50 index fund. The earlier you start, the lower the SIP needed. "
            "Consider Sukanya Samriddhi Yojana (SSY) if you have a daughter — 8.2% tax-free.",
            "#854F0B",
        )

    # H. Gold
    gold_pct = s.get("gold_value", 0) / max(1, total_assets) * 100
    if gold_pct < 5 and total_assets > 200000:
        gold_gap = total_assets * 0.08 - s.get("gold_value", 0)
        act(
            f"🥇 Add Sovereign Gold Bonds — {cr(gold_gap)} to reach 8% allocation",
            f"Your gold is {gold_pct:.0f}% of savings. Buy SGBs on Groww/Zerodha or "
            "during RBI issue windows — NOT physical gold. "
            "SGBs pay 2.5% annual interest + gold appreciation + zero capital gains at maturity.",
            "#854F0B",
        )

    # I. PPF
    if s.get("ppf_value", 0) > 0 and s.get("ppf_contributing"):
        ppf_note = (
            f"Also saves ₹{150000 * slab:,.0f} in tax via 80C."
            if old_reg
            else "No 80C deduction in new regime, but 7.1% tax-free return beats any taxable FD."
        )
        act(
            "📗 Invest full PPF quota (₹1,50,000) on April 1 every year",
            f"Transfer on April 1 — not April 30. Interest accrues from the 5th. "
            f"PPF is EEE: contribution, growth, and withdrawal all tax-free. {ppf_note}",
            "#3B6D11",
        )

    # J. SIP step-up
    sip_flat   = snapshots[-1]["committed_sip_ann"] / 12 * len(snapshots)
    sip_stepup = snapshots[-1]["assets"]["equity"]
    act(
        "🔁 Increase every SIP by 10% each April — without fail",
        "Set a phone reminder on April 1. Log into Groww/Zerodha, increase each SIP by 10%. "
        "This single habit is worth more compounding than any stock pick. "
        f"The step-up habit adds significantly to your corpus vs flat SIPs over {yrs} years.",
        "#3B6D11",
    )

    st.markdown(actions_html, unsafe_allow_html=True)

    # ── SECTION 2: WHAT-IF SLIDERS (auto-rerun) ───────────────────────────────
    st.markdown("---")
    st.markdown("## 🎛 What-If Explorer")
    st.write("Adjust these sliders — the retirement projection updates instantly.")

    w1, w2, w3 = st.columns(3)
    with w1:
        wi_sip = st.slider(
            "Monthly SIP (₹K)", 0, 300,
            int(s.get("sip_total_monthly", 0) / 1000), step=5,
        ) * 1000
    with w2:
        wi_ret = st.slider(
            "Retire at age", 40, 70,
            int(s.get("retirement_age", 55)), step=1,
        )
    with w3:
        wi_spend = st.slider(
            "Monthly spend at retirement (₹K)", 25, 500,
            int(s.get("retirement_monthly_spend", 100000) / 1000), step=5,
        ) * 1000

    # Build what-if session copy and re-run
    s_wi = dict(s)
    s_wi["sip_total_monthly"]        = wi_sip
    s_wi["retirement_age"]           = wi_ret
    s_wi["retirement_monthly_spend"] = wi_spend
    wi_snaps = run_simulation(s_wi)
    wi_proj  = project_retirement(s_wi, wi_snaps)

    wc1, wc2, wc3 = st.columns(3)
    wc1.metric(
        "Corpus needed",
        cr(wi_proj["corpus_needed"]),
        help=f"Using {wi_proj['swr']*100:.1f}% SWR for {wi_proj['post_retire_years']}-year retirement",
    )
    delta_val = wi_proj["corpus_at_ret"] - wi_proj["corpus_needed"]
    wc2.metric(
        "Projected corpus",
        cr(wi_proj["corpus_at_ret"]),
        delta=cr(abs(delta_val)) + (" surplus" if delta_val >= 0 else " shortfall"),
        delta_color="normal" if delta_val >= 0 else "inverse",
    )
    wc3.metric(
        "Status",
        "✅ On track" if wi_proj["on_track"] else "❌ Shortfall",
    )

    if not wi_proj["on_track"]:
        extra_needed = sip_needed(wi_proj["gap"], EQUITY_RETURN, wi_proj["years_to_retire"])
        st.markdown(
            f'<div class="warn-box">To close the {cr(wi_proj["gap"])} gap: invest '
            f'<strong>{cr(extra_needed)}/month extra</strong>, '
            f'or retire at age {wi_ret + 3}, '
            f'or reduce retirement spend to {cr(wi_spend * 0.85)}/month.</div>',
            unsafe_allow_html=True,
        )

    # Trajectory chart
    wi_yrs_range = wi_proj["years_to_retire"]
    ages_x, with_y, flat_y = [], [], []
    for snap in wi_snaps[:wi_yrs_range + 1]:
        ages_x.append(snap["age"])
        with_y.append(snap["total_portfolio"] / 1e7)
        flat_y.append(snap["assets"]["equity"] / 1e7)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ages_x, y=with_y, mode="lines", fill="tozeroy",
        name="Total portfolio (step-up SIPs)",
        line=dict(color="#185FA5", width=2.5),
        fillcolor="rgba(24,95,165,0.07)",
    ))
    fig.add_hline(
        y=wi_proj["corpus_needed"] / 1e7,
        line_dash="dash", line_color="#A32D2D",
        annotation_text=f"Target {cr(wi_proj['corpus_needed'])}",
        annotation_position="right",
    )
    fig.update_layout(
        height=260, margin=dict(t=20, b=20, l=10, r=80),
        xaxis_title="Age", yaxis_title="₹ Crore",
        legend=dict(orientation="h", y=-0.3, font=dict(size=11)),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── SECTION 3: HOUSE ──────────────────────────────────────────────────────
    if s.get("want_house") and s.get("house_budget", 0) > 0:
        st.markdown("---")
        st.markdown("## 🏠 Home Purchase Scenarios")

        hs = house_scenarios(s, snapshots)
        st.markdown(
            f'Max loan at 40% EMI rule: **{cr(hs["max_loan"])}** · '
            f'Stamp duty in {city}: **{hs["stamp_pct"]*100:.0f}%**'
        )

        hcols = st.columns(6)
        for h, t in zip(hcols, ["Year", "Age", "Property cost", "Stamp+reg", "You need from savings", "Feasible?"]):
            h.markdown(f"**{t}**")
        for sc in hs["scenarios"]:
            c = st.columns(6)
            c[0].write(f"Year {sc['year']}")
            c[1].write(f"{sc['age']}")
            c[2].write(cr(sc["property_cost"]))
            c[3].write(cr(sc["stamp_reg"]))
            c[4].write(cr(sc["own_needed"]))
            icon = "🟢" if sc["feasible"] else "🔴"
            c[5].write(f"{icon} {'Yes' if sc['feasible'] else 'Not yet'}")

    # ── SECTION 4: NET WORTH PIE ──────────────────────────────────────────────
    if total_assets > 0:
        st.markdown("---")
        st.markdown("## 💼 Where Your Money Is Today")

        assets_now = snapshots[0]["assets"]
        labels = ["Equity (MF + Stocks)", "PPF + EPF + NPS", "Gold", "FD", "Emergency Fund"]
        values = [
            assets_now.get("equity", 0),
            assets_now.get("ppf", 0) + assets_now.get("epf", 0) + assets_now.get("nps", 0),
            assets_now.get("gold", 0),
            assets_now.get("fd", 0),
            assets_now.get("emergency", 0),
        ]
        values = [max(0, v) for v in values]

        if sum(values) > 0:
            fig2 = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.52,
                marker_colors=["#185FA5", "#3B6D11", "#D4537E", "#EF9F27", "#888780"],
                textinfo="percent+label", textfont_size=11,
            ))
            fig2.update_layout(
                showlegend=False, height=260,
                margin=dict(t=10, b=10, l=10, r=10),
                annotations=[dict(
                    text=f"{cr(total_assets)}<br>total",
                    x=0.5, y=0.5, font_size=13, showarrow=False,
                )],
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig2, use_container_width=True)

        nc1, nc2, nc3 = st.columns(3)
        nc1.metric("Total today", cr(total_assets))
        nc2.metric(f"Projected at {ret_age}", cr(proj["corpus_at_ret"]))
        nc3.metric("Target corpus", cr(proj["corpus_needed"]))

    # ── SECTION 5: DEBT ────────────────────────────────────────────────────────
    debt_rec = debt_priority(
        s.get("loan_interest_rate", 0),
        s.get("loans_outstanding", 0),
        s.get("loan_emi_monthly", 0),
    )
    if debt_rec.get("has_loan"):
        st.markdown("---")
        st.markdown("## 💳 Your Loan")
        box_class = "warn-box" if debt_rec["should_prepay"] else "ok-box"
        prefix = "<b>Pay this loan off before investing in equity.</b><br>" if debt_rec["should_prepay"] else ""
        st.markdown(
            f'<div class="{box_class}">{prefix}{debt_rec["reason"]}</div>',
            unsafe_allow_html=True,
        )

    # ── SECTION 6: GEMINI Q&A ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🤖 Ask Anything About Your Plan")

    plan_ctx = json.dumps({
        "age": age, "city": city, "retirement_age": ret_age,
        "monthly_take_home": sal,
        "monthly_surplus": cf["surplus"],
        "total_savings_today": round(total_assets),
        "retirement_corpus_needed": round(proj["corpus_needed"]),
        "projected_corpus": round(proj["corpus_at_ret"]),
        "on_track": proj["on_track"],
        "gap_or_surplus": round(-proj["gap"]),
        "sip_monthly": s.get("sip_total_monthly", 0),
        "tax_bracket": s.get("bracket_label", ""),
        "old_regime": old_reg,
        "effective_tax_rate_pct": round(slab * 100, 1),
        "has_loan": debt_rec.get("has_loan", False),
        "loan_outstanding": s.get("loans_outstanding", 0),
        "loan_rate": s.get("loan_interest_rate", 0),
        "house_budget": s.get("house_budget", 0),
        "property_appreciation_pct": s.get("property_appr_rate", 6),
        "ppf_balance": s.get("ppf_value", 0),
        "epf_balance": s.get("epf_value", 0),
    }, indent=2)

    # Bracket-aware suggested questions
    suggestions = [
        f"How much more do I need to save to retire at {ret_age - 3}?",
        "Should I increase my SIP or prepay my loan first?",
        "Why does the plan recommend arbitrage fund over FD?",
        "What happens if property prices rise 10% per year instead?",
    ]
    if old_reg:
        suggestions.insert(1, "How much tax will ELSS save me this financial year?")

    st.write("Suggested questions:")
    cols = st.columns(len(suggestions))
    for i, sq in enumerate(suggestions):
        with cols[i]:
            if st.button(sq, key=f"sq_{i}", use_container_width=True):
                st.session_state["gemini_q_text"] = sq

    question = st.text_input(
        "Or type your own question:",
        value=st.session_state.get("gemini_q_text", ""),
        key="gemini_q_input",
    )

    if question:
        with st.spinner("Asking Gemini…"):
            answer = ask_gemini_plan(question, plan_ctx)
        st.markdown(
            f'<div class="tip-box"><b>Answer:</b> {answer}</div>',
            unsafe_allow_html=True,
        )
        # Clear after answering
        st.session_state["gemini_q_text"] = ""

    # ── SECTION 7: KEY HABITS ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📌 The 3 Habits That Determine Everything")
    st.markdown(
        '<div style="display:grid;grid-template-columns:1fr;gap:10px">'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        "<b>1. Increase all SIPs by 10% every April 1</b><br>"
        '<span style="font-size:13px;color:#666">Set a phone alarm. Log in. Increase by 10%. 15 minutes a year.</span></div>'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        "<b>2. Never pause SIPs — cut expenses instead</b><br>"
        '<span style="font-size:13px;color:#666">Pausing 3 months costs more in compounding than it saves.</span></div>'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        "<b>3. 80% of every bonus goes to goals, not upgrades</b><br>"
        '<span style="font-size:13px;color:#666">Emergency fund → house fund → SIP top-up. In that order.</span></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption(
        "⚠️ FinPlan India is a free educational calculator. Not SEBI-registered. "
        "Not financial advice. Projections are estimates — actual returns will differ. "
        "Consult a SEBI-registered investment adviser before making decisions."
    )

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("🔄 Start over", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
