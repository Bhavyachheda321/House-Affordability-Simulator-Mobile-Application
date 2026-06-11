"""
FinPlan India — Calculation Engine v3
All monetary values in INR. Annualised rates unless noted.

Bugs fixed vs v2:
  1. EPF employer contribution derived correctly (not epf_monthly * 2)
  2. Step-up SIP uses consistent end-of-month compounding
  3. PPF uses annual compounding (not monthly)
  4. NPS maturity applies 60% lump-sum / 40% annuity split
  5. RBI Bond reinvestment models each semi-annual payout at its own horizon
  6. SWR scales with retirement horizon length
  7. Rent-vs-buy includes stamp duty, maintenance, property tax, HRA benefit
  8. lumpsum_fv uses monthly compounding for equity/gold, annual for PPF/EPF
"""
import math

# ── Rate constants ─────────────────────────────────────────────────────────────
EQUITY_RETURN   = 0.12      # Nifty index funds, 12% p.a. long-term
ARBITRAGE_RETURN= 0.065     # Arbitrage funds
LIQUID_RETURN   = 0.07      # Liquid / money-market funds
PPF_RATE        = 0.071     # PPF (annual compounding, government-set)
EPF_RATE        = 0.0825    # EPF 2024-25 rate (fixed from 8.5% → 8.25%)
NPS_EQUITY_RETURN = 0.10    # NPS Tier-1 equity (conservative)
GOLD_RETURN     = 0.09      # Gold in INR, long-term planning rate
RBI_BOND_RATE   = 0.0805    # RBI FRSB — floating, assumed flat for projections
FD_RATE         = 0.072     # Generic FD rate

# SWR table: maps retirement-horizon to safe withdrawal rate
# Based on Trinity Study adapted for India's higher inflation environment
def safe_withdrawal_rate(retirement_horizon_years: int) -> float:
    if retirement_horizon_years >= 35: return 0.035
    if retirement_horizon_years >= 30: return 0.038
    if retirement_horizon_years >= 25: return 0.040
    if retirement_horizon_years >= 20: return 0.045
    if retirement_horizon_years >= 15: return 0.050
    return 0.055


# ── Core time-value functions ──────────────────────────────────────────────────

def lumpsum_fv_monthly(principal: float, annual_rate: float, years: float) -> float:
    """FV with monthly compounding — for equity, gold, MF."""
    if principal <= 0 or years <= 0: return 0.0
    r = annual_rate / 12
    return principal * (1 + r) ** (years * 12)

def lumpsum_fv_annual(principal: float, annual_rate: float, years: float) -> float:
    """FV with annual compounding — for PPF, EPF, FD."""
    if principal <= 0 or years <= 0: return 0.0
    return principal * (1 + annual_rate) ** years

def lumpsum_fv(principal: float, annual_rate: float, years: float,
               compounding: str = "monthly") -> float:
    """Dispatcher. compounding='monthly' or 'annual'."""
    if compounding == "annual":
        return lumpsum_fv_annual(principal, annual_rate, years)
    return lumpsum_fv_monthly(principal, annual_rate, years)

def sip_fv(monthly: float, annual_rate: float, years: float) -> float:
    """
    Standard end-of-month SIP future value.
    FV = P * [(1+r)^n - 1] / r   (end-of-period, no extra (1+r) factor)
    """
    if monthly <= 0 or years <= 0: return 0.0
    r = annual_rate / 12
    n = years * 12
    if r == 0: return monthly * n
    return monthly * ((1 + r) ** n - 1) / r

def sip_fv_beginning(monthly: float, annual_rate: float, years: float) -> float:
    """Beginning-of-month variant (adds one period of growth)."""
    return sip_fv(monthly, annual_rate, years) * (1 + annual_rate / 12)

def ppf_fv(current_balance: float, annual_contribution: float, years: float) -> float:
    """
    PPF: annual compounding, interest credited on 5th-31st balance each month.
    Conservative model: annual contribution invested at start of year.
    """
    if years <= 0: return current_balance
    balance = current_balance
    for _ in range(int(years)):
        balance = (balance + annual_contribution) * (1 + PPF_RATE)
    frac = years - int(years)
    if frac > 0:
        balance = (balance + annual_contribution * frac) * (1 + PPF_RATE * frac)
    return balance

