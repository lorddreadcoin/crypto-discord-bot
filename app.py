from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from discord_interactions import verify_key, InteractionType, InteractionResponseType
import json

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Your CoinMarketCap API key
CMC_API_KEY = os.getenv('CMC_API_KEY', 'a2ad9fd9-4f3d-43c7-8ad4-8efdc64c8673')
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# Discord Public Key
DISCORD_PUBLIC_KEY = "6118424de56e617b9e795e9c74394097ece7e64d3e6cf2cc7ef9c3cba9ad98e1"

@app.route('/')
def home():
    return "Crypto Discord Bot is running!"

def verify_discord_request():
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    
    if not signature or not timestamp:
        return False
        
    body = request.data
    
    return verify_key(body, signature, timestamp, DISCORD_PUBLIC_KEY)

@app.route('/api/interactions', methods=['POST'])
def handle_interaction():
    # Verify request
    if not verify_discord_request():
        return 'Invalid request signature', 401

    # Parse the request data
    interaction = request.json
    
    # Handle PING (type 1)
    if interaction.get('type') == InteractionType.PING:
        return jsonify({
            "type": InteractionResponseType.PONG
        })
    
    # Handle Slash Command (type 2)
    if interaction.get('type') == InteractionType.APPLICATION_COMMAND:
        command_name = interaction.get('data', {}).get('name')
        
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
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {
                        "content": message
                    }
                })
                
            except Exception as e:
                return jsonify({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {
                        "content": f"Error: {str(e)}"
                    }
                })

    return jsonify({"error": "Unknown command"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
