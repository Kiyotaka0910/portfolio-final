import hashlib
import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import feedparser
import requests

ROOT = Path(__file__).resolve().parents[1]
FEEDS_FILE = ROOT / "feeds.json"
ARTICLES_FILE = ROOT / "data" / "articles.json"
PAGE_FILES = {
    "ia": ROOT / "veille-ia.html",
    "cybersecurite": ROOT / "veille-cybersecurite.html",
}
MAX_NEW_PER_CATEGORY = 2
HEADERS = {"User-Agent": "PortfolioVeilleBot/1.0 (+GitHub Actions RSS updater)"}


def clean_text(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def canonical_url(url):
    url = (url or "").strip()
    if not url:
        return ""
    parts = urlsplit(url)
    kept = []
    for item in parts.query.split("&") if parts.query else []:
        key = item.split("=", 1)[0].lower()
        if key.startswith("utm_") or key in {"fbclid", "gclid"}:
            continue
        kept.append(item)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/") or "/", "&".join(kept), ""))


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href", "")
        url = canonical_url(href)
        if url.startswith(("http://", "https://")):
            self.urls.add(url)


def existing_page_urls():
    urls = set()
    for path in PAGE_FILES.values():
        if path.exists():
            parser = LinkParser()
            try:
                parser.feed(path.read_text(encoding="utf-8"))
                urls.update(parser.urls)
            except OSError as exc:
                print(f"[WARN] Impossible de lire {path.name}: {exc}")
    return urls


def get_entry_image(entry):
    for key in ("media_thumbnail", "media_content"):
        values = entry.get(key, [])
        if isinstance(values, dict):
            values = [values]
        for item in values:
            if item.get("url"):
                return item["url"]

    for item in entry.get("enclosures", []):
        href = item.get("href") or item.get("url")
        media_type = item.get("type", "")
        if href and (media_type.startswith("image/") or re.search(r"\.(jpg|jpeg|png|webp|avif)(\?|$)", href, re.I)):
            return href

    html_content = entry.get("summary", "") or entry.get("description", "")
    match = re.search(r"""<img\b[^>]*\bsrc=["']([^"']+)["']""", html_content, re.I)
    return html.unescape(match.group(1)) if match else ""


def page_image(article_url):
    if not article_url:
        return ""
    try:
        response = requests.get(article_url, headers=HEADERS, timeout=8)
        response.raise_for_status()
        head = response.text[:150_000]
        patterns = [
            r"""<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']""",
            r"""<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']""",
            r"""<meta[^>]+name=["']twitter:image["'][^>]+content=["']([^"']+)["']""",
        ]
        for pattern in patterns:
            match = re.search(pattern, head, re.I)
            if match:
                return html.unescape(match.group(1))
    except requests.RequestException as exc:
        print(f"[INFO] Image non récupérée pour {article_url}: {exc}")
    return ""


def entry_date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        try:
            return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
        except (TypeError, ValueError):
            pass
    return datetime.now(timezone.utc).isoformat()


def load_json(path, default):
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main():
    feeds = load_json(FEEDS_FILE, {})
    existing = load_json(ARTICLES_FILE, {"ia": [], "cybersecurite": []})
    ARTICLES_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Les URL déjà présentes dans les pages statiques sont également exclues.
    page_urls = existing_page_urls()
    total_added = 0

    for category in ("ia", "cybersecurite"):
        old_articles = existing.get(category, [])
        known_urls = set(page_urls)
        known_urls.update(
            canonical_url(article.get("url", ""))
            for article in old_articles if article.get("url")
        )
        candidates = []

        for feed_info in feeds.get(category, []):
            feed_url = (feed_info.get("url") or "").strip()
            if not feed_url:
                continue
            print(f"[INFO] Lecture du flux : {feed_info.get('name', feed_url)}")
            parsed = feedparser.parse(feed_url)
            if parsed.bozo and not parsed.entries:
                print(f"[WARN] Flux inaccessible ou invalide : {feed_url}")
                continue

            # On parcourt tous les éléments fournis par le flux, pas uniquement le premier.
            for entry in parsed.entries:
                url = canonical_url(entry.get("link", ""))
                title = clean_text(entry.get("title", ""))
                if not url or not title or url in known_urls:
                    continue
                summary = clean_text(entry.get("summary", "") or entry.get("description", ""))
                candidates.append({
                    "id": hashlib.sha256(url.encode("utf-8")).hexdigest()[:16],
                    "title": title,
                    "url": url,
                    "source": feed_info.get("name") or parsed.feed.get("title", "Source RSS"),
                    "published": entry_date(entry),
                    "summary": summary[:500],
                    "image": get_entry_image(entry),
                })
                known_urls.add(url)

        # Choisir les deux articles les plus récents parmi l'ensemble des flux de la catégorie.
        candidates.sort(key=lambda item: item["published"], reverse=True)
        additions = candidates[:MAX_NEW_PER_CATEGORY]

        for article in additions:
            if not article["image"]:
                article["image"] = page_image(article["url"])

        existing[category] = additions + old_articles
        total_added += len(additions)
        print(f"[INFO] {category}: {len(additions)} nouvel(aux) article(s) ajouté(s) (maximum {MAX_NEW_PER_CATEGORY}).")

    with ARTICLES_FILE.open("w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"[OK] {total_added} article(s) ajouté(s). Fichier : {ARTICLES_FILE}")


if __name__ == "__main__":
    main()