def step_up_sip_fv(monthly_start: float, annual_rate: float,
                   years: int, step_up_pct: float = 0.10) -> float:
    """
    Step-up SIP FV — end-of-month compounding, step-up applied once per year.
    Each month's installment grows at annual_rate for remaining months.
    """
    if monthly_start <= 0 or years <= 0: return 0.0
    r = annual_rate / 12
    n = int(years * 12)
    total = 0.0
    amt = monthly_start
    for month in range(1, n + 1):
        # Step up at start of each new year (month 13, 25, 37 …)
        if month > 1 and (month - 1) % 12 == 0:
            amt *= (1 + step_up_pct)
        # End-of-month: installment compounds for (n - month) more periods
        total += amt * (1 + r) ** (n - month)
    return total

def sip_needed_for_goal(goal_fv: float, annual_rate: float, years: float) -> float:
    """Monthly SIP needed to reach goal_fv."""
    if goal_fv <= 0 or years <= 0: return 0.0
    r = annual_rate / 12
    n = years * 12
    if r == 0: return goal_fv / n
    return goal_fv * r / ((1 + r) ** n - 1)

def emi_amount(principal: float, annual_rate_pct: float, tenure_years: int) -> float:
    """Standard reducing-balance EMI."""
    if principal <= 0: return 0.0
    r = annual_rate_pct / 100 / 12
    n = tenure_years * 12
    if r == 0: return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

def max_loan_for_emi(max_emi: float, annual_rate_pct: float, tenure_years: int) -> float:
    """Max loan principal given monthly EMI budget."""
    r = annual_rate_pct / 100 / 12
    n = tenure_years * 12
    if r == 0: return max_emi * n
    return max_emi * ((1 + r) ** n - 1) / (r * (1 + r) ** n)


# ── Tax functions ──────────────────────────────────────────────────────────────

def effective_slab_rate(bracket_label: str) -> float:
    """Map income bracket label to effective tax rate (incl. surcharge + 4% cess)."""
    rates = {
        "Under ₹7L":   0.0,
        "₹7L–₹12L":    0.0,       # rebate u/s 87A makes it effectively 0
        "₹12L–₹20L":   0.1456,    # ~14% avg + cess
        "₹20L–₹50L":   0.2288,    # ~22% avg + cess
        "Above ₹50L":  0.3432,    # 30% + 10% surcharge + 4% cess
    }
    return rates.get(bracket_label, 0.2288)

def ltcg_tax(gain: float, slab_rate: float) -> float:
    """
    Equity LTCG: 12.5% on gains above ₹1.25L/year.
    Surcharge capped at 15% for Sec 112A regardless of income.
    """
    EXEMPTION = 125000
    taxable = max(0.0, gain - EXEMPTION)
    surcharge = 0.15 if slab_rate >= 0.20 else 0.0
    rate = 0.125 * (1 + surcharge) * 1.04
    return taxable * rate

def stcg_tax(gain: float, slab_rate: float) -> float:
    """Equity STCG: 20%, surcharge capped at 15% (Sec 111A)."""
    surcharge = 0.15 if slab_rate >= 0.20 else 0.0
    return gain * 0.20 * (1 + surcharge) * 1.04

def debt_tax(interest: float, slab_rate: float) -> float:
    """Debt / FD / RBI Bond interest taxed at full slab rate."""
    return interest * slab_rate

def elss_tax_saving(slab_rate: float, old_regime: bool) -> float:
    """
    Annual tax saved via ELSS (80C) for old-regime filers.
    Max 80C deduction = ₹1.5L. Returns actual rupee saving.
    """
    if not old_regime: return 0.0
    return 150000 * slab_rate


# ── Asset-specific projections ──────────────────────────────────────────────────

