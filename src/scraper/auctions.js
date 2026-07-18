// Auction data scraper
// Extracts auction info and bidding history from BringATrailer

const cheerio = require('cheerio');
const { baBaseUrl } = require('../config/credentials');

class AuctionScraper {
  async parseAuctionPage(html) {
    const $ = cheerio.load(html);

    // Extract auction details (structure varies by page, needs refinement after testing)
    const auctionData = {
      title: $('h1.auction-title').text().trim(),
      askingPrice: this.parsePrice($('.asking-price').text()),
      currentBid: this.parsePrice($('.current-bid').text()),
      bidCount: parseInt($('.bid-count').text()) || 0,
      endsAt: $('[data-ends-at]').attr('data-ends-at'),
      imageUrl: $('img.main-image').attr('src'),
      description: $('.description').text().trim()
    };

    // Extract bidding history
    const biddingHistory = [];
    $('table.bid-history tbody tr').each((i, el) => {
      biddingHistory.push({
        bidder: $(el).find('td.bidder').text().trim(),
        amount: this.parsePrice($(el).find('td.amount').text()),
        timestamp: $(el).find('td.time').attr('data-timestamp')
      });
    });

    return { auctionData, biddingHistory };
  }

  parsePrice(text) {
    const match = text.match(/\$?([\d,]+)/);
    return match ? parseInt(match[1].replace(/,/g, '')) : 0;
  }

  async extractCompetitors(biddingHistory) {
    // Return unique bidders from this auction's history
    return [...new Set(biddingHistory.map(b => b.bidder))];
  }
}

module.exports = AuctionScraper;
