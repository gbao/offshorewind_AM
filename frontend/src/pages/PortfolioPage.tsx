import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';
import { getPortfolioSummary } from '../services/api';

function formatNumber(value: number | undefined, decimals = 1): string {
  if (value === undefined || value === null) return '-';
  return value.toLocaleString('en-GB', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  if (Math.abs(value) >= 1000000) {
    return `£${(value / 1000000).toFixed(1)}m`;
  }
  return `£${(value / 1000).toFixed(0)}k`;
}

export default function PortfolioPage() {
  const navigate = useNavigate();
  const { data: portfolio, isLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: getPortfolioSummary,
  });

  if (isLoading) {
    return <div>Loading portfolio...</div>;
  }

  if (!portfolio) {
    return <div>No data available</div>;
  }

  // Prepare chart data
  const projectNames = portfolio.projects.map(p => p.project_name);
  const revenues = portfolio.projects.map(p => (p.latest_revenue || 0) / 1000);
  const ebitdaMargins = portfolio.projects.map(p => p.latest_ebitda_margin_pct || 0);
  const dscrs = portfolio.projects.map(p => p.latest_dscr || 0);
  const capacityFactors = portfolio.projects.map(p => p.latest_capacity_factor_pct || 0);

  return (
    <div>
      <div className="header">
        <h1>Portfolio Overview</h1>
      </div>

      {/* Portfolio KPI Summary */}
      <div className="kpi-grid">
        <div className="kpi-tile">
          <div className="kpi-label">Total Projects</div>
          <div className="kpi-value">{portfolio.total_projects}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Total Capacity</div>
          <div className="kpi-value">{formatNumber(portfolio.total_capacity_mw, 0)} MW</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Portfolio Revenue</div>
          <div className="kpi-value">
            {formatCurrency(portfolio.projects.reduce((sum, p) => sum + (p.latest_revenue || 0), 0))}
          </div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Total Dividends (Cumulative)</div>
          <div className="kpi-value">
            {formatCurrency(portfolio.projects.reduce((sum, p) => sum + (p.cumulative_dividends || 0), 0))}
          </div>
        </div>
      </div>

      {/* Projects Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Projects Summary</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Project</th>
                <th>Capacity (MW)</th>
                <th style={{ textAlign: 'right' }}>Revenue</th>
                <th style={{ textAlign: 'right' }}>EBITDA Margin</th>
                <th style={{ textAlign: 'right' }}>Net Debt</th>
                <th style={{ textAlign: 'right' }}>DSCR</th>
                <th style={{ textAlign: 'right' }}>Capacity Factor</th>
                <th style={{ textAlign: 'right' }}>Cumul. Dividends</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.projects.map((project) => (
                <tr
                  key={project.project_id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/project/${project.project_id}`)}
                >
                  <td>{project.project_name}</td>
                  <td>{formatNumber(project.installed_capacity_mw, 0)}</td>
                  <td className="number">{formatCurrency(project.latest_revenue)}</td>
                  <td className="number">{formatNumber(project.latest_ebitda_margin_pct)}%</td>
                  <td className="number">{formatCurrency(project.latest_net_debt)}</td>
                  <td className="number">{formatNumber(project.latest_dscr, 2)}x</td>
                  <td className="number">{formatNumber(project.latest_capacity_factor_pct)}%</td>
                  <td className="number">{formatCurrency(project.cumulative_dividends)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Revenue by Project (£m)</h3>
          </div>
          <Plot
            data={[
              {
                type: 'bar',
                x: projectNames,
                y: revenues,
                marker: { color: '#3b82f6' },
              },
            ]}
            layout={{
              height: 300,
              margin: { t: 20, b: 80, l: 60, r: 20 },
              yaxis: { title: '£ millions' },
              xaxis: { tickangle: -45 },
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">DSCR vs EBITDA Margin</h3>
          </div>
          <Plot
            data={[
              {
                type: 'scatter',
                mode: 'markers+text',
                x: ebitdaMargins,
                y: dscrs,
                text: projectNames,
                textposition: 'top center',
                marker: {
                  size: capacityFactors.map(cf => cf / 3),
                  color: '#10b981',
                },
              },
            ]}
            layout={{
              height: 300,
              margin: { t: 20, b: 60, l: 60, r: 20 },
              xaxis: { title: 'EBITDA Margin (%)' },
              yaxis: { title: 'DSCR (x)' },
              shapes: [
                {
                  type: 'line',
                  x0: 0,
                  x1: 100,
                  y0: 1.1,
                  y1: 1.1,
                  line: { color: '#ef4444', dash: 'dash', width: 1 },
                },
              ],
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>
      </div>
    </div>
  );
}