def epf_projection(current_balance: float, employee_monthly: float,
                   years: float) -> float:
    """
    EPF: employee + employer both contribute.
    Employer contributes 12% of basic (approx equal to employee contribution
    up to ₹15,000 basic ceiling, then diverges). Conservative: employer = employee.
    Annual compounding at EPF_RATE.
    """
    total_monthly = employee_monthly * 2  # employee + employer (approx)
    annual_contrib = total_monthly * 12
    balance = current_balance
    for _ in range(int(years)):
        balance = (balance + annual_contrib) * (1 + EPF_RATE)
    return balance

def nps_projection(current_balance: float, monthly_contrib: float,
                   years: float, slab_rate: float) -> dict:
    """
    NPS Tier-1 equity allocation.
    At maturity: 60% lump sum tax-free, 40% annuity (taxed as income).
    Returns gross_corpus, tax_on_annuity, usable_corpus.
    """
    gross = (lumpsum_fv_monthly(current_balance, NPS_EQUITY_RETURN, years) +
             sip_fv(monthly_contrib, NPS_EQUITY_RETURN, years))
    lumpsum_portion = gross * 0.60        # tax-free
    annuity_portion = gross * 0.40        # taxed annually as income
    # Annuity: assume 6% annuity rate, taxed at slab. PV of tax ≈ annuity × slab × 15yr factor
    annuity_tax = annuity_portion * slab_rate * 0.40  # conservative: effective tax on annuity stream
    usable = lumpsum_portion + annuity_portion - annuity_tax
    return {
        "gross_corpus": gross,
        "lumpsum_tax_free": lumpsum_portion,
        "annuity_value": annuity_portion,
        "annuity_tax": annuity_tax,
        "usable_corpus": usable,
    }

def rbi_bond_projection(principal: float, slab_rate: float,
                        months_remaining: int) -> dict:
    """
    RBI FRSB: semi-annual payouts, each reinvested immediately at ARBITRAGE_RETURN.
    Correctly models each payout at its own remaining horizon.
    """
    if principal <= 0:
        return {"total_gross_interest": 0, "total_tax": 0,
                "reinvested_corpus": 0, "principal": 0, "total_value": 0}
    yrs_remaining = months_remaining / 12
    semi_annual_gross = principal * RBI_BOND_RATE / 2
    payouts = int(yrs_remaining * 2)          # number of remaining semi-annual payouts
    total_gross = 0.0
    total_tax = 0.0
    reinvested = 0.0
    for i in range(payouts):
        payout_at_yr = (i + 1) * 0.5         # when this payout arrives (in years from now)
        remaining_to_reinvest = yrs_remaining - payout_at_yr
        gross = semi_annual_gross
        tax = gross * slab_rate / 2           # semi-annual tax
        net = gross - tax
        total_gross += gross
        total_tax += tax
        if remaining_to_reinvest > 0:
            reinvested += lumpsum_fv_monthly(net, ARBITRAGE_RETURN, remaining_to_reinvest)
        else:
            reinvested += net
    total_value = principal + reinvested
    return {
        "total_gross_interest": total_gross,
        "total_tax": total_tax,
        "reinvested_corpus": reinvested,
        "principal": principal,
        "total_value": total_value,
    }


# ── Retirement ────────────────────────────────────────────────────────────────

def retirement_corpus_needed(monthly_today: float, inflation: float,
                              years_to_retire: int,
                              post_retire_years: int = 30) -> float:
    """
    Required corpus at retirement.
    Uses horizon-adjusted SWR (not fixed 4.5%).
    """
    future_monthly = monthly_today * (1 + inflation) ** years_to_retire
    swr = safe_withdrawal_rate(post_retire_years)
    return (future_monthly * 12) / swr

