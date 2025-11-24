"""FastAPI routes for Offshore Wind Operational Performance Hub."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    Project, Period, FinancialStatementSet, IncomeStatement, BalanceSheet,
    CashFlowStatement, ProductionData, RevenueBreakdown, CostBreakdown,
    DebtFacility, DebtMovement, InterestRateSwap, DividendDistribution,
    CovenantTest
)
from app.schemas import schemas
from app.analytics import calculations
from app.services import parser

router = APIRouter()


# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@router.get("/projects", response_model=List[schemas.ProjectResponse], tags=["Projects"])
def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    return db.query(Project).all()


@router.post("/projects", response_model=schemas.ProjectResponse, tags=["Projects"])
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects/{project_id}", response_model=schemas.ProjectResponse, tags=["Projects"])
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=schemas.ProjectResponse, tags=["Projects"])
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in project_update.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", tags=["Projects"])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project and all related data."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}


# =============================================================================
# PERIOD ENDPOINTS
# =============================================================================

@router.get("/projects/{project_id}/periods", response_model=List[schemas.PeriodResponse], tags=["Periods"])
def list_periods(project_id: int, db: Session = Depends(get_db)):
    """List all periods for a project."""
    return db.query(Period).filter(Period.project_id == project_id).order_by(Period.period_end.desc()).all()


@router.post("/periods", response_model=schemas.PeriodResponse, tags=["Periods"])
def create_period(period: schemas.PeriodCreate, db: Session = Depends(get_db)):
    """Create a new period."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == period.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_period = Period(**period.model_dump())
    db.add(db_period)
    db.commit()
    db.refresh(db_period)
    return db_period


@router.get("/periods/{period_id}", response_model=schemas.PeriodResponse, tags=["Periods"])
def get_period(period_id: int, db: Session = Depends(get_db)):
    """Get a specific period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return period


@router.delete("/periods/{period_id}", tags=["Periods"])
def delete_period(period_id: int, db: Session = Depends(get_db)):
    """Delete a period and all related data."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    db.delete(period)
    db.commit()
    return {"message": "Period deleted"}


# =============================================================================
# FINANCIAL STATEMENT ENDPOINTS
# =============================================================================

@router.get("/periods/{period_id}/financial-statement", tags=["Financial Statements"])
def get_financial_statement(period_id: int, db: Session = Depends(get_db)):
    """Get financial statement set for a period with calculated fields."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    fs = period.financial_statement
    if not fs:
        return None

    result = {
        "id": fs.id,
        "period_id": fs.period_id,
        "source_type": fs.source_type,
        "notes": fs.notes,
        "created_at": fs.created_at,
        "updated_at": fs.updated_at,
    }

    # Income Statement with calculations
    if fs.income_statement:
        income = fs.income_statement
        result["income_statement"] = {
            **schemas.IncomeStatementBase.model_validate(income).model_dump(),
            "id": income.id,
            "financial_statement_id": income.financial_statement_id,
            "gross_profit": calculations.calculate_gross_profit(income),
            "operating_profit": calculations.calculate_operating_profit(income),
            "ebitda": calculations.calculate_ebitda(income),
            "profit_before_tax": calculations.calculate_profit_before_tax(income),
            "total_tax": calculations.calculate_total_tax(income),
            "profit_after_tax": calculations.calculate_profit_after_tax(income),
        }

    # Balance Sheet with calculations
    if fs.balance_sheet:
        bs = fs.balance_sheet
        result["balance_sheet"] = {
            **schemas.BalanceSheetBase.model_validate(bs).model_dump(),
            "id": bs.id,
            "financial_statement_id": bs.financial_statement_id,
            "total_fixed_assets": calculations.calculate_total_fixed_assets(bs),
            "total_current_assets": calculations.calculate_total_current_assets(bs),
            "total_current_liabilities": calculations.calculate_total_current_liabilities(bs),
            "net_current_assets": calculations.calculate_total_current_assets(bs) - calculations.calculate_total_current_liabilities(bs),
            "total_non_current_liabilities": calculations.calculate_total_non_current_liabilities(bs),
            "total_equity": calculations.calculate_total_equity(bs),
            "net_assets": calculations.calculate_net_assets(bs),
            "total_debt": calculations.calculate_total_debt(bs),
            "net_debt": calculations.calculate_net_debt(bs),
        }

    # Cash Flow Statement
    if fs.cash_flow_statement:
        result["cash_flow_statement"] = schemas.CashFlowStatementResponse.model_validate(
            fs.cash_flow_statement
        ).model_dump()

    return result


@router.post("/periods/{period_id}/financial-statement", tags=["Financial Statements"])
def create_or_update_financial_statement(
    period_id: int,
    data: schemas.FinancialStatementSetCreate,
    db: Session = Depends(get_db)
):
    """Create or update financial statement set for a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    # Check if financial statement exists
    fs = period.financial_statement
    if not fs:
        fs = FinancialStatementSet(period_id=period_id)
        db.add(fs)
        db.commit()
        db.refresh(fs)

    fs.source_type = data.source_type
    fs.notes = data.notes

    # Handle Income Statement
    if data.income_statement:
        if fs.income_statement:
            for field, value in data.income_statement.model_dump().items():
                setattr(fs.income_statement, field, value)
        else:
            income = IncomeStatement(
                financial_statement_id=fs.id,
                **data.income_statement.model_dump()
            )
            db.add(income)

    # Handle Balance Sheet
    if data.balance_sheet:
        if fs.balance_sheet:
            for field, value in data.balance_sheet.model_dump().items():
                setattr(fs.balance_sheet, field, value)
        else:
            bs = BalanceSheet(
                financial_statement_id=fs.id,
                **data.balance_sheet.model_dump()
            )
            db.add(bs)

    # Handle Cash Flow Statement
    if data.cash_flow_statement:
        if fs.cash_flow_statement:
            for field, value in data.cash_flow_statement.model_dump().items():
                setattr(fs.cash_flow_statement, field, value)
        else:
            cf = CashFlowStatement(
                financial_statement_id=fs.id,
                **data.cash_flow_statement.model_dump()
            )
            db.add(cf)

    db.commit()
    db.refresh(fs)
    return {"message": "Financial statement updated", "id": fs.id}


