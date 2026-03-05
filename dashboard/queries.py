TOKEN_BY_ROLE = """
SELECT 
    u.practice,
    SUM(CAST(ev.input_tokens AS INTEGER)) AS total_input_tokens,
    SUM(CAST(ev.output_tokens AS INTEGER)) AS total_output_tokens,
    SUM(CAST(ev.input_tokens AS INTEGER) + CAST(ev.output_tokens AS INTEGER)) AS total_tokens
FROM events ev
JOIN sessions s ON ev.session_id = s.session_id
JOIN users u ON s.user_id = u.user_id
GROUP BY u.practice
ORDER BY total_tokens DESC;
"""

USAGE_HOURS = """
SELECT 
    EXTRACT(HOUR FROM ev.event_timestamp) AS hour,
    COUNT(*) AS total_events
FROM events ev
GROUP BY hour
ORDER BY hour;
"""

USAGE_BY_PERIOD = """
SELECT 
    {time_column} AS period,
    SUM(CAST(ev.input_tokens AS INTEGER) + CAST(ev.output_tokens AS INTEGER)) AS total_tokens
FROM events ev
GROUP BY period
ORDER BY period;
"""

COMMON_EVENTS = """
SELECT 
    event_type,
    COUNT(*) AS frequency
FROM events
GROUP BY event_type
ORDER BY frequency DESC;
"""

COST_BY_ROLE = """
SELECT 
    u.practice,
    SUM(CAST(ev.cost_usd AS FLOAT)) AS total_cost
FROM events ev
JOIN sessions s ON ev.session_id = s.session_id
JOIN users u ON s.user_id = u.user_id
GROUP BY u.practice
ORDER BY total_cost DESC;
"""

TOOL_DECISIONS = """
SELECT 
    tool_name,
    decision,
    COUNT(*) AS count
FROM events
WHERE event_type='tool_decision'
GROUP BY tool_name, decision
ORDER BY tool_name;
"""

PROMPT_LENGTH_BY_ROLE = """
SELECT 
    u.practice,
    AVG(CAST(ev.prompt_length AS INTEGER)) AS avg_prompt_length
FROM events ev
JOIN sessions s ON ev.session_id = s.session_id
JOIN users u ON s.user_id = u.user_id
WHERE ev.prompt_length IS NOT NULL
GROUP BY u.practice
ORDER BY avg_prompt_length DESC;
"""

TOP_BOTTOM_USERS = """
SELECT 
    s.user_id,
    u.full_name AS user_name,
    SUM(CAST(ev.input_tokens AS INTEGER) + CAST(ev.output_tokens AS INTEGER)) AS total_tokens
FROM events ev
JOIN sessions s ON ev.session_id = s.session_id
JOIN users u ON s.user_id = u.user_id
GROUP BY s.user_id, u.full_name
ORDER BY total_tokens {order}
LIMIT 10;
"""