import os
from dotenv import load_dotenv

load_dotenv()

def get_credentials():
    username = os.getenv('BA_USERNAME')
    password = os.getenv('BA_PASSWORD')

    if not username or not password:
        raise ValueError(
            'BringATrailer credentials not found in .env\n'
            'Add BA_USERNAME and BA_PASSWORD from vault to .env file\n'
            'Never commit .env to git'
        )

    return {'username': username, 'password': password}

BA_BASE_URL = 'https://www.bringatrailer.com'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
