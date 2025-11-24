"""
Text parsing service for extracting financial data from pasted text.

This module provides intelligent parsing of text extracted from:
- Annual reports / financial statements
- Loan compliance certificates
- Production reports
"""
import re
from typing import List, Dict, Optional, Tuple
from decimal import Decimal, InvalidOperation
from app.schemas.schemas import ParsedField, ParsedDataResponse


# Field mapping dictionaries - maps common terms to internal field names
INCOME_STATEMENT_MAPPINGS = {
    # Revenue
    "turnover": "turnover",
    "revenue": "turnover",
    "total revenue": "turnover",
    "sales": "turnover",
    "income": "turnover",

    # Cost of Sales
    "cost of sales": "cost_of_sales",
    "cost of goods sold": "cost_of_sales",
    "cogs": "cost_of_sales",
    "operating costs": "cost_of_sales",

    # Admin
    "administrative expenses": "administrative_expenses",
    "admin expenses": "administrative_expenses",
    "administration costs": "administrative_expenses",
    "g&a": "administrative_expenses",

    # Operating Profit
    "operating profit": "operating_profit",
    "ebit": "operating_profit",
    "profit from operations": "operating_profit",

    # Finance
    "interest receivable": "interest_receivable",
    "interest income": "interest_receivable",
    "finance income": "interest_receivable",
    "interest payable": "interest_payable",
    "interest expense": "interest_payable",
    "finance costs": "interest_payable",
    "interest payable and similar charges": "interest_payable",

    # Fair value
    "fair value movement": "fair_value_movement_derivatives",
    "fair value movements on financial instruments": "fair_value_movement_derivatives",
    "derivative fair value": "fair_value_movement_derivatives",

    # Profit
    "profit before tax": "profit_before_tax",
    "profit before taxation": "profit_before_tax",
    "pbt": "profit_before_tax",
    "profit after tax": "profit_after_tax",
    "profit for the year": "profit_after_tax",
    "profit for the period": "profit_after_tax",
    "net profit": "profit_after_tax",

    # Tax
    "taxation": "total_tax",
    "tax": "total_tax",
    "income tax": "total_tax",
    "current tax": "current_tax",
    "deferred tax": "deferred_tax",

    # Depreciation
    "depreciation": "depreciation",
    "depreciation and amortisation": "depreciation",
    "d&a": "depreciation",
}

BALANCE_SHEET_MAPPINGS = {
    # Assets
    "tangible assets": "total_fixed_assets",
    "fixed assets": "total_fixed_assets",
    "property plant and equipment": "total_fixed_assets",
    "ppe": "total_fixed_assets",
    "wind farm assets": "wind_farm_assets_cost",

    # Current assets
    "debtors": "trade_receivables",
    "trade receivables": "trade_receivables",
    "trade debtors": "trade_receivables",
    "cash at bank": "cash_and_equivalents",
    "cash and cash equivalents": "cash_and_equivalents",
    "cash": "cash_and_equivalents",

    # Liabilities
    "creditors": "trade_payables",
    "trade payables": "trade_payables",
    "trade creditors": "trade_payables",
    "loans": "long_term_loans",
    "bank loans": "long_term_loans",
    "bonds": "long_term_bonds",
    "pp notes": "long_term_bonds",

    # Provisions
    "decommissioning provision": "decommissioning_provision",
    "provisions": "other_provisions",

    # Equity
    "share capital": "share_capital",
    "called up share capital": "share_capital",
    "retained earnings": "retained_earnings",
    "profit and loss account": "retained_earnings",
    "shareholders funds": "total_equity",
    "shareholders' funds": "total_equity",
    "net assets": "net_assets",
}

PRODUCTION_MAPPINGS = {
    "generation": "net_export_mwh",
    "output": "net_export_mwh",
    "electricity generated": "net_export_mwh",
    "net generation": "net_export_mwh",
    "gross generation": "gross_generation_mwh",
    "availability": "availability_pct",
    "pba": "availability_pct",
    "production based availability": "availability_pct",
    "curtailment": "curtailment_mwh",
    "p50": "p50_generation_mwh",
    "budget": "budget_generation_mwh",
    "capacity factor": "capacity_factor_pct",
}

DEBT_MAPPINGS = {
    "opening balance": "opening_balance",
    "closing balance": "closing_balance",
    "interest charged": "interest_charged",
    "principal repaid": "principal_repaid",
    "repayments": "principal_repaid",
    "drawdowns": "drawdowns",
    "dscr": "dscr",
    "debt service coverage ratio": "dscr",
}


