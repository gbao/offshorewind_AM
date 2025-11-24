import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Plot from 'react-plotly.js';
import { getProjectKPIs, getProjectPeriods, getFinancialStatement } from '../services/api';

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-';
  if (Math.abs(value) >= 1000000) return `£${(value / 1000000).toFixed(1)}m`;
  return `£${(value / 1000).toFixed(0)}k`;
}

export default function AssetsDashboard() {
  const { projectId } = useParams();
  const { data: periods } = useQuery({
    queryKey: ['periods', projectId],
    queryFn: () => getProjectPeriods(Number(projectId)),
    enabled: !!projectId,
  });

  // Get latest period financial statement
  const latestPeriodId = periods?.[0]?.id;
  const { data: latestFS } = useQuery({
    queryKey: ['financialStatement', latestPeriodId],
    queryFn: () => getFinancialStatement(latestPeriodId!),
    enabled: !!latestPeriodId,
  });

  if (!periods || !latestFS) return <div>Loading...</div>;

  const bs = latestFS.balance_sheet;

  // Asset breakdown for pie chart
  const windFarmNBV = (bs?.wind_farm_assets_cost || 0) - (bs?.wind_farm_assets_depreciation || 0);
  const transmissionNBV = (bs?.transmission_assets_cost || 0) - (bs?.transmission_assets_depreciation || 0);
  const decomNBV = (bs?.decommissioning_asset_cost || 0) - (bs?.decommissioning_asset_depreciation || 0);

  return (
    <div>
      {/* KPI Tiles */}
      <div className="kpi-grid">
        <div className="kpi-tile">
          <div className="kpi-label">Total Fixed Assets (NBV)</div>
          <div className="kpi-value">{formatCurrency(bs?.total_fixed_assets)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Wind Farm Assets (NBV)</div>
          <div className="kpi-value">{formatCurrency(windFarmNBV)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Decommissioning Asset</div>
          <div className="kpi-value">{formatCurrency(decomNBV)}</div>
        </div>
        <div className="kpi-tile">
          <div className="kpi-label">Decommissioning Provision</div>
          <div className="kpi-value">{formatCurrency(bs?.decommissioning_provision)}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Asset Breakdown Pie */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Asset Breakdown by Class</h3>
          </div>
          <Plot
            data={[
              {
                type: 'pie',
                values: [windFarmNBV / 1000, transmissionNBV / 1000, decomNBV / 1000],
                labels: ['Wind Farm Assets', 'Transmission Assets', 'Decommissioning'],
                marker: { colors: ['#3b82f6', '#10b981', '#f59e0b'] },
                textinfo: 'label+percent',
                hovertemplate: '%{label}: £%{value:.0f}m<extra></extra>',
              },
            ]}
            layout={{
              height: 300,
              margin: { t: 20, b: 20, l: 20, r: 20 },
              showlegend: false,
            }}
            config={{ displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        {/* Balance Sheet Summary */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Balance Sheet Summary</h3>
          </div>
          <div className="table-container">
            <table>
              <tbody>
                <tr><td><strong>Fixed Assets</strong></td><td className="number">{formatCurrency(bs?.total_fixed_assets)}</td></tr>
                <tr><td>Current Assets</td><td className="number">{formatCurrency(bs?.total_current_assets)}</td></tr>
                <tr><td>Current Liabilities</td><td className="number">({formatCurrency(Math.abs(bs?.total_current_liabilities || 0))})</td></tr>
                <tr><td><strong>Net Current Assets</strong></td><td className="number">{formatCurrency((bs?.total_current_assets || 0) - (bs?.total_current_liabilities || 0))}</td></tr>
                <tr><td>Non-Current Liabilities</td><td className="number">({formatCurrency(Math.abs(bs?.total_non_current_liabilities || 0))})</td></tr>
                <tr style={{ borderTop: '2px solid var(--border)' }}><td><strong>Net Assets</strong></td><td className="number"><strong>{formatCurrency(bs?.net_assets)}</strong></td></tr>
                <tr><td><strong>Equity</strong></td><td className="number"><strong>{formatCurrency(bs?.total_equity)}</strong></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
