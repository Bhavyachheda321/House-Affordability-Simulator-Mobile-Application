"""
Core financial calculation engine for FinPlan India.
All monetary values in INR. Returns are annualised.
"""
import math


# ── constants ─────────────────────────────────────────────────────────────────
EQUITY_LONG_TERM_RETURN = 0.12      # 12% p.a. for equity index funds
ARBITRAGE_RETURN = 0.065            # 6.5% for arbitrage funds
LIQUID_RETURN = 0.07                # 7% for liquid funds
PPF_RATE = 0.071                    # 7.1% PPF
EPF_RATE = 0.085                    # 8.5% EPF
NPS_EQUITY_RETURN = 0.10            # 10% NPS
GOLD_RETURN = 0.09                  # 9% gold long term INR
RBI_BOND_RATE = 0.0805              # 8.05% (assumed flat)
SWR = 0.045                         # 4.5% safe withdrawal rate


def sip_future_value(monthly: float, annual_rate: float, years: float) -> float:
    """Standard SIP future value formula."""
    if monthly <= 0 or years <= 0:
        return 0
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return monthly * n
    return monthly * ((1 + r)**n - 1) / r * (1 + r)


def step_up_sip_fv(monthly_start: float, annual_rate: float,
                   years: int, step_up_pct: float = 0.10) -> float:
    """Future value of a step-up SIP (10% annual increment by default)."""
    if monthly_start <= 0 or years <= 0:
        return 0
    r = annual_rate / 12
    g = step_up_pct / 12
    n = years * 12
    total = 0.0
    amt = monthly_start
    for month in range(1, int(n) + 1):
        if month > 1 and (month - 1) % 12 == 0:
            amt *= (1 + step_up_pct)
        total += amt * (1 + r) ** (n - month + 1)
    return total


def lumpsum_fv(principal: float, annual_rate: float, years: float) -> float:
    if principal <= 0 or years <= 0:
        return 0
    return principal * (1 + annual_rate) ** years


def sip_needed_for_goal(goal_fv: float, annual_rate: float, years: float) -> float:
    """Monthly SIP required to reach a goal."""
    if goal_fv <= 0 or years <= 0:
        return 0
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return goal_fv / n
    return goal_fv * r / (((1 + r)**n - 1) * (1 + r))


def emi_amount(principal: float, annual_rate: float, tenure_years: int) -> float:
    """Standard EMI formula."""
    if principal <= 0:
        return 0
    r = annual_rate / 100 / 12
    n = tenure_years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r)**n / ((1 + r)**n - 1)


def max_loan_for_emi(max_emi: float, annual_rate: float, tenure_years: int) -> float:
    """Maximum loan amount given max EMI."""
    r = annual_rate / 100 / 12
    n = tenure_years * 12
    if r == 0:
        return max_emi * n
    return max_emi * ((1 + r)**n - 1) / (r * (1 + r)**n)


def retirement_corpus_needed(monthly_today: float, inflation: float,
                              years_to_retire: int, swr: float = SWR) -> float:
    future_monthly = monthly_today * (1 + inflation) ** years_to_retire
    return (future_monthly * 12) / swr


def ltcg_tax(gain: float, slab_rate: float, is_equity: bool = True) -> float:
    """
    LTCG tax after exemption.
    Equity: 12.5% on gains > 1.25L; surcharge capped at 15%.
    Debt: slab rate.
    """
    EXEMPTION = 125000
    if is_equity:
        taxable = max(0, gain - EXEMPTION)
        # determine surcharge tier from slab_rate
        if slab_rate >= 0.35:
            surcharge = 0.15
        elif slab_rate >= 0.30:
            surcharge = 0.15  # capped for 112A
        else:
            surcharge = 0.0
        rate = 0.125 * (1 + surcharge) * 1.04  # cess 4%
        return taxable * rate
    else:
        return gain * slab_rate


def stcg_tax(gain: float, slab_rate: float, is_equity: bool = True) -> float:
    """
    STCG tax.
    Equity: 20%; surcharge capped at 15% for Sec 111A.
    Debt: slab rate.
    """
    if is_equity:
        if slab_rate >= 0.30:
            surcharge = 0.15
        else:
            surcharge = 0.0
        rate = 0.20 * (1 + surcharge) * 1.04
        return gain * rate
    else:
        return gain * slab_rate


