"""SQLAlchemy database models for Offshore Wind Operational Performance Hub."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Numeric, Boolean,
    ForeignKey, Text, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PeriodType(str, enum.Enum):
    """Period type enumeration."""
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"


class SourceType(str, enum.Enum):
    """Financial statement source type."""
    AUDITED = "audited"
    MANAGEMENT = "management"
    FORECAST = "forecast"
    BUDGET = "budget"


class DebtType(str, enum.Enum):
    """Debt facility type."""
    BANK_LOAN = "bank_loan"
    BOND = "bond"
    SHAREHOLDER_LOAN = "shareholder_loan"
    REVOLVING_CREDIT = "revolving_credit"
    TERM_LOAN = "term_loan"


class AmortisationType(str, enum.Enum):
    """Debt amortisation profile type."""
    ANNUITY = "annuity"
    SCULPTED = "sculpted"
    BULLET = "bullet"
    LINEAR = "linear"


# =============================================================================
# PROJECT
# =============================================================================
class Project(Base):
    """Offshore wind project entity."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255))
    cod_date = Column(Date, nullable=False)  # Commercial Operation Date
    installed_capacity_mw = Column(Numeric(10, 2), nullable=False)
    ownership_share_pct = Column(Numeric(5, 2), default=100.00)
    currency = Column(String(3), default="GBP")
    reporting_frequency = Column(SQLEnum(PeriodType), default=PeriodType.ANNUAL)
    initial_equity_invested = Column(Numeric(15, 2))  # For IRR calculations
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    periods = relationship("Period", back_populates="project", cascade="all, delete-orphan")
    debt_facilities = relationship("DebtFacility", back_populates="project", cascade="all, delete-orphan")


# =============================================================================
# PERIOD
# =============================================================================
class Period(Base):
    """Reporting period for a project."""
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    period_type = Column(SQLEnum(PeriodType), default=PeriodType.ANNUAL)
    is_audited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="periods")
    financial_statement = relationship("FinancialStatementSet", back_populates="period", uselist=False, cascade="all, delete-orphan")
    production_data = relationship("ProductionData", back_populates="period", uselist=False, cascade="all, delete-orphan")
    revenue_breakdown = relationship("RevenueBreakdown", back_populates="period", uselist=False, cascade="all, delete-orphan")
    cost_breakdown = relationship("CostBreakdown", back_populates="period", uselist=False, cascade="all, delete-orphan")
    dividend_distribution = relationship("DividendDistribution", back_populates="period", uselist=False, cascade="all, delete-orphan")
    debt_movements = relationship("DebtMovement", back_populates="period", cascade="all, delete-orphan")
    covenant_tests = relationship("CovenantTest", back_populates="period", cascade="all, delete-orphan")


# =============================================================================
# FINANCIAL STATEMENT SET
# =============================================================================
class FinancialStatementSet(Base):
    """Container for financial statements for a period."""
    __tablename__ = "financial_statement_sets"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False, unique=True)
    source_type = Column(SQLEnum(SourceType), default=SourceType.AUDITED)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    period = relationship("Period", back_populates="financial_statement")
    income_statement = relationship("IncomeStatement", back_populates="financial_statement", uselist=False, cascade="all, delete-orphan")
    balance_sheet = relationship("BalanceSheet", back_populates="financial_statement", uselist=False, cascade="all, delete-orphan")
    cash_flow_statement = relationship("CashFlowStatement", back_populates="financial_statement", uselist=False, cascade="all, delete-orphan")


# =============================================================================
# INCOME STATEMENT
# =============================================================================
class IncomeStatement(Base):
    """Profit and Loss Account."""
    __tablename__ = "income_statements"

    id = Column(Integer, primary_key=True, index=True)
    financial_statement_id = Column(Integer, ForeignKey("financial_statement_sets.id"), nullable=False, unique=True)

    # Revenue
    turnover = Column(Numeric(15, 2))  # Total revenue

    # Cost of Sales / Operating Costs
    cost_of_sales = Column(Numeric(15, 2))

    # Gross Profit = Turnover - Cost of Sales (calculated)

    # Administrative expenses
    administrative_expenses = Column(Numeric(15, 2))
    other_operating_income = Column(Numeric(15, 2))

    # Operating Profit (EBIT)
    # Calculated: Gross Profit - Admin Expenses + Other Operating Income

    # Finance items
    interest_receivable = Column(Numeric(15, 2))
    interest_payable = Column(Numeric(15, 2))
    fair_value_movement_derivatives = Column(Numeric(15, 2))
    foreign_exchange_gain_loss = Column(Numeric(15, 2))

    # Profit Before Tax (calculated)

    # Taxation
    current_tax = Column(Numeric(15, 2))
    deferred_tax = Column(Numeric(15, 2))
    # Total Tax = Current Tax + Deferred Tax

    # Profit After Tax (calculated)

    # Depreciation (for EBITDA calculation)
    depreciation = Column(Numeric(15, 2))

    # Relationship
    financial_statement = relationship("FinancialStatementSet", back_populates="income_statement")


