// Real-time auction monitoring
// Tracks price changes, bid activity, time remaining

class AuctionMonitor {
  constructor(database) {
    this.db = database;
    this.watchlist = [];
    this.alerts = [];
  }

  async addToWatchlist(auctionId, options = {}) {
    this.watchlist.push({
      auctionId,
      targetPrice: options.targetPrice,
      maxBid: options.maxBid,
      trackedBidders: options.trackedBidders || [],
      addedAt: new Date()
    });
    console.log(`📍 Added auction ${auctionId} to watchlist`);
  }

  async checkAuction(auctionId, currentData) {
    const previous = await this.db.getAuctionData(auctionId);

    // Detect price movement
    if (previous && currentData.currentBid > previous.currentBid) {
      this.alerts.push({
        type: 'PRICE_INCREASE',
        auctionId,
        oldBid: previous.currentBid,
        newBid: currentData.currentBid,
        increase: currentData.currentBid - previous.currentBid
      });
    }

    // Detect new bidders
    if (currentData.bidCount > previous.bidCount) {
      this.alerts.push({
        type: 'NEW_BID',
        auctionId,
        bidCount: currentData.bidCount
      });
    }

    // Check if tracked competitors are bidding
    if (currentData.lastBidder && this.isTrackedCompetitor(currentData.lastBidder)) {
      this.alerts.push({
        type: 'COMPETITOR_ACTIVE',
        auctionId,
        competitor: currentData.lastBidder
      });
    }

    await this.db.updateAuction(auctionId, currentData);
  }

  isTrackedCompetitor(username) {
    // Check against list of competitors to monitor
    return false; // TODO: implement
  }

  getAlerts() {
    return this.alerts;
  }

  clearAlerts() {
    this.alerts = [];
  }
}

module.exports = AuctionMonitor;
