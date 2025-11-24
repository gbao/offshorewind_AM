import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Plot from 'react-plotly.js';
import { getProjectKPIs } from '../services/api';

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  if (Math.abs(value) >= 1000000) {
    return `£${(value / 1000000).toFixed(1)}m`;
  }
  return `£${(value / 1000).toFixed(0)}k`;
}

function formatNumber(value: number | undefined, decimals = 1): string {
  if (value === undefined || value === null) return '-';
  return value.toFixed(decimals);
}

function YoYChange({ value }: { value: number | undefined }) {
  if (value === undefined || value === null) return null;
  const isPositive = value >= 0;
  return (
    <div className={`kpi-change ${isPositive ? 'positive' : 'negative'}`}>
      {isPositive ? '+' : ''}{value.toFixed(1)}% YoY
    </div>
  );
}

export default function ProjectDashboard() {
  const { projectId } = useParams();
  const { data: kpis, isLoading } = useQuery({
    queryKey: ['projectKPIs', projectId],
    queryFn: () => getProjectKPIs(Number(projectId)),
    enabled: !!projectId,
  });

  if (isLoading) {
    return <div>Loading project data...</div>;
  }

  if (!kpis) {
    return <div>No data available</div>;
  }

  const periodKpis = kpis.period_kpis || [];
  const years = periodKpis.map(p => p.period_end.slice(0, 4)).reverse();
  const revenues = periodKpis.map(p => (p.revenue || 0) / 1000).reverse();
  const ebitdas = periodKpis.map(p => (p.ebitda || 0) / 1000).reverse();
  const netDebts = periodKpis.map(p => (p.net_debt || 0) / 1000).reverse();
  const dscrs = periodKpis.map(p => p.dscr || 0).reverse();
  const dividends = periodKpis.map(p => (p.dividends_paid || 0) / 1000).reverse();

  return (
    <div>
      {/* KPI Summary Tiles */}
      <div className="kpi-grid">
        <div className="kpi-tile">
          <div className="kpi-label">Latest Revenue</div>
          <div className="kpi-value">{formatCurrency(kpis.latest_revenue)}</div>
          <YoYChange value={kpis.revenue_yoy_pct} />
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Latest EBITDA</div>
          <div className="kpi-value">{formatCurrency(kpis.latest_ebitda)}</div>
          <YoYChange value={kpis.ebitda_yoy_pct} />
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">EBITDA Margin</div>
          <div className="kpi-value">{formatNumber(kpis.latest_ebitda_margin_pct)}%</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Net Debt</div>
          <div className="kpi-value">{formatCurrency(kpis.latest_net_debt)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">DSCR</div>
          <div className="kpi-value">{formatNumber(kpis.latest_dscr, 2)}x</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Capacity Factor</div>
          <div className="kpi-value">{formatNumber(kpis.latest_capacity_factor_pct)}%</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Availability</div>
          <div className="kpi-value">{formatNumber(kpis.latest_availability_pct)}%</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Cumulative Dividends</div>
          <div className="kpi-value">{formatCurrency(kpis.cumulative_dividends)}</div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Revenue & EBITDA Trend */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Revenue & EBITDA Trend</h3>
          </div>
          <Plot
            data={[
              {
                type: 'bar',
                name: 'Revenue',
                x: years,
                y: revenues,
                marker: { color: '#3b82f6' },
              },
              {
                type: 'scatter',
                mode: 'lines+markers',
                name: 'EBITDA',
                x: years,
                y: ebitdas,
                yaxis: 'y2',
                line: { color: '#10b981' },
                marker: { size: 8 },
              },
            ]}
            layout={{
              height: 300,
              margin: { t: 30, b: 40, l: 60, r: 60 },
              legend: { orientation: 'h', y: 1.1 },
              yaxis: { title: 'Revenue (£m)', side: 'left' },
              yaxis2: { title: 'EBITDA (£m)', side: 'right', overlaying: 'y' },
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        {/* Debt & DSCR */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Net Debt & DSCR</h3>
          </div>
          <Plot
            data={[
              {
                type: 'bar',
                name: 'Net Debt',
                x: years,
                y: netDebts,
                marker: { color: '#f59e0b' },
              },
              {
                type: 'scatter',
                mode: 'lines+markers',
                name: 'DSCR',
                x: years,
                y: dscrs,
                yaxis: 'y2',
                line: { color: '#ef4444' },
                marker: { size: 8 },
              },
            ]}
            layout={{
              height: 300,
              margin: { t: 30, b: 40, l: 60, r: 60 },
              legend: { orientation: 'h', y: 1.1 },
              yaxis: { title: 'Net Debt (£m)' },
              yaxis2: {
                title: 'DSCR (x)',
                side: 'right',
                overlaying: 'y',
                range: [0, Math.max(...dscrs) * 1.2],
              },
              shapes: [
                {
                  type: 'line',
                  xref: 'paper',
                  x0: 0,
                  x1: 1,
                  y0: 1.1,
                  y1: 1.1,
                  yref: 'y2',
                  line: { color: '#ef4444', dash: 'dash', width: 1 },
                },
              ],
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        {/* Dividends */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Dividends Paid</h3>
          </div>
          <Plot
            data={[
              {
                type: 'bar',
                name: 'Dividends',
                x: years,
                y: dividends,
                marker: { color: '#8b5cf6' },
              },
            ]}
            layout={{
              height: 300,
              margin: { t: 20, b: 40, l: 60, r: 20 },
              yaxis: { title: '£ millions' },
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        {/* Period KPIs Table */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Historical KPIs</h3>
          </div>
          <div className="table-container" style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Year</th>
                  <th style={{ textAlign: 'right' }}>Revenue</th>
                  <th style={{ textAlign: 'right' }}>EBITDA</th>
                  <th style={{ textAlign: 'right' }}>Margin</th>
                  <th style={{ textAlign: 'right' }}>DSCR</th>
                </tr>
              </thead>
              <tbody>
                {periodKpis.map((p) => (
                  <tr key={p.period_id}>
                    <td>{p.period_end.slice(0, 4)}</td>
                    <td className="number">{formatCurrency(p.revenue)}</td>
                    <td className="number">{formatCurrency(p.ebitda)}</td>
                    <td className="number">{formatNumber(p.ebitda_margin_pct)}%</td>
                    <td className="number">{formatNumber(p.dscr, 2)}x</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
