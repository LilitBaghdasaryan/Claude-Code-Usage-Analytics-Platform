import json
import csv
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
from tqdm import tqdm
import logging
from config import DB_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

TELEMETRY_FILE = "data/telemetry_logs.jsonl"
USERS_CSV = "data/employees.csv"


def parse_timestamp(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def is_db_populated(cur):
    tables = ["events", "sessions", "users", "resources"]

    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        if cur.fetchone()[0] == 0:
            return False

    return True


def insert_users(cur):
    logger.info("Loading users from CSV...")
    with open(USERS_CSV, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cur.execute(
                """
                INSERT INTO users (
                    email, full_name, practice, level, location
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                """,
                (
                    row.get("email"),
                    row.get("full_name"),
                    row.get("practice"),
                    row.get("level"),
                    row.get("location"),
                ),
            )
    logger.info("Users inserted.")


def insert_sessions_events_resources(cur):
    logger.info("Preloading users into memory...")
    cur.execute("SELECT user_id, email FROM users")
    users_map = {email: user_id for user_id, email in cur.fetchall()}
    logger.info(f"Loaded {len(users_map)} users.")

    logger.info("Preloading existing resources...")
    cur.execute("""
        SELECT resource_id, host_name, host_arch, os_type, os_version, service_name, service_version
        FROM resources
    """)
    resource_map = {tuple(row[1:]): row[0] for row in cur.fetchall()}

    sessions_batch = []
    events_batch = []
    processed_events = 0

    with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Processing telemetry"):
            log = json.loads(line)
            for log_event in log.get("logEvents", []):
                processed_events += 1
                event_id = log_event.get("id")
                message_raw = log_event.get("message", "{}")
                try:
                    message = json.loads(message_raw)
                except json.JSONDecodeError:
                    logger.warning(f"Skipping malformed JSON on event {event_id}")
                    continue

                body = message.get("body")
                attrs = message.get("attributes", {})
                resource = message.get("resource", {})

                session_id = attrs.get("session.id")
                user_email = attrs.get("user.email")
                terminal_type = attrs.get("terminal.type")
                event_timestamp = parse_timestamp(attrs.get("event.timestamp"))

                if not session_id or not user_email or not event_id:
                    continue

                user_id = users_map.get(user_email)
                if not user_id:
                    logger.warning(f"Skipping unknown user: {user_email} (event_id={event_id})")
                    continue

                resource_key = (
                    resource.get("host.name"),
                    resource.get("host.arch"),
                    resource.get("os.type"),
                    resource.get("os.version"),
                    resource.get("service.name"),
                    resource.get("service.version"),
                )
                if resource_key not in resource_map:
                    cur.execute(
                        """
                        INSERT INTO resources (
                            host_name, host_arch, os_type, os_version,
                            service_name, service_version
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (host_name, host_arch, os_type, os_version, service_name, service_version)
                        DO UPDATE SET service_name = EXCLUDED.service_name
                        RETURNING resource_id
                        """,
                        resource_key,
                    )
                    resource_map[resource_key] = cur.fetchone()[0]

                sessions_batch.append(
                    (session_id, user_id, terminal_type, event_timestamp)
                )
                events_batch.append((
                    event_id, session_id, user_id, resource_map[resource_key],
                    attrs.get("event.name") or body, event_timestamp, body,
                    attrs.get("prompt_length"), attrs.get("model"),
                    attrs.get("input_tokens"), attrs.get("output_tokens"),
                    attrs.get("cache_creation_tokens"), attrs.get("cache_read_tokens"),
                    attrs.get("cost_usd"), attrs.get("duration_ms"),
                    attrs.get("decision"), attrs.get("decision_source"),
                    attrs.get("tool_name"),
                ))

    logger.info(f"Processed {processed_events} events.")

    execute_batch(cur, """
        INSERT INTO sessions (session_id, user_id, terminal_type, started_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (session_id) DO NOTHING
        """, sessions_batch, page_size=1000)
    logger.info(f"Inserted {len(sessions_batch)} session rows.")

    execute_batch(cur, """
        INSERT INTO events (
            event_id, session_id, user_id, resource_id,
            event_type, event_timestamp, body,
            prompt_length, model, input_tokens,
            output_tokens, cache_creation_tokens,
            cache_read_tokens, cost_usd, duration_ms,
            decision, decision_source, tool_name
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_id) DO NOTHING
        """, events_batch, page_size=1000)
    logger.info(f"Inserted {len(events_batch)} events.")

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        if is_db_populated(cur):
            logger.info("Database already populated, skipping insert.")
            return
        insert_users(cur)
        insert_sessions_events_resources(cur)
        conn.commit()
        logger.info("All data loaded successfully.")
    except Exception as e:
        conn.rollback()
        logger.exception("Error loading data:")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()