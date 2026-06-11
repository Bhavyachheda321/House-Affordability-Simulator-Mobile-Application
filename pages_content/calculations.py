"""
FinPlan India v4 — Simulation Engine
Year-by-year projection aligned to Indian Financial Year (April–March).
Replaces v3's terminal-formula approach with a full simulation loop.
"""
import math
from pages_content.tax_engine import compute_annual_tax, ltcg_tax, effective_slab_rate_from_bracket

# ── Return assumptions ────────────────────────────────────────────────────────
EQUITY_RETURN    = 0.12    # Nifty index funds long-term
LIQUID_RETURN    = 0.07    # Liquid / money-market funds
ARBITRAGE_RETURN = 0.065   # Arbitrage funds
PPF_RATE         = 0.071   # EEE, annual compounding
EPF_RATE         = 0.0825  # FY 2024-25 declared rate
NPS_EQUITY       = 0.10    # NPS Tier-1 equity (conservative)
GOLD_RETURN      = 0.09    # Gold INR long-term
RBI_BOND_RATE    = 0.0805  # RBI FRSB floating (held flat)
FD_RATE          = 0.072   # Generic FD

# ── Safe withdrawal rate table ────────────────────────────────────────────────
def safe_withdrawal_rate(horizon_years: int) -> float:
    """Trinity Study adapted for India's higher inflation environment."""
    if horizon_years >= 35: return 0.035
    if horizon_years >= 30: return 0.038
    if horizon_years >= 25: return 0.040
    if horizon_years >= 20: return 0.045
    if horizon_years >= 15: return 0.050
    return 0.055


# ── Time-value helpers ────────────────────────────────────────────────────────
def fv_lumpsum(principal: float, annual_rate: float, years: float,
               compounding: str = "monthly") -> float:
    if principal <= 0 or years <= 0: return 0.0
    if compounding == "annual":
        return principal * (1 + annual_rate) ** years
    r = annual_rate / 12
    return principal * (1 + r) ** (years * 12)


def fv_sip(monthly: float, annual_rate: float, years: float) -> float:
    """End-of-month SIP future value."""
    if monthly <= 0 or years <= 0: return 0.0
    r = annual_rate / 12
    n = years * 12
    if r == 0: return monthly * n
    return monthly * ((1 + r) ** n - 1) / r


def sip_needed(goal_fv: float, annual_rate: float, years: float) -> float:
    """Monthly SIP to reach goal_fv."""
    if goal_fv <= 0 or years <= 0: return 0.0
    r = annual_rate / 12
    n = years * 12
    if r == 0: return goal_fv / n
    return goal_fv * r / ((1 + r) ** n - 1)


def emi_amount(principal: float, annual_rate_pct: float, tenure_years: int) -> float:
    if principal <= 0: return 0.0
    r = annual_rate_pct / 100 / 12
    n = tenure_years * 12
    if r == 0: return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def max_loan_for_emi(max_emi: float, annual_rate_pct: float, tenure_years: int) -> float:
    r = annual_rate_pct / 100 / 12
    n = tenure_years * 12
    if r == 0: return max_emi * n
    return max_emi * ((1 + r) ** n - 1) / (r * (1 + r) ** n)


# ── City tables ───────────────────────────────────────────────────────────────
CITY_PROPERTY_APPRECIATION = {
    "Mumbai": 7.0, "Delhi NCR": 6.0, "Bengaluru": 8.0,
    "Pune": 7.0, "Hyderabad": 7.5, "Chennai": 5.5,
    "Kolkata": 5.0, "Ahmedabad": 6.5, "Other": 6.0,
}
CITY_STAMP_DUTY = {
    "Mumbai": 0.06, "Delhi NCR": 0.06, "Bengaluru": 0.055,
    "Pune": 0.06, "Hyderabad": 0.05, "Chennai": 0.07,
    "Kolkata": 0.06, "Ahmedabad": 0.045, "Other": 0.06,
}
CITY_RENTAL_YIELD = {
    "Mumbai": 0.028, "Delhi NCR": 0.030, "Bengaluru": 0.035,
    "Pune": 0.032, "Hyderabad": 0.035, "Chennai": 0.030,
    "Kolkata": 0.028, "Ahmedabad": 0.030, "Other": 0.030,
}
CITY_LIFESTYLE_INFLATION = {
    "Mumbai": 8, "Delhi NCR": 7, "Bengaluru": 7, "Pune": 7,
    "Hyderabad": 7, "Chennai": 6, "Kolkata": 6, "Ahmedabad": 6, "Other": 6,
}


