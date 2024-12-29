from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import json

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Your CoinMarketCap API key
CMC_API_KEY = os.getenv('CMC_API_KEY', 'a2ad9fd9-4f3d-43c7-8ad4-8efdc64c8673')
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# Discord Public Key
PUBLIC_KEY = bytes.fromhex("6118424de56e617b9e795e9c74394097ece7e64d3e6cf2cc7ef9c3cba9ad98e1")
verify_key = VerifyKey(PUBLIC_KEY)

@app.route('/')
def home():
    return "Crypto Discord Bot is running!"

@app.route('/api/interactions', methods=['POST'])
def handle_interaction():
    # Get the signature and timestamp from the Discord request
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    
    if not signature or not timestamp:
        print("Missing signature or timestamp")
        return 'Invalid request signature', 401

    body = request.get_data().decode('utf-8')
    
    try:
        # Verify the signature
        message = timestamp.encode() + body.encode()
        verify_key.verify(message, bytes.fromhex(signature))
        
        # Handle the interaction
        interaction = request.json
        
        if interaction.get('type') == 1:  # PING
            return jsonify({
                "type": 1
            })
        
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
        
    except BadSignatureError as e:
        print(f"Invalid signature: {str(e)}")
        return 'Invalid request signature', 401
    except Exception as e:
        print(f"Error: {str(e)}")
        return str(e), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
