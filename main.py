#!/usr/bin/env python3
"""
Jay - BringATrailer Auction Agent
Main entry point
"""

import sys
from src.config.credentials import get_credentials
from src.browser.launcher import BrowserManager
from src.db.database import init_database, get_connection

def main():
    print('🤖 Jay - BringATrailer Agent Starting...\n')

    try:
        # Test credentials
        credentials = get_credentials()
        print(f'✓ Credentials loaded for user: {credentials["username"]}')

        # Initialize database
        init_database()

        # Launch browser
        browser = BrowserManager()
        browser.launch()

        # Test login
        if browser.login():
            print('\n📋 Jay is ready. Next steps:')
            print('1. ✓ Browser automation working')
            print('2. ✓ Database initialized')
            print('3. Build auction scraper')
            print('4. Build real-time monitoring')
            print('5. Build analysis & strategy')
            print('6. Implement automated bidding (after testing)\n')

        browser.close()

    except Exception as error:
        print(f'❌ Error starting Jay: {error}')
        sys.exit(1)

if __name__ == '__main__':
    main()
