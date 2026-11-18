"""Site portfolio : Flask (pages + petite API) et calculs en Python.

En local :  pip install -r requirements.txt  puis  python app.py
"""
import datetime
import os
import re

from flask import Flask, jsonify, render_template, request, send_from_directory

import calculs
import config

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(BASE, "public")

# Les fichiers statiques vivent dans public/ : en ligne (Vercel), le CDN les sert directement.
app = Flask(__name__, static_folder=None)

CSP = (
    "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
)


@app.after_request
def en_tetes_securite(reponse):
    reponse.headers.setdefault("X-Content-Type-Options", "nosniff")
    reponse.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if reponse.mimetype == "text/html":
        reponse.headers.setdefault("Content-Security-Policy", CSP)
    return reponse


def nombre(nom, defaut, mini, maxi):
    """Lit un nombre dans l'adresse, avec valeur par défaut et bornes (jamais d'erreur)."""
    try:
        v = float(request.args.get(nom, defaut))
    except (TypeError, ValueError):
        return defaut
    if v != v:  # NaN
        return defaut
    return min(max(v, mini), maxi)


_BALISE = re.compile(r"(<[^>]*>)")
_PONCTUATION = re.compile(r"(?<=\S) (?=[:;?!»%])|(?<=«) ")


def typographie(html):
    """Remplace par une espace insécable l'espace avant : ; ? ! » % et après «, hors des balises."""
    morceaux = _BALISE.split(html)
    return "".join(m if m.startswith("<") else _PONCTUATION.sub("\u00a0", m) for m in morceaux)


def initiales(nom):
    mots = [m for m in nom.replace("-", " ").split() if m]
    return "".join(m[0] for m in mots[:2]).upper() or "?"


@app.get("/")
def accueil():
    page = render_template(
        "index.html",
        c=config,
        cadran=calculs.cadran(),
        initiales=initiales(config.PRENOM_NOM),
        prenom=config.PRENOM_NOM.split()[0] if config.PRENOM_NOM.split() else config.PRENOM_NOM,
        annee=datetime.date.today().year,
    )
    return typographie(page)


@app.get("/api/financement")
def api_financement():
    prix = nombre("prix", 15000, 0, 500_000)
    apport = nombre("apport", 2000, 0, 500_000)
    duree = int(nombre("duree", 48, 6, 120))
    taux = nombre("taux", 5.9, 0, 25)

    emprunt = max(prix - apport, 0.0)
    mens = calculs.mensualite(emprunt, taux, duree)
    total_credit = mens * duree
    cout = max(total_credit - emprunt, 0.0)
    return jsonify(
        emprunt=round(emprunt, 2),
        mensualite=round(mens, 2),
        cout_credit=round(cout, 2),
        total_paye=round(min(apport, prix) + total_credit, 2),
        serie=calculs.amortissement(emprunt, taux, duree),
    )


@app.get("/api/budget")
def api_budget():
    revenu = nombre("revenu", 2000, 0, 50_000)
    charges = nombre("charges", 0, 0, 50_000)
    endettement = nombre("endettement", 35, 10, 50)
    apport = nombre("apport", 2000, 0, 500_000)
    duree = int(nombre("duree", 48, 6, 120))
    taux = nombre("taux", 5.9, 0, 25)

    mens_max = max(revenu * endettement / 100 - charges, 0.0)
    emprunt_max = calculs.capital_empruntable(mens_max, taux, duree)
    return jsonify(
        mensualite_max=round(mens_max, 2),
        emprunt_max=round(emprunt_max, 2),
        budget_max=round(emprunt_max + apport, 2),
    )


@app.get("/api/marge")
def api_marge():
    mode = request.args.get("mode", "marge")
    if mode not in ("pv", "marge", "marque"):
        return jsonify(erreur="Mode inconnu."), 400
    maxi = {"pv": 10_000_000, "marge": 1000, "marque": 99}[mode]
    pa = nombre("pa", 15000, 1, 5_000_000)
    tva = nombre("tva", 20, 0, 30)
    valeur = nombre("valeur", 12, 0.01, maxi)
    try:
        return jsonify(calculs.analyse_marge(pa, mode, valeur, tva))
    except ValueError as erreur:
        return jsonify(erreur=str(erreur)), 400


@app.get("/api/rentabilite")
def api_rentabilite():
    cf = nombre("cf", 20000, 0, 10_000_000)
    pvu = nombre("pvu", 18000, 0, 5_000_000)
    cvu = nombre("cvu", 15500, 0, 5_000_000)

    seuil = calculs.seuil_rentabilite(cf, pvu, cvu)
    if seuil is None:
        return jsonify(
            ok=False,
            message="Le prix de vente doit dépasser le coût variable pour atteindre un seuil.",
        )
    return jsonify(ok=True, **seuil, courbe=calculs.courbe_resultat(cf, seuil["mcv_unitaire"], seuil["quantite"]))


@app.get("/<path:chemin>")
def fichier_public(chemin):
    """En local, Flask sert public/ ; en ligne, le CDN s'en charge avant d'arriver ici."""
    return send_from_directory(PUBLIC, chemin)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
