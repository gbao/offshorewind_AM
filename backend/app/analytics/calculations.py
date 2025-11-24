"""
Analytics and KPI calculation layer for Offshore Wind Operational Performance Hub.

This module contains all financial and operational calculations with transparent,
documented formulas following UK project-finance conventions.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from app.models import (
    Project, Period, FinancialStatementSet, IncomeStatement, BalanceSheet,
    CashFlowStatement, ProductionData, DebtFacility, DebtMovement,
    DividendDistribution, CovenantTest, RevenueBreakdown, CostBreakdown
)


def decimal_or_zero(value: Optional[Decimal]) -> Decimal:
    """Return value or zero if None."""
    return value if value is not None else Decimal("0")


def safe_divide(numerator: Optional[Decimal], denominator: Optional[Decimal]) -> Optional[Decimal]:
    """Safely divide two decimals, returning None if division not possible."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return (numerator / denominator).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def pct(value: Optional[Decimal]) -> Optional[Decimal]:
    """Convert decimal to percentage (multiply by 100)."""
    if value is None:
        return None
    return (value * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# =============================================================================
# INCOME STATEMENT CALCULATIONS
# =============================================================================

def calculate_gross_profit(income: IncomeStatement) -> Optional[Decimal]:
    """
    Gross Profit = Turnover - Cost of Sales
    """
    if income.turnover is None:
        return None
    return decimal_or_zero(income.turnover) - decimal_or_zero(income.cost_of_sales)


def calculate_operating_profit(income: IncomeStatement) -> Optional[Decimal]:
    """
    Operating Profit (EBIT) = Gross Profit - Administrative Expenses + Other Operating Income
    """
    gross_profit = calculate_gross_profit(income)
    if gross_profit is None:
        return None
    return (
        gross_profit
        - decimal_or_zero(income.administrative_expenses)
        + decimal_or_zero(income.other_operating_income)
    )


def calculate_ebitda(income: IncomeStatement) -> Optional[Decimal]:
    """
    EBITDA = Operating Profit + Depreciation

    Depreciation is added back to operating profit as it's a non-cash expense.
    """
    operating_profit = calculate_operating_profit(income)
    if operating_profit is None:
        return None
    return operating_profit + decimal_or_zero(income.depreciation)


def calculate_profit_before_tax(income: IncomeStatement) -> Optional[Decimal]:
    """
    Profit Before Tax = Operating Profit + Interest Receivable - Interest Payable
                        + Fair Value Movements + FX Gains/Losses
    """
    operating_profit = calculate_operating_profit(income)
    if operating_profit is None:
        return None
    return (
        operating_profit
        + decimal_or_zero(income.interest_receivable)
        - decimal_or_zero(income.interest_payable)
        + decimal_or_zero(income.fair_value_movement_derivatives)
        + decimal_or_zero(income.foreign_exchange_gain_loss)
    )


def calculate_total_tax(income: IncomeStatement) -> Optional[Decimal]:
    """
    Total Tax = Current Tax + Deferred Tax
    """
    return decimal_or_zero(income.current_tax) + decimal_or_zero(income.deferred_tax)


def calculate_profit_after_tax(income: IncomeStatement) -> Optional[Decimal]:
    """
    Profit After Tax = Profit Before Tax - Total Tax
    """
    pbt = calculate_profit_before_tax(income)
    if pbt is None:
        return None
    return pbt - calculate_total_tax(income)


# =============================================================================
# BALANCE SHEET CALCULATIONS
# =============================================================================

def calculate_total_fixed_assets(bs: BalanceSheet) -> Decimal:
    """
    Total Fixed Assets = Sum of all asset classes (Cost - Depreciation)
    """
    wind_farm_nbv = decimal_or_zero(bs.wind_farm_assets_cost) - decimal_or_zero(bs.wind_farm_assets_depreciation)
    transmission_nbv = decimal_or_zero(bs.transmission_assets_cost) - decimal_or_zero(bs.transmission_assets_depreciation)
    decom_nbv = decimal_or_zero(bs.decommissioning_asset_cost) - decimal_or_zero(bs.decommissioning_asset_depreciation)
    other_nbv = decimal_or_zero(bs.other_ppe_cost) - decimal_or_zero(bs.other_ppe_depreciation)
    return wind_farm_nbv + transmission_nbv + decom_nbv + other_nbv


def calculate_total_current_assets(bs: BalanceSheet) -> Decimal:
    """Total Current Assets = Sum of all current asset items."""
    return (
        decimal_or_zero(bs.trade_receivables)
        + decimal_or_zero(bs.intercompany_receivables)
        + decimal_or_zero(bs.prepayments_accrued_income)
        + decimal_or_zero(bs.other_debtors)
        + decimal_or_zero(bs.derivative_assets)
        + decimal_or_zero(bs.cash_and_equivalents)
    )


def calculate_total_current_liabilities(bs: BalanceSheet) -> Decimal:
    """Total Current Liabilities = Sum of all current liability items."""
    return (
        decimal_or_zero(bs.trade_payables)
        + decimal_or_zero(bs.intercompany_payables)
        + decimal_or_zero(bs.accruals_deferred_income)
        + decimal_or_zero(bs.current_tax_liability)
        + decimal_or_zero(bs.short_term_loans)
        + decimal_or_zero(bs.short_term_bonds)
        + decimal_or_zero(bs.short_term_lease_liability)
        + decimal_or_zero(bs.derivative_liabilities_current)
        + decimal_or_zero(bs.other_current_liabilities)
    )


def calculate_total_non_current_liabilities(bs: BalanceSheet) -> Decimal:
    """Total Non-Current Liabilities = Sum of all long-term liability items."""
    return (
        decimal_or_zero(bs.long_term_loans)
        + decimal_or_zero(bs.long_term_bonds)
        + decimal_or_zero(bs.shareholder_loans)
        + decimal_or_zero(bs.long_term_lease_liability)
        + decimal_or_zero(bs.deferred_tax_liability)
        + decimal_or_zero(bs.decommissioning_provision)
        + decimal_or_zero(bs.other_provisions)
        + decimal_or_zero(bs.deferred_profit_on_disposal)
        + decimal_or_zero(bs.derivative_liabilities_noncurrent)
    )


def calculate_total_equity(bs: BalanceSheet) -> Decimal:
    """Total Equity = Share Capital + Share Premium + Retained Earnings + Other Reserves."""
    return (
        decimal_or_zero(bs.share_capital)
        + decimal_or_zero(bs.share_premium)
        + decimal_or_zero(bs.retained_earnings)
        + decimal_or_zero(bs.other_reserves)
    )


def calculate_net_assets(bs: BalanceSheet) -> Decimal:
    """
    Net Assets = Total Assets - Total Liabilities
               = Fixed Assets + Current Assets - Current Liabilities - Non-Current Liabilities

    Should equal Total Equity (balance sheet identity).
    """
    return (
        calculate_total_fixed_assets(bs)
        + calculate_total_current_assets(bs)
        - calculate_total_current_liabilities(bs)
        - calculate_total_non_current_liabilities(bs)
    )


def calculate_total_debt(bs: BalanceSheet) -> Decimal:
    """
    Total Debt = Short-term Loans + Short-term Bonds + Long-term Loans + Long-term Bonds

    Excludes shareholder loans and lease liabilities for debt covenant purposes.
    """
    return (
        decimal_or_zero(bs.short_term_loans)
        + decimal_or_zero(bs.short_term_bonds)
        + decimal_or_zero(bs.long_term_loans)
        + decimal_or_zero(bs.long_term_bonds)
    )


def calculate_net_debt(bs: BalanceSheet) -> Decimal:
    """
    Net Debt = Total Debt - Cash and Equivalents

    A key leverage metric showing debt exposure net of liquid assets.
    """
    return calculate_total_debt(bs) - decimal_or_zero(bs.cash_and_equivalents)


# =============================================================================
# DEBT AND LEVERAGE CALCULATIONS
# =============================================================================

def calculate_debt_to_equity(bs: BalanceSheet) -> Optional[Decimal]:
    """
    Debt/Equity Ratio = Total Debt / Total Equity

    Measures financial leverage.
    """
    total_debt = calculate_total_debt(bs)
    total_equity = calculate_total_equity(bs)
    return safe_divide(total_debt, total_equity)


def calculate_gearing(bs: BalanceSheet) -> Optional[Decimal]:
    """
    Gearing = Net Debt / (Net Debt + Equity)

    Expressed as percentage. Shows proportion of capital from debt.
    """
    net_debt = calculate_net_debt(bs)
    equity = calculate_total_equity(bs)
    denominator = net_debt + equity
    return pct(safe_divide(net_debt, denominator))


def calculate_debt_service(
    period: Period,
    db: Session
) -> Decimal:
    """
    Debt Service = Interest Paid + Principal Repaid

    Sum across all debt facilities for the period.
    """
    movements = db.query(DebtMovement).filter(DebtMovement.period_id == period.id).all()
    total = Decimal("0")
    for m in movements:
        total += decimal_or_zero(m.interest_charged) + decimal_or_zero(m.principal_repaid)
    return total


def calculate_cfads(
    income: Optional[IncomeStatement],
    cash_flow: Optional[CashFlowStatement],
    bs: Optional[BalanceSheet]
) -> Optional[Decimal]:
    """
    Cash Flow Available for Debt Service (CFADS)

    If explicit CFADS is provided (from loan compliance certificate), use it.
    Otherwise, approximate:

    CFADS (approx) = EBITDA - Tax Paid - Maintenance Capex - Working Capital Changes

    For simplicity, we use: EBITDA - Current Tax (proxy for cash tax)
    """
    if cash_flow and cash_flow.cfads_input is not None:
        return cash_flow.cfads_input

    if income is None:
        return None

    ebitda = calculate_ebitda(income)
    if ebitda is None:
        return None

    # Proxy: EBITDA - Current Tax
    return ebitda - decimal_or_zero(income.current_tax)


def calculate_dscr(
    cfads: Optional[Decimal],
    debt_service: Decimal
) -> Optional[Decimal]:
    """
    Debt Service Coverage Ratio (DSCR) = CFADS / Debt Service

    A key covenant metric. Typically must be > 1.10x - 1.20x.
    """
    return safe_divide(cfads, debt_service)


def calculate_dscr_headroom(
    actual_dscr: Optional[Decimal],
    required_minimum: Decimal = Decimal("1.10")
) -> Optional[Decimal]:
    """
    DSCR Headroom = (Actual DSCR - Required Minimum) / Required Minimum * 100

    Expressed as percentage above the covenant threshold.
    """
    if actual_dscr is None:
        return None
    headroom = actual_dscr - required_minimum
    return pct(safe_divide(headroom, required_minimum))


# =============================================================================
# OPERATIONAL KPI CALCULATIONS
# =============================================================================

def calculate_capacity_factor(
    production: ProductionData,
    installed_capacity_mw: Decimal
) -> Optional[Decimal]:
    """
    Capacity Factor = Actual Generation / Maximum Possible Generation * 100

    Maximum Possible = Installed Capacity (MW) * Period Hours

    Expressed as percentage. Typical offshore wind: 35-50%.
    """
    if production.net_export_mwh is None or production.period_hours is None:
        return None
    if installed_capacity_mw == 0 or production.period_hours == 0:
        return None

    max_generation = installed_capacity_mw * production.period_hours
    return pct(safe_divide(production.net_export_mwh, max_generation))


def calculate_generation_vs_p50(production: ProductionData) -> Optional[Decimal]:
    """
    Generation vs P50 = (Actual - P50) / P50 * 100

    Shows performance relative to long-term expected generation.
    """
    if production.net_export_mwh is None or production.p50_generation_mwh is None:
        return None
    if production.p50_generation_mwh == 0:
        return None
    diff = production.net_export_mwh - production.p50_generation_mwh
    return pct(safe_divide(diff, production.p50_generation_mwh))


def calculate_generation_vs_budget(production: ProductionData) -> Optional[Decimal]:
    """
    Generation vs Budget = (Actual - Budget) / Budget * 100
    """
    if production.net_export_mwh is None or production.budget_generation_mwh is None:
        return None
    if production.budget_generation_mwh == 0:
        return None
    diff = production.net_export_mwh - production.budget_generation_mwh
    return pct(safe_divide(diff, production.budget_generation_mwh))


def calculate_revenue_per_mwh(
    revenue: Optional[Decimal],
    generation_mwh: Optional[Decimal]
) -> Optional[Decimal]:
    """
    Revenue per MWh = Total Revenue / Net Generation

    Key unit economics metric (£/MWh).
    """
    return safe_divide(revenue, generation_mwh)


def calculate_cost_per_mwh(
    costs: Optional[Decimal],
    generation_mwh: Optional[Decimal]
) -> Optional[Decimal]:
    """
    Cost per MWh = Total Operating Costs / Net Generation

    Key unit economics metric (£/MWh).
    """
    return safe_divide(costs, generation_mwh)


# =============================================================================
# DIVIDEND AND EQUITY RETURN CALCULATIONS
# =============================================================================

def calculate_dividend_yield(
    dividends_paid: Optional[Decimal],
    equity_invested: Optional[Decimal]
) -> Optional[Decimal]:
    """
    Dividend Yield = Dividends Paid / Initial Equity Invested * 100

    Simple annual yield on equity.
    """
    return pct(safe_divide(dividends_paid, equity_invested))


def calculate_cumulative_dividends(
    project_id: int,
    db: Session,
    up_to_period_id: Optional[int] = None
) -> Decimal:
    """
    Sum of all dividends paid for a project up to a given period.
    """
    query = db.query(DividendDistribution).join(Period).filter(
        Period.project_id == project_id
    )
    if up_to_period_id:
        # Get the period end date for filtering
        period = db.query(Period).filter(Period.id == up_to_period_id).first()
        if period:
            query = query.filter(Period.period_end <= period.period_end)

    total = Decimal("0")
    for dd in query.all():
        total += decimal_or_zero(dd.dividends_paid)
    return total


# =============================================================================
# COMPREHENSIVE KPI CALCULATION
# =============================================================================

def calculate_period_kpis(
    period: Period,
    project: Project,
    db: Session
) -> Dict[str, Any]:
    """
    Calculate all KPIs for a given period.

    Returns a dictionary with all computed metrics.
    """
    kpis = {
        "period_id": period.id,
        "period_end": period.period_end,
    }

    # Get related data
    fs = period.financial_statement
    production = period.production_data
    dividend = period.dividend_distribution

    income = fs.income_statement if fs else None
    balance_sheet = fs.balance_sheet if fs else None
    cash_flow = fs.cash_flow_statement if fs else None

    # Income Statement KPIs
    if income:
        kpis["revenue"] = income.turnover
        kpis["ebitda"] = calculate_ebitda(income)
        kpis["ebit"] = calculate_operating_profit(income)
        kpis["net_profit"] = calculate_profit_after_tax(income)

        # Margins
        if income.turnover and income.turnover != 0:
            kpis["ebitda_margin_pct"] = pct(safe_divide(kpis.get("ebitda"), income.turnover))
            kpis["ebit_margin_pct"] = pct(safe_divide(kpis.get("ebit"), income.turnover))
            kpis["net_margin_pct"] = pct(safe_divide(kpis.get("net_profit"), income.turnover))

    # Balance Sheet KPIs
    if balance_sheet:
        kpis["net_debt"] = calculate_net_debt(balance_sheet)
        kpis["total_debt"] = calculate_total_debt(balance_sheet)
        kpis["debt_to_equity"] = calculate_debt_to_equity(balance_sheet)
        kpis["gearing_pct"] = calculate_gearing(balance_sheet)
        kpis["total_equity"] = calculate_total_equity(balance_sheet)
        kpis["net_assets"] = calculate_net_assets(balance_sheet)
        kpis["total_fixed_assets"] = calculate_total_fixed_assets(balance_sheet)

    # Cash Flow and Debt Service KPIs
    if cash_flow:
        kpis["cash_from_operations"] = cash_flow.net_cash_from_operating

    cfads = calculate_cfads(income, cash_flow, balance_sheet)
    kpis["cfads"] = cfads

    debt_service = calculate_debt_service(period, db)
    kpis["debt_service"] = debt_service

    if cfads and debt_service and debt_service > 0:
        kpis["dscr"] = calculate_dscr(cfads, debt_service)
        kpis["dscr_headroom_pct"] = calculate_dscr_headroom(kpis.get("dscr"))

    # Production KPIs
    if production:
        kpis["availability_pct"] = production.availability_pct
        kpis["capacity_factor_pct"] = calculate_capacity_factor(production, project.installed_capacity_mw)
        kpis["generation_vs_p50_pct"] = calculate_generation_vs_p50(production)
        kpis["generation_vs_budget_pct"] = calculate_generation_vs_budget(production)
        kpis["net_generation_mwh"] = production.net_export_mwh

        # Unit economics
        if income and production.net_export_mwh:
            kpis["revenue_per_mwh"] = calculate_revenue_per_mwh(income.turnover, production.net_export_mwh)
            kpis["cost_per_mwh"] = calculate_cost_per_mwh(income.cost_of_sales, production.net_export_mwh)

    # Dividend KPIs
    if dividend:
        kpis["dividends_paid"] = dividend.dividends_paid
        kpis["cash_available_for_distribution"] = dividend.cash_available_for_distribution

    if project.initial_equity_invested and dividend:
        kpis["dividend_yield_pct"] = calculate_dividend_yield(
            dividend.dividends_paid,
            project.initial_equity_invested
        )

    kpis["cumulative_dividends"] = calculate_cumulative_dividends(project.id, db, period.id)

    return kpis


def calculate_yoy_change(
    current: Optional[Decimal],
    previous: Optional[Decimal]
) -> Optional[Decimal]:
    """
    Year-over-Year Change = (Current - Previous) / Previous * 100
    """
    if current is None or previous is None or previous == 0:
        return None
    diff = current - previous
    return pct(safe_divide(diff, abs(previous)))


def get_project_kpi_summary(
    project: Project,
    db: Session
) -> Dict[str, Any]:
    """
    Get summary KPIs for a project across all periods.

    Includes latest period values and YoY comparisons.
    """
    periods = db.query(Period).filter(
        Period.project_id == project.id
    ).order_by(Period.period_end.desc()).all()

    if not periods:
        return {
            "project_id": project.id,
            "project_name": project.name,
            "installed_capacity_mw": project.installed_capacity_mw,
        }

    # Calculate KPIs for each period
    period_kpis = []
    for period in periods:
        kpis = calculate_period_kpis(period, project, db)
        period_kpis.append(kpis)

    latest = period_kpis[0] if period_kpis else {}
    previous = period_kpis[1] if len(period_kpis) > 1 else {}

    summary = {
        "project_id": project.id,
        "project_name": project.name,
        "installed_capacity_mw": project.installed_capacity_mw,
        "cod_date": project.cod_date,

        # Latest period values
        "latest_revenue": latest.get("revenue"),
        "latest_ebitda": latest.get("ebitda"),
        "latest_ebitda_margin_pct": latest.get("ebitda_margin_pct"),
        "latest_net_profit": latest.get("net_profit"),
        "latest_net_debt": latest.get("net_debt"),
        "latest_dscr": latest.get("dscr"),
        "latest_capacity_factor_pct": latest.get("capacity_factor_pct"),
        "latest_availability_pct": latest.get("availability_pct"),
        "latest_dividends": latest.get("dividends_paid"),

        # Cumulative
        "cumulative_dividends": latest.get("cumulative_dividends"),

        # YoY changes
        "revenue_yoy_pct": calculate_yoy_change(
            latest.get("revenue"),
            previous.get("revenue")
        ),
        "ebitda_yoy_pct": calculate_yoy_change(
            latest.get("ebitda"),
            previous.get("ebitda")
        ),
        "net_profit_yoy_pct": calculate_yoy_change(
            latest.get("net_profit"),
            previous.get("net_profit")
        ),

        # Historical data
        "period_kpis": period_kpis,
    }

    return summary
