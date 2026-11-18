"""Tout le contenu du site est ici : modifie les textes, sans toucher au reste.

Les textes entre guillemets peuvent être remplacés librement.
Laisse "" pour masquer un lien ou une photo.
"""

# ------------------------------------------------------------------ identité
PRENOM_NOM = "Lepied Cyprien"  # <- remplace par ton prénom et ton nom
TITRE = "Étudiant en BUT Techniques de Commercialisation"
ACCROCHE = "Passionné d'automobile, je cherche un stage en vente automobile."

STAGE_PERIODE = "du 11 janvier au 5 février 2027"
SECTEUR = "Vente automobile"
LIEU = "Rambouillet et environs"

# ------------------------------------------------------------------ liens
LINKEDIN = "https://www.linkedin.com/in/cyprien-lepied-051102356/"  # <- ton profil LinkedIn
GITHUB = "https://github.com/lepiedcyprien-cell/portfolio-stage"  # <- ton dépôt GitHub
EMAIL = "lepiedcyprien@gmail.com"  # <- ton adresse e-mail
CV_URL = "/_CV LEPIED Cyprien.stg.pdf"
# puis écris "/cv.pdf". Tant que c'est vide, le bouton propose de demander le CV par e-mail.
CV_URL = ""

# ------------------------------------------------------------------ photos (facultatif)
# Mets tes images dans public/img/ puis écris leur chemin, par exemple "/img/portrait.jpg".
# Sans photo, le site affiche un habillage graphique : il est déjà complet.
PHOTOS = {
    "hero": "",  # grande image d'ouverture (ta voiture, une route...), format paysage
    "portrait": "",  # ta photo, format portrait
    "passions": "",  # image de fond de la page « Ce que j'aime »
    "contact": "",  # image de fond de la page contact
}

# ------------------------------------------------------------------ présentation
PRESENTATION_TITRE = "Étudiant en commerce, passionné d'automobile."
PRESENTATION = [
    "Je suis en première année de BUT Techniques de Commercialisation à l'IUT de Rambouillet. "
    "J'y apprends à vendre, à analyser un marché et à construire une communication commerciale.",
    "L'automobile est ma passion : la mécanique autant que l'expérience du client. "
    "Je cherche un stage pour découvrir le métier de conseiller commercial, "
    "du premier accueil jusqu'à la remise des clés.",
]

FAITS = [
    ("Formation", "BUT Techniques de Commercialisation, 1re année"),
    ("École", "IUT de Rambouillet"),
    ("Stage recherché", STAGE_PERIODE),
    ("Domaine", SECTEUR),
    ("Zone", LIEU),
]

# ------------------------------------------------------------------ compétences
COMPETENCES_INTRO = (
    "Trois domaines travaillés en BUT, que je veux maintenant pratiquer sur le terrain."
)
# icone : "cle", "cible" ou "pourcent"
COMPETENCES = [
    {
        "icone": "cle",
        "titre": "Vente et relation client",
        "accroche": "Comprendre le besoin, argumenter, conclure.",
        "points": ["Techniques de vente", "Prospection et prise de contact", "Relation client"],
    },
    {
        "icone": "cible",
        "titre": "Marketing et communication",
        "accroche": "Lire un marché et sa communication.",
        "points": ["Communication commerciale", "Benchmark concurrentiel", "Analyse de campagnes"],
    },
    {
        "icone": "pourcent",
        "titre": "Gestion et outils",
        "accroche": "Mettre une décision en chiffres.",
        "points": ["Marges et seuil de rentabilité", "Python et développement web", "Git et GitHub"],
    },
]

# ------------------------------------------------------------------ ce que j'aime
PASSIONS_INTRO = "Ce qui me donne envie de faire ce métier."
# visuel : "moteur", "route", "chiffres" ou "son"
PASSIONS = [
    {
        "visuel": "moteur",
        "titre": "Moteurs et mécanique",
        "texte": "Compresseurs volumétriques, quatre cylindres, moteurs boxer, gros V8 américains : "
        "j'aime comprendre ce qui se passe sous le capot, et pouvoir l'expliquer simplement.",
    },
    {
        "visuel": "chiffres",
        "titre": "Les chiffres",
        "texte": "Consommation réelle, coût d'un trajet, mensualité : "
        "j'aime vérifier un chiffre par moi-même avant de l'annoncer.",
    },
    {
        "visuel": "son",
        "titre": "Musique et bonne table",
        "texte": "Écouter de la musique, bien manger : deux plaisirs simples, "
        "et un bon réflexe pour créer du lien avec les gens.",
    },
]

# ------------------------------------------------------------------ parcours et projets
PARCOURS_INTRO = "Des travaux de cours concrets, du benchmark à la recherche de stage, jusqu'à ce site."
# icone : "barres", "cible", "repere" ou "code"
PROJETS = [
    {
        "etiquette": "SAÉ Communication commerciale",
        "titre": "Benchmark concurrentiel",
        "texte": "Comparer des marques concurrentes d'un même marché pour comprendre "
        "leur positionnement et leur communication.",
        "icone": "barres",
    },
    {
        "etiquette": "Travail de communication",
        "titre": "Analyse d'une campagne",
        "texte": "Annonceur, agence, objectifs, cibles, médias et hors-médias, message, budget : "
        "décortiquer une campagne de A à Z.",
        "icone": "cible",
    },
    {
        "etiquette": "SAÉ Vente",
        "titre": "Démarche de recherche de stage",
        "texte": "Ciblage d'entreprises, candidatures (CV, lettre de motivation) "
        "et suivi dans un tableau (SAÉ Vente).",
        "icone": "repere",
    },
    {
        "etiquette": "Projet personnel",
        "titre": "Ce site",
        "texte": "Conçu et codé en Python (Flask) : design sur mesure, calculs testés, mis en ligne.",
        "icone": "code",
    },
]
