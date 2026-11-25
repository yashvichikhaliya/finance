# FinanceFlow

A full-stack personal finance tracker using Streamlit, FastAPI, SQLAlchemy and PostgreSQL-compatible storage.

## Local run

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
# Set SECRET_KEY for non-local usage. SQLite is the default.
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### Frontend (new terminal)
```bash
cd frontend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
# Windows PowerShell: $env:API_URL="http://localhost:8000"
# macOS/Linux: export API_URL="http://localhost:8000"
streamlit run app.py
```
Frontend: http://localhost:8501

## Deploy backend on Render
- Create a Render Web Service from this repository.
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `DATABASE_URL` to the Render PostgreSQL internal connection string.
- Set `SECRET_KEY` to a long random secret.
- Set `FRONTEND_ORIGINS` to your Streamlit service URL (or local origin for local use).

## Deploy Streamlit frontend on Render
- Create a second Render Web Service from the same repository.
- Root Directory: `frontend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`
- Environment variable: `API_URL=https://YOUR-BACKEND.onrender.com`

Vercel is not a native host for Streamlit Python apps. For a Vercel frontend, replace Streamlit with React/Next.js and configure it to call the Render backend.
