import streamlit as st
import pandas as pd
import math
import json

st.set_page_config(
    page_title="Can I Buy a Home?",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# CSS — mobile-first, clean, warm
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');
:root{
  --bg:#f7f9fc;--surface:#ffffff;--surface2:#f0f4f8;
  --border:#dde3ed;--border-dark:#b8c4d4;
  --accent:#1a5fce;--accent-dark:#1349a8;--accent-soft:#e8f0fb;
  --green:#15622f;--green-bg:#d6f5e3;--green-border:#6ee7a0;
  --red:#9b1c1c;--red-bg:#fde8e8;--red-border:#f8a0a0;
  --amber:#854d0e;--amber-bg:#fef3c7;--amber-border:#fcd34d;
  --text:#0f172a;--text2:#334155;--text3:#64748b;
  --r:14px;--rs:9px;
  --sh:0 2px 8px rgba(0,0,0,.07);
  --sh2:0 6px 20px rgba(0,0,0,.10);
}
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif !important;color:var(--text) !important;}
.stApp{background:var(--bg) !important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:.8rem 1rem 4rem !important;max-width:680px;margin:auto;}

/* Hero */
.hero{background:linear-gradient(135deg,#1a5fce,#2d4a9e 55%,#1e3a8a);border-radius:var(--r);
  padding:1.6rem 1.4rem 1.3rem;margin-bottom:1rem;box-shadow:var(--sh2);}
.hero-title{font-size:1.6rem;font-weight:800;color:#fff;margin:0 0 .3rem;letter-spacing:-.02em;}
.hero-sub{font-size:.88rem;color:rgba(255,255,255,.85);font-weight:500;line-height:1.5;margin:0;}

/* Cards */
.card{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--r);
  padding:1.2rem 1rem;margin-bottom:.9rem;box-shadow:var(--sh);}
.card-title{font-size:.75rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  color:var(--text3);margin-bottom:.7rem;}

/* Persona buttons */
.persona-grid{display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin:.5rem 0;}
.persona-btn{background:var(--surface);border:2px solid var(--border);border-radius:var(--r);
  padding:.8rem .7rem;cursor:pointer;text-align:left;transition:all .15s;}
.persona-btn:hover{border-color:var(--accent);background:var(--accent-soft);}
.persona-btn.active{border-color:var(--accent);background:var(--accent-soft);}
.persona-icon{font-size:1.5rem;display:block;margin-bottom:.3rem;}
.persona-name{font-size:.82rem;font-weight:700;color:var(--text);}
.persona-desc{font-size:.72rem;color:var(--text3);margin-top:.1rem;}

/* Result banner */
.result-banner{border-radius:var(--r);padding:1.3rem 1.2rem;margin-bottom:.9rem;
  border:2px solid;display:flex;align-items:flex-start;gap:1rem;box-shadow:var(--sh);}
.result-banner.ok{background:var(--green-bg);border-color:var(--green-border);}
.result-banner.no{background:var(--red-bg);border-color:var(--red-border);}
.result-banner .emoji{font-size:2rem;flex-shrink:0;line-height:1;}
.result-banner .rb-title{font-size:1.2rem;font-weight:800;line-height:1.2;}
.result-banner .rb-sub{font-size:.82rem;margin-top:.3rem;font-weight:500;line-height:1.6;}
.result-banner.ok .rb-title{color:var(--green);}
.result-banner.ok .rb-sub{color:#166534cc;}
.result-banner.no .rb-title{color:var(--red);}
.result-banner.no .rb-sub{color:var(--red);}

/* Narrative box */
.narrative{background:var(--surface);border-left:4px solid var(--accent);
  border-radius:0 var(--rs) var(--rs) 0;padding:1rem 1.1rem;
  font-size:.88rem;color:var(--text2);line-height:1.75;margin-bottom:.9rem;
  box-shadow:var(--sh);}
.narrative b{color:var(--text);}

/* KPI row */
.kpi-row{display:grid;grid-template-columns:repeat(2,1fr);gap:.6rem;margin-bottom:.9rem;}
.kpi{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--rs);
  padding:.85rem .9rem;box-shadow:var(--sh);}
.kpi .kl{font-size:.68rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--text3);margin-bottom:.3rem;}
.kpi .kv{font-size:1.25rem;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--text);}
.kpi .kd{font-size:.72rem;color:var(--text3);margin-top:.2rem;}
.kpi.accent{border-color:#93c5fd;background:#eff6ff;}.kpi.accent .kv{color:var(--accent-dark);}
.kpi.green{border-color:var(--green-border);background:var(--green-bg);}.kpi.green .kv{color:var(--green);}

/* Section header */
.sh{display:flex;align-items:center;gap:.5rem;margin:1.2rem 0 .6rem;
  padding-bottom:.5rem;border-bottom:2px solid var(--border);}
.sh .ic{width:28px;height:28px;background:var(--accent-soft);border-radius:7px;
  display:flex;align-items:center;justify-content:center;font-size:.9rem;flex-shrink:0;}
.sh h3{font-size:.82rem;font-weight:700;text-transform:uppercase;color:var(--text);margin:0;}

/* Inputs */
.stNumberInput>div>div>input,.stTextInput>div>div>input{
  background:var(--surface) !important;border:1.5px solid var(--border) !important;
  border-radius:var(--rs) !important;color:var(--text) !important;
  font-family:'Plus Jakarta Sans',sans-serif !important;font-size:.9rem !important;font-weight:500 !important;}
.stNumberInput>div>div>input:focus,.stTextInput>div>div>input:focus{
  border-color:var(--accent) !important;box-shadow:0 0 0 3px rgba(26,95,206,.15) !important;}
.stSelectbox>div>div{background:var(--surface) !important;border:1.5px solid var(--border) !important;
  border-radius:var(--rs) !important;color:var(--text) !important;}
label[data-testid="stWidgetLabel"]>div,label[data-testid="stWidgetLabel"] p{
  font-size:.75rem !important;font-weight:700 !important;color:var(--text2) !important;
  letter-spacing:.04em !important;text-transform:uppercase !important;}

/* Slider */
.stSlider>div{padding:0 !important;}
.stSlider [data-baseweb="slider"] [role="slider"]{
  background:var(--accent) !important;border-color:var(--accent) !important;}

/* Expander */
details>summary{background:var(--surface2) !important;border:1.5px solid var(--border) !important;
  border-radius:var(--rs) !important;padding:.55rem .9rem !important;
  font-size:.83rem !important;font-weight:600 !important;color:var(--text) !important;}
details>div{background:var(--surface) !important;border:1.5px solid var(--border) !important;
  border-top:none !important;border-radius:0 0 var(--rs) var(--rs) !important;padding:.7rem .9rem !important;}

/* Buttons */
.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#1a5fce,#2d4a9e) !important;border:none !important;
  border-radius:var(--rs) !important;color:#fff !important;font-weight:700 !important;
  font-size:.92rem !important;padding:.65rem 1.6rem !important;
  box-shadow:0 3px 10px rgba(26,95,206,.3) !important;transition:all .2s !important;
  width:100% !important;}
