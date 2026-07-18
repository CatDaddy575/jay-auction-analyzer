# Jay - BringATrailer Auction Analyzer

**Status:** ✅ PHASE 1 COMPLETE - WORKING LOCALLY

**Last Updated:** 2026-07-18

---

## What is Jay?

Jay is an intelligent BringATrailer auction analyzer that helps you defeat aggressive bidders by analyzing competitor bidding patterns, threat levels, and win rates. It predicts what bidders will do so you can bid strategically to win at the lowest price.

---

## What Works Right Now

### ✅ Complete Features
- **Auction Details Tab** - Extracts title, current bid, auction status
- **Market Value Tab** - Placeholder for market data aggregation
- **Max Bid Tab** - Calculates max bid based on market value + BringATrailer fees
- **Bidders Tab** - Extracts top 10 active bidders with threat assessment
  - Win rate analysis (0-100%)
  - Threat level scoring (0-100 scale)
  - Bidder type classification (Casual, Selective, Emotional, Balanced)
  - Strategy recommendations

### ✅ How to Launch
1. **Double-click "Jay" icon on your desktop** - Opens browser automatically
2. Paste any BringATrailer auction URL
3. Click "Bidders" tab to see threat analysis

### ✅ Technical Details
- Python 3.12 + Streamlit web framework
- BeautifulSoup + Requests for web scraping
- Playwright for JavaScript-rendered content (bid comments)
- SQLite database ready for caching
- GitHub repo: https://github.com/CatDaddy575/jay-auction-analyzer
- Cloud deployment: https://jay-auction-analyzer.streamlit.app (limited functionality)

---

## Key Insights Discovered

### Bidder Threat Scoring
Threat level (0-100) combines three factors:
1. **Win Rate** (0-50 pts) - High win rate = disciplined bidder
2. **Bid Frequency** (0-30 pts) - >100 bids = aggressive, <20 bids = selective
3. **Overpayment %** (0-20 pts) - Paying above market = emotional bidder

### Example: 1989 Porsche 928 S4
- 10 bidders extracted
- Highest threat: 40/100 (emotional bidders bidding a lot but losing)
- Lowest threat: 15/100 (casual bidders, low engagement)
- Strategy: You could win by bidding strategically

---

## Quick Start

1. **Double-click "Jay" icon on desktop**
2. Paste BringATrailer auction URL
3. View bidder threat assessment in "Bidders" tab

---

**Built with:** Python 3.12 | Streamlit | BeautifulSoup | Playwright
**GitHub:** https://github.com/CatDaddy575/jay-auction-analyzer
**Folder:** D:\Claude\bringatrailer-agent\