def rbi_bond_net_payout(principal: float, rate: float,
                         slab_rate: float, years: int = 7) -> dict:
    """Semi-annual payout bond. Returns gross, tax, net per period and totals."""
    semi_annual_gross = principal * rate / 2
    annual_tax = principal * rate * slab_rate
    total_gross = semi_annual_gross * years * 2
    total_tax = annual_tax * years
    return {
        "semi_annual_gross": semi_annual_gross,
        "semi_annual_net": semi_annual_gross - annual_tax / 2,
        "annual_gross": principal * rate,
        "annual_tax": annual_tax,
        "total_gross_interest": total_gross,
        "total_tax": total_tax,
        "total_net_interest": total_gross - total_tax,
        "total_in_hand": principal + total_gross - total_tax,
    }


def cashflow_analysis(s: dict) -> dict:
    """Compute monthly cashflow from session state dict."""
    income = s.get("net_take_home", 0) + s.get("annual_bonus", 0) / 12
    total_sip = sum(x["monthly"] for x in s.get("sips", []))
    family = s.get("family_contribution_annual", 0) / 12
    expenses = s.get("monthly_expenses", 0)
    other_emis = s.get("personal_loan_emi", 0) + s.get("other_emis", 0)
    committed = expenses + family + total_sip + other_emis
    surplus = income - committed
    return {
        "income": income,
        "expenses": expenses,
        "family": family,
        "total_sip": total_sip,
        "other_emis": other_emis,
        "committed": committed,
        "surplus": surplus,
    }


def projected_corpus_at_retirement(s: dict) -> dict:
    """
    Project corpus at retirement age with and without SIP step-ups.
    Returns breakdown by asset class.
    """
    age_now = s.get("age", 30)
    ret_age = s.get("retirement_age", 55)
    yrs = ret_age - age_now
    if yrs <= 0:
        yrs = 1

    infl = s.get("lifestyle_inflation", 8.0) / 100
    salary_growth = s.get("salary_growth_pct", 8.0) / 100
    slab = s.get("effective_slab_rate", 0.3432)

    total_sip_now = sum(x["monthly"] for x in s.get("sips", []))

    # Equity SIP (step-up)
    equity_sip_stepup = step_up_sip_fv(total_sip_now, EQUITY_LONG_TERM_RETURN, yrs, 0.10)
    equity_sip_flat = sip_future_value(total_sip_now, EQUITY_LONG_TERM_RETURN, yrs)

    # Existing equity corpus
    existing_equity = (s.get("equity_mf_value", 0) + s.get("direct_equity_value", 0))
    existing_equity_fv = lumpsum_fv(existing_equity, EQUITY_LONG_TERM_RETURN, yrs)

    # EPF
    epf_monthly = s.get("epf_monthly", 0)
    epf_current = s.get("epf_value", 0)
    epf_fv = (lumpsum_fv(epf_current, EPF_RATE, yrs) +
               sip_future_value(epf_monthly * 2, EPF_RATE, yrs))  # both employee+employer

    # NPS
    nps_monthly = s.get("employer_nps_monthly", 0)
    nps_current = s.get("nps_value", 0)
    nps_fv = (lumpsum_fv(nps_current, NPS_EQUITY_RETURN, yrs) +
               sip_future_value(nps_monthly, NPS_EQUITY_RETURN, yrs))

    # PPF
    ppf_current = s.get("ppf_value", 0)
    ppf_annual = s.get("ppf_annual_contribution", 150000)
    ppf_fv = (lumpsum_fv(ppf_current, PPF_RATE, yrs) +
               sip_future_value(ppf_annual / 12, PPF_RATE, yrs))

    # RBI Bond — matures, reinvested
    rbi_val = s.get("rbi_bond_value", 0)
    rbi_months_left = s.get("rbi_bond_months_left", 24)
    rbi_yrs_left = rbi_months_left / 12
    reinvest_yrs = yrs - rbi_yrs_left
    rbi_net = rbi_bond_net_payout(rbi_val, RBI_BOND_RATE, slab, 7)
    # After maturity, reinvest principal + net interest at equity returns
    rbi_fv = lumpsum_fv(rbi_net["total_in_hand"], EQUITY_LONG_TERM_RETURN,
                         max(0, reinvest_yrs)) if rbi_val > 0 else 0

    # Gold
    gold_fv = lumpsum_fv(s.get("gold_value", 0), GOLD_RETURN, yrs)

    total_stepup = (equity_sip_stepup + existing_equity_fv + epf_fv +
                    nps_fv + ppf_fv + rbi_fv + gold_fv)
    total_flat = (equity_sip_flat + existing_equity_fv + epf_fv +
                  nps_fv + ppf_fv + rbi_fv + gold_fv)

    corpus_needed = retirement_corpus_needed(
        s.get("retirement_monthly_today", 150000), infl, yrs)

    return {
        "years_to_retire": yrs,
        "equity_sip_stepup": equity_sip_stepup,
        "equity_sip_flat": equity_sip_flat,
        "existing_equity_fv": existing_equity_fv,
        "epf_fv": epf_fv,
        "nps_fv": nps_fv,
        "ppf_fv": ppf_fv,
        "rbi_fv": rbi_fv,
        "gold_fv": gold_fv,
        "total_with_stepup": total_stepup,
        "total_flat": total_flat,
        "corpus_needed": corpus_needed,
        "gap_stepup": corpus_needed - total_stepup,
        "gap_flat": corpus_needed - total_flat,
        "slab_rate": slab,
        "total_sip_now": total_sip_now,
    }


