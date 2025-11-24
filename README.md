# Offshore Wind Operational Performance Hub

A comprehensive web application for monitoring operational offshore wind projects. Built for directors, shareholders, and asset managers to track financial performance, debt repayment, production metrics, and portfolio-level comparisons.

## Features

### Financial Monitoring
- **Income Statement**: Track turnover, EBITDA, operating profit, net profit with automatic calculations
- **Balance Sheet**: Monitor assets, liabilities, equity with net debt calculations
- **Cash Flow**: Operating, investing, and financing cash flows with CFADS tracking

### Debt Management
- **Facility Tracking**: Term loans, PP Notes, shareholder loans
- **DSCR Monitoring**: Debt Service Coverage Ratio with covenant threshold alerts
- **Interest Rate Swaps**: Fair value and hedge positions
- **Debt Movements**: Track drawdowns, repayments, and balances over time

### Production & Operations
- **Capacity Factor**: Actual vs P50 generation performance
- **Availability**: Track operational availability (PBA)
- **Unit Economics**: Revenue per MWh, cost per MWh

### Portfolio View
- **Multi-Project Comparison**: Side-by-side KPI comparison
- **Scatter Analysis**: Risk-return visualization across portfolio
- **Aggregated Metrics**: Total capacity, generation, dividends

### Data Input
- **Structured Forms**: Enter financial statements via web forms
- **Paste/Upload**: Paste text from PDFs/reports with intelligent field mapping
- **Multiple Sources**: Support for audited accounts, management accounts, loan compliance certificates

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Frontend**: React 18, TypeScript, Vite
- **Database**: PostgreSQL 15
- **Charts**: Plotly.js
- **Styling**: Custom CSS (no framework dependency)

## Project Structure

```
offshorewind_AM/
├── backend/
│   ├── app/
│   │   ├── analytics/       # Financial calculations (EBITDA, DSCR, etc.)
│   │   ├── api/             # FastAPI routes
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Text parsing service
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   └── main.py          # FastAPI app
│   ├── tests/               # Pytest tests
│   ├── seed_demo_data.py    # Demo data generator
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/           # Dashboard pages
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start with Docker

1. **Clone and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Seed demo data** (in a new terminal):
   ```bash
   docker-compose exec backend python seed_demo_data.py
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set database URL (adjust as needed)
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/offshore_wind

# Create database
createdb offshore_wind

# Run the server (tables auto-create on startup)
uvicorn app.main:app --reload

# Seed demo data
python seed_demo_data.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## API Endpoints

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create a project
- `GET /api/projects/{id}` - Get project details
- `GET /api/projects/{id}/kpis` - Get calculated KPIs for all periods

### Periods
- `GET /api/projects/{id}/periods` - List periods for a project
- `POST /api/periods` - Create a reporting period

### Financial Data
- `POST /api/periods/{id}/financial-statements` - Save financial statement set
- `GET /api/periods/{id}/financial-statements` - Get financial statements with calculations
- `POST /api/periods/{id}/production-data` - Save production data
- `GET /api/periods/{id}/production-data` - Get production data with KPIs

### Debt
- `POST /api/projects/{id}/debt-facilities` - Create debt facility
- `GET /api/projects/{id}/debt-facilities` - List debt facilities
- `POST /api/debt-facilities/{id}/movements` - Record debt movement

### Analytics
- `GET /api/analytics/portfolio-summary` - Get portfolio-level KPIs
- `POST /api/parse/text` - Parse pasted text into structured fields

## Key Financial Calculations

### EBITDA
```
EBITDA = Operating Profit + Depreciation
Operating Profit = Gross Profit - Administrative Expenses - Other Operating Income
Gross Profit = Turnover - Cost of Sales
```

### DSCR (Debt Service Coverage Ratio)
```
DSCR = CFADS / (Principal Repaid + Interest Payable)
```
Typical covenant threshold: 1.10x

### Net Debt
```
Net Debt = Total Debt - Cash
Total Debt = Short-term Loans + Long-term Loans + Bonds + Shareholder Loans + Lease Liabilities
```

### Capacity Factor
```
Capacity Factor = Net Generation / (Installed Capacity × Period Hours)
```

## Demo Data

The seed script creates two fictitious UK offshore wind projects:

1. **Greater Gale Offshore Wind** (450 MW)
   - COD: 2018
   - 5 years of operational data (2019-2023)
   - PP Notes + Term Loan facility

2. **Horizon Bay Wind Farm** (320 MW)
   - COD: 2019
   - 5 years of operational data (2019-2023)
   - Term Loan + Shareholder Loan

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/offshore_wind` |
| `VITE_API_BASE_URL` | Backend API URL (frontend) | `http://localhost:8000` |

## License

Internal use only.
