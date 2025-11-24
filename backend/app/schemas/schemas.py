"""Pydantic schemas for API request/response validation."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.models import PeriodType, SourceType, DebtType, AmortisationType


# =============================================================================
# BASE SCHEMAS
# =============================================================================
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# PROJECT SCHEMAS
# =============================================================================
class ProjectBase(BaseModel):
    name: str
    location: Optional[str] = None
    cod_date: date
    installed_capacity_mw: Decimal
    ownership_share_pct: Optional[Decimal] = Decimal("100.00")
    currency: Optional[str] = "GBP"
    reporting_frequency: Optional[PeriodType] = PeriodType.ANNUAL
    initial_equity_invested: Optional[Decimal] = None
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    cod_date: Optional[date] = None
    installed_capacity_mw: Optional[Decimal] = None
    ownership_share_pct: Optional[Decimal] = None
    currency: Optional[str] = None
    reporting_frequency: Optional[PeriodType] = None
    initial_equity_invested: Optional[Decimal] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


# =============================================================================
# PERIOD SCHEMAS
# =============================================================================
class PeriodBase(BaseModel):
    period_start: date
    period_end: date
    period_type: Optional[PeriodType] = PeriodType.ANNUAL
    is_audited: Optional[bool] = False


class PeriodCreate(PeriodBase):
    project_id: int


class PeriodResponse(PeriodBase, BaseSchema):
    id: int
    project_id: int
    created_at: datetime


# =============================================================================
# INCOME STATEMENT SCHEMAS
# =============================================================================
class IncomeStatementBase(BaseModel):
    turnover: Optional[Decimal] = None
    cost_of_sales: Optional[Decimal] = None
    administrative_expenses: Optional[Decimal] = None
    other_operating_income: Optional[Decimal] = None
    interest_receivable: Optional[Decimal] = None
    interest_payable: Optional[Decimal] = None
    fair_value_movement_derivatives: Optional[Decimal] = None
    foreign_exchange_gain_loss: Optional[Decimal] = None
    current_tax: Optional[Decimal] = None
    deferred_tax: Optional[Decimal] = None
    depreciation: Optional[Decimal] = None


class IncomeStatementCreate(IncomeStatementBase):
    pass


class IncomeStatementResponse(IncomeStatementBase, BaseSchema):
    id: int
    financial_statement_id: int

    # Calculated fields
    gross_profit: Optional[Decimal] = None
    operating_profit: Optional[Decimal] = None
    profit_before_tax: Optional[Decimal] = None
    total_tax: Optional[Decimal] = None
    profit_after_tax: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None


# =============================================================================
# BALANCE SHEET SCHEMAS
# =============================================================================
class BalanceSheetBase(BaseModel):
    # Fixed Assets
    wind_farm_assets_cost: Optional[Decimal] = None
    wind_farm_assets_depreciation: Optional[Decimal] = None
    transmission_assets_cost: Optional[Decimal] = None
    transmission_assets_depreciation: Optional[Decimal] = None
    decommissioning_asset_cost: Optional[Decimal] = None
    decommissioning_asset_depreciation: Optional[Decimal] = None
    other_ppe_cost: Optional[Decimal] = None
    other_ppe_depreciation: Optional[Decimal] = None

    # Current Assets
    trade_receivables: Optional[Decimal] = None
    intercompany_receivables: Optional[Decimal] = None
    prepayments_accrued_income: Optional[Decimal] = None
    other_debtors: Optional[Decimal] = None
    derivative_assets: Optional[Decimal] = None
    cash_and_equivalents: Optional[Decimal] = None

    # Current Liabilities
    trade_payables: Optional[Decimal] = None
    intercompany_payables: Optional[Decimal] = None
    accruals_deferred_income: Optional[Decimal] = None
    current_tax_liability: Optional[Decimal] = None
    short_term_loans: Optional[Decimal] = None
    short_term_bonds: Optional[Decimal] = None
    short_term_lease_liability: Optional[Decimal] = None
    derivative_liabilities_current: Optional[Decimal] = None
    other_current_liabilities: Optional[Decimal] = None

    # Non-Current Liabilities
    long_term_loans: Optional[Decimal] = None
    long_term_bonds: Optional[Decimal] = None
    shareholder_loans: Optional[Decimal] = None
    long_term_lease_liability: Optional[Decimal] = None
    deferred_tax_liability: Optional[Decimal] = None
    decommissioning_provision: Optional[Decimal] = None
    other_provisions: Optional[Decimal] = None
    deferred_profit_on_disposal: Optional[Decimal] = None
    derivative_liabilities_noncurrent: Optional[Decimal] = None

    # Equity
    share_capital: Optional[Decimal] = None
    share_premium: Optional[Decimal] = None
    retained_earnings: Optional[Decimal] = None
    other_reserves: Optional[Decimal] = None


class BalanceSheetCreate(BalanceSheetBase):
    pass


class BalanceSheetResponse(BalanceSheetBase, BaseSchema):
    id: int
    financial_statement_id: int

    # Calculated totals
    total_fixed_assets: Optional[Decimal] = None
    total_current_assets: Optional[Decimal] = None
    total_current_liabilities: Optional[Decimal] = None
    net_current_assets: Optional[Decimal] = None
    total_non_current_liabilities: Optional[Decimal] = None
    total_equity: Optional[Decimal] = None
    net_assets: Optional[Decimal] = None
    net_debt: Optional[Decimal] = None


# =============================================================================
# CASH FLOW STATEMENT SCHEMAS
# =============================================================================
class CashFlowStatementBase(BaseModel):
    cash_from_operations: Optional[Decimal] = None
    tax_paid: Optional[Decimal] = None
    net_cash_from_operating: Optional[Decimal] = None
    capex: Optional[Decimal] = None
    proceeds_from_disposal: Optional[Decimal] = None
    interest_received: Optional[Decimal] = None
    net_cash_from_investing: Optional[Decimal] = None
    loan_drawdowns: Optional[Decimal] = None
    loan_repayments: Optional[Decimal] = None
    bond_repayments: Optional[Decimal] = None
    interest_paid: Optional[Decimal] = None
    dividends_paid: Optional[Decimal] = None
    equity_contributions: Optional[Decimal] = None
    net_cash_from_financing: Optional[Decimal] = None
    net_change_in_cash: Optional[Decimal] = None
    opening_cash: Optional[Decimal] = None
    closing_cash: Optional[Decimal] = None
    cfads_input: Optional[Decimal] = None


class CashFlowStatementCreate(CashFlowStatementBase):
    pass


class CashFlowStatementResponse(CashFlowStatementBase, BaseSchema):
    id: int
    financial_statement_id: int


# =============================================================================
# FINANCIAL STATEMENT SET SCHEMAS
# =============================================================================
class FinancialStatementSetBase(BaseModel):
    source_type: Optional[SourceType] = SourceType.AUDITED
    notes: Optional[str] = None


class FinancialStatementSetCreate(FinancialStatementSetBase):
    period_id: int
    income_statement: Optional[IncomeStatementCreate] = None
    balance_sheet: Optional[BalanceSheetCreate] = None
    cash_flow_statement: Optional[CashFlowStatementCreate] = None


class FinancialStatementSetResponse(FinancialStatementSetBase, BaseSchema):
    id: int
    period_id: int
    created_at: datetime
    updated_at: datetime
    income_statement: Optional[IncomeStatementResponse] = None
    balance_sheet: Optional[BalanceSheetResponse] = None
    cash_flow_statement: Optional[CashFlowStatementResponse] = None


# =============================================================================
# PRODUCTION DATA SCHEMAS
# =============================================================================
class ProductionDataBase(BaseModel):
    gross_generation_mwh: Optional[Decimal] = None
    net_export_mwh: Optional[Decimal] = None
    availability_pct: Optional[Decimal] = None
    curtailment_mwh: Optional[Decimal] = None
    curtailment_pct: Optional[Decimal] = None
    p50_generation_mwh: Optional[Decimal] = None
    budget_generation_mwh: Optional[Decimal] = None
    wind_index: Optional[Decimal] = None
    period_hours: Optional[Decimal] = None


class ProductionDataCreate(ProductionDataBase):
    period_id: int


class ProductionDataResponse(ProductionDataBase, BaseSchema):
    id: int
    period_id: int

    # Calculated
    capacity_factor_pct: Optional[Decimal] = None
    generation_vs_p50_pct: Optional[Decimal] = None
    generation_vs_budget_pct: Optional[Decimal] = None


# =============================================================================
# REVENUE BREAKDOWN SCHEMAS
# =============================================================================
class RevenueBreakdownBase(BaseModel):
    ppa_revenue: Optional[Decimal] = None
    cfd_revenue: Optional[Decimal] = None
    merchant_revenue: Optional[Decimal] = None
    roc_revenue: Optional[Decimal] = None
    rego_revenue: Optional[Decimal] = None
    capacity_market_revenue: Optional[Decimal] = None
    ancillary_services_revenue: Optional[Decimal] = None
    curtailment_compensation: Optional[Decimal] = None
    other_revenue: Optional[Decimal] = None


class RevenueBreakdownCreate(RevenueBreakdownBase):
    period_id: int


class RevenueBreakdownResponse(RevenueBreakdownBase, BaseSchema):
    id: int
    period_id: int
    total_revenue: Optional[Decimal] = None


# =============================================================================
# COST BREAKDOWN SCHEMAS
# =============================================================================
class CostBreakdownBase(BaseModel):
    om_fixed: Optional[Decimal] = None
    om_variable: Optional[Decimal] = None
    seabed_lease: Optional[Decimal] = None
    onshore_lease: Optional[Decimal] = None
    transmission_charges: Optional[Decimal] = None
    insurance: Optional[Decimal] = None
    management_fees: Optional[Decimal] = None
    admin_costs: Optional[Decimal] = None
    network_charges: Optional[Decimal] = None
    imbalance_costs: Optional[Decimal] = None
    community_fund: Optional[Decimal] = None
    other_opex: Optional[Decimal] = None


class CostBreakdownCreate(CostBreakdownBase):
    period_id: int


class CostBreakdownResponse(CostBreakdownBase, BaseSchema):
    id: int
    period_id: int
    total_costs: Optional[Decimal] = None


# =============================================================================
# DEBT FACILITY SCHEMAS
# =============================================================================
class DebtFacilityBase(BaseModel):
    name: str
    facility_type: DebtType
    currency: Optional[str] = "GBP"
    original_notional: Decimal
    commitment_amount: Optional[Decimal] = None
    is_fixed_rate: Optional[bool] = True
    fixed_rate_pct: Optional[Decimal] = None
    floating_reference: Optional[str] = None
    margin_pct: Optional[Decimal] = None
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    amortisation_type: Optional[AmortisationType] = AmortisationType.SCULPTED
    repayment_frequency: Optional[str] = "semi-annual"
    credit_rating: Optional[str] = None


class DebtFacilityCreate(DebtFacilityBase):
    project_id: int


class DebtFacilityResponse(DebtFacilityBase, BaseSchema):
    id: int
    project_id: int
    created_at: datetime
    current_outstanding: Optional[Decimal] = None


# =============================================================================
# DEBT MOVEMENT SCHEMAS
# =============================================================================
class DebtMovementBase(BaseModel):
    opening_balance: Optional[Decimal] = None
    drawdowns: Optional[Decimal] = Decimal("0")
    interest_charged: Optional[Decimal] = None
    principal_repaid: Optional[Decimal] = None
    fees_costs: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None


class DebtMovementCreate(DebtMovementBase):
    facility_id: int
    period_id: int


class DebtMovementResponse(DebtMovementBase, BaseSchema):
    id: int
    facility_id: int
    period_id: int


# =============================================================================
# INTEREST RATE SWAP SCHEMAS
# =============================================================================
class InterestRateSwapBase(BaseModel):
    notional_amount: Decimal
    fixed_rate_pct: Optional[Decimal] = None
    floating_reference: Optional[str] = None
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    fair_value: Optional[Decimal] = None
    counterparty: Optional[str] = None


class InterestRateSwapCreate(InterestRateSwapBase):
    facility_id: int


class InterestRateSwapResponse(InterestRateSwapBase, BaseSchema):
    id: int
    facility_id: int


# =============================================================================
# DIVIDEND DISTRIBUTION SCHEMAS
# =============================================================================
class DividendDistributionBase(BaseModel):
    cash_available_for_distribution: Optional[Decimal] = None
    dividends_declared: Optional[Decimal] = None
    dividends_paid: Optional[Decimal] = None
    retained_for_reserves: Optional[Decimal] = None
    shareholder_loan_repayments: Optional[Decimal] = None
    shareholder_loan_interest: Optional[Decimal] = None
    notes: Optional[str] = None


class DividendDistributionCreate(DividendDistributionBase):
    period_id: int


class DividendDistributionResponse(DividendDistributionBase, BaseSchema):
    id: int
    period_id: int


# =============================================================================
# COVENANT TEST SCHEMAS
# =============================================================================
class CovenantTestBase(BaseModel):
    covenant_name: str
    required_minimum: Optional[Decimal] = None
    required_maximum: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    passed: Optional[bool] = None
    headroom_absolute: Optional[Decimal] = None
    headroom_pct: Optional[Decimal] = None
    test_date: Optional[date] = None
    notes: Optional[str] = None


class CovenantTestCreate(CovenantTestBase):
    period_id: int
    facility_id: Optional[int] = None


class CovenantTestResponse(CovenantTestBase, BaseSchema):
    id: int
    period_id: int
    facility_id: Optional[int] = None


# =============================================================================
# KPI SCHEMAS (Calculated metrics)
# =============================================================================
class FinancialKPIs(BaseModel):
    """Calculated financial KPIs for a period."""
    period_id: int
    period_end: date

    # Profitability
    revenue: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    ebit: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None

    # Margins
    ebitda_margin_pct: Optional[Decimal] = None
    ebit_margin_pct: Optional[Decimal] = None
    net_margin_pct: Optional[Decimal] = None

    # Cash
    cash_from_operations: Optional[Decimal] = None
    cfads: Optional[Decimal] = None
    cfads_calculated: Optional[Decimal] = None

    # Leverage
    net_debt: Optional[Decimal] = None
    total_debt: Optional[Decimal] = None
    debt_to_equity: Optional[Decimal] = None
    gearing_pct: Optional[Decimal] = None

    # Debt Service
    debt_service: Optional[Decimal] = None
    dscr: Optional[Decimal] = None
    dscr_headroom_pct: Optional[Decimal] = None

    # Operational
    capacity_factor_pct: Optional[Decimal] = None
    availability_pct: Optional[Decimal] = None
    revenue_per_mwh: Optional[Decimal] = None
    cost_per_mwh: Optional[Decimal] = None

    # Dividends
    dividends_paid: Optional[Decimal] = None
    dividend_yield_pct: Optional[Decimal] = None


class ProjectKPISummary(BaseModel):
    """Summary KPIs for a project across all periods."""
    project_id: int
    project_name: str
    installed_capacity_mw: Decimal

    # Latest period KPIs
    latest_revenue: Optional[Decimal] = None
    latest_ebitda_margin_pct: Optional[Decimal] = None
    latest_net_debt: Optional[Decimal] = None
    latest_dscr: Optional[Decimal] = None
    latest_capacity_factor_pct: Optional[Decimal] = None
    latest_availability_pct: Optional[Decimal] = None

    # Cumulative
    cumulative_dividends: Optional[Decimal] = None
    cumulative_generation_mwh: Optional[Decimal] = None

    # YoY changes
    revenue_yoy_pct: Optional[Decimal] = None
    ebitda_yoy_pct: Optional[Decimal] = None

    # Historical KPIs per period
    period_kpis: Optional[List[FinancialKPIs]] = None


# =============================================================================
# DATA PARSING SCHEMAS
# =============================================================================
class ParsedField(BaseModel):
    """A field extracted from pasted text."""
    original_text: str
    extracted_value: Optional[str] = None
    mapped_field: Optional[str] = None
    confidence: Optional[float] = None
    needs_review: bool = False


class ParsedDataResponse(BaseModel):
    """Response from parsing pasted text."""
    income_statement_fields: List[ParsedField] = []
    balance_sheet_fields: List[ParsedField] = []
    production_fields: List[ParsedField] = []
    debt_fields: List[ParsedField] = []
    unmatched_fields: List[ParsedField] = []
