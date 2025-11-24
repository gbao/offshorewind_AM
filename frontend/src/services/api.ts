/**
 * API service for Offshore Wind Hub
 */
import axios from 'axios';
import type {
  Project,
  Period,
  FinancialStatement,
  ProductionData,
  DebtFacility,
  DividendDistribution,
  CovenantTest,
  ProjectKPISummary,
  PortfolioSummary,
  FinancialKPIs,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects
export const getProjects = () => api.get<Project[]>('/projects').then((r) => r.data);
export const getProject = (id: number) => api.get<Project>(`/projects/${id}`).then((r) => r.data);
export const createProject = (data: Partial<Project>) => api.post<Project>('/projects', data).then((r) => r.data);
export const updateProject = (id: number, data: Partial<Project>) => api.put<Project>(`/projects/${id}`, data).then((r) => r.data);
export const deleteProject = (id: number) => api.delete(`/projects/${id}`);

// Periods
export const getProjectPeriods = (projectId: number) => api.get<Period[]>(`/projects/${projectId}/periods`).then((r) => r.data);
export const createPeriod = (data: Partial<Period>) => api.post<Period>('/periods', data).then((r) => r.data);
export const getPeriod = (id: number) => api.get<Period>(`/periods/${id}`).then((r) => r.data);
export const deletePeriod = (id: number) => api.delete(`/periods/${id}`);

// Financial Statements
export const getFinancialStatement = (periodId: number) => api.get<FinancialStatement>(`/periods/${periodId}/financial-statement`).then((r) => r.data);
export const saveFinancialStatement = (periodId: number, data: Partial<FinancialStatement>) => api.post(`/periods/${periodId}/financial-statement`, data).then((r) => r.data);

// Production Data
export const getProductionData = (periodId: number) => api.get<ProductionData>(`/periods/${periodId}/production`).then((r) => r.data);
export const saveProductionData = (periodId: number, data: Partial<ProductionData>) => api.post(`/periods/${periodId}/production`, data).then((r) => r.data);

// Debt Facilities
export const getDebtFacilities = (projectId: number) => api.get<DebtFacility[]>(`/projects/${projectId}/debt-facilities`).then((r) => r.data);
export const getDebtFacility = (id: number) => api.get<DebtFacility>(`/debt-facilities/${id}`).then((r) => r.data);
export const createDebtFacility = (data: Partial<DebtFacility>) => api.post<DebtFacility>('/debt-facilities', data).then((r) => r.data);
export const getDebtMovements = (periodId: number) => api.get(`/periods/${periodId}/debt-movements`).then((r) => r.data);

// Dividends
export const getDividends = (periodId: number) => api.get<DividendDistribution>(`/periods/${periodId}/dividends`).then((r) => r.data);
export const saveDividends = (periodId: number, data: Partial<DividendDistribution>) => api.post(`/periods/${periodId}/dividends`, data).then((r) => r.data);

// Covenant Tests
export const getCovenantTests = (periodId: number) => api.get<CovenantTest[]>(`/periods/${periodId}/covenant-tests`).then((r) => r.data);

// KPIs and Analytics
export const getProjectKPIs = (projectId: number) => api.get<ProjectKPISummary>(`/projects/${projectId}/kpis`).then((r) => r.data);
export const getPeriodKPIs = (periodId: number) => api.get<FinancialKPIs>(`/periods/${periodId}/kpis`).then((r) => r.data);
export const getPortfolioSummary = () => api.get<PortfolioSummary>('/portfolio/summary').then((r) => r.data);

// Data Parsing
export const parseText = (text: string) => api.post('/parse-text', { text }).then((r) => r.data);

export default api;
