from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

from src.config.credentials import get_credentials, BA_BASE_URL

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.wait = None

    def launch(self):
        """Launch Chrome browser with Selenium"""
        print('🌐 Launching browser...')

        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Uncomment for headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={USER_AGENT}')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        """Log into BringATrailer"""
        print('🔐 Logging into BringATrailer...')

        credentials = get_credentials()
        username = credentials['username']
        password = credentials['password']

        try:
            # Navigate to login
            self.driver.get(f'{BA_BASE_URL}/login')
            time.sleep(2)

            # Find and fill username field
            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            username_field.send_keys(username)

            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, 'password')
            password_field.send_keys(password)

            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()

            # Wait for redirect after login
            time.sleep(3)

            print('✓ Login successful')
            return True

        except Exception as error:
            print(f'❌ Login failed: {error}')
            return False

    def get_auction_page(self, auction_id):
        """Navigate to an auction page"""
        url = f'{BA_BASE_URL}/auctions/{auction_id}'
        self.driver.get(url)
        return self.driver.page_source

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print('✓ Browser closed')
