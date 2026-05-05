# Mortgage Full-Stack Project on Azure

This repository now contains an end-to-end mortgage quote platform with:

- **Backend**: FastAPI + SQLite API for mortgage quote calculations and quote history.
- **Frontend**: React + Vite single-page app for entering borrower data and viewing results.
- **Infrastructure**: Azure Bicep template for deploying Linux App Services for API and web.

## Architecture

- `backend/main.py`: API endpoints (`/health`, `/api/mortgage/quote`, `/api/mortgage/quotes`).
- `frontend/src/main.jsx`: Web form, API integration, and quote history UI.
- `infra/main.bicep`: Azure App Service Plan + two Web Apps.
- `docker-compose.yml`: Local end-to-end development stack.

## Run locally

```bash
docker compose up
```

Then open:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/docs`

## Deploy to Azure

1. Create resource group:
   ```bash
   az group create -n rg-mortgage-demo -l eastus
   ```
2. Deploy infrastructure:
   ```bash
   az deployment group create -g rg-mortgage-demo -f infra/main.bicep
   ```
3. Deploy backend and frontend code to their respective App Services (zip deploy or GitHub Actions).

## Notes

- This sample uses SQLite for simplicity; for production on Azure, switch to Azure SQL or PostgreSQL.
- Add Azure Key Vault for secrets and CI/CD via GitHub Actions for complete production readiness.
