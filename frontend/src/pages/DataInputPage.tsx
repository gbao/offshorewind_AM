import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getProjectPeriods, createPeriod, saveFinancialStatement, saveProductionData, parseText } from '../services/api';

export default function DataInputPage() {
  const { projectId } = useParams();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'forms' | 'paste'>('forms');
  const [selectedPeriodId, setSelectedPeriodId] = useState<number | null>(null);
  const [pasteText, setPasteText] = useState('');
  const [parsedData, setParsedData] = useState<any>(null);

  // Form state
  const [incomeData, setIncomeData] = useState({
    turnover: '', cost_of_sales: '', administrative_expenses: '', depreciation: '',
    interest_receivable: '', interest_payable: '', current_tax: '', deferred_tax: '',
  });
  const [productionData, setProductionData] = useState({
    net_export_mwh: '', availability_pct: '', p50_generation_mwh: '', period_hours: '8760',
  });

  const { data: periods } = useQuery({
    queryKey: ['periods', projectId],
    queryFn: () => getProjectPeriods(Number(projectId)),
    enabled: !!projectId,
  });

  const createPeriodMutation = useMutation({
    mutationFn: (data: any) => createPeriod(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['periods', projectId] }),
  });

  const saveFinancialMutation = useMutation({
    mutationFn: ({ periodId, data }: any) => saveFinancialStatement(periodId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projectKPIs', projectId] }),
  });

  const saveProductionMutation = useMutation({
    mutationFn: ({ periodId, data }: any) => saveProductionData(periodId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projectKPIs', projectId] }),
  });

  const handleCreatePeriod = () => {
    const year = prompt('Enter year (e.g., 2024):');
    if (year) {
      createPeriodMutation.mutate({
        project_id: Number(projectId),
        period_start: `${year}-01-01`,
        period_end: `${year}-12-31`,
        period_type: 'annual',
        is_audited: false,
      });
    }
  };

  const handleSaveIncome = () => {
    if (!selectedPeriodId) return alert('Select a period first');
    const data = {
      source_type: 'management',
      income_statement: Object.fromEntries(
        Object.entries(incomeData).map(([k, v]) => [k, v ? parseFloat(v) : null])
      ),
    };
    saveFinancialMutation.mutate({ periodId: selectedPeriodId, data });
    alert('Income statement saved!');
  };

  const handleSaveProduction = () => {
    if (!selectedPeriodId) return alert('Select a period first');
    const data = Object.fromEntries(
      Object.entries(productionData).map(([k, v]) => [k, v ? parseFloat(v) : null])
    );
    saveProductionMutation.mutate({ periodId: selectedPeriodId, data });
    alert('Production data saved!');
  };

  const handleParseText = async () => {
    if (!pasteText.trim()) return;
    try {
      const result = await parseText(pasteText);
      setParsedData(result);
    } catch (e) {
      alert('Error parsing text');
    }
  };

  return (
    <div>
      {/* Tabs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <button className={`btn ${activeTab === 'forms' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('forms')}>
          Structured Forms
        </button>
        <button className={`btn ${activeTab === 'paste' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('paste')}>
          Paste / Upload
        </button>
      </div>

      {/* Period Selector */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <h3 className="card-title">Select Period</h3>
          <button className="btn btn-secondary" onClick={handleCreatePeriod}>+ Add Period</button>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {periods?.map(p => (
            <button
              key={p.id}
              className={`btn ${selectedPeriodId === p.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSelectedPeriodId(p.id)}
            >
              {p.period_end.slice(0, 4)}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'forms' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          {/* Income Statement Form */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Income Statement (£'000)</h3>
              <button className="btn btn-primary" onClick={handleSaveIncome}>Save</button>
            </div>
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              {[
                ['turnover', 'Turnover / Revenue'],
                ['cost_of_sales', 'Cost of Sales'],
                ['administrative_expenses', 'Administrative Expenses'],
                ['depreciation', 'Depreciation'],
                ['interest_receivable', 'Interest Receivable'],
                ['interest_payable', 'Interest Payable'],
                ['current_tax', 'Current Tax'],
                ['deferred_tax', 'Deferred Tax'],
              ].map(([key, label]) => (
                <div className="form-group" key={key} style={{ marginBottom: 0 }}>
                  <label className="form-label">{label}</label>
                  <input
                    type="number"
                    className="form-input"
                    value={(incomeData as any)[key]}
                    onChange={(e) => setIncomeData({ ...incomeData, [key]: e.target.value })}
                    placeholder="0"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Production Data Form */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Production Data</h3>
              <button className="btn btn-primary" onClick={handleSaveProduction}>Save</button>
            </div>
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              {[
                ['net_export_mwh', 'Net Generation (MWh)'],
                ['availability_pct', 'Availability (%)'],
                ['p50_generation_mwh', 'P50 Generation (MWh)'],
                ['period_hours', 'Period Hours'],
              ].map(([key, label]) => (
                <div className="form-group" key={key} style={{ marginBottom: 0 }}>
                  <label className="form-label">{label}</label>
                  <input
                    type="number"
                    className="form-input"
                    value={(productionData as any)[key]}
                    onChange={(e) => setProductionData({ ...productionData, [key]: e.target.value })}
                    placeholder="0"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'paste' && (
        <div>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Paste Text from Financial Statements</h3>
              <button className="btn btn-primary" onClick={handleParseText}>Parse</button>
            </div>
            <textarea
              style={{ width: '100%', height: '200px', padding: '0.75rem', border: '1px solid var(--border)', borderRadius: '0.375rem', fontFamily: 'monospace', fontSize: '0.875rem' }}
              placeholder="Paste text extracted from annual report, loan compliance certificate, or production report here..."
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
            />
          </div>

          {parsedData && (
            <div className="card" style={{ marginTop: '1.5rem' }}>
              <div className="card-header">
                <h3 className="card-title">Parsed Fields</h3>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                {parsedData.income_statement_fields?.length > 0 && (
                  <div>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Income Statement</h4>
                    {parsedData.income_statement_fields.map((f: any, i: number) => (
                      <div key={i} style={{ fontSize: '0.75rem', padding: '0.25rem', background: 'var(--background)', marginBottom: '0.25rem', borderRadius: '0.25rem' }}>
                        <strong>{f.mapped_field}</strong>: {f.extracted_value}
                      </div>
                    ))}
                  </div>
                )}
                {parsedData.production_fields?.length > 0 && (
                  <div>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Production</h4>
                    {parsedData.production_fields.map((f: any, i: number) => (
                      <div key={i} style={{ fontSize: '0.75rem', padding: '0.25rem', background: 'var(--background)', marginBottom: '0.25rem', borderRadius: '0.25rem' }}>
                        <strong>{f.mapped_field}</strong>: {f.extracted_value}
                      </div>
                    ))}
                  </div>
                )}
                {parsedData.unmatched_fields?.length > 0 && (
                  <div style={{ gridColumn: '1 / -1' }}>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--warning)' }}>Unmatched (Needs Review)</h4>
                    {parsedData.unmatched_fields.map((f: any, i: number) => (
                      <div key={i} style={{ fontSize: '0.75rem', padding: '0.25rem', background: '#fef3c7', marginBottom: '0.25rem', borderRadius: '0.25rem' }}>
                        {f.original_text}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
