/**
 * TypeScript type definitions for Offshore Wind Hub
 */

export interface Project {
  id: number;
  name: string;
  location?: string;
  cod_date: string;
  installed_capacity_mw: number;
  ownership_share_pct: number;
  currency: string;
  reporting_frequency: 'annual' | 'quarterly' | 'monthly';
  initial_equity_invested?: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Period {
  id: number;
  project_id: number;
  period_start: string;
  period_end: string;
  period_type: 'annual' | 'quarterly' | 'monthly';
  is_audited: boolean;
  created_at: string;
}

export interface IncomeStatement {
  id: number;
  financial_statement_id: number;
  turnover?: number;
  cost_of_sales?: number;
  administrative_expenses?: number;
  other_operating_income?: number;
  interest_receivable?: number;
  interest_payable?: number;
  fair_value_movement_derivatives?: number;
  foreign_exchange_gain_loss?: number;
  current_tax?: number;
  deferred_tax?: number;
  depreciation?: number;
  // Calculated
  gross_profit?: number;
  operating_profit?: number;
  ebitda?: number;
  profit_before_tax?: number;
  total_tax?: number;
  profit_after_tax?: number;
}

export interface BalanceSheet {
  id: number;
  financial_statement_id: number;
  // Fixed Assets
  wind_farm_assets_cost?: number;
  wind_farm_assets_depreciation?: number;
  transmission_assets_cost?: number;
  transmission_assets_depreciation?: number;
  decommissioning_asset_cost?: number;
  decommissioning_asset_depreciation?: number;
  // Current Assets
  trade_receivables?: number;
  cash_and_equivalents?: number;
  // Current Liabilities
  trade_payables?: number;
  short_term_loans?: number;
  short_term_bonds?: number;
  // Non-Current Liabilities
  long_term_loans?: number;
  long_term_bonds?: number;
  decommissioning_provision?: number;
  // Equity
  share_capital?: number;
  retained_earnings?: number;
  // Calculated
  total_fixed_assets?: number;
  total_current_assets?: number;
  total_current_liabilities?: number;
  total_non_current_liabilities?: number;
  total_equity?: number;
  net_assets?: number;
  total_debt?: number;
  net_debt?: number;
}

export interface FinancialStatement {
  id: number;
  period_id: number;
  source_type: 'audited' | 'management' | 'forecast' | 'budget';
  notes?: string;
  income_statement?: IncomeStatement;
  balance_sheet?: BalanceSheet;
  cash_flow_statement?: CashFlowStatement;
}

export interface CashFlowStatement {
  id: number;
  financial_statement_id: number;
  cash_from_operations?: number;
  net_cash_from_operating?: number;
  net_cash_from_investing?: number;
  net_cash_from_financing?: number;
  net_change_in_cash?: number;
  opening_cash?: number;
  closing_cash?: number;
  cfads_input?: number;
}

export interface ProductionData {
  id: number;
  period_id: number;
  gross_generation_mwh?: number;
  net_export_mwh?: number;
  availability_pct?: number;
  curtailment_mwh?: number;
  p50_generation_mwh?: number;
  budget_generation_mwh?: number;
  period_hours?: number;
  // Calculated
  capacity_factor_pct?: number;
  generation_vs_p50_pct?: number;
  generation_vs_budget_pct?: number;
}

export interface DebtFacility {
  id: number;
  project_id: number;
  name: string;
  facility_type: string;
  currency: string;
  original_notional: number;
  is_fixed_rate: boolean;
  fixed_rate_pct?: number;
  floating_reference?: string;
  margin_pct?: number;
  start_date?: string;
  maturity_date?: string;
  current_outstanding?: number;
}

export interface DebtMovement {
  id: number;
  facility_id: number;
  period_id: number;
  opening_balance?: number;
  interest_charged?: number;
  principal_repaid?: number;
  closing_balance?: number;
}

export interface DividendDistribution {
  id: number;
  period_id: number;
  cash_available_for_distribution?: number;
  dividends_declared?: number;
  dividends_paid?: number;
  retained_for_reserves?: number;
}

export interface CovenantTest {
  id: number;
  period_id: number;
  facility_id?: number;
  covenant_name: string;
  required_minimum?: number;
  actual_value?: number;
  passed?: boolean;
  headroom_pct?: number;
}

export interface FinancialKPIs {
  period_id: number;
  period_end: string;
  revenue?: number;
  ebitda?: number;
  ebit?: number;
  net_profit?: number;
  ebitda_margin_pct?: number;
  net_margin_pct?: number;
  net_debt?: number;
  total_debt?: number;
  dscr?: number;
  dscr_headroom_pct?: number;
  capacity_factor_pct?: number;
  availability_pct?: number;
  revenue_per_mwh?: number;
  cost_per_mwh?: number;
  dividends_paid?: number;
  cumulative_dividends?: number;
}

export interface ProjectKPISummary {
  project_id: number;
  project_name: string;
  installed_capacity_mw: number;
  cod_date?: string;
  latest_revenue?: number;
  latest_ebitda?: number;
  latest_ebitda_margin_pct?: number;
  latest_net_debt?: number;
  latest_dscr?: number;
  latest_capacity_factor_pct?: number;
  latest_availability_pct?: number;
  cumulative_dividends?: number;
  revenue_yoy_pct?: number;
  ebitda_yoy_pct?: number;
  period_kpis?: FinancialKPIs[];
}

export interface PortfolioSummary {
  total_projects: number;
  total_capacity_mw: number;
  projects: ProjectKPISummary[];
}
