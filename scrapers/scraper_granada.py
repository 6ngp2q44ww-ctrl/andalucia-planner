import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AndaluciaBot/1.0)"
}

SOURCES = [
    {
        "url": "https://worldonabudget.de/granada-sehenswuerdigkeiten/",
        "type": "editorial travel guide",
        "city": "Granada"
    },
    {
        "url": "https://travelsaroundspain.com/granada-hidden-gems/",
        "type": "editorial travel guide",
        "city": "Granada"
    },
    {
        "url": "https://reisen-nach-spanien.com/andalusien/provinz-granada/granada",
        "type": "official tourism",
        "city": "Granada"
    }
]

def scrape_page(url):
    """Lädt eine Seite und gibt Text-Absätze zurück."""
    try:
        time.sleep(random.uniform(1.5, 2.5))  # Rate-Limiting
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Entferne Navigation, Footer, Scripts
        for tag in soup(["nav", "footer", "script", "style", "header"]):
            tag.decompose()

        paragraphs = []
        for p in soup.find_all(["p", "h2", "h3", "li"]):
            text = p.get_text(strip=True)
            if len(text) > 40:  # Nur sinnvolle Texte
                paragraphs.append({
                    "tag": p.name,
                    "text": text[:500]  # Max 500 Zeichen
                })

        return paragraphs[:30]  # Max 30 Absätze pro Seite

    except requests.RequestException as e:
        print(f"  Fehler bei {url}: {e}")
        return []

def normalize_to_entry(raw_text, source_url, source_type, city):
    """
    Erstellt einen normalisierten Eintrag aus rohem Text.
    In Produktion: Claude API hier einbinden für intelligente Extraktion.
    """
    return {
        "id": f"scraped_{hash(raw_text) % 99999}",
        "name": "Zu verifizieren",
        "city": city,
        "district": "Unbekannt",
        "category": "sehenswürdigkeit",
        "tags": [],
        "short": raw_text[:120],
        "long": raw_text,
        "price": "—",
        "duration": "—",
        "hours": "—",
        "booking": False,
        "best": "—",
        "gem": False,
        "family": False,
        "evening": False,
        "indoor": False,
        "outdoor": False,
        "lat": 37.1760,
        "lng": -3.5881,
        "url": source_url,
        "sources": [{"type": source_type, "url": source_url, "conf": 0.6}],
        "conf": 0.6,
        "note": "Automatisch gescrapt — manuelle Überprüfung nötig",
        "emoji": "📍",
        "scraped_at": datetime.now().isoformat()
    }

def run():
    all_entries = []

    for source in SOURCES:
        print(f"\nScrape: {source['url']}")
        paragraphs = scrape_page(source["url"])
        print(f"  {len(paragraphs)} Absätze gefunden")

        for para in paragraphs[:5]:  # Top 5 Absätze als Kandidaten
            if para["tag"] in ["h2", "h3"]:  # Überschriften = potenzielle Orte
                entry = normalize_to_entry(
                    para["text"],
                    source["url"],
                    source["type"],
                    source["city"]
                )
                all_entries.append(entry)

    # JSON exportieren
    output = {
        "scraped_at": datetime.now().isoformat(),
        "city": "Granada",
        "count": len(all_entries),
        "entries": all_entries
    }

    with open("data/granada.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nFertig: {len(all_entries)} Einträge → data/granada.json")

if __name__ == "__main__":
    run()

