import json
import re
import feedparser

# 1. LISTE DES SOURCES DE TON DOSSIER FEEDLY "cybersecurite"
SOURCES_CYBER = [
    "https://incyber.org/feed/",           # Source : INCYBER NEWS
    "https://www.cert.ssi.gouv.fr/feed/"   # Source : CERT-FR
    # Si tu t'abonnes à d'autres sources sur Feedly, tu pourras ajouter leurs liens ici
]

def clean_html(text):
    if not text:
        return ""
    clean = re.sub('<[^<]+?>', '', text)
    return clean[:250] + "..." if len(clean) > 250 else clean

FALLBACK_IMAGE = "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80"

cyber_articles = []

print("Récupération automatique des articles Feedly...")

for url in SOURCES_CYBER:
    feed = feedparser.parse(url)
    
    # On prend les 8 derniers articles de chaque source
    for entry in feed.entries[:8]:
        image_url = FALLBACK_IMAGE
        if hasattr(entry, 'media_content') and entry.media_content:
            image_url = entry.media_content[0].get('url', FALLBACK_IMAGE)
        elif hasattr(entry, 'enclosures') and entry.enclosures:
            image_url = entry.enclosures[0].get('href', FALLBACK_IMAGE)

        summary_raw = getattr(entry, 'summary', getattr(entry, 'description', ''))

        article = {
            "title": entry.title,
            "link": entry.link,
            "summary": clean_html(summary_raw),
            "tag": "Threat Intelligence",
            "tag_class": "tag-law",
            "source": feed.feed.get("title", "Feedly Source"),
            "image": image_url
        }
        cyber_articles.append(article)

# On enregistre tout directement dans articles.json
data = {
    "cybersecurity": cyber_articles,
    "ia": []
}

with open("articles.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Succès ! {len(cyber_articles)} articles récupérés depuis tes sources Feedly.")
