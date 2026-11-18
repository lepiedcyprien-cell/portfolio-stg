import pytest

from calculs import (
    amortissement,
    analyse_marge,
    arc,
    cadran,
    capital_empruntable,
    coefficient_multiplicateur,
    courbe_resultat,
    marge_commerciale,
    mensualite,
    pv_depuis_taux_de_marge,
    pv_depuis_taux_de_marque,
    seuil_rentabilite,
    taux_de_marge,
    taux_de_marque,
)


# ---------------------------------------------------------------- financement
def test_mensualite_sans_interets():
    assert mensualite(10_000, 0, 10) == pytest.approx(1_000)


def test_mensualite_connue():
    # 13 000 € sur 48 mois à 5,9 % : valeur de référence d'un simulateur classique
    assert mensualite(13_000, 5.9, 48) == pytest.approx(304.71, abs=0.01)


def test_mensualite_et_capital_sont_inverses():
    m = mensualite(13_000, 5.9, 48)
    assert capital_empruntable(m, 5.9, 48) == pytest.approx(13_000)


def test_amortissement_solde_le_pret():
    s = amortissement(13_000, 5.9, 48)
    assert len(s["capital"]) == 48
    assert s["restant"][-1] == pytest.approx(0, abs=0.01)
    assert s["capital"][-1] == pytest.approx(13_000, abs=0.01)
    total_paye = mensualite(13_000, 5.9, 48) * 48
    assert s["capital"][-1] + s["interets"][-1] == pytest.approx(total_paye, abs=0.05)


def test_pas_de_pret_si_capital_nul():
    assert mensualite(0, 5, 12) == 0
    assert capital_empruntable(0, 5, 12) == 0


# ---------------------------------------------------------------- marges
def test_marges():
    assert marge_commerciale(100, 150) == 50
    assert taux_de_marge(100, 150) == pytest.approx(0.5)
    assert taux_de_marque(100, 150) == pytest.approx(1 / 3)
    assert coefficient_multiplicateur(100, 150, 20) == pytest.approx(1.8)


def test_prix_de_vente_depuis_les_taux():
    assert pv_depuis_taux_de_marge(100, 50) == pytest.approx(150)
    assert pv_depuis_taux_de_marque(60, 40) == pytest.approx(100)


def test_analyse_marge_coherente_quel_que_soit_le_point_de_depart():
    depuis_marge = analyse_marge(15_000, "marge", 12, 20)
    depuis_pv = analyse_marge(15_000, "pv", depuis_marge["pv_ht"], 20)
    depuis_marque = analyse_marge(15_000, "marque", depuis_marge["taux_marque"], 20)
    # le taux de marque est arrondi à 2 décimales dans la réponse : on tolère quelques euros
    for autre in (depuis_pv, depuis_marque):
        assert autre["pv_ht"] == pytest.approx(depuis_marge["pv_ht"], abs=2)
        assert autre["taux_marge"] == pytest.approx(12, abs=0.05)
    assert depuis_marge["pv_ht"] == pytest.approx(16_800)
    assert depuis_marge["pv_ttc"] == pytest.approx(20_160)
    assert depuis_marge["marge"] == pytest.approx(1_800)
    assert depuis_marge["coefficient"] == pytest.approx(1.344)


def test_analyse_marge_refuse_les_valeurs_impossibles():
    with pytest.raises(ValueError):
        analyse_marge(15_000, "marque", 100, 20)
    with pytest.raises(ValueError):
        analyse_marge(0, "marge", 10, 20)
    with pytest.raises(ValueError):
        analyse_marge(15_000, "inconnu", 10, 20)


# ---------------------------------------------------------------- rentabilité
def test_seuil_de_rentabilite():
    s = seuil_rentabilite(3_000, 50, 30)
    assert s["quantite"] == 150
    assert s["taux_mcv"] == pytest.approx(40)
    assert s["chiffre_affaires"] == pytest.approx(7_500)


def test_seuil_exemple_concession():
    s = seuil_rentabilite(20_000, 18_000, 15_500)
    assert s["mcv_unitaire"] == 2_500
    assert s["quantite"] == 8
    assert s["chiffre_affaires"] == pytest.approx(144_000)


def test_seuil_impossible_si_prix_inferieur_au_cout():
    assert seuil_rentabilite(3_000, 30, 30) is None
    assert seuil_rentabilite(3_000, 20, 30) is None
    assert seuil_rentabilite(3_000, 0, 0) is None


def test_courbe_passe_par_zero_au_seuil():
    s = seuil_rentabilite(20_000, 18_000, 15_500)
    c = courbe_resultat(20_000, s["mcv_unitaire"], s["quantite"])
    assert c["resultats"][0] == -20_000
    assert len(c["quantites"]) == len(c["resultats"])
    # perte avant le seuil, bénéfice après
    for q, r in zip(c["quantites"], c["resultats"]):
        assert (r < 0) if q < 8 else (r >= 0)


# ---------------------------------------------------------------- cadran
def test_cadran_a_les_bonnes_graduations():
    c = cadran()
    assert len(c["graduations"]) == 33
    assert sum(1 for g in c["graduations"] if g["majeur"]) == 9
    assert [n["v"] for n in c["chiffres"]] == list(range(9))
    assert all(g["rouge"] == (g["v"] >= 6.5) for g in c["graduations"])


def test_arc_complet_utilise_le_grand_arc():
    assert " 1 1 " in arc(300, 300, 100, 0, 8, 8)
    assert " 0 1 " in arc(300, 300, 100, 6.5, 8, 8)
