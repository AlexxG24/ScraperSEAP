from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import requests
import re
import os

app = Flask(__name__)
CORS(app)

# Firecrawl API
FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY', 'fc-3d6cd173506e48d5a99e3c1b189af34d')
FIRECRAWL_URL = 'https://api.firecrawl.dev/v1/scrape'

# Cache pentru a evita scraping prea frecvent
cache = {
    "data": None,
    "timestamp": None
}
CACHE_DURATION = 300  # 5 minute

def get_data_from_gist():
    """Citeste datele din GitHub Gist (actualizat de scriptul Selenium local)"""
    GIST_URL = 'https://gist.githubusercontent.com/AlexxG24/916c4f36e09196cd4e83e8e3bafe947a/raw/seap_data.json'
    today = datetime.now().strftime("%d.%m.%Y")
    
    try:
        response = requests.get(f"{GIST_URL}?t={datetime.now().timestamp()}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            data['source'] = 'gist'
            return data
        else:
            return {
                "date": today,
                "todayCount": 0,
                "totalInSystem": 0,
                "lastUpdate": datetime.now().isoformat(),
                "error": "Could not fetch from Gist"
            }
    except Exception as e:
        return {
            "date": today,
            "todayCount": 0,
            "totalInSystem": 0,
            "lastUpdate": datetime.now().isoformat(),
            "error": str(e)
        }

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "SEAP Scraper API"})

@app.route('/api/scrape')
def api_scrape():
    global cache
    
    # Check cache
    if cache["data"] and cache["timestamp"]:
        elapsed = (datetime.now() - cache["timestamp"]).total_seconds()
        if elapsed < CACHE_DURATION:
            return jsonify({
                "success": True,
                "cached": True,
                "data": cache["data"]
            })
    
    # Get data from Gist
    data = get_data_from_gist()
    
    # Update cache
    cache["data"] = data
    cache["timestamp"] = datetime.now()
    
    return jsonify({
        "success": True,
        "cached": False,
        "data": data
    })

@app.route('/api/data')
def api_data():
    """Return cached data only (no scraping)"""
    if cache["data"]:
        return jsonify({
            "success": True,
            "data": cache["data"]
        })
    return jsonify({
        "success": False,
        "error": "No data available. Call /api/scrape first."
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
