# Jay - BringATrailer Auction Analyzer

**Status:** ✅ PHASE 1 COMPLETE - LIVE & FULLY FUNCTIONAL

**Last Updated:** 2026-07-18

---

## What is Jay?

Jay is a real-time BringATrailer auction analyzer running on your desktop. It shows you the top bidders on any auction with their bid amounts, how many times they've bid, when they last bid, and their threat level based on auction history.

---

## What's Working NOW (Live)

### ✅ Bidders Tab - Complete & Tested
Shows a live snapshot of top bidders:
- **Rank** (1-10 or fewer if <10 active bidders)
- **Threat Level** (🟢 Low / 🟠 Medium / 🔴 High)
- **Bidder Name**
- **Highest Bid** (on THIS auction, actual $X,XXX)
- **Bid Count** (how many times they bid THIS auction)
- **Win Rate** (historical, all auctions)
- **Type** (Casual / Selective / Emotional / Balanced)
- **Threat Score** (0-100 calculated from win rate + bid frequency + overpayment)

### ✅ How It Works
1. **Double-click "Jay" icon** on desktop
2. Browser opens to Jay automatically
3. **Paste auction URL** (any BringATrailer listing)
4. **Click Bidders tab** to see analysis
5. **Monitor on separate screen** - updates in real-time as you refresh

### ✅ Data Extraction (Verified)
- Extracts all active bidders from auction comments
- Gets actual bid amounts ($X,XXX format)
- Captures bid timestamps ("Jul 18 at 5:46 PM")
- Ranks by highest bid (descending)
- Filters out non-bidders ($0 comments)
- Handles <10 bidders gracefully

### ✅ Threat Assessment
Combines three metrics:
1. **Win Rate** (how often they win) - 0-50 pts
2. **Bid Frequency** (how aggressive) - 0-30 pts
3. **Overpayment Tendency** (emotional vs rational) - 0-20 pts

### ✅ Tested Auctions
- 1964 International Harvester Scout 80 ✅ (7 bidders)
- 1989 Porsche 928 S4 ✅ (10+ bidders)
- 1999 Honda Integra ✅ (6 bidders)

---

## Desktop Launcher

**File:** Jay.lnk (on your desktop)

**One click to:**
- Open browser to localhost:8501
- Start Streamlit server (background)
- Load Jay interface

**To stop:** Close browser or kill streamlit in Task Manager

---

## Technical Stack

- **Backend:** Python 3.12
- **UI:** Streamlit (localhost web app)
- **Scraping:** BeautifulSoup + Requests (static HTML)
- **JavaScript Rendering:** Playwright (for bid comments)
- **Database:** SQLite (ready, not yet in use)
- **Deployment:** Local only (Streamlit Cloud has limitations)

---

## What You See In Real-Time

```
Rank  Threat  Bidder              Highest Bid    Bids On Auction  Win Rate  Type                       Level
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
1     🟢      Bobby21             $9,999         1                0.0%      Balanced                   15
2     🟢      Classichondaman     $8,600         1                0.0%      Emotional (Bids a lot...) 40
3     🟢      c2girl              $8,500         2                0.0%      Balanced                   15
4     🟢      ccpanel             $8,200         2                0.0%      Emotional (Bids a lot...) 40
5     🟢      Seanangus2316       $8,080         1                0.9%      Emotional (Bids a lot...) 40
6     🟢      Vxviper10           $5,100         1                0.0%      Casual                     15
7     🟢      Rsideout            $2,000         1                0.0%      Emotional (Bids a lot...) 40
```

This gives you a complete competitive snapshot at a glance.

---

## Quick Reference

| Question | Answer |
|----------|--------|
| How do I start Jay? | Double-click Jay icon on desktop |
| Where does it run? | http://localhost:8501 (your computer) |
| What do the numbers mean? | Bid amounts on THIS auction |
| What's "Threat"? | Risk score (0-100) based on their auction history |
| Why <10 bidders? | Only shows active bidders with real bids |
| Does it auto-refresh? | No, you refresh the browser manually |
| Can I share it? | No (local only) - but code is on GitHub |

---

## Repository

**GitHub:** https://github.com/CatDaddy575/jay-auction-analyzer
**Folder:** D:\Claude\bringatrailer-agent\

**Latest commits:**
- Stage 2: Extract and display bid timestamps
- Stage 1: Filter $0 bidders and cap at top 10
- Fix: Extract and rank bidders by actual bid amounts
- Phase 1: Desktop launcher and documentation

---

**Built with:** Python 3.12 | Streamlit | BeautifulSoup | Playwright | ❤️
