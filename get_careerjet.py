import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
import os

app = Flask(__name__)

# --- KONFIGURATION ---
SEARCH_QUERY = "Software Entwickler"
LOCATION = "Schweiz"

def get_jobs():
    """
    Robuster Scraper für Careerjet.
    Versucht mehrere URLs, um Blockaden oder 404-Fehler zu umgehen.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "de-CH,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    # Liste möglicher Such-URLs (Careerjet ändert diese manchmal)
    urls_to_try = [
        # Methode 1: Moderne Suche
        {
            "url": "https://www.careerjet.ch/search/results.html",
            "params": {"s": SEARCH_QUERY, "l": LOCATION, "sort": "date"}
        },
        # Methode 2: Klassische WS-Suche (Fallback)
        {
            "url": "https://www.careerjet.ch/ws/suche/l/s.html",
            "params": {"s": SEARCH_QUERY, "l": LOCATION}
        }
    ]

    for attempt in urls_to_try:
        try:
            print(f"Versuche URL: {attempt['url']}")
            response = requests.get(attempt['url'], params=attempt['params'], headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Erfolg! Parsing starten
                soup = BeautifulSoup(response.text, 'html.parser')
                jobs = []
                
                # Wir suchen breit nach Job-Artikeln
                job_listings = soup.select('article.job, .job, .job-display')

                for item in job_listings:
                    title_el = item.select_one('h2 a, .title a, a.job-title')
                    comp_el = item.select_one('.company_name, .company')
                    loc_el = item.select_one('.location')
                    desc_el = item.select_one('.desc, .description, .job-snippet')
                    
                    if title_el:
                        title = title_el.get_text(strip=True)
                        link = title_el['href']
                        if link.startswith('/'):
                            link = "https://www.careerjet.ch" + link
                        
                        jobs.append({
                            "title": title,
                            "link": link,
                            "company": comp_el.get_text(strip=True) if comp_el else "Firma unbekannt",
                            "location": loc_el.get_text(strip=True) if loc_el else "Schweiz",
                            "description": desc_el.get_text(strip=True) if desc_el else "Klicken für Details..."
                        })
                
                if jobs:
                    return jobs
            
        except Exception as e:
            print(f"Fehler bei Versuch {attempt['url']}: {e}")
            continue # Probiere nächste URL

    return [] # Nichts gefunden

@app.route('/')
def index():
    jobs = get_jobs()
    
    html = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Radar Schweiz</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background: #d32f2f; color: white; padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 30px; }
            .job-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #d32f2f; transition: transform 0.2s; }
            .job-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            .title { color: #d32f2f; font-size: 1.25rem; font-weight: bold; text-decoration: none; display: block; margin-bottom: 5px; }
            .meta { font-size: 0.9rem; color: #666; margin-bottom: 10px; font-weight: 500; }
            .desc { font-size: 0.95rem; color: #444; line-height: 1.5; }
            .no-jobs { background: white; padding: 40px; text-align: center; border-radius: 8px; color: #666; }
            .btn { display: inline-block; background: #d32f2f; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 0.9rem; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🇨🇭 Job-Radar</h1>
                <p>Live Scraper für Careerjet</p>
            </div>
            
            {% if jobs %}
                {% for job in jobs %}
                <div class="job-card">
                    <a href="{{ job.link }}" target="_blank" class="title">{{ job.title }}</a>
                    <div class="meta">🏢 {{ job.company }} &nbsp;|&nbsp; 📍 {{ job.location }}</div>
                    <div class="desc">{{ job.description }}</div>
                    <a href="{{ job.link }}" target="_blank" class="btn">Zum Inserat</a>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-jobs">
                    <h3>Keine Ergebnisse gefunden</h3>
                    <p>Entweder gibt es keine passenden Stellen, oder Careerjet blockiert die Anfrage momentan.</p>
                </div>
            {% endif %}
            
            <p style="text-align: center; color: #999; font-size: 0.8rem; margin-top: 40px;">Datenquelle: Careerjet.ch</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, jobs=jobs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