# ── Asset projection helpers ──────────────────────────────────────────────────
def ppf_annual_step(balance: float, annual_contrib: float) -> float:
    """PPF: annual compounding. Contribution added at start of year."""
    return (balance + annual_contrib) * (1 + PPF_RATE)


def epf_annual_step(balance: float, employee_monthly: float) -> float:
    """
    EPF: only the employee share goes to EPF corpus.
    Employer's 8.33% goes to EPS (no lump-sum for employee) so we do NOT double-count.
    Employee contribution: as entered.
    Employer EPF portion: 3.67% of basic — approximated as 30% of employee contribution
    (since employee typically contributes 12% of basic, employer EPF = 3.67/12 ≈ 30.6%).
    """
    employer_epf_monthly = employee_monthly * 0.306   # 3.67% / 12% ≈ 30.6%
    total_monthly = employee_monthly + employer_epf_monthly
    annual_contrib = total_monthly * 12
    return (balance + annual_contrib) * (1 + EPF_RATE)


def nps_step(balance: float, monthly_contrib: float, years: float = 1.0) -> float:
    return fv_lumpsum(balance, NPS_EQUITY, years) + fv_sip(monthly_contrib, NPS_EQUITY, years)


# ── Main simulation ───────────────────────────────────────────────────────────
def run_simulation(s: dict) -> list:
    """
    Year-by-year simulation aligned to Indian Financial Year.
    Each iteration = one FY (April–March).
    Returns list of annual snapshots keyed by FY index (0 = current FY).

    s: session_state dict (full)
    """
    age        = s.get("age", 30)
    ret_age    = s.get("retirement_age", 55)
    max_age    = max(ret_age + 5, age + 5)
    max_years  = max_age - age

    # Income
    gross_monthly    = s.get("income_gross_monthly", 0)
    net_monthly      = s.get("monthly_salary", 0)          # take-home
    salary_growth    = s.get("salary_growth", 8) / 100
    annual_bonus     = s.get("annual_bonus", 0)
    bonus_growth     = s.get("bonus_growth", 5) / 100

    # Spouse
    spouse_active    = s.get("has_spouse_income", False)
    spouse_net       = s.get("spouse_monthly_salary", 0)
    spouse_growth    = s.get("spouse_salary_growth", 8) / 100
    spouse_sip       = s.get("spouse_sip_monthly", 0)

    # Tax
    tax_regime       = "old" if s.get("old_regime", False) else "new"
    basic_monthly    = s.get("basic_monthly", 0)
    hra_monthly      = s.get("hra_monthly", 0)
    metro            = s.get("metro_city", True)
    other_80c        = s.get("other_80c", 0)
    nps_employer_ann = s.get("employer_nps_annual", 0)

    # Expenses
    monthly_expenses = s.get("monthly_expenses", 0)
    exp_inflation    = s.get("expense_inflation", 6) / 100
    rent_monthly     = s.get("rent_monthly", 0)
    rent_inflation   = s.get("rent_inflation", 8) / 100
    family_support   = s.get("family_support_annual", 0)

    # Assets (opening balances)
    assets = {
        "equity":    s.get("mf_value", 0) + s.get("stocks_value", 0),
        "ppf":       s.get("ppf_value", 0),
        "epf":       s.get("epf_value", 0),
        "nps":       s.get("nps_value", 0),
        "gold":      s.get("gold_value", 0),
        "fd":        s.get("fd_value", 0),
        "emergency": s.get("emergency_fund_value", 0) if s.get("has_emergency_fund") else 0,
    }

    sip_monthly      = s.get("sip_total_monthly", 0)
    sip_stepup       = s.get("sip_stepup_pct", 10) / 100   # annual % increase
    epf_employee_mo  = s.get("epf_monthly", 0)
    ppf_contributing = s.get("ppf_contributing", True)
    ppf_annual_amt   = 150_000 if ppf_contributing else 0

    # Loans
    loan_outstanding = s.get("loans_outstanding", 0)
    loan_emi         = s.get("loan_emi_monthly", 0)
    loan_rate        = s.get("loan_interest_rate", 0)

    # Inflation
    lifestyle_infl   = s.get("lifestyle_inflation", 7) / 100
    slab_scale_growth= 0.0   # slab indexation — set to 0 for conservative

    snapshots = []

    for t in range(max_years + 1):
        fy_age = age + t

        # ── Income this FY ────────────────────────────────────────────────────
        gross_ann  = gross_monthly * 12 * (1 + salary_growth) ** t
        net_ann    = net_monthly * 12 * (1 + salary_growth) ** t
        bonus_ann  = annual_bonus * (1 + bonus_growth) ** t
        spouse_ann = spouse_net * 12 * (1 + spouse_growth) ** t if spouse_active else 0

        # ── Tax this FY ───────────────────────────────────────────────────────
        rent_ann   = rent_monthly * 12 * (1 + rent_inflation) ** t
        tax_info   = compute_annual_tax(
            annual_gross      = gross_ann,
            tax_regime        = tax_regime,
            other_80c         = other_80c,
            basic_annual      = basic_monthly * 12,
            hra_annual        = hra_monthly * 12,
            rent_annual       = rent_ann,
            metro             = metro,
            nps_employer_annual = nps_employer_ann,
            slab_scale        = 1.0 + slab_scale_growth * t,
        )
        eff_rate  = tax_info["effective_rate"]
        take_home = net_ann if net_monthly > 0 else tax_info["take_home_monthly"] * 12
        take_home += spouse_ann

        # ── Expenses this FY ──────────────────────────────────────────────────
        expenses_ann     = monthly_expenses * 12 * (1 + exp_inflation) ** t
        rent_paid        = rent_ann
        family_ann       = family_support * (1 + lifestyle_infl) ** t
        loan_emi_ann     = loan_emi * 12 if loan_outstanding > 0 else 0

        # ── Surplus ───────────────────────────────────────────────────────────
        # Bonus net of tax
        bonus_net  = bonus_ann * (1 - eff_rate)
        surplus    = max(0.0,
            take_home
            - expenses_ann
            - rent_paid
            - family_ann
            - loan_emi_ann
            + bonus_net
        )

        # ── SIP contributions this FY (step-up every April = every t) ────────
        current_sip_monthly = sip_monthly * (1 + sip_stepup) ** t
        current_sip_ann     = current_sip_monthly * 12
        spouse_sip_ann      = spouse_sip * (1 + sip_stepup) ** t * 12

        # Total committed SIP (equity bucket)
        committed_sip = current_sip_ann + spouse_sip_ann

        # Excess surplus after committed SIPs → also invested in equity
        investable_surplus = max(0.0, surplus - committed_sip)

        # ── Asset growth this FY ─────────────────────────────────────────────
        # Equity (MF + stocks) — monthly compounding
        eq_return  = assets["equity"] * EQUITY_RETURN
        eq_new     = assets["equity"] + eq_return + committed_sip + investable_surplus

        # PPF — annual compounding, April 1 deposit
        ppf_new    = ppf_annual_step(assets["ppf"], ppf_annual_amt)

        # EPF — annual compounding with correct employer EPF share
        epf_new    = epf_annual_step(assets["epf"], epf_employee_mo)

        # NPS
        nps_new    = nps_step(assets["nps"], 0)   # employer NPS reflected via take-home

        # Gold
        gold_new   = assets["gold"] * (1 + GOLD_RETURN)

        # FD — annual compounding, interest taxed at slab
        fd_interest= assets["fd"] * FD_RATE
        fd_tax     = fd_interest * eff_rate
        fd_new     = assets["fd"] + fd_interest - fd_tax

        # Emergency fund — liquid rate, no tax (held in liquid fund)
        em_new     = assets["emergency"] * (1 + LIQUID_RETURN)

        assets = {
            "equity":    eq_new,
            "ppf":       ppf_new,
            "epf":       epf_new,
            "nps":       nps_new,
            "gold":      gold_new,
            "fd":        fd_new,
            "emergency": em_new,
        }

        total_portfolio = sum(assets.values())

        snapshots.append({
            "t":                   t,
            "age":                 fy_age,
            "gross_annual":        gross_ann,
            "take_home_annual":    take_home,
            "take_home_monthly":   take_home / 12,
            "effective_tax_rate":  eff_rate,
            "expenses_annual":     expenses_ann,
            "rent_annual":         rent_paid,
            "family_annual":       family_ann,
            "loan_emi_annual":     loan_emi_ann,
            "surplus_annual":      surplus,
            "committed_sip_ann":   committed_sip,
            "investable_surplus":  investable_surplus,
            "assets":              dict(assets),
            "total_portfolio":     total_portfolio,
        })

    return snapshots