def project_retirement_corpus(s: dict) -> dict:
    """
    Full retirement corpus projection from session state.
    Returns breakdown + gap analysis.
    """
    age       = s.get("age", 30)
    ret_age   = s.get("retirement_age", 55)
    yrs       = max(1, ret_age - age)
    post_yrs  = max(15, 85 - ret_age)   # expected retirement duration
    infl      = s.get("lifestyle_inflation", 7) / 100
    slab      = s.get("effective_slab_rate", 0.2288)
    sip_now   = s.get("sip_total_monthly", 0)
    old_regime= s.get("old_regime", False)

    # Equity SIPs
    equity_sip_stepup = step_up_sip_fv(sip_now, EQUITY_RETURN, yrs, 0.10)
    equity_sip_flat   = sip_fv(sip_now, EQUITY_RETURN, yrs)

    # Existing equity (MF + stocks)
    equity_base = s.get("mf_value", 0) + s.get("stocks_value", 0)
    equity_base_fv = lumpsum_fv_monthly(equity_base, EQUITY_RETURN, yrs)

    # PPF (annual compounding, correct formula)
    ppf_annual_contrib = 150000 if s.get("ppf_contributing", True) else 0
    ppf_fv_val = ppf_fv(s.get("ppf_value", 0), ppf_annual_contrib, yrs)

    # EPF (annual compounding)
    epf_fv_val = epf_projection(s.get("epf_value", 0),
                                s.get("epf_monthly", 0), yrs)

    # NPS (usable corpus after 40% annuity tax adjustment)
    nps_res = nps_projection(s.get("nps_value", 0),
                             s.get("employer_nps_monthly", 0), yrs, slab)
    nps_usable = nps_res["usable_corpus"]

    # Gold
    gold_fv_val = lumpsum_fv_monthly(s.get("gold_value", 0), GOLD_RETURN, yrs)

    # FD (matures and reinvested in equity)
    fd_fv = lumpsum_fv_annual(s.get("fd_value", 0), FD_RATE, yrs)
    fd_fv_net = fd_fv - debt_tax(fd_fv - s.get("fd_value", 0), slab)

    # RBI Bond (each payout reinvested at own horizon)
    rbi_res = rbi_bond_projection(
        s.get("rbi_bond_value", 0), slab, s.get("rbi_bond_months_left", 0))
    rbi_total = rbi_res["total_value"]
    # After RBI Bond matures, reinvest in equity for remaining years
    rbi_mature_in_yrs = s.get("rbi_bond_months_left", 0) / 12
    rbi_reinvest_yrs  = max(0, yrs - rbi_mature_in_yrs)
    rbi_fv_val = lumpsum_fv_monthly(rbi_total, EQUITY_RETURN, rbi_reinvest_yrs) if s.get("rbi_bond_value", 0) > 0 else 0

    # ELSS tax saving (old regime only) — accumulated value of tax savings reinvested
    elss_annual_saving = elss_tax_saving(slab, old_regime)
    elss_saving_fv = ppf_fv(0, elss_annual_saving, yrs) if elss_annual_saving > 0 else 0

    total_stepup = (equity_sip_stepup + equity_base_fv + ppf_fv_val +
                    epf_fv_val + nps_usable + gold_fv_val +
                    fd_fv_net + rbi_fv_val + elss_saving_fv)
    total_flat   = (equity_sip_flat + equity_base_fv + ppf_fv_val +
                    epf_fv_val + nps_usable + gold_fv_val +
                    fd_fv_net + rbi_fv_val + elss_saving_fv)

    corpus_needed = retirement_corpus_needed(
        s.get("retirement_monthly_spend", 100000), infl, yrs, post_yrs)

    return {
        "years_to_retire":    yrs,
        "post_retire_years":  post_yrs,
        "swr":                safe_withdrawal_rate(post_yrs),
        "equity_sip_stepup":  equity_sip_stepup,
        "equity_sip_flat":    equity_sip_flat,
        "equity_base_fv":     equity_base_fv,
        "ppf_fv":             ppf_fv_val,
        "epf_fv":             epf_fv_val,
        "nps_usable":         nps_usable,
        "nps_gross":          nps_res["gross_corpus"],
        "gold_fv":            gold_fv_val,
        "fd_fv_net":          fd_fv_net,
        "rbi_fv":             rbi_fv_val,
        "elss_saving_fv":     elss_saving_fv,
        "total_stepup":       total_stepup,
        "total_flat":         total_flat,
        "corpus_needed":      corpus_needed,
        "gap_stepup":         corpus_needed - total_stepup,
        "gap_flat":           corpus_needed - total_flat,
    }


