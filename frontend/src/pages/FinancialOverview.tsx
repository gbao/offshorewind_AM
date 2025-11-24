import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Plot from 'react-plotly.js';
import { getProjectKPIs, getProjectPeriods, getFinancialStatement } from '../services/api';

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  if (Math.abs(value) >= 1000000) return `£${(value / 1000000).toFixed(1)}m`;
  return `£${(value / 1000).toFixed(0)}k`;
}

export default function FinancialOverview() {
  const { projectId } = useParams();
  const { data: kpis } = useQuery({
    queryKey: ['projectKPIs', projectId],
    queryFn: () => getProjectKPIs(Number(projectId)),
    enabled: !!projectId,
  });

  if (!kpis) return <div>Loading...</div>;

  const periodKpis = kpis.period_kpis || [];
  const years = periodKpis.map(p => p.period_end.slice(0, 4)).reverse();
  const revenues = periodKpis.map(p => (p.revenue || 0) / 1000).reverse();
  const ebitdas = periodKpis.map(p => (p.ebitda || 0) / 1000).reverse();
  const netProfits = periodKpis.map(p => (p.net_profit || 0) / 1000).reverse();
  const ebitdaMargins = periodKpis.map(p => p.ebitda_margin_pct || 0).reverse();
  const netMargins = periodKpis.map(p => p.net_margin_pct || 0).reverse();

  return (
    <div>
      {/* Profitability Trend */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Profitability Trend (£m)</h3>
        </div>
        <Plot
          data={[
            { type: 'bar', name: 'Revenue', x: years, y: revenues, marker: { color: '#3b82f6' } },
            { type: 'bar', name: 'EBITDA', x: years, y: ebitdas, marker: { color: '#10b981' } },
            { type: 'bar', name: 'Net Profit', x: years, y: netProfits, marker: { color: '#8b5cf6' } },
          ]}
          layout={{
            height: 350,
            margin: { t: 30, b: 40, l: 60, r: 20 },
            barmode: 'group',
            legend: { orientation: 'h', y: 1.1 },
            yaxis: { title: '£ millions' },
          }}
          config={{ displayModeBar: false }}
          style={{ width: '100%' }}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Margin Trends */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Margin Trends (%)</h3>
          </div>
          <Plot
            data={[
              { type: 'scatter', mode: 'lines+markers', name: 'EBITDA Margin', x: years, y: ebitdaMargins, line: { color: '#10b981' } },
              { type: 'scatter', mode: 'lines+markers', name: 'Net Margin', x: years, y: netMargins, line: { color: '#8b5cf6' } },
            ]}
            layout={{
              height: 300,
              margin: { t: 20, b: 40, l: 50, r: 20 },
              legend: { orientation: 'h', y: 1.1 },
              yaxis: { title: '%', range: [0, 100] },
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        {/* P&L Summary Table */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Profit & Loss Summary</h3>
          </div>
          <div className="table-container" style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Year</th>
                  <th style={{ textAlign: 'right' }}>Revenue</th>
                  <th style={{ textAlign: 'right' }}>EBITDA</th>
                  <th style={{ textAlign: 'right' }}>Net Profit</th>
                </tr>
              </thead>
              <tbody>
                {periodKpis.map(p => (
                  <tr key={p.period_id}>
                    <td>{p.period_end.slice(0, 4)}</td>
                    <td className="number">{formatCurrency(p.revenue)}</td>
                    <td className="number">{formatCurrency(p.ebitda)}</td>
                    <td className="number">{formatCurrency(p.net_profit)}</td>
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
