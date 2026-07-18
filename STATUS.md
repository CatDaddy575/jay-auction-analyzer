# Jay - BringATrailer Auction Agent

## DONE
- Project initialized at D:\Claude\bringatrailer-agent
- BringATrailer credentials stored in vault
- Git repo set up with .gitignore
- **Rebuilt in Python** (Selenium, BeautifulSoup, SQLite)
- All Python dependencies installed (selenium, beautifulsoup4, requests, python-dotenv, schedule)
- Created .env file with BA credentials
- Core modules built:
  - Browser automation (Selenium)
  - Auction scraper (BeautifulSoup)
  - Database layer (SQLite)
  - Real-time monitoring
  - Strategy engine
  - Config management

## NOW
- ✅ Scraper successfully extracting live auction data
- ✅ Title extraction working
- ✅ Current bid extraction working
- Next: Refine bidding history extraction

## NEXT
- Extract bidding history from auction page
- Extract auction end time
- Extract description
- Build bidder intelligence/pattern analysis
- Build market value analysis & competitor tracking
- Test strategy recommendations
- Test adaptive monitoring scheduler on live auctions
- Extensive live testing before automated bidding

## ARCHITECTURE

**Adaptive Monitoring Scheduler:**
- 7+ days: Check 1x per day (minimal resources)
- 2-7 days: Check 2x per day
- 24-48 hours: Check every 2 hours
- 2-24 hours: Check every 15 minutes
- <2 hours: Check every 2-3 minutes
- <5 minutes: Real-time monitoring

**Usage:**
- `python main.py` — Test mode (verify setup)
- `python main.py --monitor` — Monitor mode (run scheduler on active auctions)