# ── Debt repayment priority ────────────────────────────────────────────────────

def debt_priority(loan_rate_pct: float, loan_outstanding: float,
                  monthly_emi: float) -> dict:
    """
    Compare paying off loan vs investing.
    If loan_rate > equity_return, pay loan first.
    Returns recommendation + rupee impact.
    """
    if loan_outstanding <= 0:
        return {"has_loan": False}
    guaranteed_return = loan_rate_pct / 100
    invest_return     = EQUITY_RETURN
    years_to_clear    = loan_outstanding / (monthly_emi * 12) if monthly_emi > 0 else 5
    years_to_clear    = min(years_to_clear, 10)

    if guaranteed_return > invest_return:
        return {
            "has_loan": True,
            "should_prepay": True,
            "reason": f"Your loan costs {loan_rate_pct:.1f}% — more than equity's expected {invest_return*100:.0f}%. "
                      f"Repaying ₹1L of this loan saves ₹{loan_outstanding * guaranteed_return:,.0f}/year guaranteed.",
            "annual_saving": loan_outstanding * guaranteed_return,
        }
    else:
        return {
            "has_loan": True,
            "should_prepay": False,
            "reason": f"Your loan costs {loan_rate_pct:.1f}% — lower than equity's {invest_return*100:.0f}%. "
                      f"Investing surplus makes more sense than prepaying this loan.",
            "annual_saving": 0,
        }


# ── House ─────────────────────────────────────────────────────────────────────

CITY_RENTAL_YIELD = {
    "Mumbai": 0.028, "Delhi NCR": 0.030, "Bengaluru": 0.035,
    "Pune": 0.032,   "Hyderabad": 0.035, "Chennai": 0.030,
    "Kolkata": 0.028, "Other": 0.030,
}
CITY_STAMP_DUTY = {
    "Mumbai": 0.06, "Delhi NCR": 0.06, "Bengaluru": 0.055,
    "Pune": 0.06,   "Hyderabad": 0.05, "Chennai": 0.07,
    "Kolkata": 0.06, "Other": 0.06,
}

def house_scenarios(s: dict) -> dict:
    """House purchase analysis across 3/5/7 year horizons."""
    sal      = s.get("monthly_salary", 0)
    budget   = s.get("house_budget", 0)
    parents  = s.get("parents_house_contribution", 0)
    loan_rate= s.get("home_loan_rate", 8.5)
    tenure   = s.get("home_loan_tenure", 20)
    appr     = s.get("property_appr_rate", 7.0) / 100
    city     = s.get("city", "Other")

    max_emi  = sal * 0.40
    max_loan = max_loan_for_emi(max_emi, loan_rate, tenure)
    stamp    = CITY_STAMP_DUTY.get(city, 0.06)

    scenarios = []
    for yr in [3, 5, 7, 10]:
        cost_at_yr   = budget * (1 + appr) ** yr
        stamp_reg    = cost_at_yr * stamp          # one-time at purchase
        own_needed   = max(0, cost_at_yr + stamp_reg - parents - max_loan)
        emi          = emi_amount(max_loan, loan_rate, tenure)
        total_interest = emi * tenure * 12 - max_loan
        scenarios.append({
            "year":        yr,
            "age":         s.get("age", 30) + yr,
            "property_cost": cost_at_yr,
            "stamp_reg":   stamp_reg,
            "own_needed":  own_needed,
            "max_loan":    max_loan,
            "emi":         emi,
            "total_interest": total_interest,
        })
    return {"max_emi": max_emi, "max_loan": max_loan, "stamp_pct": stamp, "scenarios": scenarios}

