import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def create_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE users (
        user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT,
        practice TEXT,
        level TEXT,
        location TEXT
    );
    """)

    # Resource table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        resource_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        host_name TEXT,
        host_arch TEXT,
        os_type TEXT,
        os_version TEXT,
        service_name TEXT,
        service_version TEXT,
        UNIQUE(host_name, host_arch, os_type, os_version, service_name, service_version)
    );
    """)

    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id UUID PRIMARY KEY,
        resource_id INTEGER REFERENCES resources(resource_id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
        terminal_type TEXT,
        started_at TIMESTAMP,
        ended_at TIMESTAMP
    );
    """)

    # Events table
    cursor.execute("""
    CREATE TABLE events (
        event_id TEXT PRIMARY KEY,
        session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
        resource_id INTEGER REFERENCES resources(resource_id),

        event_type TEXT,
        event_timestamp TIMESTAMP,
        body TEXT,
        prompt TEXT,
        prompt_length INTEGER,

        model TEXT,
        input_tokens INTEGER,
        output_tokens INTEGER,
        cache_creation_tokens INTEGER,
        cache_read_tokens INTEGER,

        cost_usd DOUBLE PRECISION,
        duration_ms INTEGER,

        decision TEXT,
        decision_source TEXT,
        tool_name TEXT
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Tables created successfully.")


def drop_all_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ All tables dropped successfully.")

if __name__ == "__main__":
    drop_all_tables()
    create_tables()
    print("Database schema reset complete!")