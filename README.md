# QueueStorm Ticket Sorter
**bKash × SUST CSE Carnival 2026 — Codex Community Hackathon | Mock Preliminary**

A lightweight REST API that classifies customer support tickets for a digital finance platform.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| POST | `/sort-ticket` | Classify a customer support ticket |

---

## Request Example

```json
POST /sort-ticket
{
  "ticket_id": "T-001",
  "channel": "app",
  "locale": "en",
  "message": "I sent 5000 taka to a wrong number this morning, please help me get it back"
}
```

## Response Example

```json
{
  "ticket_id": "T-001",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending money to an unintended recipient and is requesting a transfer reversal.",
  "human_review_required": true,
  "confidence": 0.88
}
```

---

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Server starts at `http://localhost:5000`

---

## Deploy on Render (Free)

1. Push this repo to GitHub (make it public)
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set these:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
5. Click Deploy
6. Your live URL will be something like `https://yourapp.onrender.com`

---

## LLM Used
No — this solution uses rule-based keyword matching only.

---

## Classification Logic

| Case Type | Keywords | Severity | Department |
|-----------|----------|----------|------------|
| wrong_transfer | "wrong number", "wrong account" | high | dispute_resolution |
| payment_failed | "payment failed", "balance deducted" | high | payments_ops |
| refund_request | "refund", "money back" | low | customer_support |
| phishing_or_social_engineering | "otp", "pin", "someone called" | critical | fraud_risk |
| other | anything else | low | customer_support |

`human_review_required` is set to `true` for phishing/critical cases and wrong transfers.
