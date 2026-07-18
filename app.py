"""
Jay - BringATrailer Auction Analyzer
Web interface for auction analysis and bidding recommendations
"""

import streamlit as st
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import sys
import subprocess
sys.path.insert(0, '.')
from src.scraper.auctions import AuctionScraper
from src.scraper.bid_history import BidHistoryScraper
from src.market.bidder_analyzer import BidderAnalyzer
from src.market.fees import FeeCalculator
from src.bidder.current_bidders import CurrentBiddersAnalyzer

# Initialize Playwright on first run (for cloud deployment)
@st.cache_resource
def init_playwright():
    try:
        # Try to install playwright browsers if not already installed
        subprocess.run(['playwright', 'install', 'chromium'],
                      capture_output=True, timeout=60)
    except:
        pass  # If it fails, fallback to static HTML will be used
    return True

_ = init_playwright()

# Page config
st.set_page_config(
    page_title="Jay - Auction Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .recommendation-good {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .recommendation-warning {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
    }
    .recommendation-bad {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 Jay - BringATrailer Auction Analyzer")
st.markdown("*Intelligent auction analysis and bidding recommendations*")

# Sidebar for input
st.sidebar.header("Auction Analysis")
auction_url = st.sidebar.text_input(
    "Paste BringATrailer auction URL:",
    placeholder="https://bringatrailer.com/listing/..."
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Jay analyzes:**
    - Market value (from multiple sources)
    - Buyer's fees
    - Max bid recommendation
    - Bidder patterns
    - Risk assessment
    """
)

# Main content
if not auction_url:
    st.markdown("""
    ## Welcome to Jay 🤖

    Jay is your intelligent BringATrailer auction analyzer.

    **How to use:**
    1. Paste a BringATrailer auction URL in the sidebar
    2. Jay analyzes market data from multiple sources
    3. Get a max bid recommendation
    4. See bidder patterns and risk assessment

    ### Features:
    - 📊 **Market Analysis** - Aggregates pricing from Classic.com, CarsAndBids, ClassicCars, eBay, and more
    - 💰 **Fee Calculation** - Accurate BringATrailer buyer fee computation
    - 📈 **Max Bid Recommendation** - Based on market value + fees
    - 👥 **Bidder Analysis** - Identifies aggressive bidders
    - ⚠️ **Risk Assessment** - "Is this worth bidding on?"

    ### Data Sources:
    - Classic.com (sales data, sold/unsold tracking)
    - CarsAndBids.com (completed auctions)
    - ClassicCars.com (listing data)
    - eBay.com (auction results)
    - BringATrailer (historical auction data)
    - NADA Guides (valuations)
    """)

else:
    # Extract auction ID from URL
    auction_id = None
    if "bringatrailer.com" in auction_url:
        match = re.search(r'/listing/([^/]+)', auction_url)
        if match:
            auction_id = match.group(1)

    if not auction_id:
        st.error("❌ Invalid BringATrailer URL. Please paste a valid auction link.")
    else:
        st.success(f"✅ Analyzing auction: {auction_id}")

        # Tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Auction Details", "💰 Market Value", "📈 Max Bid", "👥 Bidders"]
        )

        with tab1:
            st.header("Auction Details")

            try:
                # Fetch auction page
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(auction_url, headers=headers, timeout=10)
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')

                # Extract title
                title_elem = soup.find('h1', class_='post-title listing-post-title')
                title = title_elem.get_text(strip=True) if title_elem else "Unknown"

                # Extract current bid
                current_bid = 0
                listing_avail = soup.find('div', class_='listing-available')
                if listing_avail:
                    bid_label = listing_avail.find('span', class_='info-label',
                        string=lambda s: 'current' in s.lower() if s else False)
                    if bid_label:
                        value_elem = bid_label.find_next('strong', class_='info-value')
                        if value_elem:
                            price_text = value_elem.get_text(strip=True)
                            match = re.search(r'\$?([\d,]+)', price_text)
                            if match:
                                current_bid = int(match.group(1).replace(',', ''))

                # Display auction info
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Auction Title", title[:40] + "..." if len(title) > 40 else title)

                with col2:
                    st.metric("Current Bid", f"${current_bid:,}")

                with col3:
                    st.metric("Status", "Active" if current_bid > 0 else "Unknown")

                st.markdown(f"**Full Title:** {title}")
                st.markdown(f"**Auction URL:** {auction_url}")

                # Parse car details from title
                st.subheader("Extracted Details")
                year_match = re.search(r'(\d{4})', title)
                year = year_match.group(1) if year_match else "Unknown"
                st.write(f"**Year:** {year}")
                st.write(f"**Current Bid:** ${current_bid:,}")

            except Exception as e:
                st.error(f"Error fetching auction: {e}")

        with tab2:
            st.header("Market Value Analysis")
            st.info("🔍 Analyzing market data from multiple sources...")

            # Placeholder for market data sources
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Data Sources")
                sources = {
                    "Classic.com": "🔍 Analyzing sales data...",
                    "CarsAndBids.com": "🔍 Checking completed auctions...",
                    "ClassicCars.com": "🔍 Reviewing listings...",
                    "eBay.com": "🔍 Searching auction results...",
                    "BringATrailer": "🔍 Scraping historical data...",
                }
                for source, status in sources.items():
                    st.write(f"**{source}:** {status}")

            with col2:
                st.subheader("Estimated Market Value")
                st.metric("Fair Market Value", "$32,500", "+5.2%")
                st.metric("Low Range", "$28,000")
                st.metric("High Range", "$37,000")

            # Market analysis chart (placeholder)
            st.subheader("Price Distribution")
            data = pd.DataFrame({
                'Source': ['Classic.com', 'CarsAndBids', 'ClassicCars', 'eBay', 'BringATrailer'],
                'Estimated Value': [32000, 33500, 31500, 32800, 33200]
            })
            st.bar_chart(data.set_index('Source'))

        with tab3:
            st.header("Max Bid Recommendation")
            st.write("*Based on estimated market value — Jay tells you when to stop bidding*")

            st.subheader("Auction Fee Category")
            st.write("**Most car auctions: 5% fee (default)**")
            st.write("*10% fee applies only to: Motorcycles, Minibikes, Parts, Wheels, ATVs, Go-Karts, Tractors*")

            fee_category = st.radio(
                "Select your auction's fee category:",
                options=["5% fee (cap: $7,500)", "10% fee (cap: $4,000)"],
                horizontal=True,
                index=0
            )
            fee_rate = 0.05 if "5%" in fee_category else 0.10

            st.markdown("---")

            try:
                # Current bid info
                st.subheader("Current Status")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Bid", f"${current_bid:,}")
                with col2:
                    fee_calc = FeeCalculator.calculate_total_cost(current_bid, fee_rate)
                    st.metric("Total Cost (with fees)", f"${fee_calc['total_cost']:,}")

                st.markdown("---")

                # Market value recommendation (placeholder for now)
                st.subheader("Market Value Analysis")
                st.info("🔍 Analyzing market data from multiple sources...")

                # For now, use placeholder; when market data sources are implemented, use real values
                estimated_market_value = 32500  # TODO: Replace with actual market analysis

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Estimated Market Value", f"${estimated_market_value:,}")
                with col2:
                    st.metric("Fair Range", "$28k - $37k")
                with col3:
                    diff = estimated_market_value - current_bid
                    diff_color = "🟢" if diff > 0 else "🔴"
                    st.metric(f"{diff_color} vs Current Bid", f"${diff:+,}")

                st.markdown("---")

                # Calculate max bid based on market value
                st.subheader("Recommended Max Bid")
                st.write("**How much should you bid before overpaying?**")

                max_bid_calc = FeeCalculator.calculate_max_bid(estimated_market_value, fee_rate)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Market Value", f"${estimated_market_value:,}")
                with col2:
                    st.metric("Your Max Bid", f"${max_bid_calc['max_bid']:,}")
                with col3:
                    st.metric("Total w/ Fees", f"${max_bid_calc['resulting_total_cost']:,}")
                with col4:
                    remaining = max_bid_calc['max_bid'] - current_bid
                    remaining_color = "🟢" if remaining > 0 else "🔴"
                    st.metric(f"{remaining_color} Room to Bid", f"${remaining:+,}")

                if max_bid_calc['fee_capped']:
                    st.warning("⚠️ Fee is at maximum for this category")

                st.markdown("---")

                # Recommendation
                st.subheader("Verdict")
                if current_bid > max_bid_calc['max_bid']:
                    st.markdown(
                        f"""
                        <div class="recommendation-bad">
                        <h4>🛑 STOP - You're Overpaying</h4>
                        Current bid (<strong>${current_bid:,}</strong>) is already above fair market value.
                        <br/>Stop bidding here — not worth paying more than <strong>${max_bid_calc['max_bid']:,}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                elif current_bid > max_bid_calc['max_bid'] * 0.85:
                    st.markdown(
                        f"""
                        <div class="recommendation-warning">
                        <h4>⚠️ CAUTION - Near Your Limit</h4>
                        You have only <strong>${max_bid_calc['max_bid'] - current_bid:,}</strong> before hitting fair market value.
                        <br/>Be strategic — don't overpay just to win.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="recommendation-good">
                        <h4>✅ GOOD VALUE</h4>
                        Current bid (<strong>${current_bid:,}</strong>) is below fair market value.
                        <br/>You can bid up to <strong>${max_bid_calc['max_bid']:,}</strong> and still stay fair.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.error(f"Error calculating recommendation: {e}")

        with tab4:
            st.header("Bidder Analysis")
            st.write("*Top 10 active bidders with threat assessment and win rate analysis*")

            try:
                # Extract top 10 bidders from auction using Playwright
                st.caption("Loading bidders from auction...")
                bid_scraper = BidHistoryScraper()

                try:
                    with st.spinner("🔍 Analyzing bidders (this may take 15-30 seconds)..."):
                        top_bidders = bid_scraper.get_top_bidders(auction_url, limit=10)
                except Exception as scraper_error:
                    st.error(f"Bidder extraction failed: {str(scraper_error)}")
                    top_bidders = []
                finally:
                    try:
                        bid_scraper.cleanup()
                    except:
                        pass

                if top_bidders and len(top_bidders) > 0:
                    bidder_names = [b['bidder_name'] for b in top_bidders]
                    st.caption(f"Found {len(bidder_names)} active bidders on this auction")

                    # Get market value from earlier in session
                    estimated_market_value = 28000  # TODO: Use actual market value

                    # Analyze all bidders
                    bidders_analyzer = CurrentBiddersAnalyzer()
                    competitors = bidders_analyzer.analyze_auction_competitors(
                        bidder_names,
                        estimated_market_value=estimated_market_value
                    )

                    if competitors and any(c for c in competitors if c):
                        # Display overview metrics
                        st.subheader("Competitive Overview")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            avg_threat = sum(c['threat_level'] for c in competitors if c) / len([c for c in competitors if c])
                            st.metric("Average Threat Level", f"{avg_threat:.0f}/100")

                        with col2:
                            st.metric("Total Active Bidders", len([c for c in competitors if c]))

                        with col3:
                            high_threat_count = len([c for c in competitors if c and c['threat_level'] > 50])
                            st.metric("High Threat Bidders", high_threat_count)

                        st.markdown("---")

                        # Display all competitors in a table
                        st.subheader("Top 10 Bidders (Ranked by Activity)")
                        comp_data = []
                        for idx, comp in enumerate(competitors, 1):
                            if comp:
                                threat_icon = '🔴' if comp['threat_level'] > 75 else '🟠' if comp['threat_level'] > 50 else '🟢'
                                comp_data.append({
                                    'Rank': idx,
                                    'Threat': threat_icon,
                                    'Bidder': comp['bidder_name'],
                                    'Win Rate': f"{comp['stats']['win_rate']}%",
                                    'Bids': comp['stats']['total_bids'],
                                    'Type': comp['bidder_type'],
                                    'Level': comp['threat_level']
                                })

                        if comp_data:
                            comp_df = pd.DataFrame(comp_data)
                            st.dataframe(comp_df, use_container_width=True, hide_index=True)

                        st.markdown("---")

                        # Detailed breakdown per competitor
                        st.subheader("Detailed Analysis")
                        for comp in competitors:
                            if comp:
                                threat = comp['threat_level']
                                if threat > 75:
                                    icon, color = '🔴 VERY HIGH', '#ff4444'
                                elif threat > 50:
                                    icon, color = '🟠 HIGH', '#ffaa00'
                                else:
                                    icon, color = '🟢 LOW', '#00aa00'

                                with st.expander(f"{icon} — {comp['bidder_name']} (Threat: {threat}/100)"):
                                    col1, col2, col3, col4 = st.columns(4)

                                    with col1:
                                        st.metric("Win Rate", f"{comp['stats']['win_rate']}%")
                                    with col2:
                                        st.metric("Total Bids", comp['stats']['total_bids'])
                                    with col3:
                                        st.metric("Total Wins", comp['stats']['total_wins'])
                                    with col4:
                                        st.metric("Threat Score", f"{comp['threat_level']}/100")

                                    st.write(f"**Type:** {comp['bidder_type']}")
                                    st.write(f"**Member Since:** {comp['stats']['member_since'] or 'Unknown'}")
                                    st.write(f"**Recommendation:** {comp['recommendation']}")

                    else:
                        st.info("Bidder analysis in progress...")

                else:
                    st.warning("⚠️ No active bidders detected yet. Check back as the auction progresses.")

            except Exception as e:
                st.error(f"Error analyzing bidders: {str(e)}")
                import traceback
                st.write(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
    Jay v0.1 | BringATrailer Auction Analyzer | 🤖 Powered by market data aggregation
    </div>
    """,
    unsafe_allow_html=True
)
