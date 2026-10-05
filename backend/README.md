# AI Agentic Business Automation Platform

AI-powered customer support aur refund-processing platform. Multi-agent 
architecture, RAG-based policy search, human-in-the-loop approvals, 
role-based access control, aur audit logging ke saath.

## Features

- **Multi-Agent System**: Alag-alag specialized agents (customer, policy, refund)
- **RAG**: Company policies ko embeddings se search karta hai
- **Policy-Aware Decisions**: Refund-eligibility ko order-date aur policy-rules se calculate karta hai
- **Human-in-the-Loop**: Risky actions (refund-processing) manager-approval ke bina execute nahi hoti
- **Auth + RBAC**: JWT-based login, support_agent aur manager roles
- **Audit Logs**: Har tool-call ka record, sirf manager dekh sakta hai

## Tech Stack

- Backend: FastAPI, LangGraph, Groq API, MongoDB
- Frontend: Next.js, TypeScript, Tailwind CSS
- Auth: JWT (PyJWT), bcrypt
- Deployment: Docker

## Setup

### Backend
1. `pip install -r requirements.txt`
2. `.env` file banao, isme daalo: `MONGO_URI`, `GROQ_API_KEY`, `SECRET_KEY`
3. `python seed_customers.py`, `python seed_orders.py`, `python seed_users.py` chalao
4. `uvicorn main:app --reload`

### Frontend
1. `cd agentic-dashboard`
2. `npm install`
3. `npm run dev`

### Docker (Alternative)
1. `docker build -t agentic-backend .`
2. `docker run -p 8000:8000 --env-file .env agentic-backend`

## Test Users

| Email | Password | Role |
|---|---|---|
| agent@company.com | agent123 | support_agent |
| manager@company.com | manager123 | manager |

## Architecture

User -> Next.js Frontend -> FastAPI (/chat) -> Orchestrator -> 
Specialist Agent -> Tool Execution (+ RBAC + Approval Gate) -> 
MongoDB / Policy Search -> Response