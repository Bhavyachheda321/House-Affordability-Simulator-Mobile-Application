"""
FinPlan India v4 — Tax Engine
Indian Financial Year (April–March) aligned.
Handles New Regime, Old Regime, surcharge schedules, HRA exemption, NPS 80CCD(2).
All income in INR annual figures.
"""

# ── Slab tables ───────────────────────────────────────────────────────────────
# (upper_limit, rate) — income above previous limit up to upper_limit taxed at rate
NEW_REGIME_SLABS_FY25 = [
    (400_000,   0.00),
    (800_000,   0.05),
    (1_200_000, 0.10),
    (1_600_000, 0.15),
    (2_000_000, 0.20),
    (2_400_000, 0.25),
    (float('inf'), 0.30),
]

OLD_REGIME_SLABS = [
    (250_000,      0.00),
    (500_000,      0.05),
    (1_000_000,    0.20),
    (float('inf'), 0.30),
]

# Surcharge thresholds (total income → surcharge rate on base tax)
SURCHARGE_NEW = [
    (5_000_000,    0.00),
    (10_000_000,   0.10),
    (20_000_000,   0.15),
    (float('inf'), 0.25),   # Capped at 25% for new regime
]
SURCHARGE_OLD = [
    (5_000_000,    0.00),
    (10_000_000,   0.10),
    (20_000_000,   0.15),
    (50_000_000,   0.25),
    (float('inf'), 0.37),
]

CESS_RATE    = 0.04
STD_DED_OLD  = 50_000
STD_DED_NEW  = 75_000   # Effective FY 2024-25 onwards


def _scale_slabs(slabs: list, factor: float) -> list:
    """Scale slab upper limits by factor (for future slab inflation modelling)."""
    return [(l * factor if l != float('inf') else float('inf'), r) for l, r in slabs]


def _compute_slab_tax(income: float, slabs: list) -> float:
    tax, prev = 0.0, 0.0
    for limit, rate in slabs:
        if income <= prev:
            break
        taxable_in_band = min(income, limit) - prev
        tax += taxable_in_band * rate
        prev = limit
    return tax


def _get_surcharge_rate(income: float, regime: str) -> float:
    table = SURCHARGE_NEW if regime == "new" else SURCHARGE_OLD
    for limit, rate in table:
        if income <= limit:
            return rate
    return table[-1][1]


def compute_annual_tax(
    annual_gross: float,
    tax_regime: str,          # "new" or "old"
    other_80c: float = 0.0,   # EPF employee + ELSS + LIC + PPF contributions, max ₹1.5L
    basic_annual: float = 0.0,
    hra_annual: float = 0.0,
    rent_annual: float = 0.0,
    metro: bool = True,
    nps_employer_annual: float = 0.0,  # 80CCD(2) — deductible in both regimes
    nps_pct_of_basic: float = 0.0,     # alternative: compute NPS as % of basic
    slab_scale: float = 1.0,           # >1 to model future slab widening
) -> dict:
    """
    Compute Indian income tax for a given FY.

    Returns:
        total_tax          — annual tax liability (INR)
        take_home_monthly  — (annual_gross - total_tax) / 12
        effective_rate     — total_tax / annual_gross
        taxable_income     — after deductions
        base_tax           — before surcharge + cess
    """
    annual_gross = max(0.0, annual_gross)

    # ── NPS 80CCD(2) — deductible in both regimes ─────────────────────────────
    nps_ded = nps_employer_annual if nps_employer_annual > 0 else (
        basic_annual * (nps_pct_of_basic / 100.0) if basic_annual > 0 else 0.0
    )
    # Cap: 10% of basic for private sector (14% for govt — not modelled here)
    if basic_annual > 0:
        nps_ded = min(nps_ded, basic_annual * 0.10)

    if tax_regime == "old":
        # ── HRA exemption ─────────────────────────────────────────────────────
        hra_exempt = 0.0
        if basic_annual > 0 and hra_annual > 0 and rent_annual > 0:
            hra_exempt = min(
                hra_annual,
                basic_annual * (0.50 if metro else 0.40),
                max(0.0, rent_annual - 0.10 * basic_annual),
            )

        deductions = (
            STD_DED_OLD
            + hra_exempt
            + min(other_80c, 150_000)   # 80C ceiling
            + nps_ded
        )
        taxable_income = max(0.0, annual_gross - deductions)
        slabs = _scale_slabs(OLD_REGIME_SLABS, slab_scale)
        base_tax = _compute_slab_tax(taxable_income, slabs)

        # 87A rebate: if taxable income ≤ ₹5L, tax = 0
        if taxable_income <= 500_000 * slab_scale:
            base_tax = max(0.0, base_tax - 12_500)

    else:  # new regime
        deductions = STD_DED_NEW + nps_ded
        taxable_income = max(0.0, annual_gross - deductions)
        slabs = _scale_slabs(NEW_REGIME_SLABS_FY25, slab_scale)
        base_tax = _compute_slab_tax(taxable_income, slabs)

        # Section 87A rebate for new regime: full rebate if taxable ≤ ₹12L
        if taxable_income <= 1_200_000 * slab_scale:
            base_tax = 0.0
        elif taxable_income <= 1_275_000 * slab_scale:
            # Marginal relief: tax capped at (income - 12L)
            base_tax = min(base_tax, taxable_income - 1_200_000 * slab_scale)

    surcharge_rate = _get_surcharge_rate(taxable_income, tax_regime)
    surcharge      = base_tax * surcharge_rate
    cess           = (base_tax + surcharge) * CESS_RATE
    total_tax      = base_tax + surcharge + cess

    return {
        "total_tax":         total_tax,
        "take_home_monthly": (annual_gross - total_tax) / 12,
        "effective_rate":    (total_tax / annual_gross) if annual_gross > 0 else 0.0,
        "taxable_income":    taxable_income,
        "base_tax":          base_tax,
        "surcharge":         surcharge,
        "cess":              cess,
    }


def ltcg_tax(gain: float, slab_rate: float) -> float:
    """
    Equity LTCG: 12.5% on gains above ₹1.25L/year (post Budget 2024).
    Surcharge capped at 15% for Sec 112A regardless of income.
    """
    exemption = 125_000
    taxable   = max(0.0, gain - exemption)
    surcharge = 0.15 if slab_rate >= 0.20 else 0.0
    rate      = 0.125 * (1 + surcharge) * (1 + CESS_RATE)
    return taxable * rate


def stcg_tax(gain: float, slab_rate: float) -> float:
    """Equity STCG: 20% flat (post Budget 2024), surcharge capped at 15% Sec 111A."""
    surcharge = 0.15 if slab_rate >= 0.20 else 0.0
    return gain * 0.20 * (1 + surcharge) * (1 + CESS_RATE)


def effective_slab_rate_from_bracket(bracket_label: str) -> float:
    """
    Fallback lookup when full tax computation isn't available.
    Returns effective rate including surcharge + cess.
    """
    rates = {
        "Under ₹7L":   0.0,
        "₹7L–₹12L":    0.0,
        "₹12L–₹20L":   0.1456,
        "₹20L–₹50L":   0.2288,
        "₹50L–₹1Cr":   0.3432,   # 30% + 10% surcharge + 4% cess
        "₹1Cr–₹2Cr":   0.3744,   # 30% + 15% surcharge + 4% cess
        "Above ₹2Cr":  0.3900,   # 30% + 25% surcharge + 4% cess (new regime cap)
    }
    return rates.get(bracket_label, 0.2288)
