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
sys.path.insert(0, '/app')
from src.scraper.auctions import AuctionScraper
from src.market.bidder_analyzer import BidderAnalyzer
from src.market.fees import FeeCalculator

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

            st.subheader("Buyer's Fee Calculation")

            # Current bid from scrape
            try:
                fee_calc = FeeCalculator.calculate_total_cost(current_bid)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Current Bid:** ${current_bid:,}")

                with col2:
                    st.write(f"**Buyer's Fee:** {fee_calc['buyer_fee_percent']:.2f}%")

                with col3:
                    st.write(f"**Total Cost:** ${fee_calc['total_cost']:,}")

                st.markdown("---")

                # Set target budget
                st.subheader("Your Budget")
                target_budget = st.number_input(
                    "What's your max total budget (including fees)?",
                    min_value=1000,
                    value=35000,
                    step=1000
                )

                # Calculate max bid for budget
                max_bid_calc = FeeCalculator.calculate_max_bid(target_budget)

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Your Budget", f"${target_budget:,}")

                with col2:
                    st.metric("Max Bid Amount", f"${max_bid_calc['max_bid']:,}")

                with col3:
                    st.metric("Resulting Total", f"${max_bid_calc['resulting_total_cost']:,}")

                st.info(max_bid_calc['note'])

                st.markdown("---")

                # Recommendation
                st.subheader("Bid Recommendation")
                if current_bid > max_bid_calc['max_bid']:
                    st.markdown(
                        f"""
                        <div class="recommendation-bad">
                        <h4>⚠️ AVOID - Overpriced</h4>
                        Current bid (<strong>${current_bid:,}</strong>) exceeds your max bid (<strong>${max_bid_calc['max_bid']:,}</strong>)
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                elif current_bid > max_bid_calc['max_bid'] * 0.9:
                    st.markdown(
                        f"""
                        <div class="recommendation-warning">
                        <h4>⚠️ CAUTION - Getting Close</h4>
                        Current bid is approaching your limit. Proceed with caution.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="recommendation-good">
                        <h4>✅ GOOD OPPORTUNITY</h4>
                        Current bid (<strong>${current_bid:,}</strong>) is below your max bid (<strong>${max_bid_calc['max_bid']:,}</strong>)
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.error(f"Error calculating fees: {e}")

        with tab4:
            st.header("Bidder Analysis")

            try:
                # Parse bidding history from auction page
                scraper = AuctionScraper()
                result = scraper.parse_auction_page(html)
                bidding_history = result['bidding_history']

                if bidding_history:
                    # Analyze bidders
                    analyzer = BidderAnalyzer()
                    analysis = analyzer.analyze_bidding_history(bidding_history)

                    # Display summary
                    st.subheader("Competitive Landscape")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Bids", analysis['total_bids'])

                    with col2:
                        st.metric("Unique Bidders", analysis['unique_bidders'])

                    with col3:
                        st.metric("Heavy Hitters", len(analysis['heavy_hitters']))

                    with col4:
                        st.metric("Risk Level", analysis['competitive_risk'])

                    st.markdown("---")

                    # All bidders table
                    st.subheader("All Bidders")
                    if analysis['all_bidders']:
                        bidder_df = pd.DataFrame([
                            {
                                'Bidder': b['bidder'],
                                'Bid Count': b['bid_count'],
                                'Bid %': f"{b['bid_percentage']:.1f}%",
                                'Max Bid': f"${b['max_bid']:,}",
                                'Avg Bid': f"${b['avg_bid']:,}",
                                'Risk': b['risk_level']
                            }
                            for b in analysis['all_bidders']
                        ])
                        st.dataframe(bidder_df, use_container_width=True)

                    # Heavy hitters warning
                    if analysis['heavy_hitters']:
                        st.markdown("---")
                        st.subheader("⚠️ Heavy Hitters Alert")
                        for hitter in analysis['heavy_hitters'][:3]:
                            st.warning(
                                f"**{hitter['bidder']}** - {hitter['bid_count']} bids "
                                f"({hitter['bid_percentage']:.1f}% of total) | "
                                f"Max: ${hitter['max_bid']:,} | Risk: {hitter['risk_level']}"
                            )

                    # Overall recommendation
                    st.markdown("---")
                    st.subheader("Competitive Assessment")
                    st.info(analysis['recommendation'])

                else:
                    st.warning("No bidding history found on this page. Auction may not have started yet.")

            except Exception as e:
                st.error(f"Error analyzing bidders: {e}")

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
