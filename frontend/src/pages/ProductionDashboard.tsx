import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Plot from 'react-plotly.js';
import { getProjectKPIs } from '../services/api';

export default function ProductionDashboard() {
  const { projectId } = useParams();
  const { data: kpis } = useQuery({
    queryKey: ['projectKPIs', projectId],
    queryFn: () => getProjectKPIs(Number(projectId)),
    enabled: !!projectId,
  });

  if (!kpis) return <div>Loading...</div>;

  const periodKpis = kpis.period_kpis || [];
  const years = periodKpis.map(p => p.period_end.slice(0, 4)).reverse();
  const capacityFactors = periodKpis.map(p => p.capacity_factor_pct || 0).reverse();
  const availabilities = periodKpis.map(p => p.availability_pct || 0).reverse();
  const revenuePerMwh = periodKpis.map(p => p.revenue_per_mwh || 0).reverse();
  const costPerMwh = periodKpis.map(p => p.cost_per_mwh || 0).reverse();
  const revenues = periodKpis.map(p => (p.revenue || 0) / 1000).reverse();

  return (
    <div>
      {/* KPI Tiles */}
      <div className="kpi-grid">
        <div className="kpi-tile">
          <div className="kpi-label">Capacity Factor</div>
          <div className="kpi-value">{(periodKpis[0]?.capacity_factor_pct || 0).toFixed(1)}%</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Availability (PBA)</div>
          <div className="kpi-value">{(periodKpis[0]?.availability_pct || 0).toFixed(1)}%</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Revenue / MWh</div>
          <div className="kpi-value">£{(periodKpis[0]?.revenue_per_mwh || 0).toFixed(0)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Cost / MWh</div>
          <div className="kpi-value">£{(periodKpis[0]?.cost_per_mwh || 0).toFixed(0)}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Capacity Factor & Availability */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Capacity Factor & Availability</h3>
          </div>
          <Plot
            data={[
              { type: 'scatter', mode: 'lines+markers', name: 'Capacity Factor', x: years, y: capacityFactors, line: { color: '#3b82f6' } },
              { type: 'scatter', mode: 'lines+markers', name: 'Availability', x: years, y: availabilities, line: { color: '#10b981' } },
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

        {/* Unit Economics */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Unit Economics (£/MWh)</h3>
          </div>
          <Plot
            data={[
              { type: 'bar', name: 'Revenue/MWh', x: years, y: revenuePerMwh, marker: { color: '#3b82f6' } },
              { type: 'bar', name: 'Cost/MWh', x: years, y: costPerMwh, marker: { color: '#ef4444' } },
            ]}
            layout={{
              height: 300,
              margin: { t: 20, b: 40, l: 60, r: 20 },
              barmode: 'group',
              legend: { orientation: 'h', y: 1.1 },
              yaxis: { title: '£/MWh' },
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>
      </div>

      {/* Revenue Waterfall (simplified) */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Revenue Over Time (£m)</h3>
        </div>
        <Plot
          data={[
            { type: 'bar', name: 'Revenue', x: years, y: revenues, marker: { color: '#3b82f6' } },
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
  );
}