# ── Retirement projection ─────────────────────────────────────────────────────
def project_retirement(s: dict, snapshots: list) -> dict:
    age        = s.get("age", 30)
    ret_age    = s.get("retirement_age", 55)
    yrs        = max(1, ret_age - age)
    post_yrs   = max(15, 85 - ret_age)
    infl       = s.get("lifestyle_inflation", 7) / 100
    monthly_spend = s.get("retirement_monthly_spend", 100_000)

    # Find snapshot closest to retirement year
    snap = snapshots[min(yrs, len(snapshots) - 1)]
    corpus_at_ret = snap["total_portfolio"]

    # Corpus needed
    future_monthly = monthly_spend * (1 + infl) ** yrs
    swr = safe_withdrawal_rate(post_yrs)
    corpus_needed  = (future_monthly * 12) / swr

    gap = corpus_needed - corpus_at_ret

    return {
        "years_to_retire":  yrs,
        "post_retire_years": post_yrs,
        "swr":              swr,
        "corpus_at_ret":    corpus_at_ret,
        "corpus_needed":    corpus_needed,
        "gap":              gap,
        "on_track":         gap <= 0,
        "assets_at_ret":    snap["assets"],
    }


# ── Cashflow summary ──────────────────────────────────────────────────────────
def monthly_cashflow(s: dict) -> dict:
    income   = s.get("monthly_salary", 0) + s.get("annual_bonus", 0) / 12
    if s.get("has_spouse_income"):
        income += s.get("spouse_monthly_salary", 0)
    expenses = s.get("monthly_expenses", 0)
    family   = s.get("family_support_annual", 0) / 12
    sip      = s.get("sip_total_monthly", 0)
    loan_emi = s.get("loan_emi_monthly", 0)
    surplus  = income - expenses - family - sip - loan_emi
    return {
        "income": income, "expenses": expenses, "family": family,
        "sip": sip, "loan_emi": loan_emi, "surplus": surplus,
    }


