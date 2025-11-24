import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Plot from 'react-plotly.js';
import { getProjectKPIs, getProject } from '../services/api';

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  if (Math.abs(value) >= 1000000) return `£${(value / 1000000).toFixed(1)}m`;
  return `£${(value / 1000).toFixed(0)}k`;
}

export default function DividendsDashboard() {
  const { projectId } = useParams();
  const { data: kpis } = useQuery({
    queryKey: ['projectKPIs', projectId],
    queryFn: () => getProjectKPIs(Number(projectId)),
    enabled: !!projectId,
  });
  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => getProject(Number(projectId)),
    enabled: !!projectId,
  });

  if (!kpis || !project) return <div>Loading...</div>;

  const periodKpis = kpis.period_kpis || [];
  const years = periodKpis.map(p => p.period_end.slice(0, 4)).reverse();
  const dividends = periodKpis.map(p => (p.dividends_paid || 0) / 1000).reverse();

  // Calculate cumulative dividends over time
  let cumulative = 0;
  const cumulativeDividends = dividends.map(d => {
    cumulative += d;
    return cumulative;
  });

  // Calculate yield
  const equity = project.initial_equity_invested || 1;
  const latestDividend = periodKpis[0]?.dividends_paid || 0;
  const annualYield = (latestDividend / equity) * 100;
  const cumulativeYield = ((kpis.cumulative_dividends || 0) / equity) * 100;

  return (
    <div>
      {/* KPI Tiles */}
      <div className="kpi-grid">
        <div className="kpi-tile">
          <div className="kpi-label">Latest Dividends</div>
          <div className="kpi-value">{formatCurrency(latestDividend)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Cumulative Dividends</div>
          <div className="kpi-value">{formatCurrency(kpis.cumulative_dividends)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Annual Dividend Yield</div>
          <div className="kpi-value">{annualYield.toFixed(1)}%</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Cumulative Yield</div>
          <div className="kpi-value">{cumulativeYield.toFixed(1)}%</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Annual Dividends */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Annual Dividends (£m)</h3>
          </div>
          <Plot
            data={[
              { type: 'bar', name: 'Dividends', x: years, y: dividends, marker: { color: '#8b5cf6' } },
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

        {/* Cumulative Dividends */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Cumulative Dividends (£m)</h3>
          </div>
          <Plot
            data={[
              { type: 'scatter', mode: 'lines+markers', fill: 'tozeroy', name: 'Cumulative', x: years, y: cumulativeDividends, line: { color: '#10b981' }, fillcolor: 'rgba(16, 185, 129, 0.2)' },
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
      </div>

      {/* Dividend History Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Dividend History</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Year</th>
                <th style={{ textAlign: 'right' }}>Dividends Paid</th>
                <th style={{ textAlign: 'right' }}>Yield (%)</th>
                <th style={{ textAlign: 'right' }}>Net Profit</th>
                <th style={{ textAlign: 'right' }}>Payout Ratio</th>
              </tr>
            </thead>
            <tbody>
              {periodKpis.map(p => {
                const div = p.dividends_paid || 0;
                const profit = p.net_profit || 1;
                const payoutRatio = (div / profit) * 100;
                const yieldPct = (div / equity) * 100;
                return (
                  <tr key={p.period_id}>
                    <td>{p.period_end.slice(0, 4)}</td>
                    <td className="number">{formatCurrency(div)}</td>
                    <td className="number">{yieldPct.toFixed(1)}%</td>
                    <td className="number">{formatCurrency(p.net_profit)}</td>
                    <td className="number">{payoutRatio.toFixed(0)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
