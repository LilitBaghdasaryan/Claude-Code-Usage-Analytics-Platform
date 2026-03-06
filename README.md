# Claude Code Usage Analytics Platform

A Streamlit-based analytics platform to visualize Claude Code usage telemetry. Tracks token consumption, tool usage, and other metrics through an interactive dashboard backed by PostgreSQL.

---

## Requirements

- Docker
- Docker Compose

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/LilitBaghdasaryan/Claude-Code-Usage-Analytics-Platform.git
cd Claude-Code-Usage-Analytics-Platform
```

### 2. Unzip dataset folder

```bash
unzip data.zip
```

### 3. Configure environment variables

Copy the example env file and **edit it manually** before starting any services:

```bash
cp .env.example .env
```

Open `.env` in your editor and fill in the required values (database credentials, ports, etc.). The application will not work correctly without this step.

### 4. Build and start services

```bash
docker-compose up --build
```

> The first build may take several minutes. This will start both the PostgreSQL database (`telemetry_db`) and the Streamlit dashboard (`dashboard`) containers.

### 5. Open the dashboard

Navigate to [http://localhost:8501](http://localhost:8501) in your browser.

### 6. Stop the services

```bash
docker-compose down
```

---

## Project Structure

```
.
├── data.zip                       # Zipped dataset
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── config.py
├── requirements.txt
├── .env                        # Environment variables (edit manually — not committed)
├── .env.example                # Template for environment variables
├── dashboard/                  # Streamlit dashboard
│   ├── pages/                  # Multi-page app screens
│   │   ├── 1_Token_Usage.py
│   │   ├── 2_Cost_Analysis.py
│   │   ├── 3_User_Analysis.py
│   │   ├── 4_Events_and_Tools.py
│   │   └── 5_Forecasting.py
│   ├── Dashboard.py            # Main dashboard entry point
│   ├── database.py             # Database connection logic
│   ├── queries.py              # SQL queries
│   └── utils.py                # Shared utilities
├── db/                         # Database initialization scripts
│   ├── create_tables.py
│   └── insert_data.py
├── telemetry_generation/       # Synthetic data generator
│   └── generate_fake_data.py
└── README.md
```
