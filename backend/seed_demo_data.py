"""
Seed demo data for Offshore Wind Operational Performance Hub.

Creates two fictitious offshore wind projects with 5 years of operational data.
All data is illustrative and does not represent any real project.
"""
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    Project, Period, FinancialStatementSet, IncomeStatement, BalanceSheet,
    CashFlowStatement, ProductionData, RevenueBreakdown, CostBreakdown,
    DebtFacility, DebtMovement, InterestRateSwap, DividendDistribution,
    CovenantTest, PeriodType, SourceType, DebtType, AmortisationType
)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def seed_project_alpha(db: Session):
    """
    Create Project Alpha - Greater Gale Offshore Wind
    A 450 MW offshore wind farm in the North Sea.
    """
    project = Project(
        name="Greater Gale Offshore Wind",
        location="North Sea, UK",
        cod_date=date(2019, 6, 15),
        installed_capacity_mw=Decimal("450"),
        ownership_share_pct=Decimal("100"),
        currency="GBP",
        reporting_frequency=PeriodType.ANNUAL,
        initial_equity_invested=Decimal("350000"),  # £350m
        description="450 MW offshore wind farm located 35km off the Yorkshire coast"
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Create debt facilities
    pp_notes = DebtFacility(
        project_id=project.id,
        name="Senior Secured PP Notes",
        facility_type=DebtType.BOND,
        currency="GBP",
        original_notional=Decimal("520000"),
        is_fixed_rate=True,
        fixed_rate_pct=Decimal("3.15"),
        start_date=date(2019, 6, 1),
        maturity_date=date(2034, 6, 15),
        amortisation_type=AmortisationType.SCULPTED,
        repayment_frequency="semi-annual",
        credit_rating="BBB"
    )
    db.add(pp_notes)

    tlf = DebtFacility(
        project_id=project.id,
        name="Term Loan Facility",
        facility_type=DebtType.TERM_LOAN,
        currency="GBP",
        original_notional=Decimal("380000"),
        is_fixed_rate=False,
        floating_reference="SONIA",
        margin_pct=Decimal("1.25"),
        start_date=date(2019, 6, 1),
        maturity_date=date(2029, 6, 15),
        amortisation_type=AmortisationType.SCULPTED,
        repayment_frequency="semi-annual"
    )
    db.add(tlf)
    db.commit()

    # Interest rate swap
    swap = InterestRateSwap(
        facility_id=tlf.id,
        notional_amount=Decimal("380000"),
        fixed_rate_pct=Decimal("1.85"),
        floating_reference="SONIA",
        start_date=date(2019, 6, 1),
        maturity_date=date(2029, 6, 15),
        fair_value=Decimal("12500"),
        counterparty="Major Bank PLC"
    )
    db.add(swap)
    db.commit()

    # Annual data for 2019-2023
    annual_data = [
        {
            "year": 2019,
            "turnover": Decimal("185000"),
            "cost_of_sales": Decimal("58000"),
            "admin": Decimal("7500"),
            "depreciation": Decimal("42000"),
            "interest_payable": Decimal("38500"),
            "interest_receivable": Decimal("450"),
            "fv_movement": Decimal("5200"),
            "current_tax": Decimal("15800"),
            "deferred_tax": Decimal("2100"),
            "generation_mwh": Decimal("1420000"),
            "availability": Decimal("94.5"),
            "p50_mwh": Decimal("1480000"),
            "ppa_revenue": Decimal("72000"),
            "cfd_revenue": Decimal("108000"),
            "merchant_revenue": Decimal("5000"),
            "om_fixed": Decimal("28000"),
            "om_variable": Decimal("12000"),
            "insurance": Decimal("8500"),
            "seabed_lease": Decimal("4200"),
            "transmission": Decimal("5300"),
            "pp_balance": Decimal("505000"),
            "tlf_balance": Decimal("365000"),
            "dividends": Decimal("42000"),
        },
        {
            "year": 2020,
            "turnover": Decimal("198000"),
            "cost_of_sales": Decimal("61000"),
            "admin": Decimal("7800"),
            "depreciation": Decimal("42000"),
            "interest_payable": Decimal("36200"),
            "interest_receivable": Decimal("380"),
            "fv_movement": Decimal("-3500"),
            "current_tax": Decimal("17200"),
            "deferred_tax": Decimal("1800"),
            "generation_mwh": Decimal("1510000"),
            "availability": Decimal("95.2"),
            "p50_mwh": Decimal("1480000"),
            "ppa_revenue": Decimal("78000"),
            "cfd_revenue": Decimal("115000"),
            "merchant_revenue": Decimal("5000"),
            "om_fixed": Decimal("29000"),
            "om_variable": Decimal("13000"),
            "insurance": Decimal("8800"),
            "seabed_lease": Decimal("4350"),
            "transmission": Decimal("5850"),
            "pp_balance": Decimal("485000"),
            "tlf_balance": Decimal("342000"),
            "dividends": Decimal("48000"),
        },
        {
            "year": 2021,
            "turnover": Decimal("192000"),
            "cost_of_sales": Decimal("63000"),
            "admin": Decimal("8100"),
            "depreciation": Decimal("42000"),
            "interest_payable": Decimal("33800"),
            "interest_receivable": Decimal("290"),
            "fv_movement": Decimal("8200"),
            "current_tax": Decimal("16500"),
            "deferred_tax": Decimal("1500"),
            "generation_mwh": Decimal("1385000"),
            "availability": Decimal("94.8"),
            "p50_mwh": Decimal("1480000"),
            "ppa_revenue": Decimal("75000"),
            "cfd_revenue": Decimal("112000"),
            "merchant_revenue": Decimal("5000"),
            "om_fixed": Decimal("30500"),
            "om_variable": Decimal("13500"),
            "insurance": Decimal("9100"),
            "seabed_lease": Decimal("4500"),
            "transmission": Decimal("5400"),
            "pp_balance": Decimal("462000"),
            "tlf_balance": Decimal("318000"),
            "dividends": Decimal("45000"),
        },
        {
            "year": 2022,
            "turnover": Decimal("215000"),
            "cost_of_sales": Decimal("68000"),
            "admin": Decimal("8500"),
            "depreciation": Decimal("42000"),
            "interest_payable": Decimal("31200"),
            "interest_receivable": Decimal("520"),
            "fv_movement": Decimal("15800"),
            "current_tax": Decimal("19800"),
            "deferred_tax": Decimal("2200"),
            "generation_mwh": Decimal("1465000"),
            "availability": Decimal("95.5"),
            "p50_mwh": Decimal("1480000"),
            "ppa_revenue": Decimal("95000"),
            "cfd_revenue": Decimal("115000"),
            "merchant_revenue": Decimal("5000"),
            "om_fixed": Decimal("32000"),
            "om_variable": Decimal("15000"),
            "insurance": Decimal("9500"),
            "seabed_lease": Decimal("4650"),
            "transmission": Decimal("6850"),
            "pp_balance": Decimal("438000"),
            "tlf_balance": Decimal("285000"),
            "dividends": Decimal("55000"),
        },
        {
            "year": 2023,
            "turnover": Decimal("248000"),
            "cost_of_sales": Decimal("72000"),
            "admin": Decimal("8900"),
            "depreciation": Decimal("42000"),
            "interest_payable": Decimal("28500"),
            "interest_receivable": Decimal("680"),
            "fv_movement": Decimal("-5200"),
            "current_tax": Decimal("25200"),
            "deferred_tax": Decimal("1800"),
            "generation_mwh": Decimal("1545000"),
            "availability": Decimal("96.1"),
            "p50_mwh": Decimal("1480000"),
            "ppa_revenue": Decimal("115000"),
            "cfd_revenue": Decimal("128000"),
            "merchant_revenue": Decimal("5000"),
            "om_fixed": Decimal("34000"),
            "om_variable": Decimal("16500"),
            "insurance": Decimal("9800"),
            "seabed_lease": Decimal("4800"),
            "transmission": Decimal("6900"),
            "pp_balance": Decimal("412000"),
            "tlf_balance": Decimal("248000"),
            "dividends": Decimal("68000"),
        },
    ]

    prev_pp_balance = Decimal("520000")
    prev_tlf_balance = Decimal("380000")

    for data in annual_data:
        year = data["year"]

        # Create period
        period = Period(
            project_id=project.id,
            period_start=date(year, 1, 1),
            period_end=date(year, 12, 31),
            period_type=PeriodType.ANNUAL,
            is_audited=True
        )
        db.add(period)
        db.commit()
        db.refresh(period)

        # Financial Statement Set
        fs = FinancialStatementSet(
            period_id=period.id,
            source_type=SourceType.AUDITED
        )
        db.add(fs)
        db.commit()
        db.refresh(fs)

        # Income Statement
        income = IncomeStatement(
            financial_statement_id=fs.id,
            turnover=data["turnover"],
            cost_of_sales=data["cost_of_sales"],
            administrative_expenses=data["admin"],
            other_operating_income=Decimal("2500"),
            interest_receivable=data["interest_receivable"],
            interest_payable=data["interest_payable"],
            fair_value_movement_derivatives=data["fv_movement"],
            current_tax=data["current_tax"],
            deferred_tax=data["deferred_tax"],
            depreciation=data["depreciation"]
        )
        db.add(income)

        # Balance Sheet
        years_since_cod = year - 2019
        fixed_assets_nbv = Decimal("1150000") - (Decimal("42000") * years_since_cod)

        bs = BalanceSheet(
            financial_statement_id=fs.id,
            wind_farm_assets_cost=Decimal("1150000"),
            wind_farm_assets_depreciation=Decimal("42000") * years_since_cod,
            transmission_assets_cost=Decimal("0"),
            transmission_assets_depreciation=Decimal("0"),
            decommissioning_asset_cost=Decimal("65000"),
            decommissioning_asset_depreciation=Decimal("2400") * years_since_cod,
            trade_receivables=data["turnover"] * Decimal("0.08"),
            prepayments_accrued_income=Decimal("15000"),
            cash_and_equivalents=Decimal("35000") + (Decimal("5000") * years_since_cod),
            trade_payables=Decimal("12000"),
            accruals_deferred_income=Decimal("18000"),
            short_term_loans=Decimal("45000"),
            short_term_bonds=Decimal("25000"),
            long_term_loans=data["tlf_balance"],
            long_term_bonds=data["pp_balance"],
            decommissioning_provision=Decimal("72000") + (Decimal("2800") * years_since_cod),
            deferred_tax_liability=Decimal("25000") + (data["deferred_tax"] * years_since_cod),
            share_capital=Decimal("0"),
            retained_earnings=Decimal("45000") + (Decimal("15000") * years_since_cod),
        )
        db.add(bs)

        # Cash Flow Statement
        ebitda = data["turnover"] - data["cost_of_sales"] - data["admin"] + Decimal("2500") + data["depreciation"]
        cf = CashFlowStatement(
            financial_statement_id=fs.id,
            cash_from_operations=ebitda - data["current_tax"],
            tax_paid=data["current_tax"],
            net_cash_from_operating=ebitda - data["current_tax"],
            capex=Decimal("-5000"),
            net_cash_from_investing=Decimal("-5000"),
            loan_repayments=prev_tlf_balance - data["tlf_balance"],
            bond_repayments=prev_pp_balance - data["pp_balance"],
            interest_paid=data["interest_payable"],
            dividends_paid=data["dividends"],
            net_cash_from_financing=-(data["interest_payable"] + data["dividends"] + (prev_tlf_balance - data["tlf_balance"]) + (prev_pp_balance - data["pp_balance"])),
            opening_cash=Decimal("35000") + (Decimal("5000") * (years_since_cod - 1)) if years_since_cod > 0 else Decimal("35000"),
            closing_cash=Decimal("35000") + (Decimal("5000") * years_since_cod),
        )
        db.add(cf)

        # Production Data
        hours_in_year = Decimal("8760")
        prod = ProductionData(
            period_id=period.id,
            gross_generation_mwh=data["generation_mwh"] * Decimal("1.02"),
            net_export_mwh=data["generation_mwh"],
            availability_pct=data["availability"],
            curtailment_mwh=data["generation_mwh"] * Decimal("0.015"),
            curtailment_pct=Decimal("1.5"),
            p50_generation_mwh=data["p50_mwh"],
            budget_generation_mwh=data["p50_mwh"] * Decimal("0.98"),
            period_hours=hours_in_year
        )
        db.add(prod)

        # Revenue Breakdown
        rev = RevenueBreakdown(
            period_id=period.id,
            ppa_revenue=data["ppa_revenue"],
            cfd_revenue=data["cfd_revenue"],
            merchant_revenue=data["merchant_revenue"],
            rego_revenue=Decimal("2500"),
            other_revenue=Decimal("2500")
        )
        db.add(rev)

        # Cost Breakdown
        cost = CostBreakdown(
            period_id=period.id,
            om_fixed=data["om_fixed"],
            om_variable=data["om_variable"],
            insurance=data["insurance"],
            seabed_lease=data["seabed_lease"],
            transmission_charges=data["transmission"],
            management_fees=Decimal("3500"),
            admin_costs=data["admin"],
            community_fund=Decimal("150")
        )
        db.add(cost)

        # Debt Movements
        pp_movement = DebtMovement(
            facility_id=pp_notes.id,
            period_id=period.id,
            opening_balance=prev_pp_balance,
            interest_charged=prev_pp_balance * Decimal("0.0315"),
            principal_repaid=prev_pp_balance - data["pp_balance"],
            closing_balance=data["pp_balance"]
        )
        db.add(pp_movement)

        tlf_movement = DebtMovement(
            facility_id=tlf.id,
            period_id=period.id,
            opening_balance=prev_tlf_balance,
            interest_charged=prev_tlf_balance * Decimal("0.031"),
            principal_repaid=prev_tlf_balance - data["tlf_balance"],
            closing_balance=data["tlf_balance"]
        )
        db.add(tlf_movement)

        # Dividend Distribution
        div = DividendDistribution(
            period_id=period.id,
            cash_available_for_distribution=data["dividends"] * Decimal("1.15"),
            dividends_declared=data["dividends"],
            dividends_paid=data["dividends"],
            retained_for_reserves=data["dividends"] * Decimal("0.15")
        )
        db.add(div)

        # Covenant Test (DSCR)
        debt_service = (prev_pp_balance - data["pp_balance"]) + (prev_tlf_balance - data["tlf_balance"]) + data["interest_payable"]
        cfads = ebitda - data["current_tax"]
        dscr = cfads / debt_service if debt_service > 0 else Decimal("0")

        covenant = CovenantTest(
            period_id=period.id,
            facility_id=pp_notes.id,
            covenant_name="DSCR",
            required_minimum=Decimal("1.10"),
            actual_value=dscr.quantize(Decimal("0.01")),
            passed=dscr >= Decimal("1.10"),
            headroom_absolute=cfads - (debt_service * Decimal("1.10")),
            headroom_pct=((dscr / Decimal("1.10")) - 1) * 100 if dscr > 0 else Decimal("0"),
            test_date=date(year, 12, 31)
        )
        db.add(covenant)

        prev_pp_balance = data["pp_balance"]
        prev_tlf_balance = data["tlf_balance"]

    db.commit()
    print(f"Created Project Alpha: {project.name}")
    return project


def seed_project_beta(db: Session):
    """
    Create Project Beta - Horizon Bay Wind Farm
    A 320 MW offshore wind farm in the Irish Sea.
    """
    project = Project(
        name="Horizon Bay Wind Farm",
        location="Irish Sea, UK",
        cod_date=date(2020, 3, 1),
        installed_capacity_mw=Decimal("320"),
        ownership_share_pct=Decimal("100"),
        currency="GBP",
        reporting_frequency=PeriodType.ANNUAL,
        initial_equity_invested=Decimal("280000"),
        description="320 MW offshore wind farm located 28km off the Welsh coast"
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Create debt facility
    senior_debt = DebtFacility(
        project_id=project.id,
        name="Senior Term Loan",
        facility_type=DebtType.BANK_LOAN,
        currency="GBP",
        original_notional=Decimal("580000"),
        is_fixed_rate=False,
        floating_reference="SONIA",
        margin_pct=Decimal("1.45"),
        start_date=date(2020, 3, 1),
        maturity_date=date(2035, 3, 1),
        amortisation_type=AmortisationType.SCULPTED,
        repayment_frequency="semi-annual"
    )
    db.add(senior_debt)
    db.commit()

    # Simplified annual data for 2020-2023
    annual_data = [
        {"year": 2020, "turnover": Decimal("125000"), "generation": Decimal("980000"), "debt": Decimal("565000"), "dividends": Decimal("28000")},
        {"year": 2021, "turnover": Decimal("148000"), "generation": Decimal("1085000"), "debt": Decimal("538000"), "dividends": Decimal("35000")},
        {"year": 2022, "turnover": Decimal("165000"), "generation": Decimal("1120000"), "debt": Decimal("505000"), "dividends": Decimal("42000")},
        {"year": 2023, "turnover": Decimal("182000"), "generation": Decimal("1155000"), "debt": Decimal("468000"), "dividends": Decimal("52000")},
    ]

    prev_debt = Decimal("580000")

    for data in annual_data:
        year = data["year"]

        period = Period(
            project_id=project.id,
            period_start=date(year, 1, 1),
            period_end=date(year, 12, 31),
            period_type=PeriodType.ANNUAL,
            is_audited=True
        )
        db.add(period)
        db.commit()
        db.refresh(period)

        fs = FinancialStatementSet(period_id=period.id, source_type=SourceType.AUDITED)
        db.add(fs)
        db.commit()
        db.refresh(fs)

        cost_of_sales = data["turnover"] * Decimal("0.32")
        admin = data["turnover"] * Decimal("0.04")
        depreciation = Decimal("32000")
        interest = prev_debt * Decimal("0.035")

        income = IncomeStatement(
            financial_statement_id=fs.id,
            turnover=data["turnover"],
            cost_of_sales=cost_of_sales,
            administrative_expenses=admin,
            interest_payable=interest,
            interest_receivable=Decimal("200"),
            depreciation=depreciation,
            current_tax=(data["turnover"] - cost_of_sales - admin - interest) * Decimal("0.19"),
            deferred_tax=Decimal("800")
        )
        db.add(income)

        years_since_cod = year - 2020
        bs = BalanceSheet(
            financial_statement_id=fs.id,
            wind_farm_assets_cost=Decimal("850000"),
            wind_farm_assets_depreciation=depreciation * years_since_cod,
            decommissioning_asset_cost=Decimal("48000"),
            decommissioning_asset_depreciation=Decimal("1800") * years_since_cod,
            trade_receivables=data["turnover"] * Decimal("0.07"),
            cash_and_equivalents=Decimal("28000"),
            trade_payables=Decimal("9500"),
            short_term_loans=Decimal("35000"),
            long_term_loans=data["debt"],
            decommissioning_provision=Decimal("52000"),
            retained_earnings=Decimal("35000") + (Decimal("12000") * years_since_cod)
        )
        db.add(bs)

        prod = ProductionData(
            period_id=period.id,
            net_export_mwh=data["generation"],
            gross_generation_mwh=data["generation"] * Decimal("1.02"),
            availability_pct=Decimal("94.5") + (Decimal("0.3") * years_since_cod),
            p50_generation_mwh=Decimal("1100000"),
            period_hours=Decimal("8760")
        )
        db.add(prod)

        movement = DebtMovement(
            facility_id=senior_debt.id,
            period_id=period.id,
            opening_balance=prev_debt,
            interest_charged=interest,
            principal_repaid=prev_debt - data["debt"],
            closing_balance=data["debt"]
        )
        db.add(movement)

        div = DividendDistribution(
            period_id=period.id,
            dividends_paid=data["dividends"],
            dividends_declared=data["dividends"]
        )
        db.add(div)

        prev_debt = data["debt"]

    db.commit()
    print(f"Created Project Beta: {project.name}")
    return project


def main():
    """Main function to seed demo data."""
    print("Creating database tables...")
    create_tables()

    db = SessionLocal()
    try:
        # Check if data already exists
        existing = db.query(Project).first()
        if existing:
            print("Demo data already exists. Skipping seed.")
            return

        print("Seeding demo data...")
        seed_project_alpha(db)
        seed_project_beta(db)
        print("Demo data seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
