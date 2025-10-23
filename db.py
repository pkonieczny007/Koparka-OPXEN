import sqlite3

DB_NAME = "mints.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS mints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tx_hash TEXT UNIQUE,
            token_id INTEGER,
            wallet TEXT,
            count INTEGER,
            term_days INTEGER,
            timestamp_utc TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_mint(tx_hash, token_id, wallet, count, term_days, timestamp_utc):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO mints (tx_hash, token_id, wallet, count, term_days, timestamp_utc)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tx_hash, token_id, wallet, count, term_days, timestamp_utc))
    conn.commit()
    conn.close()
