import psycopg2
from app.core.config import settings
from app.utils.logger import logger

def init_db():
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()

        # Users table (with is_admin)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(200) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        )
        """)

        # Transactions table (with category_id reference for future categories)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount NUMERIC(10,2) NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT,
            owner_id INT REFERENCES users(id) ON DELETE CASCADE,
            category_id INT NULL REFERENCES categories(id)
        )
        """)

        # Refresh tokens table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) ON DELETE CASCADE,
            token TEXT NOT NULL,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
        """)

        # Categories table (global + user-specific)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            user_id INT NULL REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (name, user_id)
        )
        """)

        # Budgets table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id) ON DELETE CASCADE,
            category_id INT NULL REFERENCES categories(id),
            amount NUMERIC(12,2) NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        cur.close()
        conn.close()
        logger.info("✅ All tables created or verified successfully")

    except Exception as e:
        logger.error(f"❌ Error initializing database: {str(e)}")
        raise