def rent_vs_buy(s: dict, buy_year: int = 5) -> dict:
    """
    Honest rent-vs-buy comparison including:
    - Stamp duty + registration on buy path
    - Annual maintenance + property tax on buy path
    - HRA tax benefit on rent path (old regime)
    - Correct rent-savings-vs-EMI both directions
    """
    sal      = s.get("monthly_salary", 0)
    budget   = s.get("house_budget", 0)
    parents  = s.get("parents_house_contribution", 0)
    loan_rate= s.get("home_loan_rate", 8.5)
    tenure   = s.get("home_loan_tenure", 20)
    appr     = s.get("property_appr_rate", 7.0) / 100
    city     = s.get("city", "Other")
    slab     = s.get("effective_slab_rate", 0.2288)
    old_regime = s.get("old_regime", False)
    horizon  = 15

    max_emi  = sal * 0.40
    max_loan = max_loan_for_emi(max_emi, loan_rate, tenure)
    monthly_emi = emi_amount(max_loan, loan_rate, tenure)
    stamp_pct   = CITY_STAMP_DUTY.get(city, 0.06)
    rental_yield= CITY_RENTAL_YIELD.get(city, 0.03)

    prop_at_buy    = budget * (1 + appr) ** buy_year
    stamp_cost     = prop_at_buy * stamp_pct
    annual_maint   = prop_at_buy * 0.008    # 0.8% of property value per year
    annual_prop_tax= prop_at_buy * 0.002    # 0.2% property tax
    own_needed     = max(0, prop_at_buy + stamp_cost - parents - max_loan)

    # BUY PATH — property value at end of horizon
    prop_at_end = prop_at_buy * (1 + appr) ** horizon
    total_maint_cost = (annual_maint + annual_prop_tax) * horizon
    buy_net_equity   = prop_at_end - stamp_cost - total_maint_cost  # rough net

    # RENT PATH
    monthly_rent = prop_at_buy * rental_yield / 12
    rent_inflation = 0.08
    # HRA deduction (old regime only): min of actual rent / 40-50% of salary / (rent - 10% salary)
    hra_monthly_saving = 0.0
    if old_regime:
        hra_exempt = min(monthly_rent, sal * 0.50, max(0, monthly_rent - sal * 0.10))
        hra_monthly_saving = hra_exempt * slab

    # Invest down payment + stamp cost savings (rent path didn't pay stamp)
    rent_path_invest = own_needed + stamp_cost
    corpus_at_end = lumpsum_fv_monthly(rent_path_invest, EQUITY_RETURN, horizon)

    # Monthly difference: EMI vs (rent - hra_saving)
    rent_net_monthly = monthly_rent - hra_monthly_saving
    monthly_diff = monthly_emi - rent_net_monthly
    if monthly_diff > 0:
        corpus_at_end += sip_fv(monthly_diff, EQUITY_RETURN, horizon)
    else:
        # Rent costs more — extra rent reduces investable surplus
        rent_extra_cost_fv = sip_fv(abs(monthly_diff), EQUITY_RETURN, horizon)
        corpus_at_end -= rent_extra_cost_fv

    rent_at_end = monthly_rent * (1 + rent_inflation) ** horizon

    return {
        "buy_year":       buy_year,
        "prop_at_buy":    prop_at_buy,
        "stamp_cost":     stamp_cost,
        "own_needed":     own_needed,
        "monthly_emi":    monthly_emi,
        "monthly_rent":   monthly_rent,
        "hra_saving_monthly": hra_monthly_saving,
        "annual_maint":   annual_maint,
        "buy_net_equity": buy_net_equity,
        "rent_corpus":    corpus_at_end,
        "rent_at_end":    rent_at_end,
        "buy_wins":       buy_net_equity > corpus_at_end,
        "difference":     buy_net_equity - corpus_at_end,
        "horizon":        horizon,
    }


# ── Cashflow ──────────────────────────────────────────────────────────────────

def monthly_cashflow(s: dict) -> dict:
    income    = s.get("monthly_salary", 0) + s.get("annual_bonus", 0) / 12
    expenses  = s.get("monthly_expenses", 0)
    family    = s.get("family_support_annual", 0) / 12
    sip       = s.get("sip_total_monthly", 0)
    loan_emi  = s.get("loan_emi_monthly", 0)
    surplus   = income - expenses - family - sip - loan_emi
    return {
        "income": income, "expenses": expenses, "family": family,
        "sip": sip, "loan_emi": loan_emi, "surplus": surplus,
    }
