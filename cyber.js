document.addEventListener("DOMContentLoaded", () => {
    const feedContainer = document.getElementById("cyber-feed");
    const totalIncidents = document.getElementById("total-incidents");

    if (!feedContainer) return;

    fetch("articles.json")
        .then(response => response.json())
        .then(data => {
            const articles = data.cybersecurity || [];
            
            if (totalIncidents) {
                totalIncidents.textContent = articles.length;
            }

            if (articles.length === 0) {
                feedContainer.innerHTML = "<p style='text-align: center; color: #888;'>Aucun article disponible pour le moment.</p>";
                return;
            }

            // Image HD Cyber par défaut si l'image distante plante ou est bloquée
            const fallbackImg = "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80";

            feedContainer.innerHTML = articles.map(art => {
                const imgSrc = (art.image && art.image.trim() !== "") ? art.image : fallbackImg;

                return `
                    <div class="timeline-item">
                        <div class="timeline-badge"></div>
                        <div class="timeline-content">
                            <div class="article-card">
                                <div class="card-body">
                                    <div class="card-meta">
                                        <span class="tag ${art.tag_class || 'tag-law'}">${art.tag || 'Threat Intelligence'}</span>
                                        <span class="source-name"><i class="fa-solid fa-rss"></i> ${art.source || 'Feedly'}</span>
                                    </div>
                                    <h3 class="card-title">${art.title}</h3>
                                    <p class="card-summary">${art.summary || ''}</p>
                                    <a href="${art.link}" target="_blank" rel="noopener noreferrer" class="btn-primary">
                                        Ouvrir l'article d'origine <i class="fa-solid fa-arrow-up-right-from-square"></i>
                                    </a>
                                </div>
                                <div class="card-image-wrapper">
                                    <img src="${imgSrc}" 
                                         alt="Illustration article" 
                                         loading="lazy"
                                         onerror="this.onerror=null; this.src='${fallbackImg}';">
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join("");
        })
        .catch(err => {
            console.error("Erreur de chargement des articles :", err);
            feedContainer.innerHTML = "<p style='text-align: center; color: #ff6b6b;'>Impossible de charger les flux pour le moment.</p>";
        });
});
