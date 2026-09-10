document.addEventListener("DOMContentLoaded", () => {
  fetch('articles.json')
    .then(response => {
      if (!response.ok) throw new Error("Fichier JSON introuvable");
      return response.json();
    })
    .then(data => {
      const articles = data.cybersecurity || [];
      const container = document.getElementById('cyber-feed');
      const counter = document.getElementById('total-incidents');

      if (counter) counter.textContent = articles.length;

      if (articles.length === 0) {
        container.innerHTML = '<p style="text-align:center;">Aucun article trouvé pour le moment.</p>';
        return;
      }

      container.innerHTML = articles.map(article => `
        <div class="timeline-item">
            <div class="timeline-meta">
                <span class="axis-tag ${article.tag_class || 'tag-law'}">${article.tag || 'Threat Intelligence'}</span>
                <span class="source-text"><i class="fa-solid fa-newspaper"></i> ${article.source || 'Feedly'}</span>
            </div>
            <div class="timeline-card">
                <div class="card-split">
                    <div class="card-content">
                        <h3>${article.title}</h3>
                        <p class="summary-text">${article.summary}</p>
                        <a href="${article.link}" target="_blank" class="source-link-btn">Ouvrir l'article d'origine <i class="fa-solid fa-external-link"></i></a>
                    </div>
                    <div class="card-img-zone">
                        <img src="${article.image || 'images/default-cyber.jpg'}" alt="${article.title}">
                    </div>
                </div>
            </div>
        </div>
      `).join('');
    })
    .catch(err => {
      console.error("Erreur de chargement de la veille :", err);
      document.getElementById('cyber-feed').innerHTML = '<p style="color:red; text-align:center;">Erreur lors du chargement des articles.</p>';
    });
});