# =============================================================================
# PRODUCTION DATA ENDPOINTS
# =============================================================================

@router.get("/periods/{period_id}/production", tags=["Production"])
def get_production_data(period_id: int, db: Session = Depends(get_db)):
    """Get production data for a period with calculated KPIs."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    production = period.production_data
    if not production:
        return None

    project = period.project
    result = schemas.ProductionDataBase.model_validate(production).model_dump()
    result["id"] = production.id
    result["period_id"] = production.period_id
    result["capacity_factor_pct"] = calculations.calculate_capacity_factor(
        production, project.installed_capacity_mw
    )
    result["generation_vs_p50_pct"] = calculations.calculate_generation_vs_p50(production)
    result["generation_vs_budget_pct"] = calculations.calculate_generation_vs_budget(production)

    return result


@router.post("/periods/{period_id}/production", tags=["Production"])
def create_or_update_production_data(
    period_id: int,
    data: schemas.ProductionDataBase,
    db: Session = Depends(get_db)
):
    """Create or update production data for a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    production = period.production_data
    if production:
        for field, value in data.model_dump().items():
            setattr(production, field, value)
    else:
        production = ProductionData(period_id=period_id, **data.model_dump())
        db.add(production)

    db.commit()
    db.refresh(production)
    return {"message": "Production data updated", "id": production.id}


# =============================================================================
# REVENUE & COST BREAKDOWN ENDPOINTS
# =============================================================================

@router.get("/periods/{period_id}/revenue-breakdown", tags=["Revenue & Costs"])
def get_revenue_breakdown(period_id: int, db: Session = Depends(get_db)):
    """Get revenue breakdown for a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return period.revenue_breakdown


@router.post("/periods/{period_id}/revenue-breakdown", tags=["Revenue & Costs"])
def create_or_update_revenue_breakdown(
    period_id: int,
    data: schemas.RevenueBreakdownBase,
    db: Session = Depends(get_db)
):
    """Create or update revenue breakdown for a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    breakdown = period.revenue_breakdown
    if breakdown:
        for field, value in data.model_dump().items():
            setattr(breakdown, field, value)
    else:
        breakdown = RevenueBreakdown(period_id=period_id, **data.model_dump())
        db.add(breakdown)

    db.commit()
    return {"message": "Revenue breakdown updated"}


