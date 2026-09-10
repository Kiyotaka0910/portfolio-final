import json
import re
import feedparser

# 1. LISTE DES SOURCES DE TON DOSSIER FEEDLY
SOURCES_CYBER = [
    "https://incyber.org/feed/",           # Source : INCYBER NEWS
    "https://www.cert.ssi.gouv.fr/feed/"   # Source : CERT-FR
]

def clean_html(text):
    """Enlève les balises HTML pour garder un résumé propre"""
    if not text:
        return ""
    clean = re.sub('<[^<]+?>', '', text)
    return clean[:250].strip() + "..." if len(clean) > 250 else clean.strip()

def find_image(entry):
    """Cherche l'image dans les balises RSS ou directement dans le texte HTML"""
    # Recherche 1 : Balises RSS officielles
    if hasattr(entry, 'media_content') and entry.media_content:
        url = entry.media_content[0].get('url')
        if url: return url
    if hasattr(entry, 'enclosures') and entry.enclosures:
        url = entry.enclosures[0].get('href')
        if url: return url

    # Recherche 2 : Extraction de la balise <img src="..."> dans le texte
    full_text = ""
    if hasattr(entry, 'content'):
        for c in entry.content:
            full_text += c.get('value', '')
    full_text += getattr(entry, 'summary', '') + getattr(entry, 'description', '')

    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', full_text, re.IGNORECASE)
    if match:
        return match.group(1)

    return None

# Images par défaut si la source n'en fournit pas
FALLBACK_IMAGES = {
    "CERT": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=600&q=80",
    "DEFAULT": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80"
}

cyber_articles = []
print("Récupération intelligente des articles et des visuels...")

for url in SOURCES_CYBER:
    feed = feedparser.parse(url)
    source_title = feed.feed.get("title", "Source Veille")

    for entry in feed.entries[:8]:
        # Récupération ou attribution d'une image
        image_url = find_image(entry)
        if not image_url:
            image_url = FALLBACK_IMAGES["CERT"] if "CERT" in source_title.upper() or "CERT" in url.upper() else FALLBACK_IMAGES["DEFAULT"]

        summary_raw = getattr(entry, 'summary', getattr(entry, 'description', ''))

        article = {
            "title": entry.title,
            "link": entry.link,
            "summary": clean_html(summary_raw),
            "tag": "Threat Intelligence",
            "tag_class": "tag-law",
            "source": source_title,
            "image": image_url
        }
        cyber_articles.append(article)

# Sauvegarde dans articles.json
data = {
    "cybersecurity": cyber_articles,
    "ia": []
}

with open("articles.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Succès ! {len(cyber_articles)} articles mis à jour avec leurs visuels.")
