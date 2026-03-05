# Claude Code Usage Analytics Platform

A Streamlit-based analytics platform to visualize Claude Code usage telemetry. Tracks token consumption, tool usage, and other metrics through an interactive dashboard backed by PostgreSQL.

---

## Features

- **Data Processing** — Ingest, clean, and structure telemetry data into PostgreSQL
- **Analytics & Insights** — Token usage trends, peak activity times, and common code generation behaviors
- **Visualization** — Interactive charts (stacked bar, line, pie) powered by Streamlit
- **Dockerized** — Simple deployment with Docker Compose

---

## Requirements

- Docker ≥ 20.10
- Docker Compose ≥ 2.0

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/LilitBaghdasaryan/Claude-Code-Usage-Analytics-Platform.git
cd Claude-Code-Usage-Analytics-Platform
```

### 2. Configure environment variables

Copy the example env file and **edit it manually** before starting any services:

```bash
cp .env.example .env
```

Open `.env` in your editor and fill in the required values (database credentials, ports, etc.).


### 3. Build and start services

```bash
docker-compose up --build
```

> The first build may take several minutes. This will start both the PostgreSQL database (`telemetry_db`) and the Streamlit dashboard (`dashboard`) containers.


### 4. Open the dashboard

Navigate to [http://localhost:8501](http://localhost:8501) in your browser.


### 5. Stop the services

```bash
docker-compose down
```

---

## Project Structure

```
.
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── config.py
├── requirements.txt
├── .env                    # Environment variables (edit manually — not committed)
├── .env.example            # Template for environment variables
├── dashboard/              # Streamlit dashboard
│   ├── pages/              # Multi-page app screens
│   │   ├── 1_Token_Usage.py
│   │   ├── 2_Cost_Analysis.py
│   │   ├── 3_User_Analysis.py
│   │   └── 4_Events_and_Tools.py
│   ├── Dashboard.py        # Main dashboard entry point
│   ├── database.py         # Database connection logic
│   ├── queries.py          # SQL queries
│   └── utils.py            # Shared utilities
├── data/
│   ├── employees.csv
│   └── telemetry_logs.jsonl
├── db/                     # Database initialization scripts
│   ├── create_tables.py
│   └── insert_data.py
└── README.md
```
