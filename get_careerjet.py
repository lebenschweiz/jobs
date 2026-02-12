import requests
import json

# ==========================================
# KONFIGURATION
# ==========================================
# Careerjet verwendet URL-Parameter für die Suche
CAREERJET_API_URL = "http://public.api.careerjet.net/search"

# Deine Suchparameter
KEYWORDS = "Software Entwickler"
LOCATION = "Schweiz" 
PAGESIZE = 20

def handler(event, context):
    """
    Diese Funktion agiert als Proxy. Der Browser ruft diese Funktion auf,
    und diese Funktion ruft dann die Careerjet API ab.
    """
    
    # Parameter für die Careerjet API
    params = {
        "keywords": KEYWORDS,
        "location": LOCATION,
        "affid": "none", 
        "user_ip": "127.0.0.1",
        "user_agent": "Mozilla/5.0",
        "locale_code": "de_CH", 
        "pagesize": PAGESIZE,
        "sort": "date" 
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # Wir führen den Request auf dem Server aus, um CORS zu umgehen
        response = requests.get(CAREERJET_API_URL, params=params, headers=headers, timeout=10)
        
        # Falls Careerjet einen Fehler liefert
        if response.status_code != 200:
            return {
                "statusCode": response.status_code,
                "body": json.dumps({"error": "Careerjet API nicht erreichbar"})
            }

        data = response.json()
        jobs = data.get("jobs", [])
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*" # Damit dein Frontend darauf zugreifen kann
            },
            "body": json.dumps(jobs)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }