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


def load_users_from_csv(cur):
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
    logger.info("Users loaded.")


def insert_sessions_events_resources(cur):
    # preload users
    logger.info("Preloading users into memory...")
    cur.execute("SELECT user_id, email FROM users")
    users_map = {email: user_id for user_id, email in cur.fetchall()}
    logger.info(f"Loaded {len(users_map)} users.")

    # preload existing resources
    logger.info("Preloading existing resources...")
    cur.execute("""
        SELECT resource_id, host_name, host_arch, os_type, os_version, service_name, service_version
        FROM resources
    """)
    resource_map = {tuple(row[1:]): row[0] for row in cur.fetchall()}
    new_resources_batch = []

    total_lines = sum(1 for _ in open(TELEMETRY_FILE, "r", encoding="utf-8"))
    events_batch = []
    sessions_batch = []

    processed_events = 0

    with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
        for line in tqdm(f, total=total_lines, desc="Processing telemetry"):
            log = json.loads(line)
            for log_event in log.get("logEvents", []):
                processed_events += 1
                event_id = log_event.get("id")
                message_raw = log_event.get("message", "{}")
                try:
                    message = json.loads(message_raw)
                except:
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

                # get user_id
                user_id = users_map.get(user_email)
                if not user_id:
                    raise ValueError(
                        f"Unknown user: {user_email} "
                        f"(session_id={session_id}, event_id={event_id})"
                    )

                # deduplicate resource
                resource_key = (
                    resource.get("host.name"),
                    resource.get("host.arch"),
                    resource.get("os.type"),
                    resource.get("os.version"),
                    resource.get("service.name"),
                    resource.get("service.version"),
                )
                resource_id = resource_map.get(resource_key)
                if not resource_id:
                    new_resources_batch.append(resource_key)

                # session batch
                sessions_batch.append(
                    (session_id, user_id, terminal_type, event_timestamp)
                )

                # event batch
                events_batch.append(
                    (
                        event_id,
                        session_id,
                        user_id,
                        resource_key,  # tmp key
                        attrs.get("event.name") or body,
                        event_timestamp,
                        body,
                        attrs.get("prompt_length"),
                        attrs.get("model"),
                        attrs.get("input_tokens"),
                        attrs.get("output_tokens"),
                        attrs.get("cache_creation_tokens"),
                        attrs.get("cache_read_tokens"),
                        attrs.get("cost_usd"),
                        attrs.get("duration_ms"),
                        attrs.get("decision"),
                        attrs.get("decision_source"),
                        attrs.get("tool_name"),
                    )
                )
    new_resources_batch = list({r: None for r in new_resources_batch}.keys())

    logger.info(f"Processed {processed_events} events.")
    logger.info(f"New resources to insert: {len(new_resources_batch)}")

    # insert new resources
    if new_resources_batch:
        execute_batch(
            cur,
            """
            INSERT INTO resources (
                host_name, host_arch, os_type, os_version,
                service_name, service_version
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING resource_id
            """,
            new_resources_batch,
            page_size=1000,
        )
        returned_ids = cur.fetchall()
        for key, row in zip(new_resources_batch, returned_ids):
            resource_map[key] = row[0]

    logger.info(f"Total resources after dedup: {len(resource_map)}")

    # insert sessions
    execute_batch(
        cur,
        """
        INSERT INTO sessions (session_id, user_id, terminal_type, started_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (session_id) DO NOTHING
        """,
        sessions_batch,
        page_size=1000,
    )
    logger.info(f"Inserted {len(sessions_batch)} session rows.")

    # replace resource_key with real resource_id
    final_events_batch = []
    for event in events_batch:
        resource_key = event[3]
        resource_id = resource_map.get(resource_key)
        final_events_batch.append(event[:3] + (resource_id,) + event[4:])

    # insert events
    execute_batch(
        cur,
        """
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
        """,
        final_events_batch,
        page_size=1000,
    )
    logger.info(f"Inserted {len(final_events_batch)} events.")


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        load_users_from_csv(cur)
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