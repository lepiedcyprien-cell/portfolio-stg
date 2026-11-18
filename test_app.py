from html import unescape

import pytest

import app as site
import config


@pytest.fixture()
def client():
    site.app.config["TESTING"] = True
    return site.app.test_client()


def test_page_d_accueil_contient_tout_le_contenu(client):
    r = client.get("/")
    assert r.status_code == 200
    html = unescape(r.get_data(as_text=True))  # les apostrophes sont échappées dans le HTML
    assert config.PRENOM_NOM in html
    for ancre in ("accueil", "moi", "competences", "passions", "parcours", "preuve", "financement", "marge", "rentabilite", "contact"):
        assert f'id="{ancre}"' in html
    assert html.count('class="g-tick') == 33
    for passion in config.PASSIONS:
        assert passion["titre"] in html
    for projet in config.PROJETS:
        assert projet["titre"] in html


def test_securite_de_la_page(client):
    r = client.get("/")
    assert "script-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    # aucun script en ligne : la politique de sécurité l'interdit
    assert "<script>" not in r.get_data(as_text=True)


def test_fichiers_publics_servis_en_local(client):
    for chemin in ("css/style.css", "js/site.js", "js/tools.js", "js/boot.js", "fonts/archivo.woff2", "favicon.svg"):
        assert client.get("/" + chemin).status_code == 200, chemin
    assert client.get("/inexistant.txt").status_code == 404
    assert client.get("/..%2fconfig.py").status_code == 404
    assert client.get("/api/inconnu").status_code == 404


def test_api_financement(client):
    d = client.get("/api/financement?prix=15000&apport=2000&duree=48&taux=5.9").get_json()
    assert d["emprunt"] == 13000
    assert d["mensualite"] == pytest.approx(304.71, abs=0.01)
    assert d["cout_credit"] == pytest.approx(d["mensualite"] * 48 - 13000, abs=0.05)
    assert len(d["serie"]["capital"]) == 48


def test_api_financement_apport_superieur_au_prix(client):
    d = client.get("/api/financement?prix=1000&apport=5000").get_json()
    assert d["emprunt"] == 0 and d["mensualite"] == 0 and d["cout_credit"] == 0
    assert d["total_paye"] == 1000


def test_api_resiste_aux_valeurs_absurdes(client):
    for adresse in (
        "/api/financement?prix=abc&duree=-5&taux=nan",
        "/api/financement?prix=1e999&apport=-1",
        "/api/budget?revenu=&endettement=999",
        "/api/rentabilite?cf=&pvu=inf",
    ):
        assert client.get(adresse).status_code == 200, adresse


def test_api_budget(client):
    d = client.get("/api/budget?revenu=2000&charges=0&endettement=35&apport=2000&duree=48&taux=5.9").get_json()
    assert d["mensualite_max"] == 700
    assert d["budget_max"] == pytest.approx(d["emprunt_max"] + 2000, abs=0.01)
    assert d["emprunt_max"] == pytest.approx(29864, abs=1)


def test_api_budget_credits_en_cours_trop_lourds(client):
    d = client.get("/api/budget?revenu=1500&charges=1000&endettement=35").get_json()
    assert d["mensualite_max"] == 0 and d["emprunt_max"] == 0


def test_api_marge(client):
    d = client.get("/api/marge?mode=marge&pa=15000&valeur=12&tva=20").get_json()
    assert d["pv_ht"] == 16800 and d["pv_ttc"] == 20160 and d["marge"] == 1800
    d = client.get("/api/marge?mode=pv&pa=15000&valeur=14000").get_json()
    assert d["marge"] == -1000  # vente à perte : la page l'affiche en avertissement


def test_api_marge_erreurs(client):
    assert client.get("/api/marge?mode=zzz").status_code == 400
    r = client.get("/api/marge?mode=marque&valeur=99&pa=100")
    assert r.status_code == 200 and r.get_json()["pv_ht"] == pytest.approx(10000)


def test_api_rentabilite(client):
    d = client.get("/api/rentabilite?cf=20000&pvu=18000&cvu=15500").get_json()
    assert d["ok"] and d["quantite"] == 8 and d["chiffre_affaires"] == 144000
    assert len(d["courbe"]["quantites"]) == len(d["courbe"]["resultats"])


def test_api_rentabilite_impossible(client):
    d = client.get("/api/rentabilite?cf=20000&pvu=15000&cvu=16000").get_json()
    assert d["ok"] is False and "dépasser" in d["message"]


def test_initiales():
    assert site.initiales("Jean-Pierre Martin") == "JP"
    assert site.initiales("Léa") == "L"
    assert site.initiales("") == "?"


def test_typographie_francaise_hors_balises():
    brut = '<p class="a" data-x="a : b">Combien ? Voilà : « oui » à 5 %.</p>'
    propre = site.typographie(brut)
    assert 'data-x="a : b"' in propre  # les attributs ne sont pas touchés
    assert "Combien\u00a0?" in propre
    assert "Voilà\u00a0:" in propre
    assert "«\u00a0oui\u00a0»" in propre
    assert "5\u00a0%" in propre


def test_la_page_servie_utilise_les_espaces_insecables(client):
    html = client.get("/").get_data(as_text=True)
    assert "Combien par mois\u00a0?" in html
