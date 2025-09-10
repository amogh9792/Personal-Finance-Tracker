import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from app.core.config import settings
from app.utils.logger import logger

# Connection factory
def get_connection():
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

# Context manager for transactions
@contextmanager
def get_cursor():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"DB transaction failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()
