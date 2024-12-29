from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Your CoinMarketCap API key
CMC_API_KEY = "a2ad9fd9-4f3d-43c7-8ad4-8efdc64c8673"
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

@app.route('/api/interactions', methods=['POST'])
def handle_interaction():
    if request.json['type'] == 1:  # Discord PING
        return jsonify({"type": 1})
    
    if request.json['type'] == 2:  # Application Command
        command_name = request.json['data']['name']
        
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
                    message = "Top 10 Cryptocurrencies:\n"
                    for crypto in data:
                        price = crypto['quote']['USD']['price']
                        message += f"{crypto['name']} ({crypto['symbol']}): ${price:.2f}\n"
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
    app.run(host='0.0.0.0', port=5000)
