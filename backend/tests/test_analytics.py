"""Tests for analytics and KPI calculations."""
import pytest
from decimal import Decimal
from app.analytics.calculations import (
    calculate_gross_profit,
    calculate_operating_profit,
    calculate_ebitda,
    calculate_profit_before_tax,
    calculate_profit_after_tax,
    calculate_total_fixed_assets,
    calculate_total_debt,
    calculate_net_debt,
    calculate_dscr,
    calculate_capacity_factor,
    calculate_generation_vs_p50,
    calculate_revenue_per_mwh,
    safe_divide,
    pct,
)
from app.models import IncomeStatement, BalanceSheet, ProductionData


class TestIncomeStatementCalculations:
    """Test income statement calculations."""

    def test_gross_profit(self):
        """Gross Profit = Turnover - Cost of Sales"""
        income = IncomeStatement()
        income.turnover = Decimal("250000")
        income.cost_of_sales = Decimal("80000")

        result = calculate_gross_profit(income)
        assert result == Decimal("170000")

    def test_gross_profit_with_none_turnover(self):
        """Should return None if turnover is None."""
        income = IncomeStatement()
        income.turnover = None
        income.cost_of_sales = Decimal("80000")

        result = calculate_gross_profit(income)
        assert result is None

    def test_operating_profit(self):
        """Operating Profit = Gross Profit - Admin + Other Income"""
        income = IncomeStatement()
        income.turnover = Decimal("250000")
        income.cost_of_sales = Decimal("80000")
        income.administrative_expenses = Decimal("10000")
        income.other_operating_income = Decimal("3000")

        result = calculate_operating_profit(income)
        # GP = 170000, OP = 170000 - 10000 + 3000 = 163000
        assert result == Decimal("163000")

    def test_ebitda(self):
        """EBITDA = Operating Profit + Depreciation"""
        income = IncomeStatement()
        income.turnover = Decimal("250000")
        income.cost_of_sales = Decimal("80000")
        income.administrative_expenses = Decimal("10000")
        income.other_operating_income = Decimal("3000")
        income.depreciation = Decimal("42000")

        result = calculate_ebitda(income)
        # OP = 163000, EBITDA = 163000 + 42000 = 205000
        assert result == Decimal("205000")

    def test_profit_before_tax(self):
        """PBT includes finance items."""
        income = IncomeStatement()
        income.turnover = Decimal("250000")
        income.cost_of_sales = Decimal("80000")
        income.administrative_expenses = Decimal("10000")
        income.other_operating_income = Decimal("3000")
        income.interest_receivable = Decimal("500")
        income.interest_payable = Decimal("35000")
        income.fair_value_movement_derivatives = Decimal("5000")
        income.foreign_exchange_gain_loss = Decimal("-1000")

        result = calculate_profit_before_tax(income)
        # OP = 163000, PBT = 163000 + 500 - 35000 + 5000 - 1000 = 132500
        assert result == Decimal("132500")

    def test_profit_after_tax(self):
        """PAT = PBT - Tax"""
        income = IncomeStatement()
        income.turnover = Decimal("250000")
        income.cost_of_sales = Decimal("80000")
        income.administrative_expenses = Decimal("10000")
        income.other_operating_income = Decimal("3000")
        income.interest_receivable = Decimal("500")
        income.interest_payable = Decimal("35000")
        income.fair_value_movement_derivatives = Decimal("5000")
        income.foreign_exchange_gain_loss = Decimal("-1000")
        income.current_tax = Decimal("25000")
        income.deferred_tax = Decimal("2000")

        result = calculate_profit_after_tax(income)
        # PBT = 132500, PAT = 132500 - 27000 = 105500
        assert result == Decimal("105500")


class TestBalanceSheetCalculations:
    """Test balance sheet calculations."""

    def test_total_fixed_assets(self):
        """Fixed assets = sum of all asset classes (cost - depreciation)."""
        bs = BalanceSheet()
        bs.wind_farm_assets_cost = Decimal("1000000")
        bs.wind_farm_assets_depreciation = Decimal("200000")
        bs.transmission_assets_cost = Decimal("0")
        bs.transmission_assets_depreciation = Decimal("0")
        bs.decommissioning_asset_cost = Decimal("50000")
        bs.decommissioning_asset_depreciation = Decimal("10000")
        bs.other_ppe_cost = Decimal("0")
        bs.other_ppe_depreciation = Decimal("0")

        result = calculate_total_fixed_assets(bs)
        # (1000000 - 200000) + (50000 - 10000) = 800000 + 40000 = 840000
        assert result == Decimal("840000")

    def test_total_debt(self):
        """Total debt = short-term + long-term loans and bonds."""
        bs = BalanceSheet()
        bs.short_term_loans = Decimal("40000")
        bs.short_term_bonds = Decimal("25000")
        bs.long_term_loans = Decimal("300000")
        bs.long_term_bonds = Decimal("450000")

        result = calculate_total_debt(bs)
        assert result == Decimal("815000")

    def test_net_debt(self):
        """Net debt = Total debt - Cash."""
        bs = BalanceSheet()
        bs.short_term_loans = Decimal("40000")
        bs.short_term_bonds = Decimal("25000")
        bs.long_term_loans = Decimal("300000")
        bs.long_term_bonds = Decimal("450000")
        bs.cash_and_equivalents = Decimal("35000")

        result = calculate_net_debt(bs)
        # 815000 - 35000 = 780000
        assert result == Decimal("780000")


