import json
import re
import feedparser
from urllib.parse import urljoin

SOURCES_CYBER = [
    "https://incyber.org/feed/",
    "https://www.cert.ssi.gouv.fr/feed/"
]

FALLBACK_CYBER = "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80"
FALLBACK_CERT = "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=600&q=80"

def clean_html(text):
    if not text:
        return ""
    clean = re.sub('<[^<]+?>', '', text)
    return clean[:250].strip() + "..." if len(clean) > 250 else clean.strip()

def extract_image(entry, base_url):
    # 1. Media content RSS
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            url = media.get('url')
            if url and not url.endswith(('.gif', '.ico')):
                return urljoin(base_url, url)
    
    # 2. Enclosures RSS
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            url = enc.get('href')
            if url and any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                return urljoin(base_url, url)

    # 3. Extraction dans le texte HTML
    content = ""
    if hasattr(entry, 'content'):
        for c in entry.content:
            content += c.get('value', '')
    content += getattr(entry, 'summary', '') + getattr(entry, 'description', '')

    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
    if match:
        img_url = match.group(1)
        if not any(bad in img_url.lower() for bad in ['pixel', 'avatar', 'logo', '1x1', '.gif', 'feeds.feedburner']):
            return urljoin(base_url, img_url)

    return None

cyber_articles = []

for url in SOURCES_CYBER:
    feed = feedparser.parse(url)
    source_title = feed.feed.get("title", "Source Cyber")

    for entry in feed.entries[:8]:
        img_url = extract_image(entry, url)
        
        if not img_url:
            img_url = FALLBACK_CERT if "CERT" in source_title.upper() or "CERT" in url.upper() else FALLBACK_CYBER

        summary_raw = getattr(entry, 'summary', getattr(entry, 'description', ''))

        article = {
            "title": entry.title,
            "link": entry.link,
            "summary": clean_html(summary_raw),
            "tag": "Threat Intelligence",
            "tag_class": "tag-law",
            "source": source_title,
            "image": img_url
        }
        cyber_articles.append(article)

data = {
    "cybersecurity": cyber_articles,
    "ia": []
}

with open("articles.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Succès ! {len(cyber_articles)} articles générés.")
