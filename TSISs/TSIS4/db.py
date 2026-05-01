import psycopg2
from config import load_config


def connect():
    return psycopg2.connect(**load_config())


# ============================================================
#  Schema setup — run once
# ============================================================
def init_db():
    """Create tables if they don't exist."""
    conn = connect()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER   NOT NULL,
            level_reached INTEGER   NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    conn.close()


# ============================================================
#  Player helpers
# ============================================================
def get_or_create_player(username):
    """Return the player id, creating the player if needed."""
    conn = connect()
    cur  = conn.cursor()
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        pid = row[0]
    else:
        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
        pid = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return pid


def save_result(username, score, level_reached):
    """Save a game session to the database."""
    conn = connect()
    cur  = conn.cursor()
    pid  = get_or_create_player(username)
    cur.execute("""
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s)
    """, (pid, score, level_reached))
    conn.commit()
    conn.close()


def get_personal_best(username):
    """Return the player's all-time best score, or 0 if none."""
    conn = connect()
    cur  = conn.cursor()
    cur.execute("""
        SELECT MAX(gs.score)
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        WHERE p.username = %s
    """, (username,))
    row = conn.cursor().fetchone() if False else cur.fetchone()
    conn.close()
    return row[0] if row and row[0] else 0


def get_leaderboard():
    """Return top 10 all-time scores as list of (rank, username, score, level, date)."""
    conn = connect()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached,
               TO_CHAR(gs.played_at, 'YYYY-MM-DD')
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
