from flask import Flask, render_template, render_template_string, request
import pandas as pd
import os
import sys
from qsar.product_resolver import resoudre_produit
# =========================================================
# SENTOX — CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

QSAR_DIR = os.path.join(
    BASE_DIR,
    "qsar"
)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

if QSAR_DIR not in sys.path:
    sys.path.insert(0, QSAR_DIR)


# =========================================================
# SENTOX — MODULES SCIENTIFIQUES
# =========================================================

from sentox_engine import (
    analyser_element,
    analyser_melange
)

from sentox_interaction import (
    analyser_melange_interactions
)

from sentox_adme import (
    analyser_adme_melange
)

from sentox_toxicologie import (
    analyser_toxicologie_melange
)

from sentox_evidence import (
    creer_fiche_scientifique
)

from sentox_pubchem import rechercher_pubchem

from sentox_3d import (
    analyser_melange_3d
)


# =========================================================
# APPLICATION FLASK
# =========================================================

app = Flask(__name__)


# =========================================================
# BASE DE DONNÉES SENTOX
# =========================================================

FICHIER = os.path.join(
    BASE_DIR,
    "data",
    "constituants_enrichis.csv"
)


def charger_donnees():

    if not os.path.exists(FICHIER):
        return pd.DataFrame()

    try:

        df = pd.read_csv(
            FICHIER
        )

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        return df.fillna("")

    except Exception:

        return pd.DataFrame()


# =========================================================
# ACCUEIL / RECHERCHE
# =========================================================

@app.route("/")
def accueil():

    df = charger_donnees()

    recherche = request.args.get(
        "q",
        ""
    ).strip().lower()

    if recherche:

        masque = df.astype(str).apply(
            lambda ligne:
                ligne.str.lower().str.contains(
                    recherche,
                    na=False,
                    regex=False
                )
        ).any(axis=1)

        df = df[masque]

    constituants = df.to_dict(
        orient="records"
    )

    return render_template(

        "index.html",

        constituants=constituants,

        recherche=recherche,

        nombre=len(
            constituants
        )
    )


# =========================================================
# FICHE CONSTITUANT
# =========================================================

@app.route(
    "/constituant/<int:index>"
)
def constituant(index):

    df = charger_donnees()

    if (
        index < 0
        or index >= len(df)
    ):

        return (
            "Constituant introuvable",
            404
        )

    donnees = df.iloc[
        index
    ].to_dict()

    return render_template(

        "fiche.html",

        donnees=donnees
    )


# =========================================================
# FICHE MOLÉCULE
# =========================================================

@app.route(
    "/molecule/<int:index>"
)
def molecule(index):

    df = charger_donnees()

    if (
        index < 0
        or index >= len(df)
    ):

        return (
            "Molécule introuvable",
            404
        )

    donnees = df.iloc[
        index
    ].to_dict()

    return render_template(

        "molecule.html",

        donnees=donnees
    )


# =========================================================
# SENTOX — ANALYSE INDIVIDUELLE
# =========================================================

@app.route(
    "/analyse",
    methods=["POST"]
)
def analyse():

    element = request.form.get(
        "element",
        ""
    ).strip()

    concentration_mg_g = float(request.form.get("concentration_mg_g", 2.0))
    quantite_g_jour = float(request.form.get("quantite_g_jour", 10.0))
    poids_kg = float(request.form.get("poids_kg", 70.0))
    frequence = float(request.form.get("frequence", 1.0))
    type_element = request.form.get(
        "type",
        "auto"
    ).strip()

    if not element:

        return (
            "Aucun élément fourni",
            400
        )

    # -----------------------------------------------------
    # APPEL DU MOTEUR SENTOX
    # -----------------------------------------------------

    resultat = analyser_element(

        element,

        type_element,
        concentration_mg_g,
        quantite_g_jour,
        poids_kg,
        frequence
    )

    # -----------------------------------------------------
    # AFFICHAGE
    # -----------------------------------------------------

    return render_template(

        "analyse.html",

        element=element,

        type_element=type_element,

        resultat=resultat,

        mode="individuel"
    )


# =========================================================
# SENTOX — ANALYSE MULTI-PRODUITS / MÉLANGE
# =========================================================