def clean_numeric_value(value_str: str) -> Optional[Decimal]:
    """
    Clean and convert a string value to Decimal.

    Handles:
    - Parentheses for negatives: (1,234) -> -1234
    - Commas: 1,234,567 -> 1234567
    - Currency symbols: £1,234 -> 1234
    - 'k' or 'm' suffixes: 1.5m -> 1500000
    """
    if not value_str:
        return None

    # Remove common prefixes/suffixes
    cleaned = value_str.strip()
    cleaned = re.sub(r'[£$€]', '', cleaned)
    cleaned = cleaned.replace(',', '')

    # Handle parentheses as negative
    is_negative = False
    if cleaned.startswith('(') and cleaned.endswith(')'):
        is_negative = True
        cleaned = cleaned[1:-1]

    # Handle k/m suffixes
    multiplier = Decimal("1")
    if cleaned.lower().endswith('k'):
        multiplier = Decimal("1000")
        cleaned = cleaned[:-1]
    elif cleaned.lower().endswith('m'):
        multiplier = Decimal("1000000")
        cleaned = cleaned[:-1]

    # Handle explicit negative sign
    if cleaned.startswith('-'):
        is_negative = True
        cleaned = cleaned[1:]

    try:
        value = Decimal(cleaned.strip()) * multiplier
        if is_negative:
            value = -value
        return value
    except (InvalidOperation, ValueError):
        return None


def extract_key_value_pairs(text: str) -> List[Tuple[str, str]]:
    """
    Extract key-value pairs from text.

    Looks for patterns like:
    - "Key: Value"
    - "Key    Value" (table format)
    - "Key £1,234"
    """
    pairs = []

    # Pattern 1: Key: Value
    pattern1 = re.findall(r'([A-Za-z][A-Za-z\s&\']+?):\s*([\d,.()\-£$€]+(?:\s*[km])?)', text, re.IGNORECASE)
    pairs.extend(pattern1)

    # Pattern 2: Key followed by number (tabular)
    lines = text.split('\n')
    for line in lines:
        # Match: text followed by whitespace and a number
        match = re.match(r'^([A-Za-z][A-Za-z\s&\']+?)\s{2,}([\d,.()\-£$€]+(?:\s*[km])?)\s*$', line.strip(), re.IGNORECASE)
        if match:
            pairs.append((match.group(1).strip(), match.group(2).strip()))

    return pairs


def find_best_mapping(key: str, mappings: Dict[str, str]) -> Optional[str]:
    """Find the best matching field for a key."""
    key_lower = key.lower().strip()

    # Direct match
    if key_lower in mappings:
        return mappings[key_lower]

    # Partial match
    for pattern, field in mappings.items():
        if pattern in key_lower or key_lower in pattern:
            return field

    return None


def parse_financial_text(text: str) -> ParsedDataResponse:
    """
    Parse financial text and extract structured data.

    Returns parsed fields organized by category.
    """
    pairs = extract_key_value_pairs(text)

    income_fields = []
    balance_fields = []
    production_fields = []
    debt_fields = []
    unmatched_fields = []

    for key, value_str in pairs:
        parsed_value = clean_numeric_value(value_str)

        # Try to match against each category
        income_match = find_best_mapping(key, INCOME_STATEMENT_MAPPINGS)
        balance_match = find_best_mapping(key, BALANCE_SHEET_MAPPINGS)
        production_match = find_best_mapping(key, PRODUCTION_MAPPINGS)
        debt_match = find_best_mapping(key, DEBT_MAPPINGS)

        field = ParsedField(
            original_text=f"{key}: {value_str}",
            extracted_value=str(parsed_value) if parsed_value else value_str,
            confidence=0.8 if parsed_value else 0.5,
            needs_review=parsed_value is None,
        )

        if income_match:
            field.mapped_field = income_match
            income_fields.append(field)
        elif balance_match:
            field.mapped_field = balance_match
            balance_fields.append(field)
        elif production_match:
            field.mapped_field = production_match
            production_fields.append(field)
        elif debt_match:
            field.mapped_field = debt_match
            debt_fields.append(field)
        else:
            field.needs_review = True
            unmatched_fields.append(field)

    return ParsedDataResponse(
        income_statement_fields=income_fields,
        balance_sheet_fields=balance_fields,
        production_fields=production_fields,
        debt_fields=debt_fields,
        unmatched_fields=unmatched_fields,
    )
