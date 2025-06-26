import requests
from bs4 import BeautifulSoup
from functools import lru_cache
import sqlite3
import json
from datetime import datetime

# Database setup (same as before)
DB_PATH = 'eta_cache.db'

def init_db():
    """Initialize the database"""
    # ... (keep existing database code)

def get_bus_eta_api(route, stop_id, company='KMB'):
    """
    Primary method: Get bus ETA from official API
    """
    base_url = "https://data.etabus.gov.hk/v1/transport/kmb/eta"
    url = f"{base_url}/{stop_id}/{route}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except requests.exceptions.RequestException:
        return None  # Signal that API failed

def get_bus_eta_scrape(route, stop_id, company='KMB'):
    """
    Fallback method: Scrape ETA from website when API fails
    """
    try:
        # Example - you'll need to research actual HK bus sites to scrape
        if company == 'KMB':
            url = f"https://search.kmb.hk/KMBWebSite/ETA/ETAResult.aspx?route={route}&stop={stop_id}"
        else:
            url = f"https://otherbuscompany.com/eta?route={route}&stop={stop_id}"
        
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # You'll need to inspect the actual website structure
        etas = []
        for item in soup.select('.eta-item'):
            time = item.select_one('.time').text.strip()
            remark = item.select_one('.remark').text.strip()
            etas.append({
                'route': route,
                'eta': time,  # May need to convert to ISO format
                'rmk_en': remark,
                'dir': 'OUTBOUND'  # Example - get actual direction
            })
        return etas
    except Exception as e:
        print(f"Scraping failed: {e}")
        return None

@lru_cache(maxsize=128)
def get_bus_eta(route, stop_id, company='KMB'):
    """
    Main function that tries API first, falls back to scraping
    """
    # Try to get cached data first
    cached_data = get_cached_eta(route, stop_id, company)
    if cached_data:
        return cached_data
    
    # Try official API first
    api_data = get_bus_eta_api(route, stop_id, company)
    if api_data is not None:
        cache_eta(route, stop_id, company, api_data)
        return api_data
    
    # If API fails, try scraping
    print("API failed, attempting web scraping...")
    scraped_data = get_bus_eta_scrape(route, stop_id, company)
    if scraped_data:
        cache_eta(route, stop_id, company, scraped_data)
        return scraped_data
    
    # If both methods fail
    print("Both API and scraping failed for", route, stop_id)
    return []
