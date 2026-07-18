// Credential loader from vault
// Reads BringATrailer credentials from C:\Users\info\passwords\credentials.md
// in .env file for local development

require('dotenv').config();

const getCredentials = () => {
  const username = process.env.BA_USERNAME;
  const password = process.env.BA_PASSWORD;

  if (!username || !password) {
    throw new Error(
      'BringATrailer credentials not found in .env\n' +
      'Add BA_USERNAME and BA_PASSWORD from vault to .env file\n' +
      'Never commit .env to git'
    );
  }

  return { username, password };
};

module.exports = {
  getCredentials,
  baBaseUrl: 'https://www.bringatrailer.com',
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
};