# =============================================================================
# BALANCE SHEET
# =============================================================================
class BalanceSheet(Base):
    """Balance Sheet / Statement of Financial Position."""
    __tablename__ = "balance_sheets"

    id = Column(Integer, primary_key=True, index=True)
    financial_statement_id = Column(Integer, ForeignKey("financial_statement_sets.id"), nullable=False, unique=True)

    # FIXED ASSETS - Tangible Assets by class
    wind_farm_assets_cost = Column(Numeric(15, 2))
    wind_farm_assets_depreciation = Column(Numeric(15, 2))
    transmission_assets_cost = Column(Numeric(15, 2))
    transmission_assets_depreciation = Column(Numeric(15, 2))
    decommissioning_asset_cost = Column(Numeric(15, 2))
    decommissioning_asset_depreciation = Column(Numeric(15, 2))
    other_ppe_cost = Column(Numeric(15, 2))
    other_ppe_depreciation = Column(Numeric(15, 2))

    # CURRENT ASSETS
    trade_receivables = Column(Numeric(15, 2))
    intercompany_receivables = Column(Numeric(15, 2))
    prepayments_accrued_income = Column(Numeric(15, 2))
    other_debtors = Column(Numeric(15, 2))
    derivative_assets = Column(Numeric(15, 2))
    cash_and_equivalents = Column(Numeric(15, 2))

    # CURRENT LIABILITIES
    trade_payables = Column(Numeric(15, 2))
    intercompany_payables = Column(Numeric(15, 2))
    accruals_deferred_income = Column(Numeric(15, 2))
    current_tax_liability = Column(Numeric(15, 2))
    short_term_loans = Column(Numeric(15, 2))
    short_term_bonds = Column(Numeric(15, 2))
    short_term_lease_liability = Column(Numeric(15, 2))
    derivative_liabilities_current = Column(Numeric(15, 2))
    other_current_liabilities = Column(Numeric(15, 2))

    # NON-CURRENT LIABILITIES
    long_term_loans = Column(Numeric(15, 2))
    long_term_bonds = Column(Numeric(15, 2))
    shareholder_loans = Column(Numeric(15, 2))
    long_term_lease_liability = Column(Numeric(15, 2))
    deferred_tax_liability = Column(Numeric(15, 2))
    decommissioning_provision = Column(Numeric(15, 2))
    other_provisions = Column(Numeric(15, 2))
    deferred_profit_on_disposal = Column(Numeric(15, 2))
    derivative_liabilities_noncurrent = Column(Numeric(15, 2))

    # EQUITY
    share_capital = Column(Numeric(15, 2))
    share_premium = Column(Numeric(15, 2))
    retained_earnings = Column(Numeric(15, 2))
    other_reserves = Column(Numeric(15, 2))

    # Relationship
    financial_statement = relationship("FinancialStatementSet", back_populates="balance_sheet")