# ── Goal projections ──────────────────────────────────────────────────────────
def goal_corpus_needed(amount_today: float, years: float, inflation: float) -> float:
    return amount_today * (1 + inflation) ** years


def goal_monthly_sip(goal_fv: float, years: float,
                     annual_rate: float = EQUITY_RETURN) -> float:
    return sip_needed(goal_fv, annual_rate, years)


# ── House scenarios ───────────────────────────────────────────────────────────
def house_scenarios(s: dict, snapshots: list) -> dict:
    sal       = s.get("monthly_salary", 0)
    budget    = s.get("house_budget", 0)
    parents   = s.get("parents_house_contribution", 0)
    loan_rate = s.get("home_loan_rate", 8.5)
    tenure    = s.get("home_loan_tenure", 20)
    appr      = s.get("property_appr_rate",
                      CITY_PROPERTY_APPRECIATION.get(s.get("city", "Other"), 6.0)) / 100
    city      = s.get("city", "Other")
    stamp     = CITY_STAMP_DUTY.get(city, 0.06)

    max_emi   = sal * 0.40
    max_loan  = max_loan_for_emi(max_emi, loan_rate, tenure)

    scenarios = []
    for yr in [3, 5, 7, 10]:
        cost_at_yr     = budget * (1 + appr) ** yr
        stamp_reg      = cost_at_yr * stamp
        own_needed     = max(0, cost_at_yr + stamp_reg - parents - max_loan)
        emi            = emi_amount(max_loan, loan_rate, tenure)
        # Portfolio at that year from simulation
        portfolio_yr   = snapshots[min(yr, len(snapshots) - 1)]["total_portfolio"] \
                         if yr < len(snapshots) else 0
        scenarios.append({
            "year":          yr,
            "age":           s.get("age", 30) + yr,
            "property_cost": cost_at_yr,
            "stamp_reg":     stamp_reg,
            "own_needed":    own_needed,
            "max_loan":      max_loan,
            "emi":           emi,
            "portfolio":     portfolio_yr,
            "feasible":      portfolio_yr >= own_needed,
        })
    return {"max_emi": max_emi, "max_loan": max_loan, "stamp_pct": stamp, "scenarios": scenarios}


# ── Debt priority ─────────────────────────────────────────────────────────────
def debt_priority(loan_rate_pct: float, loan_outstanding: float,
                  monthly_emi: float) -> dict:
    if loan_outstanding <= 0:
        return {"has_loan": False}
    guaranteed_return = loan_rate_pct / 100
    # Note: equity return is probabilistic; loan savings are guaranteed.
    # We recommend prepayment when loan rate > 10% (not 12%), giving equity
    # the benefit of the doubt only for clearly lower-cost debt (home loans).
    PREPAY_THRESHOLD = 0.10
    if guaranteed_return > PREPAY_THRESHOLD:
        return {
            "has_loan": True,
            "should_prepay": True,
            "reason": (
                f"Your loan costs {loan_rate_pct:.1f}% — that's a guaranteed saving, "
                f"whereas equity returns of 12% are uncertain. "
                f"Paying off high-interest debt first is the lower-risk choice."
            ),
        }
    else:
        return {
            "has_loan": True,
            "should_prepay": False,
            "reason": (
                f"Your loan costs {loan_rate_pct:.1f}% — low enough that investing "
                f"in equity (expected 12%, not guaranteed) likely wins over time. "
                f"Continue EMIs and invest surplus."
            ),
        }
