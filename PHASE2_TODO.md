# Jay - Phase 2 TODO

## Completed (Phase 1)
- ✅ Bidder profile stats extraction (bids, wins, member since)
- ✅ Win rate calculation
- ✅ Current bidders analysis framework
- ✅ Threat level scoring
- ✅ Bidder type classification

## Phase 2 - Detailed Bid History & Market Analysis

### 1. Complete Bid History Scraper
**Priority: HIGH**
**Effort: 3-4 hours**

Currently, we extract bidders from auction pages but can't get their detailed bid history because:
- BringATrailer profile pages show listing links but no structured bid history table
- Solution: Scrape each of bidder's 20+ auction pages to extract:
  - Their bid amount on that auction
  - Whether they won/lost
  - Auction end date
  - Estimated market value at that time

**Files to modify:**
- `src/bidder/profile_scraper.py` - Add `_extract_bidding_history_from_listings()`
- `src/bidder/analyzer.py` - Enhance with real bid history data

**Implementation notes:**
- Use caching (SQLite) to avoid re-scraping same bidder
- Consider background job for first-time bidder profiles
- Estimate: 1-2 min per bidder (20-50 pages × Playwright)

---

### 2. Market Value Analysis for Winning Auctions
**Priority: HIGH**
**Effort: 2-3 hours**

When bidder has winning auctions, analyze if they overpaid:

```
Overpayment % = (Winning Bid - Market Value at Time) / Market Value × 100
```

- Negative % = Got a deal (rational/educated buyer)
- Positive % = Overpaid (emotional/desperate)

**Tasks:**
- Fetch each winning auction page
- Extract: Final price, vehicle specs, auction date
- Estimate market value at that time (using historical market data)
- Calculate overpayment percentage
- Store in `competitive_history` table

**Files to create:**
- `src/market/historical_analyzer.py` - Estimate market value for past auctions

---

### 3. Real-Time Bidder Updates
**Priority: MEDIUM**
**Effort: 2-3 hours**

As auction approaches close (last 30 minutes):
- Poll current auction bid history every 10 seconds
- Detect new bidders or bid changes
- Update threat level analysis in real-time
- Show "NEW BIDDER" alerts with their threat level

**Implementation:**
- Add Streamlit refresh interval to Bidders tab
- Keep bidder cache in memory during session
- Show timestamp of last update

---

### 4. Bidding Pattern Visualization
**Priority: MEDIUM**
**Effort: 2-3 hours**

Visualize each bidder's pattern:
- Bid escalation chart (time vs amount)
- Win/loss history by vehicle type
- Win/loss history by price range
- Aggressiveness over time

**Tools:**
- Use Streamlit charts + matplotlib
- Files: `src/visualization/bidder_patterns.py`

---

### 5. Market Data Sources Integration
**Priority: HIGH** (blocks full market value analysis)
**Effort: 4-6 hours**

Implement scrapers for:
- Classic.com (sales data)
- CarsAndBids.com (completed auctions)
- ClassicCars.com (listings)
- eBay.com (completed auctions)
- NADA Guides API (valuations)

Current status: All have TODO stubs in `src/market/analyzer.py`

**Why needed:**
- Calculate fair market value for current auction
- Normalize historical winning prices to current market
- Assess if bidder overpaid (accounting for time/market changes)

---

### 6. Database Schema
**Priority: MEDIUM**
**Effort: 1 hour**

Add tables for caching:

```sql
CREATE TABLE bidder_profiles (
  bidder_name TEXT PRIMARY KEY,
  total_bids INTEGER,
  total_wins INTEGER,
  member_since TEXT,
  last_updated TIMESTAMP,
  cached_data JSON
);

CREATE TABLE bidder_bid_history (
  bidder_name TEXT,
  auction_id TEXT,
  auction_name TEXT,
  bid_amount INTEGER,
  result TEXT, -- 'won', 'lost'
  auction_date TEXT,
  market_value INTEGER,
  overpayment_percent FLOAT
);
```

---

### 7. Performance Optimization
**Priority: LOW**
**Effort: 2 hours**

- Cache bidder profiles (don't re-scrape daily)
- Cache market value estimates (use 30-day rolling average)
- Async scraping for multiple bidders in parallel
- Estimated wait: Currently 2-4 min per bidder → target: 30-60 sec

---

## Testing Checklist

- [ ] Bid history scraper works for 10+ different bidders
- [ ] Overpayment analysis matches manual spot-checks
- [ ] Threat level scoring correlates with actual auction outcomes
- [ ] Real-time updates don't crash Streamlit
- [ ] Market value estimates are within ±10% of actual sales

---

## Success Criteria

When complete, Jay should:
1. Show each current bidder's stats (win rate, threat level)
2. Indicate if each bidder is emotional/rational based on overpayment history
3. Update in real-time as auction closes
4. Recommend bidding strategy for each competitor
5. Calculate accurate max bid based on market value + competition

---

## Estimated Timeline
- Phase 2 MVP (bid history + overpayment): 1-2 weeks (10-15 hours)
- Full Phase 2 (all features): 3-4 weeks (20-30 hours)
- Optimization: Ongoing

