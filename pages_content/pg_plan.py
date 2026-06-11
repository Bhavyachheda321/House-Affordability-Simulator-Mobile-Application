import streamlit as st
import plotly.graph_objects as go
import json, re

from pages_content.calculations import (
    monthly_cashflow, project_retirement_corpus,
    house_scenarios, rent_vs_buy,
    sip_fv, step_up_sip_fv, lumpsum_fv_monthly,
    sip_needed_for_goal, emi_amount, max_loan_for_emi,
    debt_priority, elss_tax_saving,
    EQUITY_RETURN, ARBITRAGE_RETURN, LIQUID_RETURN,
    PPF_RATE, EPF_RATE, NPS_EQUITY_RETURN, GOLD_RETURN
)

# ── helpers ───────────────────────────────────────────────────────────────────
def cr(x):
    if   x >= 1e7: return f"₹{x/1e7:.1f} Cr"
    elif x >= 1e5: return f"₹{x/1e5:.1f}L"
    elif x >= 1e3: return f"₹{x/1e3:.0f}K"
    return f"₹{x:,.0f}"

def pct(x): return f"{x*100:.1f}%"

def card(title, detail, col="#185FA5"):
    bg = {"#185FA5":"#E6F1FB","#A32D2D":"#FCEBEB",
          "#854F0B":"#FAEEDA","#3B6D11":"#EAF3DE"}.get(col,"#E6F1FB")
    return (f'<div style="border:.5px solid #ddd;border-radius:10px;padding:14px 16px;'
            f'margin-bottom:12px;background:var(--background-color)">'
            f'<div style="display:flex;gap:10px;align-items:flex-start">'
            f'<div style="width:10px;height:10px;border-radius:50%;background:{col};'
            f'margin-top:5px;flex-shrink:0"></div>'
            f'<div><div style="font-size:14px;font-weight:500;margin-bottom:3px">{title}</div>'
            f'<div style="font-size:13px;color:#666;line-height:1.6">{detail}</div>'
            f'</div></div></div>')