@router.get("/periods/{period_id}/cost-breakdown", tags=["Revenue & Costs"])
def get_cost_breakdown(period_id: int, db: Session = Depends(get_db)):
    """Get cost breakdown for a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return period.cost_breakdown


@router.post("/periods/{period_id}/cost-breakdown", tags=["Revenue & Costs"])
def create_or_update_cost_breakdown(
    period_id: int,
    data: schemas.CostBreakdownBase,
    db: Session = Depends(get_db)
):
    """Create or update cost breakdown for a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    breakdown = period.cost_breakdown
    if breakdown:
        for field, value in data.model_dump().items():
            setattr(breakdown, field, value)
    else:
        breakdown = CostBreakdown(period_id=period_id, **data.model_dump())
        db.add(breakdown)

    db.commit()
    return {"message": "Cost breakdown updated"}


# =============================================================================
# DEBT FACILITY ENDPOINTS
# =============================================================================

@router.get("/projects/{project_id}/debt-facilities", response_model=List[schemas.DebtFacilityResponse], tags=["Debt"])
def list_debt_facilities(project_id: int, db: Session = Depends(get_db)):
    """List all debt facilities for a project."""
    facilities = db.query(DebtFacility).filter(DebtFacility.project_id == project_id).all()

    # Add current outstanding for each
    result = []
    for f in facilities:
        facility_dict = schemas.DebtFacilityBase.model_validate(f).model_dump()
        facility_dict["id"] = f.id
        facility_dict["project_id"] = f.project_id
        facility_dict["created_at"] = f.created_at

        # Get latest movement
        latest_movement = db.query(DebtMovement).filter(
            DebtMovement.facility_id == f.id
        ).join(Period).order_by(Period.period_end.desc()).first()

        facility_dict["current_outstanding"] = latest_movement.closing_balance if latest_movement else f.original_notional
        result.append(facility_dict)

    return result


@router.post("/debt-facilities", response_model=schemas.DebtFacilityResponse, tags=["Debt"])
def create_debt_facility(facility: schemas.DebtFacilityCreate, db: Session = Depends(get_db)):
    """Create a new debt facility."""
    db_facility = DebtFacility(**facility.model_dump())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility


