import sqlite3
import json
import os
from datetime import datetime, timedelta
from models.response import SearchResponse

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "cache.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS search_cache (
            product TEXT PRIMARY KEY,
            result JSON NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_cached(product: str) -> SearchResponse | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT result, created_at FROM search_cache WHERE product = ?",
        (product.lower(),)
    ).fetchone()
    conn.close()

    if not row:
        return None

    # Cache expires after 24 hours
    created_at = datetime.fromisoformat(row["created_at"])
    if datetime.now() - created_at > timedelta(hours=24):
        delete_cached(product)
        return None

    return SearchResponse(**json.loads(row["result"]))

def save_cached(product: str, result: SearchResponse):
    conn = get_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO search_cache (product, result, created_at)
        VALUES (?, ?, ?)
        """,
        (product.lower(), result.model_dump_json(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def delete_cached(product: str):
    conn = get_connection()
    conn.execute(
        "DELETE FROM search_cache WHERE product = ?",
        (product.lower(),)
    )
    conn.commit()
    conn.close()
