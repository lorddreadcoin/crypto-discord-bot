from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
import nacl.signing
import json

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Your CoinMarketCap API key
CMC_API_KEY = os.getenv('CMC_API_KEY', 'a2ad9fd9-4f3d-43c7-8ad4-8efdc64c8673')
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# Discord Public Key (full key)
PUBLIC_KEY = "6118424de56e617b9e795e9c74394097ece7e64d3e6cf2cc7ef9c3cba9ad98e1"
verify_key = nacl.signing.VerifyKey(bytes.fromhex(PUBLIC_KEY))

@app.route('/')
def home():
    return "Crypto Discord Bot is running!"

@app.route('/api/interactions', methods=['POST'])
def handle_interaction():
    # Verify the request
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')
    
    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except Exception as e:
        return 'Invalid request signature', 401

    # Handle the interaction
    interaction = request.json
    
    if interaction.get('type') == 1:  # PING
        return jsonify({"type": 1})
    
    if interaction.get('type') == 2:  # APPLICATION_COMMAND
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