@app.route(
    "/analyse-melange",
    methods=["POST"]
)
def analyse_melange():

    # -----------------------------------------------------
    # 1. RÉCUPÉRATION
    # -----------------------------------------------------

    elements = request.form.getlist(
        "elements[]"
    )

    types = request.form.getlist(
        "types[]"
    )

    donnees = []

    for i, element in enumerate(
        elements
    ):

        element = element.strip()

        if not element:
            continue

        if (
            i < len(types)
            and types[i].strip()
        ):

            type_element = (
                types[i].strip()
            )

        else:

            type_element = "auto"

        donnees.append({

            "nom": element,

            "type": type_element

        })

    # -----------------------------------------------------
    # 2. VÉRIFICATION
    # -----------------------------------------------------

    if not donnees:

        return (
            "Aucun élément fourni",
            400
        )

    # -----------------------------------------------------
    # 3. MOTEUR CENTRAL SENTOX
    # -----------------------------------------------------

    resultat = analyser_melange(
        donnees
    )

    # -----------------------------------------------------
    # 4. ANALYSES INDIVIDUELLES
    # -----------------------------------------------------

    analyses_individuelles = (
        resultat.get(
            "elements",
            []
        )
    )

    # -----------------------------------------------------
    # 5. INTERACTIONS
    # -----------------------------------------------------

    interactions = (
        resultat.get(
            "interactions",
            []
        )
    )

    # -----------------------------------------------------
    # 6. ADME
    # -----------------------------------------------------

    adme = (
        resultat.get(
            "adme",
            {}
        )
    )

    # -----------------------------------------------------
    # 7. TOXICOLOGIE
    # -----------------------------------------------------

    toxicologie = (
        resultat.get(
            "toxicologie",
            {}
        )
    )

    # -----------------------------------------------------
    # 8. CONCLUSION
    # -----------------------------------------------------

    conclusion = (
        resultat.get(
            "conclusion",
            ""
        )
    )

    # -----------------------------------------------------
    # 9. CONSTITUANTS
    # -----------------------------------------------------

    tous_constituants = []

    for analyse_element_resultat in (
        analyses_individuelles
    ):

        identification = (
            analyse_element_resultat.get(
                "identification",
                {}
            )
        )

        nom = identification.get(
            "nom_recherche",
            ""
        )

        resultats_base = (
            identification.get(
                "resultats_base",
                []
            )
        )

        for constituant in resultats_base:

            tous_constituants.append({

                "produit": nom,

                "donnees": constituant

            })

    # -----------------------------------------------------
    # 10. ORGANES CIBLES
    # -----------------------------------------------------

    organes = []

    for analyse_element_resultat in (
        analyses_individuelles
    ):

        toxicologie_element = (
            analyse_element_resultat.get(
                "toxicologie",
                {}
            )
        )

        organes_element = (
            toxicologie_element.get(
                "organes_cibles",
                []
            )
        )

        for organe in organes_element:

            if organe not in organes:

                organes.append(
                    organe
                )

    # -----------------------------------------------------
    # 11. STRUCTURES MOLÉCULAIRES
    # -----------------------------------------------------

    structures_3d = []

    for analyse_element_resultat in (
        analyses_individuelles
    ):

        identification = (
            analyse_element_resultat.get(
                "identification",
                {}
            )
        )

        molecule = (
            analyse_element_resultat.get(
                "molecule",
                {}
            )
        )

        structures_3d.append({

            "nom":
                identification.get(
                    "nom_recherche",
                    ""
                ),

            "nom_identifie":
                identification.get(
                    "nom_identifie"
                ),

            "formule":
                molecule.get(
                    "formule_brute"
                ),

            "masse_molaire":
                molecule.get(
                    "masse_molaire"
                ),

            "smiles":
                molecule.get(
                    "smiles"
                ),

            "inchi":
                molecule.get(
                    "inchi"
                ),

            "structure_2d":
                molecule.get(
                    "structure_2d"
                ),

            "structure_3d":
                molecule.get(
                    "structure_3d"
                ),

            "descripteurs":
                molecule.get(
                    "descripteurs",
                    {}
                )

        })

    # -----------------------------------------------------
    # 12. AFFICHAGE
    # -----------------------------------------------------

    return render_template(

        "analyse.html",

        elements=donnees,

        resultat=resultat,

        analyses_individuelles=(
            analyses_individuelles
        ),

        tous_constituants=(
            tous_constituants
        ),

        interactions=(
            interactions
        ),

        adme=adme,

        organes=organes,

        toxicologie=toxicologie,

        structures_3d=structures_3d,

        conclusion=conclusion,

        mode="melange"
    )

