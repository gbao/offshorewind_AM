import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Plot from 'react-plotly.js';
import { getProjectKPIs, getDebtFacilities } from '../services/api';

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  if (Math.abs(value) >= 1000000) return `£${(value / 1000000).toFixed(1)}m`;
  return `£${(value / 1000).toFixed(0)}k`;
}

export default function DebtDashboard() {
  const { projectId } = useParams();
  const { data: kpis } = useQuery({
    queryKey: ['projectKPIs', projectId],
    queryFn: () => getProjectKPIs(Number(projectId)),
    enabled: !!projectId,
  });
  const { data: facilities } = useQuery({
    queryKey: ['debtFacilities', projectId],
    queryFn: () => getDebtFacilities(Number(projectId)),
    enabled: !!projectId,
  });

  if (!kpis) return <div>Loading...</div>;

  const periodKpis = kpis.period_kpis || [];
  const years = periodKpis.map(p => p.period_end.slice(0, 4)).reverse();
  const totalDebts = periodKpis.map(p => (p.total_debt || 0) / 1000).reverse();
  const netDebts = periodKpis.map(p => (p.net_debt || 0) / 1000).reverse();
  const dscrs = periodKpis.map(p => p.dscr || 0).reverse();
  const debtServices = periodKpis.map(p => (p.debt_service || 0) / 1000).reverse();

  return (
    <div>
      {/* KPI Tiles */}
      <div className="kpi-grid">
        <div className="kpi-tile">
          <div className="kpi-label">Total Debt</div>
          <div className="kpi-value">{formatCurrency(periodKpis[0]?.total_debt)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Net Debt</div>
          <div className="kpi-value">{formatCurrency(periodKpis[0]?.net_debt)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Latest DSCR</div>
          <div className="kpi-value">{periodKpis[0]?.dscr?.toFixed(2) || '-'}x</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">DSCR Headroom</div>
          <div className="kpi-value">{periodKpis[0]?.dscr_headroom_pct?.toFixed(1) || '-'}%</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Debt Balance Over Time */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Debt Balance Over Time (£m)</h3>
          </div>
          <Plot
            data={[
              { type: 'scatter', mode: 'lines+markers', name: 'Total Debt', x: years, y: totalDebts, fill: 'tozeroy', fillcolor: 'rgba(239, 68, 68, 0.2)', line: { color: '#ef4444' } },
              { type: 'scatter', mode: 'lines+markers', name: 'Net Debt', x: years, y: netDebts, line: { color: '#f59e0b' } },
            ]}
            layout={{
              height: 300,
              margin: { t: 20, b: 40, l: 60, r: 20 },
              legend: { orientation: 'h', y: 1.1 },
              yaxis: { title: '£ millions' },
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        {/* DSCR with Covenant Line */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">DSCR vs Covenant Threshold</h3>
          </div>
          <Plot
            data={[
              { type: 'bar', name: 'DSCR', x: years, y: dscrs, marker: { color: dscrs.map(d => d >= 1.1 ? '#10b981' : '#ef4444') } },
            ]}
            layout={{
              height: 300,
              margin: { t: 20, b: 40, l: 60, r: 20 },
              yaxis: { title: 'DSCR (x)', range: [0, Math.max(...dscrs) * 1.2] },
              shapes: [
                { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 1.1, y1: 1.1, line: { color: '#ef4444', dash: 'dash', width: 2 } },
              ],
              annotations: [
                { x: 1, y: 1.1, xref: 'paper', yref: 'y', text: 'Min DSCR: 1.10x', showarrow: false, xanchor: 'left', font: { color: '#ef4444', size: 10 } },
              ],
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>
      </div>

      {/* Debt Facilities Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Debt Facilities</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Facility</th>
                <th>Type</th>
                <th style={{ textAlign: 'right' }}>Original</th>
                <th style={{ textAlign: 'right' }}>Outstanding</th>
                <th style={{ textAlign: 'right' }}>Interest Rate</th>
                <th>Maturity</th>
              </tr>
            </thead>
            <tbody>
              {facilities?.map(f => (
                <tr key={f.id}>
                  <td>{f.name}</td>
                  <td>{f.facility_type.replace('_', ' ')}</td>
                  <td className="number">{formatCurrency(f.original_notional)}</td>
                  <td className="number">{formatCurrency(f.current_outstanding)}</td>
                  <td className="number">{f.is_fixed_rate ? `${f.fixed_rate_pct}%` : `${f.floating_reference} + ${f.margin_pct}%`}</td>
                  <td>{f.maturity_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
