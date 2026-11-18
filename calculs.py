"""Formules du site (sans Flask) : faciles à tester."""
import math

# ------------------------------------------------------------------ financement


def _taux_mensuel(taux_annuel_pct):
    return taux_annuel_pct / 100 / 12


def mensualite(capital, taux_annuel_pct, mois):
    """Mensualité constante d'un prêt amortissable (hors assurance)."""
    if capital <= 0 or mois <= 0:
        return 0.0
    t = _taux_mensuel(taux_annuel_pct)
    if t == 0:
        return capital / mois
    return capital * t / (1 - (1 + t) ** -mois)


def capital_empruntable(mensualite_max, taux_annuel_pct, mois):
    """Capital que l'on peut emprunter pour une mensualité donnée."""
    if mensualite_max <= 0 or mois <= 0:
        return 0.0
    t = _taux_mensuel(taux_annuel_pct)
    if t == 0:
        return mensualite_max * mois
    return mensualite_max * (1 - (1 + t) ** -mois) / t


def amortissement(capital, taux_annuel_pct, mois):
    """Séries mois par mois : capital remboursé et intérêts payés (cumulés), capital restant dû."""
    t = _taux_mensuel(taux_annuel_pct)
    m = mensualite(capital, taux_annuel_pct, mois)
    reste = capital
    capital_cumule = interets_cumules = 0.0
    serie = {"capital": [], "interets": [], "restant": []}
    for _ in range(int(mois)):
        interets = reste * t
        rembourse = m - interets
        reste -= rembourse
        capital_cumule += rembourse
        interets_cumules += interets
        serie["capital"].append(round(capital_cumule, 2))
        serie["interets"].append(round(interets_cumules, 2))
        serie["restant"].append(round(max(reste, 0.0), 2))
    return serie


# ------------------------------------------------------------------ marges


def marge_commerciale(prix_achat_ht, prix_vente_ht):
    return prix_vente_ht - prix_achat_ht


def taux_de_marge(prix_achat_ht, prix_vente_ht):
    """Marge ÷ prix d'achat HT."""
    return (prix_vente_ht - prix_achat_ht) / prix_achat_ht


def taux_de_marque(prix_achat_ht, prix_vente_ht):
    """Marge ÷ prix de vente HT."""
    return (prix_vente_ht - prix_achat_ht) / prix_vente_ht


def coefficient_multiplicateur(prix_achat_ht, prix_vente_ht, tva_pct):
    """Prix de vente TTC ÷ prix d'achat HT."""
    return prix_vente_ht * (1 + tva_pct / 100) / prix_achat_ht


def pv_depuis_taux_de_marge(prix_achat_ht, taux_pct):
    return prix_achat_ht * (1 + taux_pct / 100)


def pv_depuis_taux_de_marque(prix_achat_ht, taux_pct):
    return prix_achat_ht / (1 - taux_pct / 100)


def analyse_marge(prix_achat_ht, mode, valeur, tva_pct):
    """Part d'un prix de vente HT, d'un taux de marge ou d'un taux de marque et déduit le reste."""
    if prix_achat_ht <= 0:
        raise ValueError("Le prix d'achat doit être positif.")
    if mode == "pv":
        pv = valeur
    elif mode == "marge":
        pv = pv_depuis_taux_de_marge(prix_achat_ht, valeur)
    elif mode == "marque":
        if valeur >= 100:
            raise ValueError("Le taux de marque doit rester inférieur à 100 %.")
        pv = pv_depuis_taux_de_marque(prix_achat_ht, valeur)
    else:
        raise ValueError("Mode inconnu.")
    if pv <= 0:
        raise ValueError("Le prix de vente doit être positif.")
    pv_ttc = pv * (1 + tva_pct / 100)
    return {
        "pa": round(prix_achat_ht, 2),
        "pv_ht": round(pv, 2),
        "pv_ttc": round(pv_ttc, 2),
        "tva_montant": round(pv_ttc - pv, 2),
        "marge": round(marge_commerciale(prix_achat_ht, pv), 2),
        "taux_marge": round(taux_de_marge(prix_achat_ht, pv) * 100, 2),
        "taux_marque": round(taux_de_marque(prix_achat_ht, pv) * 100, 2),
        "coefficient": round(coefficient_multiplicateur(prix_achat_ht, pv, tva_pct), 3),
    }