# =========================================================
# PAGE TABLEAU DE BORD SENTOX
# =========================================================

@app.route("/dashboard")
def dashboard():
    return render_template("modules/dashboard.html")

# =========================================================
# MODULES SENTOX : ROUTES DE NAVIGATION
# =========================================================

from flask import render_template_string

MODULES_SENTOX = {
    "plantes": {
        "titre": "Plantes médicinales",
        "description": "Recherche et exploration des plantes médicinales.",
        "champs": ["Nom de la plante", "Nom scientifique", "Partie utilisée"]
    },
   
    "molecules": {
        "titre": "Molécules & QSAR",
        "description": "Recherche par nom commercial, nom chimique, substance active, SMILES ou identifiant PubChem.",
        "champs": [
            "Nom commercial ou nom connu (obligatoire)",
            "Nom de la substance active (facultatif)",
            "SMILES (facultatif)",
            "Identifiant PubChem (facultatif)"
        ]
    },

    "melanges": {
        "titre": "Mélanges & interactions",
        "description": "Étude des préparations contenant plusieurs plantes ou substances.",
        "champs": ["Nom du mélange", "Composition", "Proportions"]
    },
    "toxicologie": {
        "titre": "Toxicologie & exposition",
        "description": "Consultation des données toxicologiques et d'exposition.",
        "champs": ["Substance", "Dose", "Voie d'exposition"]
    },
    "preuves": {
        "titre": "Preuves scientifiques",
        "description": "Consultation des sources et du niveau de preuve disponible.",
        "champs": ["Substance ou plante", "Référence scientifique"]
    },
    "rapports": {
        "titre": "Rapports d'expertise",
        "description": "Préparation des analyses et synthèses scientifiques.",
        "champs": ["Nom de l'analyse", "Nom de l'expert"]
    }
}