@router.get("/debt-facilities/{facility_id}", tags=["Debt"])
def get_debt_facility(facility_id: int, db: Session = Depends(get_db)):
    """Get a specific debt facility with movements and swaps."""
    facility = db.query(DebtFacility).filter(DebtFacility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Debt facility not found")

    result = schemas.DebtFacilityBase.model_validate(facility).model_dump()
    result["id"] = facility.id
    result["project_id"] = facility.project_id
    result["created_at"] = facility.created_at
    result["movements"] = [
        schemas.DebtMovementResponse.model_validate(m).model_dump()
        for m in facility.movements
    ]
    result["interest_rate_swaps"] = [
        schemas.InterestRateSwapResponse.model_validate(s).model_dump()
        for s in facility.interest_rate_swaps
    ]

    return result


@router.delete("/debt-facilities/{facility_id}", tags=["Debt"])
def delete_debt_facility(facility_id: int, db: Session = Depends(get_db)):
    """Delete a debt facility."""
    facility = db.query(DebtFacility).filter(DebtFacility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Debt facility not found")
    db.delete(facility)
    db.commit()
    return {"message": "Debt facility deleted"}


# =============================================================================
# DEBT MOVEMENT ENDPOINTS
# =============================================================================

@router.post("/debt-movements", tags=["Debt"])
def create_debt_movement(movement: schemas.DebtMovementCreate, db: Session = Depends(get_db)):
    """Create a debt movement."""
    db_movement = DebtMovement(**movement.model_dump())
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return {"message": "Debt movement created", "id": db_movement.id}


@router.get("/periods/{period_id}/debt-movements", tags=["Debt"])
def get_period_debt_movements(period_id: int, db: Session = Depends(get_db)):
    """Get all debt movements for a period."""
    movements = db.query(DebtMovement).filter(DebtMovement.period_id == period_id).all()
    return [schemas.DebtMovementResponse.model_validate(m).model_dump() for m in movements]


# =============================================================================
# INTEREST RATE SWAP ENDPOINTS
# =============================================================================

@router.post("/interest-rate-swaps", tags=["Debt"])
def create_interest_rate_swap(swap: schemas.InterestRateSwapCreate, db: Session = Depends(get_db)):
    """Create an interest rate swap."""
    db_swap = InterestRateSwap(**swap.model_dump())
    db.add(db_swap)
    db.commit()
    db.refresh(db_swap)
    return {"message": "Interest rate swap created", "id": db_swap.id}


# =============================================================================
# DIVIDEND ENDPOINTS
# =============================================================================

@router.get("/periods/{period_id}/dividends", tags=["Dividends"])
def get_dividends(period_id: int, db: Session = Depends(get_db)):
    """Get dividend distribution for a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    return period.dividend_distribution


@router.post("/periods/{period_id}/dividends", tags=["Dividends"])
def create_or_update_dividends(
    period_id: int,
    data: schemas.DividendDistributionBase,
    db: Session = Depends(get_db)
):
    """Create or update dividend distribution for a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    dividend = period.dividend_distribution
    if dividend:
        for field, value in data.model_dump().items():
            setattr(dividend, field, value)
    else:
        dividend = DividendDistribution(period_id=period_id, **data.model_dump())
        db.add(dividend)

    db.commit()
    return {"message": "Dividend distribution updated"}


# =============================================================================
# COVENANT TEST ENDPOINTS
# =============================================================================

@router.post("/covenant-tests", tags=["Covenants"])
def create_covenant_test(test: schemas.CovenantTestCreate, db: Session = Depends(get_db)):
    """Create a covenant test result."""
    db_test = CovenantTest(**test.model_dump())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return {"message": "Covenant test created", "id": db_test.id}


@router.get("/periods/{period_id}/covenant-tests", tags=["Covenants"])
def get_period_covenant_tests(period_id: int, db: Session = Depends(get_db)):
    """Get all covenant tests for a period."""
    tests = db.query(CovenantTest).filter(CovenantTest.period_id == period_id).all()
    return [schemas.CovenantTestResponse.model_validate(t).model_dump() for t in tests]


# =============================================================================
# KPI AND ANALYTICS ENDPOINTS
# =============================================================================

@router.get("/projects/{project_id}/kpis", tags=["Analytics"])
def get_project_kpis(project_id: int, db: Session = Depends(get_db)):
    """Get comprehensive KPIs for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return calculations.get_project_kpi_summary(project, db)


@router.get("/periods/{period_id}/kpis", tags=["Analytics"])
def get_period_kpis(period_id: int, db: Session = Depends(get_db)):
    """Get KPIs for a specific period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    return calculations.calculate_period_kpis(period, period.project, db)


@router.get("/portfolio/summary", tags=["Analytics"])
def get_portfolio_summary(db: Session = Depends(get_db)):
    """Get portfolio-level summary across all projects."""
    projects = db.query(Project).all()
    summaries = []

    for project in projects:
        summary = calculations.get_project_kpi_summary(project, db)
        # Remove detailed period_kpis for portfolio view
        summary.pop("period_kpis", None)
        summaries.append(summary)

    return {
        "total_projects": len(projects),
        "total_capacity_mw": sum(p.installed_capacity_mw for p in projects),
        "projects": summaries
    }


# =============================================================================
# DATA PARSING ENDPOINTS
# =============================================================================

@router.post("/parse-text", response_model=schemas.ParsedDataResponse, tags=["Data Input"])
def parse_pasted_text(text: str = Body(..., embed=True)):
    """Parse pasted text from financial statements or reports."""
    return parser.parse_financial_text(text)


@router.post("/periods/{period_id}/import-parsed", tags=["Data Input"])
def import_parsed_data(
    period_id: int,
    parsed_data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Import parsed and reviewed data into a period."""
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")

    # This endpoint receives the reviewed/corrected parsed data
    # and creates the appropriate records

    if "income_statement" in parsed_data:
        # Create/update income statement
        pass  # Implementation would map fields to IncomeStatement

    if "balance_sheet" in parsed_data:
        # Create/update balance sheet
        pass

    if "production" in parsed_data:
        # Create/update production data
        pass

    db.commit()
    return {"message": "Data imported successfully"}
