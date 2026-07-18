// Browser automation using Playwright
// Handles login and page interactions

const { chromium } = require('playwright');
const { getCredentials, baBaseUrl } = require('../config/credentials');

class BrowserManager {
  constructor() {
    this.browser = null;
    this.page = null;
    this.context = null;
  }

  async launch() {
    console.log('🌐 Launching browser...');
    this.browser = await chromium.launch({
      headless: process.env.HEADLESS_BROWSER !== 'false'
    });
    this.context = await this.browser.createContext();
    this.page = await this.context.newPage();
    this.page.setDefaultTimeout(parseInt(process.env.BROWSER_TIMEOUT || 30000));
  }

  async login() {
    console.log('🔐 Logging into BringATrailer...');
    const { username, password } = getCredentials();

    try {
      // Navigate to login page
      await this.page.goto(`${baBaseUrl}/login`, { waitUntil: 'domcontentloaded' });

      // Fill login form
      await this.page.fill('input[name="username"]', username);
      await this.page.fill('input[name="password"]', password);

      // Submit form
      await this.page.click('button[type="submit"]');

      // Wait for navigation
      await this.page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 10000 });

      console.log('✓ Login successful');
      return true;
    } catch (error) {
      console.error('❌ Login failed:', error.message);
      return false;
    }
  }

  async getAuctionPage(auctionId) {
    const url = `${baBaseUrl}/auctions/${auctionId}`;
    await this.page.goto(url, { waitUntil: 'networkidle' });
    return this.page;
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      console.log('✓ Browser closed');
    }
  }
}

module.exports = BrowserManager;
