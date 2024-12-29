from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from discord_interactions import verify_key_decorator
import json

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Your CoinMarketCap API key
CMC_API_KEY = os.getenv('CMC_API_KEY', 'a2ad9fd9-4f3d-43c7-8ad4-8efdc64c8673')
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# Discord Public Key (from your Discord Application)
DISCORD_PUBLIC_KEY = "6118424de54e617b9e7995e7c7439409f7ece7e644d3e6cf2cc7ef9c3cba9d98c1"

@app.route('/')
def home():
    return "Crypto Discord Bot is running!"

@app.route('/api/interactions', methods=['POST'])
@verify_key_decorator(DISCORD_PUBLIC_KEY)
def handle_interaction():
    if request.json.get('type') == 1:  # Discord PING
        return jsonify({"type": 1})
    
    if request.json.get('type') == 2:  # Application Command
        command_name = request.json.get('data', {}).get('name')
        
        if command_name == 'crypto':
            try:
                # Get cryptocurrency data from CoinMarketCap
                headers = {
                    'X-CMC_PRO_API_KEY': CMC_API_KEY,
                    'Accept': 'application/json'
                }
                response = requests.get(f"{CMC_BASE_URL}/cryptocurrency/listings/latest", 
                                     headers=headers, 
                                     params={'limit': 10})
                
                if response.status_code == 200:
                    data = response.json()['data']
                    message = "**Top 10 Cryptocurrencies:**\n"
                    for crypto in data:
                        price = crypto['quote']['USD']['price']
                        change_24h = crypto['quote']['USD']['percent_change_24h']
                        message += f"**{crypto['name']}** ({crypto['symbol']}): ${price:.2f} | 24h: {change_24h:.2f}%\n"
                else:
                    message = "Failed to fetch cryptocurrency data"
                
                return jsonify({
                    "type": 4,
                    "data": {
                        "content": message
                    }
                })
                
            except Exception as e:
                return jsonify({
                    "type": 4,
                    "data": {
                        "content": f"Error: {str(e)}"
                    }
                })
    
    return jsonify({"error": "Unknown command"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
