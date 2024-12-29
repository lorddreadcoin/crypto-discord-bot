# Crypto Discord Bot

This Discord bot provides cryptocurrency information using the CoinMarketCap API.

## Setup Instructions

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Deploy this Flask application to a hosting service (like Heroku, DigitalOcean, etc.)

3. Set your deployed URL in Discord Developer Portal:
   - Go to your application settings
   - In the "Interactions Endpoint URL" field, enter:
     `https://your-domain.com/api/interactions`

4. Add the /crypto command to your Discord application:
   - Go to "Bot Commands" in Discord Developer Portal
   - Create a new command:
     - Name: crypto
     - Description: Get current cryptocurrency prices

## Features
- `/crypto` - Shows top 10 cryptocurrencies with their current prices
