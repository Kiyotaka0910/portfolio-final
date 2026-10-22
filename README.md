# Portfolio de veille — automatisation RSS pour le dépôt de test

Cette version est préparée à partir des flux du fichier OPML Feedly fourni. Elle garde les cartes HTML existantes et ajoute automatiquement jusqu'à **2 nouveaux articles IA** et **2 nouveaux articles cybersécurité** par exécution.

## Fichiers inclus

- `veille-ia.html`, `veille-cybersecurite.html` et `style.css` : pages et style actuels.
- `feeds.json` : les 6 flux RSS exportés de Feedly.
- `scripts/update_articles.py` : lit les flux, évite les URL déjà présentes dans les pages et dans l'historique JSON, puis conserve les anciens articles.
- `scripts/render_articles.js` : affiche les nouvelles cartes dans les pages avec le style existant.
- `data/articles.json` : historique des articles ajoutés par l'automatisation.
- `.github/workflows/update-feedly.yml` : exécution mensuelle et lancement manuel.

## Installation dans le dépôt de test

1. Télécharge cette archive et décompresse-la sur ton ordinateur.
2. Ouvre **ton nouveau dépôt GitHub de test** (pas le portfolio principal).
3. Téléverse les fichiers et dossiers de l'archive à la racine du dépôt, en conservant la structure des dossiers. Autorise le remplacement des trois fichiers `veille-ia.html`, `veille-cybersecurite.html` et `style.css` par ceux de l'archive si ce sont bien les versions que tu as données pour ce test.
4. Dans GitHub, ouvre `Settings → Actions → General → Workflow permissions` et sélectionne `Read and write permissions`, puis enregistre.
5. Ouvre l'onglet `Actions`, sélectionne `Mettre à jour les articles de veille`, puis `Run workflow` pour lancer un premier essai.
6. Consulte les journaux de l'action et le fichier `data/articles.json`. Si des articles ont été ajoutés, attends la fin de l'action puis actualise les pages GitHub Pages.

## Planification

Le workflow s'exécute automatiquement le 5 de chaque mois à 07:00 UTC. GitHub peut retarder les exécutions planifiées. Le bouton `Run workflow` permet de tester sans attendre le mois suivant.

## À savoir

- Le système ajoute **jusqu'à** deux articles par catégorie à chaque exécution. Il ne peut pas garantir deux articles si les flux n'offrent pas deux articles inédits.
- Le script compare les liens des articles RSS avec les liens déjà présents dans les pages et dans `data/articles.json` pour limiter les doublons.
- Les flux RSS ne fournissent pas toujours assez d'anciens articles : le script examine tous les éléments exposés par chaque flux.
- Les images sont récupérées lorsqu'elles sont exposées dans le RSS ou dans les métadonnées de la page. Certains sites bloquent cette récupération ou n'offrent pas d'image ; la carte s'affichera alors sans image.
- Les anciennes images locales absentes du dépôt de test seront masquées automatiquement pour éviter les icônes d'image cassée.
- Le workflow ne peut écrire dans le dépôt que si les permissions Actions sont activées et si les règles du dépôt autorisent le push.
