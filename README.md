# Jay - BringATrailer Auction Agent

An intelligent agent for monitoring, analyzing, and bidding on BringATrailer auctions.

## Features (Planned)

- **Auction Monitoring** — Real-time tracking of auctions with price/time alerts
- **Bidder Intelligence** — Track competitor patterns and predict bidding behavior
- **Market Analysis** — Historical price data and fair-value detection
- **Strategy Engine** — Bid recommendations and timing optimization
- **Automated Bidding** — Execute bids when conditions are met (after testing)

## Setup

1. **Install dependencies:**
   ```
   npm install
   ```

2. **Create .env file:**
   Copy `.env.example` to `.env` and add your BringATrailer credentials from the vault

3. **Initialize database:**
   ```
   npm run init-db
   ```

4. **Run agent:**
   ```
   npm start
   ```

## Architecture

- `src/config/` — Configuration and credential handling
- `src/browser/` — Playwright browser automation
- `src/scraper/` — BringATrailer data extraction
- `src/monitor/` — Real-time auction tracking
- `src/analysis/` — Bidder intelligence and market analysis
- `src/strategy/` — Bid recommendations
- `src/bidder/` — Automated bidding (future)
- `src/db/` — SQLite data persistence
- `src/index.js` — Main entry point

## Status

Current phase: **Foundation & Setup**

See `STATUS.md` for detailed progress.
