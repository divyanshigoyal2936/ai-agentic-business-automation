# AI Agentic Business Automation Platform

AI-powered customer support aur refund-processing platform. Multi-agent
architecture, RAG-based policy search, human-in-the-loop approvals,
role-based access control, aur audit logging ke saath banaya gaya hai —
ek fictional electronics-company ke customer-support workflow ko
automate karne ke liye.

## Features

- **Multi-Agent System** — Orchestrator user ke sawaal ko category ke
  hisaab se teen specialized agents (Customer, Policy, Refund) mein
  route karta hai
- **RAG (Retrieval-Augmented Generation)** — Company policies ko chunk
  karke embeddings se semantic-search karta hai, sirf keyword-match nahi
- **Policy-Aware Decisions** — Refund-eligibility order-date aur policy
  ke 7-din window se dynamically calculate hoti hai, hardcoded jawaab
  nahi
- **Human-in-the-Loop Approvals** — Risky actions (refund process
  karna) sirf manager-approval milne ke baad hi execute hoti hain
- **Auth + RBAC** — JWT-based login, do roles (`support_agent`,
  `manager`) ke saath permission-levels
- **Audit Logging** — Har tool-call (safe ya risky) ka record MongoDB
  mein save hota hai; sirf manager role audit-logs dekh sakta hai
- **Evaluation Suite** — Orchestrator ki routing-accuracy ko known
  test-cases ke against measure karta hai

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, LangGraph-style agent loop, Groq API (LLM) |
| Database | MongoDB Atlas |
| RAG | sentence-transformers (multilingual embeddings) |
| Auth | PyJWT, bcrypt |
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Deployment | Docker |

## Project Structure

AI-Agentic-Business-Automation/
│
├── backend/
│   ├── main.py
│   ├── agents.py
│   │
│   ├── core/
│   │   └── database.py
│   │
│   ├── tools/
│   │   ├── customer_tools.py
│   │   ├── order_tools.py
│   │   └── policy_tools.py
│   │
│   ├── company_policies.txt
│   ├── seed_customers.py
│   ├── seed_orders.py
│   ├── seed_users.py
│   ├── run_eval.py
│   ├── eval_tests.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   ├── public/
│   ├── package.json
│   └── package-lock.json
│
├── .gitignore
└── README.md


## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with:

MONGO_URI=your_mongodb_connection_string
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=a_long_random_string


Seed the database:
```bash
python seed_customers.py
python seed_orders.py
python seed_users.py
```

Run the server:
```bash
uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000` — interactive API docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000`.

### Docker (backend alternative)

```bash
cd backend
docker build -t agentic-backend .
docker run -p 8000:8000 --env-file .env agentic-backend
```

### Running the evaluation suite

```bash
cd backend
python run_eval.py
```
Prints a pass/fail report and an accuracy percentage for the
orchestrator's category-routing.

## Test Users

| Email | Password | Role |
|---|---|---|
| agent@company.com | agent123 | support_agent |
| manager@company.com | manager123 | manager |

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | none | Health check |
| POST | `/login` | none | Returns a JWT + role |
| POST | `/chat` | Bearer token | Sends a message through the agent pipeline |
| GET | `/audit-logs` | Bearer token, manager only | Returns all logged tool-calls |

## Architecture

User
│
▼
Next.js Frontend (login + chat)
│ Authorization: Bearer <JWT>
▼
FastAPI /chat
│ verify_token()
▼
Orchestrator (classifies: customer / policy / refund)
│
├─ Customer Agent → customer_tools (MongoDB lookups)
├─ Policy Agent → policy_tools (RAG over company_policies.txt)
└─ Refund Agent → order_tools
├─ check_refund_eligibility (read-only)
└─ process_refund (risky)
├─ role check (manager only)
└─ human approval gate (yes/no)
│
▼
MongoDB + audit_logs_collection (every tool-call is logged)
│
▼
Natural-language response → User


## Known Limitations

- Policy-search (RAG) can occasionally retrieve the wrong chunk for
  complex, indirect Hinglish phrasing — plain English or direct
  phrasing works reliably
- The 7-day refund window is currently hardcoded in `order_tools.py`
  rather than derived dynamically from the policy document
- Manager approval for risky actions happens via a terminal prompt on
  the backend — a real web request blocks until someone responds in
  that terminal; a proper approve/reject UI is a planned improvement
- The JWT is kept only in React state on the frontend, so refreshing
  the page logs the user out; a production version would persist it
  in localStorage or a cookie
- `SECRET_KEY` and other secrets must be supplied via `.env` (or the
  hosting platform's environment-variable settings) — never commit
  `.env` to version control
