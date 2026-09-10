import json
import os
import feedparser

# Remplace les URLs ci-dessous par les liens RSS de tes dossiers/tableaux Feedly
FEEDS = {
    "cybersecurity": "https://incyber.org/feed/", # Ex: Flux RSS InCyber ou ton flux Feedly
    "ia": "https://sante.Incyber.org/feed/"         # Remplace par ton flux RSS IA Feedly
}

JSON_FILE = "articles.json"

# 1. Charger les articles existants
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {"cybersecurity": [], "ia": []}

# 2. Parcourir chaque catégorie et ajouter au maximum 2 nouveaux articles
for category, rss_url in FEEDS.items():
    parsed_feed = feedparser.parse(rss_url)
    existing_links = {art["link"] for art in data.get(category, [])}
    
    added_count = 0
    for entry in parsed_feed.entries:
        if added_count >= 2:
            break
            
        if entry.link not in existing_links:
            # Récupérer l'image si disponible
            image_url = "images/default-cyber.jpg"
            if "media_content" in entry and len(entry.media_content) > 0:
                image_url = entry.media_content[0].get("url", image_url)
                
            new_article = {
                "title": entry.title,
                "link": entry.link,
                "summary": getattr(entry, "summary", getattr(entry, "description", ""))[:250] + "...",
                "tag": "Mise à jour mensuelle",
                "tag_class": "tag-law",
                "source": "Feedly",
                "image": image_url
            }
            # Insérer en haut de liste
            data[category].insert(0, new_article)
            added_count += 1

# 3. Enregistrer les modifications dans le fichier JSON
with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Synchronisation mensuelle terminée !")
