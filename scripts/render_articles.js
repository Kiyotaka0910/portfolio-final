(() => {
  "use strict";

  const path = window.location.pathname.toLowerCase();
  const category = path.endsWith("veille-ia.html")
    ? "ia"
    : path.endsWith("veille-cybersecurite.html")
      ? "cybersecurite"
      : null;

  // Les anciennes images locales peuvent ne plus exister dans le dépôt de test.
  document.querySelectorAll(".card-img-zone img").forEach((img) => {
    img.addEventListener("error", () => {
      const zone = img.closest(".card-img-zone");
      if (zone) zone.remove();
    }, { once: true });
  });

  if (!category) return;

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);

  fetch("./data/articles.json", { cache: "no-store" })
    .then((response) => {
      if (!response.ok) throw new Error("Le fichier des articles n'est pas disponible.");
      return response.json();
    })
    .then((data) => {
      const feed = document.querySelector(".timeline-feed");
      if (!feed) return;

      const articles = Array.isArray(data[category]) ? data[category] : [];
      const existingUrls = new Set(
        Array.from(feed.querySelectorAll('.source-link-btn[href]'))
          .map((link) => canonicalize(link.href))
      );

      const fresh = articles.filter((article) => {
        const url = canonicalize(article.url);
        if (!url || existingUrls.has(url)) return false;
        existingUrls.add(url);
        return true;
      });

      fresh.slice().reverse().forEach((article) => {
        const item = document.createElement("div");
        item.className = "timeline-item";

        const source = escapeHtml(article.source || "Source RSS");
        const title = escapeHtml(article.title || "Article de veille");
        const summary = escapeHtml(article.summary || "Résumé non fourni par la source. Ouvrez l'article pour en savoir plus.");
        const url = escapeHtml(article.url || "#");
        const image = String(article.image || "").trim();
        const imageZone = /^https?:\/\//i.test(image)
          ? `<div class="card-img-zone"><img src="${escapeHtml(image)}" alt="Illustration : ${title}" loading="lazy"></div>`
          : "";

        item.innerHTML = `
          <div class="timeline-meta">
            <span class="axis-tag tag-tech">Nouvel article</span>
            <span class="source-text"><i class="fa-solid fa-newspaper"></i> ${source}</span>
          </div>
          <div class="timeline-card">
            <div class="card-split">
              <div class="card-content">
                <h3>${title}</h3>
                <p class="summary-text">${summary}</p>
                <a href="${url}" target="_blank" rel="noopener noreferrer" class="source-link-btn">Ouvrir l'article d'origine <i class="fa-solid fa-external-link"></i></a>
              </div>
              ${imageZone}
            </div>
          </div>`;
        feed.prepend(item);

        const img = item.querySelector(".card-img-zone img");
        if (img) img.addEventListener("error", () => img.closest(".card-img-zone")?.remove(), { once: true });
      });
    })
    .catch((error) => console.warn("[Veille RSS]", error));

  function canonicalize(value) {
    try {
      const url = new URL(value, window.location.href);
      url.hash = "";
      ["fbclid", "gclid"].forEach((key) => url.searchParams.delete(key));
      Array.from(url.searchParams.keys()).filter((key) => key.toLowerCase().startsWith("utm_"))
        .forEach((key) => url.searchParams.delete(key));
      url.pathname = url.pathname.replace(/\/+$/, "") || "/";
      return url.href;
    } catch {
      return "";
    }
  }
})();