# =============================================================================
# CASH FLOW STATEMENT
# =============================================================================
class CashFlowStatement(Base):
    """Statement of Cash Flows (simplified indirect method)."""
    __tablename__ = "cash_flow_statements"

    id = Column(Integer, primary_key=True, index=True)
    financial_statement_id = Column(Integer, ForeignKey("financial_statement_sets.id"), nullable=False, unique=True)

    # Operating Activities
    cash_from_operations = Column(Numeric(15, 2))
    tax_paid = Column(Numeric(15, 2))
    net_cash_from_operating = Column(Numeric(15, 2))

    # Investing Activities
    capex = Column(Numeric(15, 2))
    proceeds_from_disposal = Column(Numeric(15, 2))
    interest_received = Column(Numeric(15, 2))
    net_cash_from_investing = Column(Numeric(15, 2))

    # Financing Activities
    loan_drawdowns = Column(Numeric(15, 2))
    loan_repayments = Column(Numeric(15, 2))
    bond_repayments = Column(Numeric(15, 2))
    interest_paid = Column(Numeric(15, 2))
    dividends_paid = Column(Numeric(15, 2))
    equity_contributions = Column(Numeric(15, 2))
    net_cash_from_financing = Column(Numeric(15, 2))

    # Cash Movement
    net_change_in_cash = Column(Numeric(15, 2))
    opening_cash = Column(Numeric(15, 2))
    closing_cash = Column(Numeric(15, 2))

    # CFADS (can be input or calculated)
    cfads_input = Column(Numeric(15, 2))  # Manual override from loan compliance

    # Relationship
    financial_statement = relationship("FinancialStatementSet", back_populates="cash_flow_statement")


# =============================================================================
# DEBT FACILITY
# =============================================================================
class DebtFacility(Base):
    """Debt facility/instrument definition."""
    __tablename__ = "debt_facilities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    name = Column(String(255), nullable=False)
    facility_type = Column(SQLEnum(DebtType), nullable=False)
    currency = Column(String(3), default="GBP")

    # Amounts
    original_notional = Column(Numeric(15, 2), nullable=False)
    commitment_amount = Column(Numeric(15, 2))  # For revolving facilities

    # Interest terms
    is_fixed_rate = Column(Boolean, default=True)
    fixed_rate_pct = Column(Numeric(6, 4))  # e.g., 2.7400 for 2.74%
    floating_reference = Column(String(50))  # e.g., "SONIA", "SOFR"
    margin_pct = Column(Numeric(6, 4))

    # Dates
    start_date = Column(Date)
    maturity_date = Column(Date)

    # Amortisation
    amortisation_type = Column(SQLEnum(AmortisationType), default=AmortisationType.SCULPTED)
    repayment_frequency = Column(String(50), default="semi-annual")  # semi-annual, quarterly, etc.

    # Credit rating
    credit_rating = Column(String(20))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="debt_facilities")
    movements = relationship("DebtMovement", back_populates="facility", cascade="all, delete-orphan")
    covenant_tests = relationship("CovenantTest", back_populates="facility")
    interest_rate_swaps = relationship("InterestRateSwap", back_populates="facility", cascade="all, delete-orphan")


# =============================================================================
# DEBT MOVEMENT
# =============================================================================
class DebtMovement(Base):
    """Debt movement for a facility in a period."""
    __tablename__ = "debt_movements"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("debt_facilities.id"), nullable=False)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False)

    opening_balance = Column(Numeric(15, 2))
    drawdowns = Column(Numeric(15, 2), default=0)
    interest_charged = Column(Numeric(15, 2))
    principal_repaid = Column(Numeric(15, 2))
    fees_costs = Column(Numeric(15, 2))
    closing_balance = Column(Numeric(15, 2))

    # Relationships
    facility = relationship("DebtFacility", back_populates="movements")
    period = relationship("Period", back_populates="debt_movements")


# =============================================================================
# INTEREST RATE SWAP
# =============================================================================
class InterestRateSwap(Base):
    """Interest rate swap details."""
    __tablename__ = "interest_rate_swaps"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("debt_facilities.id"), nullable=False)

    notional_amount = Column(Numeric(15, 2), nullable=False)
    fixed_rate_pct = Column(Numeric(6, 4))
    floating_reference = Column(String(50))  # e.g., "SONIA"
    start_date = Column(Date)
    maturity_date = Column(Date)
    fair_value = Column(Numeric(15, 2))  # Current fair value
    counterparty = Column(String(255))

    # Relationship
    facility = relationship("DebtFacility", back_populates="interest_rate_swaps")


