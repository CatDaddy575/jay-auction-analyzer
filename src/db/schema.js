// Database schema for Jay

const schema = {
  auctions: `
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
  `,

  bidders: `
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
  `,

  bidding_history: `
    CREATE TABLE IF NOT EXISTS bidding_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      auction_id INTEGER NOT NULL,
      bidder_username TEXT NOT NULL,
      bid_amount INTEGER,
      bid_time DATETIME,
      bid_position INTEGER,
      FOREIGN KEY (auction_id) REFERENCES auctions(id)
    )
  `,

  market_data: `
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
  `,

  alerts: `
    CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      auction_id INTEGER NOT NULL,
      alert_type TEXT,
      triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      message TEXT,
      FOREIGN KEY (auction_id) REFERENCES auctions(id)
    )
  `
};

module.exports = schema;
