import psycopg2
from app.core.config import settings
from app.utils.logger import logger

def init_db():
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()

        # Users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(200) NOT NULL
        )
        """)

        # Transactions table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount NUMERIC(10,2) NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT,
            owner_id INT REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        conn.commit()
        cur.close()
        conn.close()
        logger.info("✅ Tables created or verified successfully")

    except Exception as e:
        logger.error(f"❌ Error initializing database: {str(e)}")
        raise