MODELE_MODULE_SENTOX = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ module.titre }} - SENTOX</title>
<style>
body{margin:0;font-family:Arial,sans-serif;background:#f2f6f4;color:#24332c}
header{background:linear-gradient(135deg,#126b45,#075b91);color:white;padding:22px}
main{max-width:1000px;margin:25px auto;padding:22px}
.carte{background:white;padding:25px;border-radius:15px;box-shadow:0 3px 15px #0001}
h1,h2{color:#126b45}
label{display:block;margin-top:16px;font-weight:bold}
input{width:100%;padding:12px;margin-top:7px;box-sizing:border-box;border:1px solid #ccd8d1;border-radius:7px}
button,a{display:inline-block;margin-top:20px;padding:11px 16px;border-radius:7px}
button{background:#126b45;color:white;border:0;cursor:pointer}
a{color:#126b45}
.note{background:#fff5d9;padding:12px;border-radius:8px;margin-top:20px;line-height:1.5}
.resultat{background:#eef8f1;padding:15px;border-radius:8px;margin-top:20px;overflow-wrap:anywhere}
.erreur{background:#fdecec;padding:12px;border-radius:8px;margin-top:15px}
small{color:#64748b}
</style>
</head>
<body>
<header><strong>SENTOX</strong> — Espace scientifique</header>
<main><div class="carte">
<h1>{{ module.titre }}</h1>
<p>{{ module.description }}</p>

{% if request.method == "POST" and request.path.endswith("/molecules") %}
<form method="post">
<label>Nom commercial ou nom connu</label>
<input name="nom_connu" value="{{ request.form.get('nom_connu', '') }}"
       placeholder="Ex. Doliprane" >

<label>Nom de la substance active (facultatif)</label>
<input name="nom_substance" value="{{ request.form.get('nom_substance', '') }}"
       placeholder="Ex. paracétamol">

<label>SMILES (facultatif)</label>
<input name="smiles" value="{{ request.form.get('smiles', '') }}"
       placeholder="Laisser vide si inconnu">

<label>Identifiant PubChem (facultatif)</label>
<input name="pubchem_cid" value="{{ request.form.get('pubchem_cid', '') }}"
       placeholder="Ex. 1983">

<button type="submit">Rechercher la substance</button>
</form>
{% elif request.path.endswith("/molecules") %}
<form method="post">
<label>Nom commercial ou nom connu</label>
<input name="nom_connu" placeholder="Ex. Doliprane">

<label>Nom de la substance active (facultatif)</label>
<input name="nom_substance" placeholder="Ex. paracétamol">

<label>SMILES (facultatif)</label>
<input name="smiles" placeholder="Laisser vide si inconnu">

<label>Identifiant PubChem (facultatif)</label>
<input name="pubchem_cid" placeholder="Laisser vide si inconnu">

<button type="submit">Rechercher la substance</button>
</form>
{% else %}
<form method="get">
{% for champ in module.champs %}
<label>{{ champ }}</label>
<input name="champ{{ loop.index }}" placeholder="Saisir : {{ champ }}">
{% endfor %}
<button type="submit">Afficher les informations saisies</button>
</form>
{% endif %}

{% if resultat %}
{% if resultat.get('erreur') %}
<div class="erreur">{{ resultat.get('erreur') }}</div>
{% else %}
<div class="resultat">
<h2>Résultat de la recherche</h2>
<p><strong>Statut :</strong> {{ resultat.get('statut', 'Non précisé') }}</p>
{% if resultat.get('message') %}
<p>{{ resultat.get('message') }}</p>
{% endif %}
{% for candidat in resultat.get('candidats', []) %}
<hr>
<h3>{{ candidat.get('nom_pubchem') or candidat.get('nom_recherche', 'Candidat') }}</h3>
<p><strong>CID PubChem :</strong> {{ candidat.get('cid') or 'Non disponible' }}</p>
<p><strong>Nom IUPAC :</strong> {{ candidat.get('nom_iupac') or 'Non disponible' }}</p>
<p><strong>Formule :</strong> {{ candidat.get('formule') or 'Non disponible' }}</p>
<p><strong>Masse molaire :</strong> {{ candidat.get('masse_molaire') or 'Non disponible' }}</p>
<p><strong>SMILES :</strong> {{ candidat.get('smiles_canonique') or 'Non disponible' }}</p>
<p><strong>Source :</strong> {{ candidat.get('source', 'Non précisée') }}</p>
<p><strong>Identité :</strong> {{ candidat.get('statut_identite', 'À vérifier') }}</p>
{% endfor %}
{% if resultat.get('avertissement') %}
<div class="note">{{ resultat.get('avertissement') }}</div>
{% endif %}
</div>
{% endif %}
{% endif %}

{% if request.args and request.path.endswith("/molecules") == false %}
<h2>Informations saisies</h2>
<ul>
{% for champ in module.champs %}
{% set valeur = request.args.get("champ" ~ loop.index, "") %}
{% if valeur %}
<li><strong>{{ champ }} :</strong> {{ valeur }}</li>
{% endif %}
{% endfor %}
</ul>
{% endif %}

<div class="note">
<strong>Précaution scientifique :</strong>
une correspondance chimique ne confirme pas à elle seule la composition
d'un produit commercial. Vérifier l'identité avant toute analyse QSAR.
Les résultats affichés ne constituent pas un avis médical.
</div>
<a href="/dashboard">← Retour au tableau de bord</a>
</div></main>
</body>
</html>
"""


@app.route("/module/<nom_module>", methods=["GET", "POST"])
def afficher_module_sentox(nom_module):
    module = MODULES_SENTOX.get(nom_module)
    if module is None:
        return "Module SENTOX inconnu", 404

    resultat = None

    if nom_module == "molecules" and request.method == "POST":
        nom_connu = request.form.get("nom_connu", "").strip()
        nom_substance = request.form.get("nom_substance", "").strip()
        smiles = request.form.get("smiles", "").strip()
        pubchem_cid = request.form.get("pubchem_cid", "").strip()

        if not nom_connu and not nom_substance and not smiles and not pubchem_cid:
            resultat = {
                "erreur": "Saisis au moins un nom, un SMILES ou un CID PubChem."
            }
        else:
            try:
                resultat = resoudre_produit(
                    nom_connu=nom_connu,
                    nom_substance=nom_substance,
                    smiles=smiles,
                    pubchem_cid=pubchem_cid
                )
            except Exception:
                resultat = {
                    "erreur": "La recherche a échoué. Vérifie les données et la connexion."
                }

    return render_template_string(
        MODELE_MODULE_SENTOX,
        module=module,
        resultat=resultat
    )

# =========================================================
# LANCEMENT
# =========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False
    )
