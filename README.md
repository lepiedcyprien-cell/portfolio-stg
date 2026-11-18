# Portfolio de recherche de stage

Un site en Python (Flask) qui se découvre en faisant défiler la page avec la molette :
une présentation, tes compétences, ce que tu aimes, ton parcours, puis trois calculateurs
liés à la vente automobile (financement, marge, seuil de rentabilité) qui prouvent ce que tu sais faire.

Aucune bibliothèque JavaScript : tout est écrit à la main, les calculs sont en Python et testés.

## 1. Personnaliser le site (5 minutes)

Tout le contenu est dans **`config.py`**. Tu n'as pas besoin de toucher au reste.

| À changer | Où |
|---|---|
| Ton prénom et ton nom | `PRENOM_NOM` |
| LinkedIn, GitHub, e-mail | `LINKEDIN`, `GITHUB`, `EMAIL` |
| Ton CV | mets le PDF dans `public/` (par exemple `public/cv.pdf`), puis `CV_URL = "/cv.pdf"` |
| Tes photos (facultatif) | mets-les dans `public/img/`, puis renseigne `PHOTOS`, par exemple `"/img/portrait.jpg"` |
| Les textes, les compétences, les passions, les projets | `PRESENTATION`, `COMPETENCES`, `PASSIONS`, `PROJETS` |

Tant que `CV_URL` est vide, le bouton affiche « Demander mon CV » et ouvre un e-mail vers toi.
Tant qu'une photo est vide, le site affiche un habillage graphique : il est déjà complet sans image.

**À relire absolument** : les textes de compétences et de passions ont été rédigés à partir de ce que tu m'as dit.
Corrige tout ce qui ne te ressemble pas. Un recruteur peut t'interroger sur chaque ligne.

Conseil pour les photos : moins de 500 Ko chacune, 1 600 px de large au maximum.

## 2. Tester sur ton ordinateur

```bash
pip install -r requirements.txt
python app.py
```

Ouvre ensuite http://127.0.0.1:5001. Pour lancer les 30 tests de calcul et de sécurité :

```bash
pip install pytest
python -m pytest -q
```

## 3. Mettre le site en ligne avec un lien public

La méthode ci-dessous utilise Vercel, qui sait héberger une application Flask sans configuration :
il repère `app.py` et la variable `app`, et sert le dossier `public/` directement.
Le plan gratuit (Hobby) existe : la documentation indique par exemple 100 Go de transfert et 1 000 000 d'appels de fonction par mois,
largement assez pour un portfolio. Les conditions peuvent changer, vérifie-les sur
[vercel.com/docs/plans/hobby](https://vercel.com/docs/plans/hobby) avant de t'inscrire.

**Méthode A : depuis GitHub (la plus simple à refaire plus tard)**

1. Crée un compte sur [github.com](https://github.com), puis un nouveau dépôt **public** nommé par exemple `portfolio-stage`.
2. Envoie-y tous les fichiers de ce dossier (sur la page du dépôt : *Add file → Upload files*, puis *Commit changes*).
   Garde la structure : `app.py`, `config.py`, `requirements.txt`, et les dossiers `templates/` et `public/`.
3. Crée un compte sur [vercel.com](https://vercel.com) en choisissant « Continue with GitHub ».
4. Sur Vercel, ajoute un nouveau projet (*Add New → Project*), choisis ton dépôt `portfolio-stage`, puis lance le déploiement (*Deploy*) sans rien modifier.
5. Au bout d'une ou deux minutes, Vercel te donne une adresse du type `portfolio-stage.vercel.app`.
   C'est ce lien que tu mets sur LinkedIn.
6. Pour modifier le site plus tard : change le fichier sur GitHub, Vercel republie tout seul.

**Méthode B : en ligne de commande**

```bash
npm install -g vercel
vercel login
vercel deploy --prod
```

Les boutons et menus de Vercel changent de temps en temps : si un libellé ne correspond pas exactement, cherche le plus proche.

**Avant de publier le lien sur LinkedIn**, ouvre-le sur ton téléphone et sur un autre navigateur,
et vérifie que le CV s'ouvre, que l'e-mail et les liens sont les bons, et que les trois calculateurs répondent.

## 4. Comment le site est construit

- `app.py` : le serveur Flask, les routes de calcul (`/api/...`) et les en-têtes de sécurité.
- `calculs.py` : toutes les formules (mensualité, capacité d'emprunt, marge, seuil de rentabilité), sans dépendance.
- `config.py` : tous les textes et liens.
- `templates/index.html` : la page.
- `public/` : le style (`css/`), le comportement (`js/`), la police (`fonts/`) et tes images (`img/`).
- `test_calculs.py`, `test_app.py` : les tests automatiques.

Le défilement « façon site automobile premium » repose sur des scènes qui restent fixées à l'écran pendant que tu défiles.
Si la personne a réglé son système sur « réduire les animations », elles sont désactivées.
Sur téléphone et sur petit écran, les scènes s'empilent normalement.

## Licences

La police Archivo (variable) est sous licence SIL Open Font License : le texte est dans `public/fonts/LICENSE-Archivo-OFL.txt`.
