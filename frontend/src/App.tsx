import { Routes, Route, NavLink, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getProjects, getProject } from './services/api';
import PortfolioPage from './pages/PortfolioPage';
import ProjectDashboard from './pages/ProjectDashboard';
import FinancialOverview from './pages/FinancialOverview';
import DebtDashboard from './pages/DebtDashboard';
import AssetsDashboard from './pages/AssetsDashboard';
import ProductionDashboard from './pages/ProductionDashboard';
import DividendsDashboard from './pages/DividendsDashboard';
import DataInputPage from './pages/DataInputPage';

function Sidebar() {
  const { projectId } = useParams();
  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: getProjects,
  });

  return (
    <aside className="sidebar">
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--primary)' }}>
          Offshore Wind Hub
        </h2>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          Operational Performance
        </p>
      </div>

      <nav className="nav-section">
        <h3>Portfolio</h3>
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          Portfolio Overview
        </NavLink>
      </nav>

      <nav className="nav-section">
        <h3>Projects</h3>
        {projects?.map((project) => (
          <NavLink
            key={project.id}
            to={`/project/${project.id}`}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            {project.name}
          </NavLink>
        ))}
      </nav>

      {projectId && (
        <nav className="nav-section">
          <h3>Dashboards</h3>
          <NavLink
            to={`/project/${projectId}/financial`}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            Financial Overview
          </NavLink>
          <NavLink
            to={`/project/${projectId}/debt`}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            Debt & Covenants
          </NavLink>
          <NavLink
            to={`/project/${projectId}/assets`}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            Assets & Depreciation
          </NavLink>
          <NavLink
            to={`/project/${projectId}/production`}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            Production & Revenue
          </NavLink>
          <NavLink
            to={`/project/${projectId}/dividends`}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            Dividends & Returns
          </NavLink>
          <NavLink
            to={`/project/${projectId}/input`}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            Data Input
          </NavLink>
        </nav>
      )}
    </aside>
  );
}

function ProjectLayout() {
  const { projectId } = useParams();
  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => getProject(Number(projectId)),
    enabled: !!projectId,
  });

  return (
    <>
      <Sidebar />
      <main className="main-content">
        {project && (
          <div className="header">
            <div>
              <h1>{project.name}</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                {project.location} | {project.installed_capacity_mw} MW | COD: {project.cod_date}
              </p>
            </div>
          </div>
        )}
        <Routes>
          <Route index element={<ProjectDashboard />} />
          <Route path="financial" element={<FinancialOverview />} />
          <Route path="debt" element={<DebtDashboard />} />
          <Route path="assets" element={<AssetsDashboard />} />
          <Route path="production" element={<ProductionDashboard />} />
          <Route path="dividends" element={<DividendsDashboard />} />
          <Route path="input" element={<DataInputPage />} />
        </Routes>
      </main>
    </>
  );
}

function App() {
  return (
    <div className="app-container">
      <Routes>
        <Route
          path="/"
          element={
            <>
              <Sidebar />
              <main className="main-content">
                <PortfolioPage />
              </main>
            </>
          }
        />
        <Route path="/project/:projectId/*" element={<ProjectLayout />} />
      </Routes>
    </div>
  );
}

export default App;