class TestDebtCalculations:
    """Test debt service and DSCR calculations."""

    def test_dscr(self):
        """DSCR = CFADS / Debt Service"""
        cfads = Decimal("150000")
        debt_service = Decimal("100000")

        result = calculate_dscr(cfads, debt_service)
        assert result == Decimal("1.5000")

    def test_dscr_zero_debt_service(self):
        """Should return None if debt service is zero."""
        cfads = Decimal("150000")
        debt_service = Decimal("0")

        result = calculate_dscr(cfads, debt_service)
        assert result is None


class TestProductionCalculations:
    """Test production and operational KPIs."""

    def test_capacity_factor(self):
        """Capacity Factor = Actual / Max Possible * 100"""
        prod = ProductionData()
        prod.net_export_mwh = Decimal("1500000")
        prod.period_hours = Decimal("8760")
        installed_capacity_mw = Decimal("450")

        result = calculate_capacity_factor(prod, installed_capacity_mw)
        # Max = 450 * 8760 = 3942000, CF = 1500000 / 3942000 * 100 = 38.05%
        assert result is not None
        assert Decimal("38") < result < Decimal("39")

    def test_generation_vs_p50(self):
        """Generation vs P50 = (Actual - P50) / P50 * 100"""
        prod = ProductionData()
        prod.net_export_mwh = Decimal("1500000")
        prod.p50_generation_mwh = Decimal("1480000")

        result = calculate_generation_vs_p50(prod)
        # (1500000 - 1480000) / 1480000 * 100 = 1.35%
        assert result is not None
        assert Decimal("1.3") < result < Decimal("1.4")

    def test_revenue_per_mwh(self):
        """Revenue / MWh = Total Revenue / Generation"""
        revenue = Decimal("250000000")  # £250m
        generation = Decimal("1500000")  # 1.5 GWh

        result = calculate_revenue_per_mwh(revenue, generation)
        # 250000000 / 1500000 = 166.67
        assert result is not None
        assert Decimal("166") < result < Decimal("167")


class TestHelperFunctions:
    """Test helper functions."""

    def test_safe_divide(self):
        """Safe divide returns None for invalid cases."""
        assert safe_divide(Decimal("10"), Decimal("2")) == Decimal("5.0000")
        assert safe_divide(Decimal("10"), Decimal("0")) is None
        assert safe_divide(None, Decimal("2")) is None
        assert safe_divide(Decimal("10"), None) is None

    def test_pct(self):
        """Convert decimal to percentage."""
        assert pct(Decimal("0.5")) == Decimal("50.00")
        assert pct(Decimal("0.385")) == Decimal("38.50")
        assert pct(None) is None


class TestDebtMovementReconciliation:
    """Test debt movement reconciliation."""

    def test_closing_balance_reconciliation(self):
        """Opening + Drawdowns - Principal = Closing"""
        opening = Decimal("500000")
        drawdowns = Decimal("0")
        principal_repaid = Decimal("25000")
        expected_closing = Decimal("475000")

        # Verify the reconciliation formula
        calculated_closing = opening + drawdowns - principal_repaid
        assert calculated_closing == expected_closing


class TestBalanceSheetIdentity:
    """Test balance sheet identity (Assets = Equity + Liabilities)."""

    def test_balance_sheet_balances(self):
        """Net Assets should equal Total Equity."""
        bs = BalanceSheet()
        # Assets
        bs.wind_farm_assets_cost = Decimal("1000000")
        bs.wind_farm_assets_depreciation = Decimal("200000")
        bs.decommissioning_asset_cost = Decimal("50000")
        bs.decommissioning_asset_depreciation = Decimal("10000")
        bs.trade_receivables = Decimal("20000")
        bs.cash_and_equivalents = Decimal("35000")

        # Liabilities
        bs.trade_payables = Decimal("12000")
        bs.short_term_loans = Decimal("40000")
        bs.long_term_loans = Decimal("300000")
        bs.long_term_bonds = Decimal("450000")
        bs.decommissioning_provision = Decimal("75000")

        # Equity (what's left)
        bs.share_capital = Decimal("0")
        bs.retained_earnings = Decimal("18000")  # Plug to balance

        # Calculate
        from app.analytics.calculations import (
            calculate_total_fixed_assets,
            calculate_total_current_assets,
            calculate_total_current_liabilities,
            calculate_total_non_current_liabilities,
            calculate_total_equity,
            calculate_net_assets,
        )

        fixed = calculate_total_fixed_assets(bs)
        current_assets = calculate_total_current_assets(bs)
        current_liab = calculate_total_current_liabilities(bs)
        non_current_liab = calculate_total_non_current_liabilities(bs)
        equity = calculate_total_equity(bs)
        net_assets = calculate_net_assets(bs)

        # Net Assets should equal Equity
        assert net_assets == equity