.stButton>button[kind="primary"]:hover{transform:translateY(-1px) !important;
  box-shadow:0 5px 18px rgba(26,95,206,.45) !important;}
.stButton>button[kind="secondary"],.stButton>button:not([kind]){
  background:var(--surface) !important;border:1.5px solid var(--border-dark) !important;
  border-radius:var(--rs) !important;color:var(--text2) !important;font-weight:600 !important;}
.stDownloadButton>button{background:var(--surface) !important;
  border:1.5px solid var(--border-dark) !important;border-radius:var(--rs) !important;
  color:var(--text) !important;font-weight:600 !important;width:100% !important;}

/* What-if card */
.whatif-card{background:var(--amber-bg);border:1.5px solid var(--amber-border);
  border-radius:var(--r);padding:1rem 1.1rem;margin-bottom:.9rem;}
.whatif-title{font-size:.75rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--amber);margin-bottom:.5rem;}

/* Advanced mode link */
.adv-link{background:var(--surface2);border:1.5px solid var(--border);border-radius:var(--rs);
  padding:.7rem 1rem;font-size:.82rem;color:var(--text2);text-align:center;margin-top:1rem;}
.adv-link a{color:var(--accent);font-weight:700;text-decoration:none;}

/* Misc */
hr{border-color:var(--border) !important;margin:1rem 0 !important;}
.stCheckbox label p{font-size:.85rem !important;color:var(--text2) !important;font-weight:500 !important;}
.stRadio label p{font-size:.85rem !important;color:var(--text2) !important;font-weight:500 !important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-thumb{background:var(--border-dark);border-radius:3px;}
.stAlert{border-radius:var(--rs) !important;}
[data-testid="metric-container"]{background:var(--surface) !important;
  border:1.5px solid var(--border) !important;border-radius:var(--rs) !important;
  padding:.8rem 1rem !important;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# DATA: City × BHK lookup table
# Prices are approximate mid-2024 ready-to-move market rates
# in ₹ (total flat price, not per sqft)
# ─────────────────────────────────────────────────────────────
CITY_BHK_PRICES = {
    "Mumbai":      {"1BHK":8_500_000,"2BHK":15_000_000,"3BHK":25_000_000,"4BHK":40_000_000,"5BHK":65_000_000,"Villa":120_000_000},
    "Delhi NCR":   {"1BHK":5_500_000,"2BHK":9_500_000, "3BHK":16_000_000,"4BHK":28_000_000,"5BHK":45_000_000,"Villa":80_000_000},
    "Bengaluru":   {"1BHK":5_000_000,"2BHK":9_000_000, "3BHK":15_000_000,"4BHK":25_000_000,"5BHK":40_000_000,"Villa":70_000_000},
    "Hyderabad":   {"1BHK":4_500_000,"2BHK":8_000_000, "3BHK":13_000_000,"4BHK":22_000_000,"5BHK":35_000_000,"Villa":60_000_000},
    "Pune":        {"1BHK":4_000_000,"2BHK":7_500_000, "3BHK":12_000_000,"4BHK":20_000_000,"5BHK":32_000_000,"Villa":55_000_000},
    "Chennai":     {"1BHK":4_200_000,"2BHK":7_800_000, "3BHK":13_500_000,"4BHK":22_000_000,"5BHK":35_000_000,"Villa":58_000_000},
    "Kolkata":     {"1BHK":3_500_000,"2BHK":6_000_000, "3BHK":10_000_000,"4BHK":17_000_000,"5BHK":28_000_000,"Villa":45_000_000},
    "Ahmedabad":   {"1BHK":3_000_000,"2BHK":5_500_000, "3BHK":9_500_000, "4BHK":16_000_000,"5BHK":26_000_000,"Villa":42_000_000},
    "Other City":  {"1BHK":3_000_000,"2BHK":5_000_000, "3BHK":8_500_000, "4BHK":14_000_000,"5BHK":22_000_000,"Villa":38_000_000},
}

CITY_BHK_SQFT = {
    "Mumbai":      {"1BHK":450,"2BHK":750,"3BHK":1100,"4BHK":1600,"5BHK":2200,"Villa":3500},
    "Delhi NCR":   {"1BHK":500,"2BHK":900,"3BHK":1400,"4BHK":2000,"5BHK":2800,"Villa":4500},
    "Bengaluru":   {"1BHK":550,"2BHK":950,"3BHK":1500,"4BHK":2100,"5BHK":3000,"Villa":4800},
    "Hyderabad":   {"1BHK":600,"2BHK":1000,"3BHK":1600,"4BHK":2200,"5BHK":3200,"Villa":5000},
    "Pune":        {"1BHK":550,"2BHK":950,"3BHK":1500,"4BHK":2000,"5BHK":2900,"Villa":4500},
    "Chennai":     {"1BHK":500,"2BHK":900,"3BHK":1400,"4BHK":2000,"5BHK":2800,"Villa":4500},
    "Kolkata":     {"1BHK":600,"2BHK":1050,"3BHK":1600,"4BHK":2200,"5BHK":3000,"Villa":5000},
    "Ahmedabad":   {"1BHK":650,"2BHK":1100,"3BHK":1700,"4BHK":2400,"5BHK":3300,"Villa":5500},
    "Other City":  {"1BHK":600,"2BHK":1000,"3BHK":1600,"4BHK":2200,"5BHK":3000,"Villa":5000},
}

CITY_INFL = {
    "Mumbai":8.5,"Delhi NCR":7.5,"Bengaluru":8.0,"Hyderabad":9.0,
    "Pune":8.0,"Chennai":7.5,"Kolkata":6.5,"Ahmedabad":7.0,"Other City":7.0,
}

# ─────────────────────────────────────────────────────────────
# PERSONAS
# ─────────────────────────────────────────────────────────────
PERSONAS = {
    "salaried_mid": {
        "label": "Salaried Professional",
        "icon": "🧑‍💼",
        "desc": "₹75K–₹2L/month take-home",
        "take_home": 100_000,
        "inc_growth": 10.0,
        "exp_frac": 0.45,
        "savings_existing": 1_500_000,
        "monthly_sip": 15_000,
        "sip_return": 12.0,
        "bonus": 100_000,
        "tx_cost": 7.0,
        "cash_buf_months": 6,
        "loan_rate": 8.75,
        "loan_tenure": 20,
        "emi_frac": 0.40,
        "bank_mult": 60,
        "type": "salaried",
    },
    "family": {
        "label": "Family / Home Upgrade",
        "icon": "👨‍👩‍👧",
        "desc": "Dual income or upgrading",
        "take_home": 180_000,
        "inc_growth": 9.0,
        "exp_frac": 0.50,
        "savings_existing": 3_500_000,
        "monthly_sip": 25_000,
        "sip_return": 11.0,
        "bonus": 200_000,
        "tx_cost": 7.0,
        "cash_buf_months": 6,
        "loan_rate": 8.75,
        "loan_tenure": 20,
        "emi_frac": 0.40,
        "bank_mult": 60,
        "type": "salaried",
    },
    "couple_dual": {
        "label": "Dual-Income Couple",
        "icon": "🧑‍🤝‍🧑",
        "desc": "Two salaries, buying together",
        "take_home": 250_000,
        "inc_growth": 10.0,
        "exp_frac": 0.42,
        "savings_existing": 4_000_000,
        "monthly_sip": 35_000,
        "sip_return": 12.0,
        "bonus": 300_000,
        "tx_cost": 7.0,
        "cash_buf_months": 4,
        "loan_rate": 8.5,
        "loan_tenure": 20,
        "emi_frac": 0.38,
        "bank_mult": 60,
        "type": "salaried",
    },
    "self_employed": {
        "label": "Self-Employed / Business",
        "icon": "🏢",
        "desc": "Business owner or freelancer",
        "take_home": 150_000,
        "inc_growth": 12.0,
        "exp_frac": 0.48,
        "savings_existing": 2_500_000,
        "monthly_sip": 20_000,
        "sip_return": 12.0,
        "bonus": 0,
        "tx_cost": 7.0,
        "cash_buf_months": 9,   # larger buffer for irregular income
        "loan_rate": 9.25,      # slightly higher rate for self-employed
        "loan_tenure": 15,
        "emi_frac": 0.35,
        "bank_mult": 48,        # banks are more conservative
        "type": "self_employed",
    },
}

# ─────────────────────────────────────────────────────────────
# FINANCIAL ENGINE (self-contained, no external deps)
# ─────────────────────────────────────────────────────────────

def emi_monthly(principal, r_ann, years):
    if principal <= 0 or years <= 0: return 0.0
    n = years * 12
    if r_ann == 0: return principal / n
    r = r_ann / 12
    return principal * r * ((1+r)**n) / (((1+r)**n) - 1)

def max_loan_from_emi(emi, r_ann, years):
    if emi <= 0 or years <= 0: return 0.0
    n = years * 12
    if r_ann == 0: return emi * n
    r = r_ann / 12
    return emi * (((1+r)**n) - 1) / (r * ((1+r)**n))

def simulate(p):
    """
    p keys (all required):
      age, max_age, take_home_0, inc_growth, exp_frac,
      savings_0, monthly_sip, sip_return, sip_stepup,
      bonus_annual, house_price, house_infl, tx_cost,
      cash_buf_months, buf_infl, loan_rate, loan_tenure,
      emi_frac, bank_mult, user_max_loan,
      persona_type  ('salaried' | 'self_employed')
      se_volatility_months  (self-employed: extra buffer months)
      income_volatility_pct (self-employed: % of months that are lean)
    """
    max_years = p['max_age'] - p['age']
    rows = []

    portfolio = p['savings_0']
    r_monthly = (1 + p['sip_return']/100) ** (1/12) - 1

    for t in range(max_years + 1):
        age = p['age'] + t
        take_home = p['take_home_0'] * ((1 + p['inc_growth']/100) ** t)
        expenses  = take_home * p['exp_frac']
        rent      = p.get('rent_0', 0) * ((1 + p.get('rent_infl', 0.08)) ** t)

        # For self-employed: reduce effective income by volatility adjustment
        if p.get('persona_type') == 'self_employed':
            vol_pct = p.get('income_volatility_pct', 20) / 100
            lean_discount = vol_pct * 0.40  # lean months earn ~40% less
            take_home = take_home * (1 - lean_discount)

        bonus = p.get('bonus_annual', 0) * ((1 + p.get('bonus_growth', 0.08)) ** t)
        surplus_yr = max(0., (take_home - expenses - rent) * 12 + bonus)

        # SIP with stepup
        sip_yr_monthly = p['monthly_sip'] * ((1 + p.get('sip_stepup', 5)/100) ** t)

        # Portfolio growth: existing grows at sip_return, new SIPs added monthly
        portfolio = portfolio * (1 + p['sip_return']/100)
        portfolio += sip_yr_monthly * 12  # simplified annual addition

        # Surplus invested in same asset
        surplus_invested = max(0., surplus_yr - sip_yr_monthly * 12)
        portfolio += surplus_invested

        # House price this year
        h_t = p['house_price'] * ((1 + p['house_infl']/100) ** t)
        outlay = h_t * (1 + p['tx_cost']/100)

        # Required cash buffer
        buf_months = p['cash_buf_months']
        if p.get('persona_type') == 'self_employed':
            buf_months = max(buf_months, p.get('se_volatility_months', 9))
        req_buf = take_home * buf_months

        # Loan eligibility
        emi_cap = take_home * p['emi_frac']
        max_loan = min(
            max_loan_from_emi(emi_cap, p['loan_rate']/100, p['loan_tenure']),
            take_home * 12 * p['bank_mult'] / 12  # bank_mult as monthly×12 gross proxy
        )
        if p.get('user_max_loan', 0) > 0:
            max_loan = min(max_loan, p['user_max_loan'])

        actual_loan = min(max_loan, outlay)
        down_payment = max(0., outlay - actual_loan)
        cash_after   = portfolio - down_payment
        actual_emi   = emi_monthly(actual_loan, p['loan_rate']/100, p['loan_tenure'])

        c1 = (portfolio + max_loan) >= outlay
        c2 = cash_after >= req_buf
        c3 = actual_emi <= emi_cap
        affordable = c1 and c2 and c3

        # Affordable sqft
        target_sqft = p.get('target_sqft', 0)
        if target_sqft > 0 and h_t > 0:
            psf = (h_t * (1 + p['tx_cost']/100)) / target_sqft
            net_budget = portfolio + max_loan - req_buf
            aff_sqft = max(0., net_budget / psf)
        else:
            aff_sqft = 0.0

        rows.append({
            'age': age, 'take_home': take_home, 'surplus_yr': surplus_yr,
            'portfolio': portfolio, 'house_price': h_t, 'outlay': outlay,
            'max_loan': max_loan, 'actual_loan': actual_loan,
            'actual_emi': actual_emi, 'emi_cap': emi_cap,
            'cash_after': cash_after, 'req_buf': req_buf,
            'down_payment': down_payment,
            'affordable': affordable, 'aff_sqft': aff_sqft,
            'c1': c1, 'c2': c2, 'c3': c3,
        })

    return rows


def first_affordable(rows):
    for r in rows:
        if r['affordable']:
            return r
    return None


def build_narrative(rows, p, first):
    age_now = p['age']
    target_sqft = p.get('target_sqft', 0)
    flat_label = p.get('flat_label', 'home')
    city = p.get('city', 'your city')

    if first is None:
        last = rows[-1]
        gap = last['house_price'] - last['portfolio'] - last['max_loan']
        return (
            f"Based on your current numbers, your <b>target {flat_label} in {city}</b> "
            f"isn't affordable by age {p['max_age']}. "
            f"At age {p['max_age']}, your portfolio will be "
            f"<b>₹{last['portfolio']/1e7:.1f} Cr</b> and maximum loan "
            f"<b>₹{last['max_loan']/1e7:.1f} Cr</b>, still short by roughly "
            f"<b>₹{max(0,gap)/1e5:.0f}L</b>. "
            f"The biggest levers are: increase your monthly SIP, negotiate a larger loan, "
            f"or consider a slightly smaller home to start with."
        )

    yrs = first['age'] - age_now
    yr_word = "this year" if yrs == 0 else f"in <b>{yrs} year{'s' if yrs>1 else ''}</b>"

    # identify which test is the binding constraint in years before first
    failing_rows = [r for r in rows if not r['affordable'] and r['age'] < first['age']]
    constraint = ""
    if failing_rows:
        last_fail = failing_rows[-1]
        if not last_fail['c1']:
            constraint = "Your portfolio + loan wasn't enough to cover the full outlay."
        elif not last_fail['c2']:
            constraint = "You didn't have enough cash left over after the down payment."
        elif not last_fail['c3']:
            constraint = "The EMI was above your comfortable limit."

    sqft_note = ""
    if target_sqft > 0:
        sqft_note = f" That's a <b>{target_sqft} sq ft</b> home at today's rate in {city}."

    return (
        f"You can afford your <b>{flat_label} in {city}</b> {yr_word}, at age <b>{first['age']}</b>.{sqft_note} "
        f"By then your portfolio will be <b>₹{first['portfolio']/1e7:.1f} Cr</b>, "
        f"you'll take a loan of <b>₹{first['actual_loan']/1e7:.1f} Cr</b> "
        f"at an EMI of <b>₹{first['actual_emi']/1000:.0f}K/month</b>, "
        f"and you'll still have <b>₹{first['cash_after']/1e5:.0f}L</b> left as emergency reserve. "
        + (f"The main constraint before this age: {constraint} " if constraint else "")
        + f"Your biggest risk is property inflation — at {p['house_infl']}%/year, "
        f"every year you delay adds roughly "
        f"<b>₹{(first['house_price']*p['house_infl']/100)/1e5:.0f}L</b> to the price."
    )


# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
def _ss(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

_ss('step', 'persona')          # persona | questionnaire | results
_ss('persona_key', None)
_ss('params', {})
_ss('sim_rows', None)
_ss('whatif', {})


def reset():
    for k in ['step','persona_key','params','sim_rows','whatif']:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


# ─────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🏠 Can I Buy a Home?</div>
  <div class="hero-sub">Answer 5 questions. Get a clear, honest answer — no jargon, no guesswork.</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# STEP 1 — PERSONA
# ─────────────────────────────────────────────────────────────
if st.session_state['step'] == 'persona':
    st.markdown("""
    <div class="sh"><div class="ic">👋</div><h3>Who are you?</h3></div>
    <p style="font-size:.88rem;color:#334155;margin-bottom:.8rem;">
    Pick the option that best describes you. We'll pre-fill sensible numbers you can tweak.
    </p>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    persona_items = list(PERSONAS.items())
    for idx, (pk, pv) in enumerate(persona_items):
        with cols[idx % 2]:
            is_active = st.session_state['persona_key'] == pk
            border_c = "#1a5fce" if is_active else "#dde3ed"
            bg_c = "#e8f0fb" if is_active else "#ffffff"
            st.markdown(f"""
            <div style="background:{bg_c};border:2.5px solid {border_c};border-radius:14px;
              padding:.9rem .8rem;margin-bottom:.5rem;cursor:pointer;">
              <span style="font-size:1.6rem">{pv['icon']}</span>
              <div style="font-size:.84rem;font-weight:700;color:#0f172a;margin-top:.25rem">{pv['label']}</div>
              <div style="font-size:.72rem;color:#64748b;margin-top:.1rem">{pv['desc']}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Select", key=f"sel_{pk}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state['persona_key'] = pk
                st.rerun()

    if st.session_state['persona_key']:
        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
        if st.button("Continue →", type="primary"):
            st.session_state['step'] = 'questionnaire'
            st.rerun()


# ─────────────────────────────────────────────────────────────
# STEP 2 — QUESTIONNAIRE
# ─────────────────────────────────────────────────────────────
elif st.session_state['step'] == 'questionnaire':
    pk = st.session_state['persona_key']
    pv = PERSONAS[pk]
    is_se = pv['type'] == 'self_employed'

    st.markdown(f"""
    <div class="sh"><div class="ic">{pv['icon']}</div>
    <h3>Tell us about yourself</h3></div>
    <p style="font-size:.84rem;color:#64748b;margin-bottom:.8rem;">
    We've pre-filled typical numbers for a <b>{pv['label']}</b>. Change anything that doesn't fit.
    </p>""", unsafe_allow_html=True)

    # ── Q1: The home ──
    st.markdown('<div class="card"><div class="card-title">🏡 The Home You Want</div>', unsafe_allow_html=True)
    city = st.selectbox("Which city?",
        options=list(CITY_BHK_PRICES.keys()), index=0,
        help="We'll use typical prices for this city. You can override below.")
    bhk  = st.selectbox("What size home?",
        options=["1BHK","2BHK","3BHK","4BHK","5BHK","Villa"], index=1,
        help="Pick the flat type you're planning to buy.")

    default_price = CITY_BHK_PRICES[city][bhk]
    default_sqft  = CITY_BHK_SQFT[city][bhk]
    default_infl  = CITY_INFL[city]

    knows_price = st.checkbox("I know the exact price / sq ft rate in my area",
        help="Tick this if you've done research and know the current market price.")
    if knows_price:
        col_p, col_s = st.columns(2)
        with col_p:
            house_price = st.number_input("House Price Today (₹)", value=default_price,
                step=500_000, min_value=500_000,
                help="Total cost of the flat you want to buy today.")
        with col_s:
            target_sqft = st.number_input("Size (sq ft)", value=default_sqft,
                step=50, min_value=100,
                help="Carpet area in sq ft.")
    else:
        house_price = default_price
        target_sqft = default_sqft
        st.info(f"📍 Using typical {bhk} price in {city}: **₹{house_price/1e7:.1f} Cr** "
                f"({target_sqft} sq ft at ₹{house_price//target_sqft:,}/sq ft)", icon="ℹ️")

    house_infl = st.slider("How fast do you expect prices to rise? (%/year)",
        min_value=4.0, max_value=15.0, value=float(default_infl), step=0.5,
        help="Higher = harder to catch up. Metro cities average 7–10%.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Q2: Your income ──
    st.markdown('<div class="card"><div class="card-title">💰 Your Income</div>', unsafe_allow_html=True)
    if is_se:
        st.caption("Self-employed income is averaged over good and lean months.")
        take_home = st.number_input("Average Monthly Take-Home (₹)",
            value=pv['take_home'], step=5_000, min_value=10_000,
            help="Your typical monthly in-hand earnings, averaged across the year.")
        se_vol = st.slider("How many months per year are 'lean' months?",
            min_value=0, max_value=6, value=2,
            help="Months where income is significantly lower than average.")
        income_vol_pct = (se_vol / 12) * 100
        buf_months = st.slider("How many months of expenses to keep as safety buffer?",
            min_value=3, max_value=18, value=pv['cash_buf_months'],
            help="Self-employed: keep more buffer for dry spells. 9–12 months recommended.")
        rent_0 = st.number_input("Current Monthly Rent (₹)", value=20_000,
            step=1_000, min_value=0,
            help="Rent you pay today. Assumed to stop when you buy the house.")
    else:
        take_home = st.number_input("Monthly Take-Home Salary (₹)",
            value=pv['take_home'], step=5_000, min_value=10_000,
            help="Your in-hand salary after all deductions.")
        income_vol_pct = 0
        se_vol = 0
        buf_months = st.slider("Months of salary to keep as emergency buffer",
            min_value=3, max_value=12, value=pv['cash_buf_months'],
            help="After buying, keep at least this many months of salary liquid.")
        rent_0 = st.number_input("Current Monthly Rent (₹)", value=20_000,
            step=1_000, min_value=0,
            help="Rent you pay today. Assumed to stop when you buy the house.")

    inc_growth = st.slider("Expected salary growth (%/year)",
        min_value=3.0, max_value=25.0, value=float(pv['inc_growth']), step=0.5,
        help="10–12% is typical for mid-career professionals. Be realistic, not optimistic.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Q3: Spending ──
    st.markdown('<div class="card"><div class="card-title">🛒 Monthly Spending</div>', unsafe_allow_html=True)
    exp_pct = st.slider("What % of your salary goes to expenses (excluding rent)?",
        min_value=20, max_value=80, value=int(pv['exp_frac']*100), step=5,
        help="Include food, transport, utilities, subscriptions, clothing, dining out. Exclude rent.")
    st.caption(f"₹{take_home * exp_pct/100:,.0f}/month on expenses + ₹{rent_0:,}/month rent = "
               f"₹{(take_home * exp_pct/100 + rent_0):,.0f}/month total spend")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Q4: Savings & Investments ──
    st.markdown('<div class="card"><div class="card-title">📈 Savings & Investments</div>', unsafe_allow_html=True)
    savings_existing = st.number_input("Total savings & investments today (₹)",
        value=pv['savings_existing'], step=100_000, min_value=0,
        help="Add up everything: FD, mutual funds, stocks, PPF, EPF, gold, savings account. Rough estimate is fine.")

    col_sip, col_ret = st.columns(2)
    with col_sip:
        monthly_sip = st.number_input("Monthly SIP / investment (₹)",
            value=pv['monthly_sip'], step=1_000, min_value=0,
            help="Total amount you invest every month across all instruments.")
    with col_ret:
        sip_return = st.number_input("Expected annual return (%)",
            value=float(pv['sip_return']), step=0.5, min_value=1.0, max_value=30.0,
            help="12% for equity MFs, 7–8% for debt/PPF/FD, 10–11% for a mix.")

    sip_stepup = st.slider("SIP growth rate (%/year)",
        min_value=0, max_value=20, value=5,
        help="How much you increase your SIP each year. 5–10% is healthy.")

    bonus = 0
    if not is_se:
        bonus = st.number_input("Annual bonus (₹, after tax)",
            value=pv['bonus'], step=10_000, min_value=0,
            help="Any annual variable pay, incentive or bonus you receive. Enter net of tax.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Q5: Loan ──
    st.markdown('<div class="card"><div class="card-title">🏦 Home Loan</div>', unsafe_allow_html=True)
    want_loan = st.checkbox("I plan to take a home loan", value=True)
    if want_loan:
        col_r, col_t = st.columns(2)
        with col_r:
            loan_rate = st.number_input("Interest rate (%)",
                value=float(pv['loan_rate']), step=0.25, min_value=5.0, max_value=15.0,
                help="Current rates: 8.5–9.5% salaried, 9–10.5% self-employed.")
        with col_t:
            loan_tenure = st.number_input("Loan tenure (years)",
                value=int(pv['loan_tenure']), step=1, min_value=5, max_value=30,
                help="Longer tenure = lower EMI but more total interest.")
        emi_comfort = st.slider("Max EMI as % of take-home salary",
            min_value=20, max_value=55, value=int(pv['emi_frac']*100), step=5,
            help="Financial advisors recommend ≤40–45%. Higher = more financial stress.")
        user_max_loan = st.number_input("Max loan amount you want (₹) — 0 for no limit",
            value=0, step=500_000, min_value=0,
            help="If you don't want to borrow more than a certain amount regardless of eligibility.")
    else:
        loan_rate, loan_tenure, emi_comfort, user_max_loan = 0., 20, 40, 0
        want_loan = False
    st.markdown('</div>', unsafe_allow_html=True)

    # Age
    st.markdown('<div class="card"><div class="card-title">🎂 Your Age</div>', unsafe_allow_html=True)
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        age_now = st.number_input("Current age", value=30, min_value=18, max_value=70)
    with col_a2:
        max_age = st.number_input("Simulate until age", value=60, min_value=age_now+1, max_value=80)
    st.markdown('</div>', unsafe_allow_html=True)

    col_back, col_go = st.columns([1,2])
    with col_back:
        if st.button("← Back"):
            st.session_state['step'] = 'persona'
            st.rerun()
    with col_go:
        if st.button("See My Results →", type="primary"):
            st.session_state['params'] = {
                'age': age_now, 'max_age': max_age,
                'take_home_0': take_home, 'inc_growth': inc_growth,
                'exp_frac': exp_pct / 100,
                'rent_0': rent_0, 'rent_infl': 0.08,
                'savings_0': savings_existing,
                'monthly_sip': monthly_sip, 'sip_return': sip_return,
                'sip_stepup': sip_stepup, 'bonus_annual': bonus,
                'bonus_growth': 0.08,
                'house_price': house_price, 'house_infl': house_infl,
                'tx_cost': 7.0,
                'cash_buf_months': buf_months, 'buf_infl': 0.06,
                'loan_rate': loan_rate if want_loan else 0,
                'loan_tenure': loan_tenure,
                'emi_frac': emi_comfort / 100,
                'bank_mult': pv['bank_mult'],
                'user_max_loan': user_max_loan,
                'target_sqft': target_sqft,
                'persona_type': pv['type'],
                'se_volatility_months': buf_months,
                'income_volatility_pct': income_vol_pct,
                'city': city, 'flat_label': bhk,
            }
            rows = simulate(st.session_state['params'])
            st.session_state['sim_rows'] = rows
            st.session_state['whatif'] = {}
            st.session_state['step'] = 'results'
            st.rerun()


# ─────────────────────────────────────────────────────────────
# STEP 3 — RESULTS
# ─────────────────────────────────────────────────────────────
elif st.session_state['step'] == 'results':
    p    = st.session_state['params']
    rows = st.session_state['sim_rows']
    wi   = st.session_state.get('whatif', {})
    first = first_affordable(rows)

    # ── Apply what-if overrides and re-simulate if needed ──
    if wi:
        p2 = {**p, **wi}
        rows2 = simulate(p2)
        first2 = first_affordable(rows2)
    else:
        p2, rows2, first2 = p, rows, first

    # ── Result Banner ──
    if first2:
        yrs = first2['age'] - p2['age']
        st.markdown(f"""
        <div class="result-banner ok">
          <div class="emoji">🎉</div>
          <div>
            <div class="rb-title">You can buy at age {first2['age']}
              {"— that's now!" if yrs==0 else f"— {yrs} year{'s' if yrs>1 else ''} away"}</div>
            <div class="rb-sub">
              ₹{first2['portfolio']/1e7:.1f} Cr portfolio &nbsp;·&nbsp;
              ₹{first2['actual_loan']/1e7:.1f} Cr loan &nbsp;·&nbsp;
              EMI ₹{first2['actual_emi']/1000:.0f}K/mo
              {f"&nbsp;·&nbsp; {first2['aff_sqft']:,.0f} sq ft" if p2.get('target_sqft',0)>0 else ""}
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        last = rows2[-1]
        st.markdown(f"""
        <div class="result-banner no">
          <div class="emoji">❌</div>
          <div>
            <div class="rb-title">Not affordable by age {p2['max_age']}</div>
            <div class="rb-sub">
              Portfolio at {p2['max_age']}: ₹{last['portfolio']/1e7:.1f} Cr &nbsp;·&nbsp;
              Home will cost: ₹{last['house_price']/1e7:.1f} Cr<br>
              Try the what-if sliders below to find a path forward.
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Plain-English Narrative ──
    narrative = build_narrative(rows2, p2, first2)
    st.markdown(f'<div class="narrative">{narrative}</div>', unsafe_allow_html=True)

    # ── KPI cards ──
    r = first2 if first2 else rows2[-1]
    target_sqft = p2.get('target_sqft', 0)
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi accent">
        <div class="kl">Portfolio at {"age "+str(r['age']) if first2 else "age "+str(p2['max_age'])}</div>
        <div class="kv">₹{r['portfolio']/1e7:.2f} Cr</div>
        <div class="kd">savings + SIPs + surplus</div>
      </div>
      <div class="kpi">
        <div class="kl">Home Price Then</div>
        <div class="kv">₹{r['house_price']/1e7:.2f} Cr</div>
        <div class="kd">at {p2['house_infl']}%/yr inflation</div>
      </div>
      <div class="kpi {'green' if first2 else ''}">
        <div class="kl">Max Loan</div>
        <div class="kv">₹{r['max_loan']/1e7:.2f} Cr</div>
        <div class="kd">EMI ₹{r['actual_emi']/1000:.0f}K/mo</div>
      </div>
      <div class="kpi">
        <div class="kl">Cash Reserve After</div>
        <div class="kv">₹{max(0,r['cash_after'])/1e5:.0f}L</div>
        <div class="kd">needs ₹{r['req_buf']/1e5:.0f}L minimum</div>
      </div>
      {f'''<div class="kpi">
        <div class="kl">Affordable Sq Ft</div>
        <div class="kv">{r["aff_sqft"]:,.0f}</div>
        <div class="kd">target: {target_sqft:,} sq ft</div>
      </div>''' if target_sqft > 0 else ''}
    </div>""", unsafe_allow_html=True)

    # ── What-If Sliders ──
    st.markdown("""
    <div class="whatif-card">
      <div class="whatif-title">🎛️ What If? — drag to see impact instantly</div>
    </div>""", unsafe_allow_html=True)

    with st.container():
        wi_new = {}
        c1, c2 = st.columns(2)
        with c1:
            wi_sip = st.slider("Monthly SIP (₹K)",
                min_value=1, max_value=200,
                value=int(wi.get('monthly_sip', p['monthly_sip']) / 1000),
                step=1,
                help="Increase your SIP to accelerate portfolio growth.")
            wi_new['monthly_sip'] = wi_sip * 1000

            wi_ret = st.slider("Investment return (%/yr)",
                min_value=5.0, max_value=18.0,
                value=float(wi.get('sip_return', p['sip_return'])),
                step=0.5,
                help="Expected annual return on your investments.")
            wi_new['sip_return'] = wi_ret

        with c2:
            wi_inc = st.slider("Salary growth (%/yr)",
                min_value=3.0, max_value=20.0,
                value=float(wi.get('inc_growth', p['inc_growth'])),
                step=0.5,
                help="Higher growth = more surplus sooner.")
            wi_new['inc_growth'] = wi_inc

            wi_hinfl = st.slider("Property inflation (%/yr)",
                min_value=3.0, max_value=15.0,
                value=float(wi.get('house_infl', p['house_infl'])),
                step=0.5,
                help="Lower = the gap closes faster.")
            wi_new['house_infl'] = wi_hinfl

        wi_exp = st.slider("Monthly expenses (% of salary)",
            min_value=20, max_value=75,
            value=int(wi.get('exp_frac', p['exp_frac']) * 100),
            step=5,
            help="Spending less means more surplus to invest.")
        wi_new['exp_frac'] = wi_exp / 100

        if wi_new != {k: wi.get(k, p[k]) for k in wi_new}:
            st.session_state['whatif'] = wi_new
            st.rerun()

    # ── Year-by-Year Table ──
    st.markdown('<div class="sh"><div class="ic">📋</div><h3>Year-by-Year Forecast</h3></div>',
                unsafe_allow_html=True)

    df = pd.DataFrame([{
        'Age': r['age'],
        'Take Home/mo': f"₹{r['take_home']/1000:.0f}K",
        'Portfolio': f"₹{r['portfolio']/1e7:.2f}Cr",
        'Home Price': f"₹{r['house_price']/1e7:.2f}Cr",
        'Max Loan': f"₹{r['max_loan']/1e7:.2f}Cr",
        'EMI': f"₹{r['actual_emi']/1000:.0f}K",
        'Affordable': "✅ YES" if r['affordable'] else "❌ No",
        **({'Aff Sq Ft': f"{r['aff_sqft']:,.0f}" } if target_sqft > 0 else {}),
    } for r in rows2])

    def _style(val):
        if val == "✅ YES": return 'color:#15622f;font-weight:700'
        if val == "❌ No":  return 'color:#9b1c1c'
        return ''

    st.dataframe(
        df.style.applymap(_style, subset=['Affordable']),
        use_container_width=True, height=380, hide_index=True)

    # ── Download ──
    import io
    buf = io.BytesIO()
    df_full = pd.DataFrame(rows2)
    with pd.ExcelWriter(buf, engine='xlsxwriter') as w:
        df_full.to_excel(w, sheet_name='Forecast', index=False)
    st.download_button("📥 Download Full Forecast (Excel)",
        data=buf.getvalue(),
        file_name="home_affordability.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

    # ── Advanced mode link ──
    st.markdown("""
    <div class="adv-link">
      🔬 Need more control? Model taxes, EPF, NPS, rebalancing rules and more in the
      <a href="https://your-advanced-app-url.streamlit.app" target="_blank">Advanced Simulator →</a><br>
      <span style="font-size:.75rem;color:#94a3b8">
        Replace the URL above with your Streamlit app URL after deploying advanced_app.py
      </span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    if st.button("← Start Over", use_container_width=True):
        reset()

