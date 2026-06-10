# FinPlan India 📊

Goal-based financial planning for Indian investors. Built with Streamlit.

## Features

- **Net worth tracker** — full asset/liability breakdown with visual allocation
- **Cashflow analysis** — surplus identification and deployment suggestions
- **Goal planner** — emergency fund, marriage, house, child education, retirement
- **Rent vs buy model** — Mumbai-specific with property appreciation sensitivity
- **Retirement projector** — with vs without SIP step-up, corpus breakdown by asset class
- **Action plan** — prioritised, personalised steps generated from your data
- **Tax-aware** — LTCG, STCG, slab rates, PPF/EPF/NPS all computed correctly

---

## Deploy to Streamlit Community Cloud (free, 5 minutes)

### Step 1 — Push to GitHub
```bash
# Create a new repo on github.com, then:
git init
git add .
git commit -m "FinPlan India initial commit"
git remote add origin https://github.com/YOUR_USERNAME/finplan-india.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repo → Branch: `main` → Main file: `app.py`
5. Click **Deploy**

Done. Your app is live at `https://YOUR_USERNAME-finplan-india-app-XXXX.streamlit.app`

---

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## File structure
```
finplan_app/
├── app.py                    # Entry point + navigation
├── requirements.txt          # Dependencies
├── .streamlit/
│   └── config.toml           # Theme and server config
└── pages_content/
    ├── __init__.py
    ├── home.py               # Landing page
    ├── profile.py            # Age, city, tax regime
    ├── income.py             # Salary, SIPs, expenses
    ├── assets.py             # All assets and liabilities
    ├── goals.py              # All financial goals
    ├── plan.py               # Full plan output (6 tabs)
    └── calculations.py       # Pure financial math engine
```

---

## Tax assumptions (current as of FY 2025-26)
- **LTCG (equity):** 12.5% on gains > ₹1.25L | surcharge capped at 15% (Sec 112A)
- **STCG (equity):** 20% | surcharge capped at 15% (Sec 111A)
- **Slab rate (30% bracket):** 30% + 10% surcharge + 4% cess = 34.32% effective
- **PPF:** EEE — fully exempt
- **EPF:** EEE — fully exempt on qualifying withdrawals
- **NPS:** 60% lump sum tax-free at maturity; 40% annuity taxable

---

## Return assumptions
| Instrument | Return used |
|---|---|
| Equity index funds | 12% p.a. |
| Arbitrage funds | 6.5% p.a. |
| Liquid funds | 7.0% p.a. |
| PPF | 7.1% p.a. |
| EPF | 8.5% p.a. |
| NPS (equity) | 10% p.a. |
| Gold | 9% p.a. (INR) |
| RBI Floating Bond | 8.05% p.a. (assumed flat) |

---

## Disclaimer
FinPlan India is an **educational financial calculator**. It does not constitute
financial advice. All projections are based on assumptions that may not reflect
actual market conditions. Past returns are not indicative of future performance.
This tool is not registered with SEBI as an Investment Adviser.
Please consult a SEBI-registered investment advisor before making financial decisions.

---

## Roadmap (future versions)
- [ ] SIP step-up simulator with customisable step-up %
- [ ] Tax harvesting calendar (LTCG exemption ₹1.25L/year)
- [ ] Loan amortisation table with prepayment impact
- [ ] PDF export of full plan
- [ ] WhatsApp share of plan summary
- [ ] Multi-goal priority matrix
- [ ] Spouse income integration
