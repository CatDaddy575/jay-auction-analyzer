# Jay Streamlit Web App - Deployment Guide

Jay now has a beautiful web interface for auction analysis. Here's how to use it.

## Quick Start (Run Locally)

### 1. Install Streamlit
```bash
cd D:\Claude\bringatrailer-agent
pip install streamlit pandas
```

### 2. Run the app
```bash
streamlit run app.py
```

The web app will open at `http://localhost:8501`

### 3. Use Jay
- Paste a BringATrailer auction URL
- Jay analyzes and shows:
  - Auction details (title, current bid)
  - Market value from multiple sources
  - Max bid recommendation (with buyer's fees)
  - Bidder analysis (identify heavy hitters)
  - Risk assessment

## Deploy to Streamlit Cloud (Free & Shareable)

### 1. Create GitHub Repository
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Add Streamlit web interface for Jay"
git remote add origin https://github.com/YOUR_USERNAME/jay-auction-analyzer.git
git push -u origin main
```

### 2. Deploy to Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Click "Deploy an app"
3. Connect your GitHub account
4. Select the repository: `jay-auction-analyzer`
5. Branch: `main`
6. Main file path: `app.py`
7. Click "Deploy"

Streamlit will automatically build and deploy your app. You'll get a URL like:
```
https://jay-auction-analyzer.streamlit.app
```

### 3. Share with Friends
Just send them the URL! No installation needed. Anyone can:
- Paste an auction URL
- See analysis instantly
- Get bidding recommendations

## Features Currently Working

✅ **Auction Input** - Paste any BringATrailer URL
✅ **Title & Bid Extraction** - Scrapes live auction data
✅ **UI/Dashboard** - Beautiful, responsive interface
✅ **Fee Calculator** - BringATrailer 8% buyer's fee

## Features to Build Next

🔨 **Market Data Integration** - Connect to data sources:
   - Classic.com
   - CarsAndBids.com
   - ClassicCars.com
   - eBay.com
   - BringATrailer historical data
   - NADA Guides

🔨 **Market Value Analysis** - Aggregate and analyze pricing

🔨 **Bidder Heat Analysis** - Full bidding history parsing

🔨 **Risk Scoring** - Complete recommendation engine

## Environment Setup

Create a `.streamlit/config.toml` in your project directory:

```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#f0f2f6"
secondaryBackgroundColor = "#e0e6f6"
textColor = "#262730"
font = "sans serif"

[logger]
level = "info"
```

## Architecture

```
D:\Claude\bringatrailer-agent\
├── app.py                          # Streamlit web interface
├── src\
│   ├── market\
│   │   ├── analyzer.py            # Market value aggregation
│   │   ├── fees.py                # Fee calculations
│   │   ├── bidder_analyzer.py     # Competitive analysis
│   │   └── __init__.py
│   ├── scraper\
│   │   └── auctions.py            # BringATrailer scraper
│   └── ...
└── requirements.txt               # Streamlit, pandas, etc.
```

## Next Steps

1. ✅ Web interface built
2. 🔨 Integrate market data sources
3. 🔨 Build market value analysis
4. 🔨 Full bidder analysis
5. 🔨 Deploy to Streamlit Cloud
6. 🔨 Share with friends

## Troubleshooting

**"ModuleNotFoundError: No module named 'streamlit'"**
- Run: `pip install streamlit pandas`

**"Port 8501 already in use"**
- Run on different port: `streamlit run app.py --server.port 8502`

**Slow loading**
- Add caching: `@st.cache_data`
- Avoid scraping on every load

## Questions?

Check the README.md or STATUS.md for more info on Jay's architecture.
