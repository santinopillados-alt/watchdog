# Watchdog

**Lightweight real-time observability agent for any server.**

Watchdog is an open-source monitoring system that captures system metrics every second, detects anomalies automatically, and visualizes everything in a live dashboard — no configuration required, no paid plan, no vendor lock-in.

Built to understand how systems like Datadog work at scale, from the ground up.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![React](https://img.shields.io/badge/React-18-61dafb)
![Tests](https://img.shields.io/badge/tests-7%20passing-brightgreen)
![Deploy](https://img.shields.io/badge/deploy-vercel-black)
![Database](https://img.shields.io/badge/database-PostgreSQL-336791)

---

## Live Demo

**[https://watchdog-eosin.vercel.app](https://watchdog-eosin.vercel.app)**

> Note: the dashboard requires the local agent running to display live data.
> The UI, charts, and alert system are fully functional — connect your own agent in 30 seconds.

---

## The Problem

When something breaks in production at 2am, engineers need answers fast:
- Is the CPU spiking?
- Is memory leaking?
- When did it start?

Most observability tools are either too expensive (Datadog starts at $15/host/month) or too complex to set up. Watchdog solves that: clone the repo, run three commands, get answers in seconds.

---

## Architecture

```
Agent (Python)
  → reads CPU + memory every second via psutil
  → sends structured metrics to backend via HTTP POST

Backend (FastAPI)
  → receives and stores metrics in PostgreSQL (Neon)
  → runs anomaly detection on every incoming metric
  → exposes REST API: /metricas, /alertas, /status

Dashboard (React + Recharts)
  → polls backend every 2 seconds
  → renders live CPU and memory charts
  → displays active alerts with timestamps
```

---

## Key Engineering Decisions

### Why PostgreSQL instead of in-memory storage?

Earlier versions stored metrics in a Python list. Simple, but data was lost on every restart — exactly the wrong behavior for an observability tool. The fix is PostgreSQL: metrics survive restarts, historical queries become possible, and multi-agent support is now straightforward to add. The trade-off is a network round-trip on every metric ingestion. At one metric per second, this is negligible.

### Why Neon for the database?

Neon is a serverless PostgreSQL provider with a generous free tier and no cold-start penalty for always-on connections. The alternative was a self-hosted PostgreSQL instance, which adds operational overhead without benefit for a single-agent setup. Neon provides the same wire protocol as standard PostgreSQL — swapping providers requires changing one environment variable.

### Why polling instead of WebSockets?

For a single-agent setup, polling every 2 seconds is simpler to operate and debug — no persistent connection to manage, no reconnection logic, no client state to synchronize. The trade-off is 2 seconds of latency vs real-time push. For a multi-agent production system serving dozens of dashboards simultaneously, WebSockets or Server-Sent Events would be the correct choice. At this scale, the operational simplicity of polling outweighs the latency cost.

### Why configurable thresholds?

```python
CPU_THRESHOLD = 80
MEMORIA_THRESHOLD = 90
```

Hard-coded thresholds don't work in production. A batch processing server running at 95% CPU is normal. The same reading on an API server is critical. Thresholds are defined at the top of `main.py` so any team can adjust them without touching business logic. The next step is exposing thresholds as environment variables so they can be set at deploy time without modifying code.

### Why psutil instead of a system call?

`psutil` provides a cross-platform abstraction over OS-level metrics. A raw `subprocess` call to read `/proc/stat` on Linux would be faster but breaks on macOS and Windows. For an observability tool that should run anywhere, portability matters more than microseconds of overhead on the metric collection side.

---

## Known Limitations

### No deduplication on alerts

Currently, if CPU stays above threshold for 60 seconds, Watchdog generates 60 alerts — one per second. This produces alert fatigue, which is the exact problem that makes on-call rotations miserable. The correct behavior is to fire once when the threshold is crossed, then suppress until the metric recovers. This requires stateful alert tracking, which is the first item on the roadmap.

### Single-agent only

The backend assumes one agent reporting metrics. A second agent running on a different server would merge its metrics into the same list with no way to distinguish the source. Multi-agent support requires a `host` field on each metric and per-host queries — straightforward to add, not yet implemented.

---

## What Happens When It Fails?

| Failure | Behavior | Impact |
|---|---|---|
| Agent can't reach backend | HTTP request fails silently, agent retries next second | At most 1 second of missing data |
| Backend restarts | Metrics persist in PostgreSQL — no data loss | Zero impact on historical data |
| Dashboard loses connection | Shows last known values until reconnection | Stale data displayed without warning to user |
| CPU spike detected | Alert generated with exact timestamp and value | Alert storm if spike persists — see Known Limitations |
| Threshold set too low | False positives flood the alerts panel | Operational noise — adjust CPU_THRESHOLD |
| Database connection lost | Backend returns 500 until connection recovers | Metrics lost during outage window |

---

## Local Setup

**Prerequisites:** Python 3.10+, Node.js 18+

```bash
git clone https://github.com/santinopillados-alt/watchdog
cd watchdog

# Create .env file
echo "DATABASE_URL=your_postgresql_connection_string" > .env

# Terminal 1 — start backend
pip install fastapi uvicorn psutil requests psycopg2-binary python-dotenv
uvicorn main:app --reload

# Terminal 2 — start agent
python agent.py

# Terminal 3 — start dashboard
cd dashboard
npm install
npm run dev
```

- Dashboard: http://localhost:5173
- API docs: http://localhost:8000/docs

> For the database, any PostgreSQL provider works. [Neon](https://neon.tech) offers a free tier with no credit card required.

---

## API Reference

```
POST /metricas?cpu=45.2&memoria=87.1&timestamp=1234567890
→ Receives a metric. Runs anomaly detection. Persists to PostgreSQL. Returns alert count.

GET /metricas
→ Returns last 100 stored metrics from the database.

GET /alertas
→ Returns all triggered alerts with timestamps and values.

GET /status
→ Returns current CPU, memory, measurement count, and system state.
```

---

## Running Tests

```bash
pip install pytest httpx
pytest test_main.py -v
```

7 tests covering: metric ingestion, anomaly detection at both thresholds,
status endpoint with and without data, and alert retrieval.

---

## Project Structure

```
watchdog/
├── main.py           # FastAPI backend — ingestion, anomaly detection, PostgreSQL, API
├── agent.py          # Python agent — captures system metrics, sends to backend
├── test_main.py      # 7 pytest tests — covers all endpoints and edge cases
├── .env              # Database connection string (not committed)
├── dashboard/
│   └── src/
│       └── App.jsx   # React dashboard — live charts, status cards, alert feed
└── README.md
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Agent | Python + psutil | Cross-platform, minimal dependencies, no root required |
| Backend | FastAPI | Auto-generated OpenAPI docs, async-ready, Pydantic validation |
| Database | PostgreSQL (Neon) | Persistent storage, survives restarts, standard wire protocol |
| Dashboard | React 18 + Recharts | Lightweight, no heavy dependencies, no build complexity |
| Testing | pytest + httpx | Standard Python testing stack, readable assertions |
| CI | GitHub Actions | Runs tests on every push, provides the green check on commits |

---

## Roadmap

- [x] PostgreSQL persistence — survive restarts, query historical data (Neon)
- [ ] Stateful alert tracking — fire once, suppress until recovery
- [ ] Multi-agent support — monitor multiple servers from one dashboard  
- [ ] WebSocket streaming — push updates instead of polling
- [ ] Slack/email alerting — notify teams when thresholds are exceeded
- [ ] Docker Compose — single command to start everything
- [ ] Threshold configuration via environment variables

---

## Why I Built This

I built Watchdog to understand observability from the inside — how metrics flow from a running process to a dashboard, how anomaly detection works at the data layer, and what trade-offs engineers make when designing systems like Datadog.

The result is a minimal but complete observability pipeline: agent → ingestion → detection → visualization. Every component is intentionally simple so the architecture is readable. Every limitation is documented so the next step is always clear.

The Known Limitations section is not an apology. It is an engineering decision log.

---

## Author

**Santino Coronel** — self-taught backend engineer, Córdoba, Argentina.  
Seeking a junior engineering role in Portugal (available from mid-2027).

- GitHub: [santinopillados-alt](https://github.com/santinopillados-alt)
- See also: [ObserveIQ](https://github.com/santinopillados-alt/observeiq) · [Global-Relay Sync](https://github.com/santinopillados-alt/global-relay-sync) · [Log-Lens](https://github.com/santinopillados-alt/log-lens)