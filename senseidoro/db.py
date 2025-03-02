import sqlite3

DB_PATH = "doro.db"


async def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table for storing user preferences and subscription status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT NOT NULL,
            subscription_tier TEXT DEFAULT 'free',
            subscription_expires_at TIMESTAMP,
            last_vote_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create servers table for storing server-specific settings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            server_id BIGINT PRIMARY KEY,
            server_name TEXT NOT NULL,
            subscription_tier TEXT DEFAULT 'free',
            subscription_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create sessions table for tracking pomodoro sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT 'Pomodoro',
            server_id BIGINT NOT NULL,
            info_channel_id BIGINT NOT NULL,
            lobby_channel_id BIGINT NOT NULL,
            work_channel_id BIGINT,
            started_by_user_id BIGINT NOT NULL,
            current_repetition INTEGER DEFAULT 0,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            status TEXT DEFAULT 'active' CHECK (status IN ('active', 'break', 'completed', 'cancelled')),
            settings JSON DEFAULT '{"mute_admins": true, "work_time": 25, "break_time": 5, "repetitions": 4}',
            FOREIGN KEY (server_id) REFERENCES servers (server_id),
            FOREIGN KEY (started_by_user_id) REFERENCES users (user_id)
        )
    """)

    # Create session_participants table for tracking who joined sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_participants (
            session_id INTEGER,
            user_id BIGINT,
            join_time TIMESTAMP NOT NULL,
            leave_time TIMESTAMP,
            total_focus_time INTEGER DEFAULT 0,
            total_breaks INTEGER DEFAULT 0,
            PRIMARY KEY (session_id, user_id),
            FOREIGN KEY (session_id) REFERENCES sessions (session_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    conn.close()


def get_db() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)