# ── Gemini Q&A ────────────────────────────────────────────────────────────────
def ask_gemini(question: str, plan_context: str, api_key: str) -> str:
    """Call Gemini Flash to answer a question about the user's plan."""
    try:
        import urllib.request, json as _json
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"gemini-1.5-flash:generateContent?key={api_key}")
        prompt = (
            f"You are a plain-language financial planning assistant for Indian investors. "
            f"The user's financial plan data is below. Answer their question clearly in 3-5 sentences. "
            f"Do not invent numbers. Only use numbers from the plan data provided. "
            f"End with one practical action they can take today.\n\n"
            f"PLAN DATA:\n{plan_context}\n\n"
            f"USER QUESTION: {question}"
        )
        payload = _json.dumps({"contents":[{"parts":[{"text": prompt}]}]}).encode()
        req = urllib.request.Request(url, data=payload,
            headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Could not reach Gemini API: {e}. Check your API key and internet connection."


# ── Main render ───────────────────────────────────────────────────────────────
def render():
    s = st.session_state

    if s.get("monthly_salary", 0) == 0:
        st.warning("Please fill in your income first.")
        if st.button("← Go to income"):
            s["step"] = 1; st.rerun()
        return

    # ── Compute all numbers ───────────────────────────────────────────────────
    cf       = monthly_cashflow(s)
    proj     = project_retirement_corpus(s)
    slab     = s.get("effective_slab_rate", 0.2288)
    old_reg  = s.get("old_regime", False)
    age      = s.get("age", 30)
    ret_age  = s.get("retirement_age", 55)
    yrs      = max(1, ret_age - age)
    infl     = s.get("lifestyle_inflation", 7) / 100
    city     = s.get("city", "Mumbai")
    sal      = s.get("monthly_salary", 0)
    spouse_sal = s.get("spouse_monthly_salary", 0) if s.get("has_spouse_income") else 0
    total_income = cf["income"] + spouse_sal

    total_assets = (s.get("mf_value",0) + s.get("stocks_value",0) +
                    s.get("ppf_value",0) + s.get("epf_value",0) +
                    s.get("nps_value",0) + s.get("fd_value",0) +
                    s.get("gold_value",0) + s.get("rbi_bond_value",0) +
                    s.get("emergency_fund_value",0))

    # Debt priority analysis
    debt_rec = debt_priority(
        s.get("loan_interest_rate", 0),
        s.get("loans_outstanding", 0),
        s.get("loan_emi_monthly", 0))

    # ELSS annual saving
    elss_saving = elss_tax_saving(slab, old_reg)

    st.title("📊 Your financial plan")
    st.caption(f"Age {age} · {city} · Retirement target: age {ret_age} · "
               f"Tax bracket: {s.get('bracket_label','–')} · "
               f"{'Old regime' if old_reg else 'New regime'}")

    # ── SECTION 1: WHAT TO DO THIS MONTH ─────────────────────────────────────
    st.markdown("---")
    st.markdown("## ✅ What to do right now")
    st.write("In order of importance. Do the first item before moving to the second.")

    actions_html = ""
    num = 0

    def act(title, detail, col="#185FA5"):
        nonlocal num, actions_html
        num += 1
        bg = {"#185FA5":"#E6F1FB","#A32D2D":"#FCEBEB",
              "#854F0B":"#FAEEDA","#3B6D11":"#EAF3DE"}.get(col,"#E6F1FB")
        actions_html += (
            f'<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;'
            f'border:.5px solid #ddd;border-radius:10px;padding:14px 16px">'
            f'<div style="width:28px;height:28px;border-radius:50%;background:{bg};color:{col};'
            f'display:flex;align-items:center;justify-content:center;font-size:13px;'
            f'font-weight:600;flex-shrink:0">{num}</div>'
            f'<div><div style="font-size:14px;font-weight:500;margin-bottom:3px">{title}</div>'
            f'<div style="font-size:13px;color:#666;line-height:1.6">{detail}</div>'
            f'</div></div>')

    # A. Emergency fund
    ef_monthly = s.get("monthly_expenses",0) + s.get("family_support_annual",0)/12
    ef_target  = ef_monthly * 6
    ef_have    = s.get("emergency_fund_value",0) if s.get("has_emergency_fund") else 0
    if ef_have < ef_target:
        months_to_build = max(1, int((ef_target - ef_have) / 25000))
        act("🛡 Build your emergency fund first",
            f"Target: {cr(ef_target)} (6 months of expenses). You have {cr(ef_have)} so far. "
            f"Open Parag Parikh or HDFC Liquid Fund on Groww. Invest ₹25,000/month. "
            f"Ready in ~{months_to_build} months. Withdraw any day if needed.", "#A32D2D")

    # B. Debt priority (before investing if high-rate loan)
    if debt_rec.get("has_loan") and debt_rec.get("should_prepay"):
        act("💳 Pay off your loan before investing",
            debt_rec["reason"] + f" Use your monthly surplus of {cr(cf['surplus'])} "
            f"to make extra loan payments first. Once the loan is cleared, redirect everything to investments.",
            "#A32D2D")

    # C. Insurance — age-adjusted premium
    base_premium = 10000 + age * 300  # rough age-scaling
    health_premium = 8000 + (age - 25) * 200
    act("❤️ Buy term life insurance + personal health insurance",
        f"Term cover needed: {cr(sal * 12 * 20)} "
        f"(LIC Tech Term / HDFC Click2Protect / Max Life Smart Term). "
        f"Estimated premium at age {age}: ~₹{base_premium:,.0f}–₹{base_premium+6000:,.0f}/year. "
        f"Personal health insurance: ₹10L cover ~₹{health_premium:,.0f}/year. "
        f"Do NOT rely on employer cover — it stops the day you change jobs.", "#A32D2D")

    # D. ELSS — only if old regime and meaningful bracket
    if old_reg and slab >= 0.15 and not debt_rec.get("should_prepay"):
        act(f"📗 Start ELSS SIP first — saves ₹{elss_saving:,.0f} in tax this year",
            f"You file under the old regime. Investing ₹12,500/month in an ELSS fund (tax-saving MF) "
            f"gives you ₹1,50,000 deduction under 80C — saving ₹{elss_saving:,.0f} in tax annually. "
            f"Best ELSS: Mirae Asset ELSS, Quant ELSS (check Groww ratings). "
            f"3-year lock-in, then treated as equity LTCG.", "#854F0B")

    # E. SIP increase / start — bracket-sensitive instrument choice
    surplus = cf["surplus"] + spouse_sal - s.get("loan_emi_monthly", 0)
    if not debt_rec.get("should_prepay") and surplus > 5000:
        new_sip = int(surplus * 0.75 / 500) * 500

        # Instrument choice differs by bracket
        if slab == 0.0:
            instrument_note = ("You pay no income tax currently, so an FD or liquid fund works "
                               "just as well as arbitrage for short-term goals — keep it simple.")
            arb_note = "For parking money, use Parag Parikh Liquid Fund (7%) or a bank FD."
        elif slab <= 0.15:
            instrument_note = ("At your tax rate, the difference between FD and arbitrage fund is small. "
                               "Prefer a short-duration debt fund for 1-3 year goals.")
            arb_note = "Use Kotak Arbitrage Fund only if your holding is 12+ months."
        else:
            instrument_note = ("At 30%+ tax, arbitrage funds are far more efficient than FDs for "
                               "short-term goals — you pay only 12.5% LTCG after 12 months vs 34.3% on FD interest.")
            arb_note = "For 12+ month parking: Kotak / Nippon Arbitrage Fund. Under 12 months: Liquid fund."

        act(f"📈 Invest {cr(new_sip)} more per month",
            f"You have {cr(surplus)}/month unallocated. Invest {cr(new_sip)}/month in equity index SIPs. "
            f"Suggested split: Nifty 50 (40%) · Nifty Next 50 (30%) · Nifty Midcap 150 (30%). "
            f"{instrument_note} {arb_note}", "#3B6D11")

    # F. Marriage corpus (bracket-sensitive)
    if s.get("want_marriage_savings") and s.get("marriage_cost",0) > 0:
        m_fv = s["marriage_cost"] * (1 + infl) ** s.get("marriage_years", 2)
        if slab >= 0.20:
            instr = "Kotak/Nippon Arbitrage Fund (taxed at equity rates — much better than FD at your tax bracket)"
        elif slab > 0:
            instr = "short-duration debt fund or bank FD (both work fine at your bracket)"
        else:
            instr = "bank FD or liquid fund (simplest option since you pay no tax currently)"
        act(f"💍 Build marriage savings — {cr(m_fv)} needed in {s.get('marriage_years',2)} years",
            f"Open a separate SIP of ₹30,000/month in a {instr}. "
            f"Keep this completely separate from your long-term investments.", "#854F0B")

    # G. Gold
    gold_pct = s.get("gold_value",0) / max(1, total_assets) * 100
    if gold_pct < 5 and total_assets > 200000:
        gold_gap = total_assets * 0.08 - s.get("gold_value",0)
        act(f"🥇 Buy Sovereign Gold Bonds — {cr(gold_gap)} needed (target 8% of savings)",
            f"Your gold is {gold_pct:.0f}% of savings. Buy SGBs on Groww/Zerodha or during RBI windows. "
            f"NOT physical gold — SGBs pay 2.5% annual interest + gold appreciation + zero capital gains tax at maturity. "
            f"Physical gold has no return and high making charges.", "#854F0B")

    # H. PPF (regime-sensitive message)
    if s.get("ppf_value",0) > 0 and s.get("ppf_contributing"):
        if old_reg:
            ppf_note = f"Also saves ₹{150000 * slab:,.0f} in tax via 80C deduction."
        else:
            ppf_note = "No 80C deduction in new regime, but the 7.1% tax-free return is still better than any taxable FD."
        act("📗 Invest full PPF quota (₹1,50,000) on April 1 every year",
            f"Transfer on April 1 — not April 30. Earns interest from the 5th of April onward. "
            f"PPF is EEE: contribution, growth, and withdrawal all tax-free. {ppf_note}", "#3B6D11")

    # I. Annual step-up
    stepup_gain = proj["equity_sip_stepup"] - proj["equity_sip_flat"]
    act("🔁 Increase every SIP by 10% each April — forever",
        f"Set a phone reminder for April 1. Log into Groww/Zerodha, increase each SIP by 10%. "
        f"Over {yrs} years this habit alone adds {cr(stepup_gain)} to your retirement corpus "
        f"compared to keeping SIPs flat. The April step-up + PPF top-up takes 15 minutes and is "
        f"worth more than any stock tip.", "#3B6D11")

    st.markdown(actions_html, unsafe_allow_html=True)

    # ── SECTION 2: WHAT-IF SLIDERS ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🎛 What if I change something?")
    st.write("Adjust these sliders — the retirement projection updates instantly.")

    w1, w2, w3 = st.columns(3)
    with w1:
        what_if_sip = st.slider("Monthly SIP (₹K)", 0, 300,
            int(s.get("sip_total_monthly",0)/1000), step=5,
            key="wi_sip") * 1000
    with w2:
        what_if_ret = st.slider("Retire at age", 40, 70,
            int(s.get("retirement_age",55)), step=1, key="wi_ret")
    with w3:
        what_if_spend = st.slider("Monthly spend at retirement (₹K)", 25, 500,
            int(s.get("retirement_monthly_spend",100000)/1000), step=5,
            key="wi_spend") * 1000

    wi_yrs = max(1, what_if_ret - age)
    wi_post = max(15, 85 - what_if_ret)
    from pages_content.calculations import safe_withdrawal_rate, retirement_corpus_needed
    wi_corpus_needed = retirement_corpus_needed(what_if_spend, infl, wi_yrs, wi_post)
    wi_stepup = step_up_sip_fv(what_if_sip, EQUITY_RETURN, wi_yrs, 0.10)
    wi_flat   = sip_fv(what_if_sip, EQUITY_RETURN, wi_yrs)
    equity_base = s.get("mf_value",0) + s.get("stocks_value",0)
    wi_base_fv  = lumpsum_fv_monthly(equity_base, EQUITY_RETURN, wi_yrs)
    wi_total_stepup = wi_stepup + wi_base_fv + proj["ppf_fv"] + proj["epf_fv"] + proj["nps_usable"] + proj["gold_fv"]
    wi_gap = wi_corpus_needed - wi_total_stepup
    wi_on_track = wi_gap <= 0

    wc1, wc2, wc3 = st.columns(3)
    wc1.metric("Target corpus", cr(wi_corpus_needed),
               help=f"Using {safe_withdrawal_rate(wi_post)*100:.1f}% SWR for {wi_post}yr retirement")
    wc2.metric("Projected (with 10% step-up)", cr(wi_total_stepup),
               delta=cr(wi_total_stepup - wi_corpus_needed),
               delta_color="normal" if wi_on_track else "inverse")
    wc3.metric("Gap / Surplus", cr(abs(wi_gap)),
               delta="✅ On track" if wi_on_track else "❌ Shortfall",
               delta_color="normal" if wi_on_track else "inverse")

    if not wi_on_track:
        extra_needed = sip_needed_for_goal(wi_gap, EQUITY_RETURN, wi_yrs)
        st.markdown(f'<div class="warn-box">To close the {cr(wi_gap)} gap: invest <b>₹{extra_needed:,.0f}/month extra</b>, '
                    f'or retire at age {what_if_ret+3} instead, or reduce retirement spend to '
                    f'{cr(what_if_spend*0.85)}/month.</div>', unsafe_allow_html=True)

    # Corpus trajectory chart
    ages_x, with_y, flat_y = [], [], []
    for a in range(age, what_if_ret + 1):
        y = a - age
        su = step_up_sip_fv(what_if_sip, EQUITY_RETURN, y, 0.10)
        fl = sip_fv(what_if_sip, EQUITY_RETURN, y)
        bfv = lumpsum_fv_monthly(equity_base, EQUITY_RETURN, y)
        ages_x.append(a)
        with_y.append((su + bfv) / 1e7)
        flat_y.append((fl + bfv) / 1e7)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ages_x, y=with_y, mode="lines", fill="tozeroy",
        name="With 10% annual step-up", line=dict(color="#185FA5", width=2.5),
        fillcolor="rgba(24,95,165,0.07)"))
    fig.add_trace(go.Scatter(x=ages_x, y=flat_y, mode="lines",
        name="Flat SIPs (no increase)", line=dict(color="#aaa", width=1.5, dash="dot")))
    fig.add_hline(y=wi_corpus_needed/1e7, line_dash="dash", line_color="#A32D2D",
        annotation_text=f"Target {cr(wi_corpus_needed)}", annotation_position="right")
    fig.update_layout(height=260, margin=dict(t=20,b=20,l=10,r=80),
        xaxis_title="Age", yaxis_title="₹ Crore",
        legend=dict(orientation="h", y=-0.3, font=dict(size=11)),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    # ── SECTION 3: HOUSE ──────────────────────────────────────────────────────
    if s.get("want_house") and s.get("house_budget",0) > 0:
        st.markdown("---")
        st.markdown("## 🏠 Your home purchase plan")

        hs = house_scenarios(s)
        max_loan = hs["max_loan"]
        parents  = s.get("parents_house_contribution",0)

        st.markdown(
            f'Max loan at 40% EMI rule: **{cr(max_loan)}** · '
            f'Stamp duty in {city}: **{hs["stamp_pct"]*100:.0f}%** · '
            f'Family contribution: **{cr(parents)}**')

        # Scenario table
        hcols = st.columns(5)
        for h, t in zip(hcols, ["Year","Age","Property cost","Stamp+reg","You need from savings"]):
            h.markdown(f"**{t}**")
        for sc in hs["scenarios"]:
            c = st.columns(5)
            c[0].write(f"Year {sc['year']}")
            c[1].write(f"{sc['age']}")
            c[2].write(cr(sc['property_cost']))
            c[3].write(cr(sc['stamp_reg']))
            pct_coverage = (equity_base / sc['own_needed'] * 100) if sc['own_needed'] > 0 else 100
            icon = "🟢" if pct_coverage >= 80 else "🟡" if pct_coverage >= 40 else "🔴"
            c[4].write(f"{icon} {cr(sc['own_needed'])}")

        # Rent vs buy
        st.markdown("#### 🏠 vs 📈 Rent + invest — which wins?")
        rvb_yr = st.slider("Evaluate: buy at year…", 1, 10, 5, key="rvb")
        rvb = rent_vs_buy(s, rvb_yr)

        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("**Buy path**")
            st.write(f"Property at purchase: {cr(rvb['prop_at_buy'])}")
            st.write(f"Stamp + registration: {cr(rvb['stamp_cost'])}")
            st.write(f"Monthly EMI: ₹{rvb['monthly_emi']:,.0f}")
            st.write(f"Annual maintenance: {cr(rvb['annual_maint'])}")
            st.write(f"Property value in {rvb['horizon']}yr: {cr(rvb['prop_at_buy'] * (1 + s.get('property_appr_rate',7)/100)**rvb['horizon'])}")
            st.markdown(f"**Net equity: {cr(rvb['buy_net_equity'])}**")
        with rc2:
            st.markdown("**Rent + invest path**")
            st.write(f"Monthly rent: ₹{rvb['monthly_rent']:,.0f}")
            if rvb['hra_saving_monthly'] > 0:
                st.write(f"HRA tax saving: ₹{rvb['hra_saving_monthly']:,.0f}/mo (old regime)")
            st.write(f"Down payment invested at 12%: included")
            st.write(f"Rent after {rvb['horizon']}yr: ₹{rvb['rent_at_end']:,.0f}/mo")
            st.markdown(f"**Total financial corpus: {cr(rvb['rent_corpus'])}**")

        diff = abs(rvb['difference'])
        if rvb['buy_wins']:
            st.markdown(f'<div class="ok-box"><b>🏠 Buying wins</b> by {cr(diff)} over {rvb["horizon"]} years '
                        f'at {s.get("property_appr_rate",7):.0f}% property appreciation in {city}. '
                        f'But the {cr(rvb["stamp_cost"])} stamp duty is a real upfront cost.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warn-box"><b>📈 Renting + investing wins</b> by {cr(diff)} on pure numbers. '
                        f'However: rent at ₹{rvb["rent_at_end"]:,.0f}/month in {rvb["horizon"]} years '
                        f'is a real ongoing liability — a fixed corpus funding an ever-rising rent is risky at retirement.</div>',
                        unsafe_allow_html=True)

    # ── SECTION 4: NET WORTH PICTURE ─────────────────────────────────────────
    if total_assets > 0:
        st.markdown("---")
        st.markdown("## 💼 Where your money is today")

        labels = ["Mutual funds & stocks","PPF + EPF + NPS","Gold","FD + RBI Bond","Emergency fund"]
        values = [s.get("mf_value",0)+s.get("stocks_value",0),
                  s.get("ppf_value",0)+s.get("epf_value",0)+s.get("nps_value",0),
                  s.get("gold_value",0),
                  s.get("fd_value",0)+s.get("rbi_bond_value",0),
                  s.get("emergency_fund_value",0)]
        values = [max(0,v) for v in values]
        if sum(values) > 0:
            fig2 = go.Figure(go.Pie(labels=labels, values=values, hole=0.52,
                marker_colors=["#185FA5","#3B6D11","#D4537E","#EF9F27","#888780"],
                textinfo="percent+label", textfont_size=11))
            fig2.update_layout(showlegend=False, height=260,
                margin=dict(t=10,b=10,l=10,r=10),
                annotations=[dict(text=f"{cr(total_assets)}<br>total",
                    x=0.5,y=0.5,font_size=13,showarrow=False)],
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

        nc1, nc2, nc3 = st.columns(3)
        nc1.metric("Total savings", cr(total_assets))
        nc2.metric(f"Projected at {ret_age}", cr(proj["total_stepup"]))
        nc3.metric("Target corpus", cr(proj["corpus_needed"]))

    # ── SECTION 5: DEBT REPAYMENT ─────────────────────────────────────────────
    if debt_rec.get("has_loan"):
        st.markdown("---")
        st.markdown("## 💳 Your loan")
        if debt_rec["should_prepay"]:
            st.markdown(f'<div class="warn-box"><b>Pay this loan off before investing.</b> '
                        f'{debt_rec["reason"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ok-box">{debt_rec["reason"]}</div>', unsafe_allow_html=True)

    # ── SECTION 6: GEMINI Q&A ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 🤖 Ask a question about your plan")

    with st.expander("Ask AI — type any question about your finances"):
        st.markdown('<p class="skip-note">Powered by Google Gemini. Enter your free API key from aistudio.google.com</p>', unsafe_allow_html=True)

        api_key = st.text_input("Gemini API key (free at aistudio.google.com)",
            value=st.session_state.get("gemini_api_key",""),
            type="password", key="gemini_key_input",
            placeholder="AIza...")
        if api_key:
            st.session_state["gemini_api_key"] = api_key

        # Suggested questions — bracket-aware
        suggestions = [
            "Why does the plan recommend arbitrage fund over FD for me?",
            f"What happens if I delay buying the house by 3 more years?",
            f"How much more do I need to invest to retire at age {what_if_ret - 3}?",
            "Should I increase my SIP or prepay my loan first?",
        ]
        if old_reg:
            suggestions.insert(1, "How much tax will ELSS save me this year?")

        st.write("Suggested questions:")
        for sq in suggestions:
            if st.button(sq, key=f"sq_{sq[:20]}"):
                st.session_state["gemini_question"] = sq

        question = st.text_input("Or type your own question:",
            value=st.session_state.get("gemini_question",""),
            key="gemini_q_input")

        if st.button("Get answer →", type="primary") and question:
            if not st.session_state.get("gemini_api_key"):
                st.warning("Please enter your Gemini API key above. Get one free at aistudio.google.com")
            else:
                plan_ctx = json.dumps({
                    "age": age, "city": city, "retirement_age": ret_age,
                    "monthly_salary": sal, "monthly_surplus": cf["surplus"],
                    "total_savings": total_assets,
                    "retirement_corpus_needed": round(proj["corpus_needed"]),
                    "projected_corpus_with_stepup": round(proj["total_stepup"]),
                    "on_track": proj["gap_stepup"] <= 0,
                    "gap_or_surplus": round(-proj["gap_stepup"]),
                    "sip_monthly": s.get("sip_total_monthly",0),
                    "tax_bracket": s.get("bracket_label",""),
                    "old_regime": old_reg,
                    "effective_slab_pct": round(slab*100,1),
                    "has_loan": debt_rec.get("has_loan",False),
                    "loan_outstanding": s.get("loans_outstanding",0),
                    "loan_rate": s.get("loan_interest_rate",0),
                    "house_budget": s.get("house_budget",0),
                    "ppf_value": s.get("ppf_value",0),
                    "city_property_appr_pct": s.get("property_appr_rate",7),
                }, indent=2)
                with st.spinner("Asking Gemini…"):
                    answer = ask_gemini(question, plan_ctx, st.session_state["gemini_api_key"])
                st.markdown(f'<div class="tip-box"><b>Answer:</b> {answer}</div>', unsafe_allow_html=True)

    # ── Key habits ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📌 The 3 habits that determine everything")
    st.markdown(
        '<div style="display:grid;grid-template-columns:1fr;gap:10px">'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        '<b>1. Increase SIPs 10% every April</b><br>'
        '<span style="font-size:13px;color:#666">Set a phone alarm. Log in. Increase by 10%. 15 minutes a year.</span></div>'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        '<b>2. Never pause SIPs — cut expenses instead</b><br>'
        '<span style="font-size:13px;color:#666">Pausing 3 months costs more in compounding than it saves.</span></div>'
        '<div style="border:.5px solid #ddd;border-radius:10px;padding:14px">'
        '<b>3. 80% of every bonus goes to goals, not upgrades</b><br>'
        '<span style="font-size:13px;color:#666">Emergency fund → house fund → SIP top-up. In that order.</span></div>'
        '</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("⚠️ FinPlan India is a free educational calculator. Not SEBI-registered. "
               "Not financial advice. Returns assumed may not be achieved. "
               "Consult a SEBI-registered investment adviser before making decisions.")

    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("🔄 Start over", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
