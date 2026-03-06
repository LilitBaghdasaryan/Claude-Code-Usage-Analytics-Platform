import psycopg2
from config import DB_CONFIG

def create_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Tables created successfully.")


def create_tables():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
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
        CREATE TABLE IF NOT EXISTS events (
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
        print("Tables created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Failed to create tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database schema created.")