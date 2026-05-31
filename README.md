# Watchdog

**Lightweight real-time observability agent for any server.**

Watchdog is an open-source monitoring system that captures system metrics every second, detects anomalies automatically, and visualizes everything in a live dashboard — no configuration required, no paid plan, no vendor lock-in.

Built to understand how systems like Datadog work at scale, from the ground up.

→ **[Live Demo](https://watchdog-demo.vercel.app)** · [Backend API docs](https://watchdog-api.railway.app/docs)

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![React](https://img.shields.io/badge/React-18-61dafb)

---

## The Problem

When something breaks in production at 2am, engineers need answers fast:
- Is the CPU spiking?
- Is memory leaking?
- When did it start?

Most observability tools are either too expensive (Datadog starts at $15/host/month) or too complex to set up. Watchdog solves that: install in one command, get answers in seconds.

---

## Architecture

```
Agent (Python)
  → reads CPU + memory every second via psutil
  → sends structured metrics to backend via HTTP POST

Backend (FastAPI)
  → receives and stores metrics in memory
  → runs anomaly detection on every incoming metric
  → exposes REST API: /metrics, /alerts, /status

Dashboard (React + Recharts)
  → polls backend every 2 seconds
  → renders live CPU and memory charts
  → displays active alerts with timestamps
```

---

## Key Engineering Decisions

### Why polling instead of WebSockets?

For a single-agent setup, polling every 2 seconds is simpler to operate and debug — no persistent connection to manage, no reconnection logic needed. The trade-off is 2 seconds of latency vs real-time push. For a multi-agent production system, WebSockets or Server-Sent Events would be the correct choice.

### Why in-memory storage instead of a database?

This version stores metrics in a Python list intentionally. The goal is to demonstrate the core observability pipeline clearly — adding PostgreSQL would be the next step for persistence across restarts, historical queries, and multi-agent support.

### Why configurable thresholds?

```python
CPU_THRESHOLD = 80
MEMORIA_THRESHOLD = 90
```

Hard-coded thresholds don't work in production. A batch processing server running at 95% CPU is normal; the same reading on an API server is critical. Thresholds are defined at the top of `main.py` so any team can adjust them without touching business logic.

---

## What Happens When It Fails?

| Failure | Behavior |
|---|---|
| Agent can't reach backend | HTTP request fails silently, agent continues capturing |
| Backend restarts | Metrics in memory are lost — agent resumes sending automatically |
| Dashboard loses connection | Shows last known values until connection restores |
| CPU spike detected | Alert generated with exact timestamp and value |

---

## Local Setup

**Prerequisites:** Python 3.10+, Node.js 18+

```bash
git clone https://github.com/santinopillados-alt/watchdog
cd watchdog

# Start backend
pip install fastapi uvicorn psutil requests
uvicorn main:app --reload

# Start agent (new terminal)
python agent.py

# Start dashboard (new terminal)
cd dashboard
npm install
npm run dev
```

- Dashboard: http://localhost:5173
- API docs: http://localhost:8000/docs

---

## API Reference

```
POST /metricas?cpu=45.2&memoria=87.1&timestamp=1234567890
→ Receives a metric from the agent. Runs anomaly detection.

GET /metricas
→ Returns all stored metrics.

GET /alertas
→ Returns all triggered alerts with timestamps.

GET /status
→ Returns current CPU, memory, total measurements, and system state.
```

---

## Project Structure

```
watchdog/
├── main.py          # FastAPI backend — metrics ingestion, anomaly detection, API
├── agent.py         # Python agent — captures system metrics, sends to backend
├── dashboard/
│   └── src/
│       └── App.jsx  # React dashboard — live charts, status cards, alert feed
└── README.md
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Agent | Python + psutil | Cross-platform, minimal dependencies |
| Backend | FastAPI | Auto-generated OpenAPI docs, fast, async-ready |
| Dashboard | React 18 + Recharts | Lightweight, no heavy dependencies |
| Deployment | Railway + Vercel | Zero-config, free tier |

---

## What's Next

- [ ] PostgreSQL persistence — survive restarts, query historical data
- [ ] Multi-agent support — monitor multiple servers from one dashboard
- [ ] WebSocket streaming — push updates instead of polling
- [ ] Slack/email alerting — notify teams when thresholds are exceeded
- [ ] Docker Compose — single command to start everything

---

## Why I Built This

I built Watchdog to understand observability from the inside — how metrics flow from a running process to a dashboard, how anomaly detection works at the data layer, and what trade-offs engineers make when designing systems like Datadog.

The result is a minimal but complete observability pipeline: agent → ingestion → detection → visualization. Every component is replaceable and the architecture scales.

---

## Author

**Santino Coronel** — self-taught backend engineer, Córdoba, Argentina.

Seeking a junior engineering role in Portugal (available from March 2027).

- GitHub: [santinopillados-alt](https://github.com/santinopillados-alt)
- See also: [ObserveIQ](https://github.com/santinopillados-alt/observeiq) · [Global-Relay Sync](https://github.com/santinopillados-alt/global-relay-sync) · [Log-Lens](https://github.com/santinopillados-alt/log-lens)
