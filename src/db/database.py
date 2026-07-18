import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv('DB_PATH', './data/jay.db')

def init_database():
    """Initialize SQLite database with schema"""
    os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Auctions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ba_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            make TEXT,
            model TEXT,
            year INTEGER,
            asking_price INTEGER,
            current_bid INTEGER,
            reserve_price INTEGER,
            bid_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            ends_at DATETIME,
            url TEXT
        )
    ''')

    # Bidders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bidders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            win_rate REAL DEFAULT 0,
            total_bids INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            avg_bid_amount REAL DEFAULT 0,
            max_bid_amount INTEGER DEFAULT 0,
            bidding_style TEXT,
            last_active DATETIME,
            is_competitor BOOLEAN DEFAULT false,
            tracked BOOLEAN DEFAULT false
        )
    ''')

    # Bidding history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bidding_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auction_id INTEGER NOT NULL,
            bidder_username TEXT NOT NULL,
            bid_amount INTEGER,
            bid_time DATETIME,
            bid_position INTEGER,
            FOREIGN KEY (auction_id) REFERENCES auctions(id)
        )
    ''')

    # Market data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT,
            model TEXT,
            year INTEGER,
            avg_selling_price REAL,
            median_selling_price REAL,
            avg_final_bid REAL,
            sample_size INTEGER,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auction_id INTEGER NOT NULL,
            alert_type TEXT,
            triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            message TEXT,
            FOREIGN KEY (auction_id) REFERENCES auctions(id)
        )
    ''')

    conn.commit()
    conn.close()
    print('✓ Database initialized')

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def close_connection(conn):
    """Close database connection"""
    if conn:
        conn.close()