# =============================================================================
# PRODUCTION DATA
# =============================================================================
class ProductionData(Base):
    """Production and operational data for a period."""
    __tablename__ = "production_data"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False, unique=True)

    gross_generation_mwh = Column(Numeric(15, 2))
    net_export_mwh = Column(Numeric(15, 2))
    availability_pct = Column(Numeric(6, 2))  # Production-based availability
    curtailment_mwh = Column(Numeric(15, 2))
    curtailment_pct = Column(Numeric(6, 2))

    # Reference for comparison
    p50_generation_mwh = Column(Numeric(15, 2))  # Expected generation at P50
    budget_generation_mwh = Column(Numeric(15, 2))

    # Wind index (if available)
    wind_index = Column(Numeric(6, 2))  # e.g., 98.5 meaning 98.5% of long-term average

    # Hours
    period_hours = Column(Numeric(10, 2))  # Total hours in period

    # Relationship
    period = relationship("Period", back_populates="production_data")


# =============================================================================
# REVENUE BREAKDOWN
# =============================================================================
class RevenueBreakdown(Base):
    """Detailed revenue breakdown by source."""
    __tablename__ = "revenue_breakdowns"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False, unique=True)

    # PPA / Power sales
    ppa_revenue = Column(Numeric(15, 2))

    # Contract for Difference
    cfd_revenue = Column(Numeric(15, 2))

    # Merchant / Market revenue
    merchant_revenue = Column(Numeric(15, 2))

    # ROCs / REGOs
    roc_revenue = Column(Numeric(15, 2))
    rego_revenue = Column(Numeric(15, 2))

    # Other
    capacity_market_revenue = Column(Numeric(15, 2))
    ancillary_services_revenue = Column(Numeric(15, 2))
    curtailment_compensation = Column(Numeric(15, 2))
    other_revenue = Column(Numeric(15, 2))

    # Relationship
    period = relationship("Period", back_populates="revenue_breakdown")


# =============================================================================
# COST BREAKDOWN
# =============================================================================
class CostBreakdown(Base):
    """Detailed cost breakdown."""
    __tablename__ = "cost_breakdowns"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False, unique=True)

    # O&M
    om_fixed = Column(Numeric(15, 2))
    om_variable = Column(Numeric(15, 2))

    # Leases and rent
    seabed_lease = Column(Numeric(15, 2))
    onshore_lease = Column(Numeric(15, 2))
    transmission_charges = Column(Numeric(15, 2))  # TNUoS, BSUoS

    # Insurance
    insurance = Column(Numeric(15, 2))

    # Management and admin
    management_fees = Column(Numeric(15, 2))
    admin_costs = Column(Numeric(15, 2))

    # Other operating
    network_charges = Column(Numeric(15, 2))
    imbalance_costs = Column(Numeric(15, 2))
    community_fund = Column(Numeric(15, 2))
    other_opex = Column(Numeric(15, 2))

    # Relationship
    period = relationship("Period", back_populates="cost_breakdown")


# =============================================================================
# DIVIDEND DISTRIBUTION
# =============================================================================
class DividendDistribution(Base):
    """Dividend and distribution data for a period."""
    __tablename__ = "dividend_distributions"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False, unique=True)

    cash_available_for_distribution = Column(Numeric(15, 2))
    dividends_declared = Column(Numeric(15, 2))
    dividends_paid = Column(Numeric(15, 2))
    retained_for_reserves = Column(Numeric(15, 2))

    # Shareholder loan movements
    shareholder_loan_repayments = Column(Numeric(15, 2))
    shareholder_loan_interest = Column(Numeric(15, 2))

    # Notes
    notes = Column(Text)

    # Relationship
    period = relationship("Period", back_populates="dividend_distribution")


# =============================================================================
# COVENANT TEST
# =============================================================================
class CovenantTest(Base):
    """Covenant test results for a period."""
    __tablename__ = "covenant_tests"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("debt_facilities.id"))

    covenant_name = Column(String(100), nullable=False)  # e.g., "DSCR", "LLCR", "Gearing"

    # Values
    required_minimum = Column(Numeric(10, 4))
    required_maximum = Column(Numeric(10, 4))
    actual_value = Column(Numeric(10, 4))

    # Results
    passed = Column(Boolean)
    headroom_absolute = Column(Numeric(15, 2))
    headroom_pct = Column(Numeric(6, 2))

    # Date tested
    test_date = Column(Date)

    notes = Column(Text)

    # Relationships
    period = relationship("Period", back_populates="covenant_tests")
    facility = relationship("DebtFacility", back_populates="covenant_tests")
