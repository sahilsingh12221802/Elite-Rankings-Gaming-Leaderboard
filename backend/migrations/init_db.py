"""
Database migration script to create tables and indexes.
Run this to set up the PostgreSQL database.
"""
from app.core import settings
from app.models import Base, create_all_tables
from sqlalchemy import create_engine, text

# SQL statements for optimal indexes (these are created by SQLAlchemy models)
ADDITIONAL_INDEXES = """
-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_leaderboard_active_top ON leaderboard(is_active, total_score DESC, rank);

-- Partial indexes for active users (optimize space)
CREATE INDEX IF NOT EXISTS idx_user_active ON users(is_active) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS idx_leaderboard_active ON leaderboard(is_active) WHERE is_active = 1;

-- Covering indexes for popular queries
CREATE INDEX IF NOT EXISTS idx_session_user_score ON game_sessions(user_id, score DESC);
"""


def init_database():
    """Initialize the database with all tables and indexes."""
    print("🗄️  Initializing database...")
    
    # Create engine
    engine = create_engine(
        settings.DATABASE_URL,
        echo=True,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")

    # Create additional indexes
    with engine.begin() as connection:
        for statement in ADDITIONAL_INDEXES.split(";"):
            if statement.strip():
                try:
                    connection.execute(text(statement))
                except Exception as e:
                    print(f"⚠️  Index creation note: {e}")

    print("✓ Indexes created")
    engine.dispose()
    print("✓ Database initialization complete")


if __name__ == "__main__":
    init_database()