# ------------------------------------------------------------------ rentabilité


def seuil_rentabilite(charges_fixes, prix_vente_unitaire, cout_variable_unitaire):
    """Seuil de rentabilité, ou None si la marge sur coût variable est <= 0."""
    mcv_unitaire = prix_vente_unitaire - cout_variable_unitaire
    if prix_vente_unitaire <= 0 or mcv_unitaire <= 0:
        return None
    taux_mcv = mcv_unitaire / prix_vente_unitaire
    return {
        "mcv_unitaire": round(mcv_unitaire, 2),
        "taux_mcv": round(taux_mcv * 100, 2),
        "quantite": math.ceil(round(charges_fixes / mcv_unitaire, 9)),
        "chiffre_affaires": round(charges_fixes / taux_mcv, 2),
    }


def courbe_resultat(charges_fixes, mcv_unitaire, quantite_seuil, points=60):
    """Résultat (bénéfice ou perte) selon la quantité vendue."""
    q_max = max(math.ceil(quantite_seuil * 2), 10)
    pas = max(q_max // points, 1)
    quantites = list(range(0, q_max + 1, pas))
    return {
        "quantites": quantites,
        "resultats": [round(q * mcv_unitaire - charges_fixes, 2) for q in quantites],
    }


# ------------------------------------------------------------------ cadran (décor du site)


def _point(cx, cy, rayon, valeur, maxi):
    """Point du cadran : 0 en bas à gauche, maxi en bas à droite, 270° de balayage."""
    angle = math.radians(135 + 270 * valeur / maxi)
    return cx + rayon * math.cos(angle), cy + rayon * math.sin(angle)


def arc(cx, cy, rayon, v0, v1, maxi):
    """Tracé SVG d'un arc de cadran entre deux valeurs."""
    x0, y0 = _point(cx, cy, rayon, v0, maxi)
    x1, y1 = _point(cx, cy, rayon, v1, maxi)
    grand = 1 if 270 * (v1 - v0) / maxi > 180 else 0
    return f"M{x0:.2f} {y0:.2f}A{rayon} {rayon} 0 {grand} 1 {x1:.2f} {y1:.2f}"


def cadran(maxi=8, zone_rouge=6.5, cx=300, cy=300, rayon=268):
    """Graduations d'un compte-tours : graduation tous les 0,25 ; grand trait chaque tour."""
    graduations = []
    for i in range(int(maxi * 4) + 1):
        v = i / 4
        majeur = i % 4 == 0
        x1, y1 = _point(cx, cy, rayon, v, maxi)
        x2, y2 = _point(cx, cy, rayon - (34 if majeur else 16), v, maxi)
        graduations.append(
            {
                "v": v,
                "majeur": majeur,
                "rouge": v >= zone_rouge,
                "x1": round(x1, 2),
                "y1": round(y1, 2),
                "x2": round(x2, 2),
                "y2": round(y2, 2),
            }
        )
    chiffres = []
    for v in range(0, maxi + 1):
        x, y = _point(cx, cy, rayon - 68, v, maxi)
        chiffres.append({"v": v, "x": round(x, 2), "y": round(y, 2)})
    return {
        "graduations": graduations,
        "chiffres": chiffres,
        "arc_fond": arc(cx, cy, rayon + 14, 0, maxi, maxi),
        "arc_rouge": arc(cx, cy, rayon + 14, zone_rouge, maxi, maxi),
    }
