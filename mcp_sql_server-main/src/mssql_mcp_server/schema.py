"""Database schema for metrics and optimization."""

CREATE_METRICS_TABLES = """
-- Query execution history
CREATE TABLE IF NOT EXISTS query_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    original_nl NVARCHAR(MAX),
    generated_sql NVARCHAR(MAX),
    execution_time_ms FLOAT,
    cost_estimate FLOAT,
    rows_affected INT,
    success BIT,
    error_message NVARCHAR(MAX),
    timestamp DATETIME DEFAULT GETDATE(),
    user_id NVARCHAR(100)
);

-- SQL candidate queries
CREATE TABLE IF NOT EXISTS query_candidates (
    id INT IDENTITY(1,1) PRIMARY KEY,
    query_history_id INT,
    candidate_sql NVARCHAR(MAX),
    estimated_cost FLOAT,
    actual_cost FLOAT,
    execution_time_ms FLOAT,
    selected BIT,
    timestamp DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (query_history_id) REFERENCES query_history(id)
);

-- Optimization metrics
CREATE TABLE IF NOT EXISTS optimization_metrics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    query_pattern NVARCHAR(500),
    avg_latency_ms FLOAT,
    min_latency_ms FLOAT,
    max_latency_ms FLOAT,
    success_rate FLOAT,
    execution_count INT,
    last_updated DATETIME DEFAULT GETDATE()
);

-- Reinforcement learning state
CREATE TABLE IF NOT EXISTS rl_state (
    id INT IDENTITY(1,1) PRIMARY KEY,
    state_hash NVARCHAR(64),
    action_id INT,
    reward FLOAT,
    q_value FLOAT,
    timestamp DATETIME DEFAULT GETDATE()
);

-- Q-table for RL
CREATE TABLE IF NOT EXISTS q_table (
    id INT IDENTITY(1,1) PRIMARY KEY,
    state_hash NVARCHAR(64),
    action_id INT,
    q_value FLOAT,
    visit_count INT DEFAULT 0,
    last_updated DATETIME DEFAULT GETDATE(),
    UNIQUE(state_hash, action_id)
);
"""

def create_metrics_tables(conn):
    """Create all metrics tables."""
    cursor = conn.cursor()
    for statement in CREATE_METRICS_TABLES.split(';'):
        statement = statement.strip()
        if statement:
            try:
                cursor.execute(statement)
            except Exception as e:
                # Table might already exist
                pass
    conn.commit()
    cursor.close()