def house_analysis(s: dict) -> dict:
    """House purchase feasibility analysis."""
    age = s.get("age", 30)
    budget_today = s.get("house_budget_today", 0)
    parents = s.get("house_parents_contribution", 0)
    rate = s.get("house_loan_rate", 8.5)
    tenure = s.get("house_loan_tenure", 20)
    salary = s.get("net_take_home", 0)
    prop_appr = s.get("property_appreciation", 7.0) / 100

    max_emi = salary * 0.40
    max_loan = max_loan_for_emi(max_emi, rate, tenure)

    results = []
    for yr in [3, 5, 7, 10]:
        cost_at_yr = budget_today * (1 + prop_appr) ** yr
        own_needed = cost_at_yr - parents - max_loan
        results.append({
            "year": yr,
            "age_at_purchase": age + yr,
            "property_cost": cost_at_yr,
            "parents": parents,
            "max_loan": max_loan,
            "own_corpus_needed": max(0, own_needed),
            "emi": emi_amount(max_loan, rate, tenure),
            "total_interest": emi_amount(max_loan, rate, tenure) * tenure * 12 - max_loan,
        })

    return {
        "max_emi": max_emi,
        "max_loan": max_loan,
        "scenarios": results,
    }


def rent_vs_buy(s: dict, buy_year: int = 5) -> dict:
    """Compare renting + investing vs buying at a given year."""
    budget_today = s.get("house_budget_today", 0)
    parents = s.get("house_parents_contribution", 0)
    rate = s.get("house_loan_rate", 8.5)
    tenure = s.get("house_loan_tenure", 20)
    salary = s.get("net_take_home", 0)
    prop_appr = s.get("property_appreciation", 7.0) / 100
    rent_inflation = 0.08
    equity_return = EQUITY_LONG_TERM_RETURN
    age = s.get("age", 30)
    horizon = 15  # compare over 15 years post-decision

    max_emi = salary * 0.40
    max_loan = max_loan_for_emi(max_emi, rate, tenure)
    monthly_emi = emi_amount(max_loan, rate, tenure)

    property_at_buy = budget_today * (1 + prop_appr) ** buy_year
    own_needed = property_at_buy - parents - max_loan

    # BUY PATH: property value after horizon
    property_at_horizon = property_at_buy * (1 + prop_appr) ** horizon

    # RENT PATH: rent + invest own_needed in equity
    monthly_rent_today = budget_today * 0.028 / 12  # 2.8% yield
    rent_at_buy_year = monthly_rent_today * (1 + rent_inflation) ** buy_year
    rent_savings_vs_emi = monthly_emi - rent_at_buy_year  # could be negative
    # invest down payment
    invested_corpus = lumpsum_fv(own_needed, equity_return, horizon)
    # invest monthly savings (EMI - rent)
    if rent_savings_vs_emi > 0:
        savings_corpus = sip_future_value(rent_savings_vs_emi, equity_return, horizon)
    else:
        savings_corpus = 0
    rent_total_corpus = invested_corpus + savings_corpus

    # rent at end of horizon
    rent_at_horizon = rent_at_buy_year * (1 + rent_inflation) ** horizon

    return {
        "buy_year": buy_year,
        "property_at_buy": property_at_buy,
        "own_needed": own_needed,
        "monthly_emi": monthly_emi,
        "monthly_rent_at_buy": rent_at_buy_year,
        "property_at_horizon": property_at_horizon,
        "rent_corpus_at_horizon": rent_total_corpus,
        "rent_at_horizon": rent_at_horizon,
        "buy_wins": property_at_horizon > rent_total_corpus,
        "difference": property_at_horizon - rent_total_corpus,
        "horizon": horizon,
    }
