from flask import Flask, render_template, request
import pandas as pd
import os
import sys

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

    type_element = request.form.get(
        "type",
        "auto"
    ).strip()

    # -----------------------------------------------------
    # DONNÉES D'EXPOSITION HUMAINE — OPTIONNELLES
    # -----------------------------------------------------

    exposition_humaine = request.form.get(
        "exposition_humaine",
        ""
    ).strip()

    valeur_reference = request.form.get(
        "valeur_reference",
        ""
    ).strip()

    point_depart = request.form.get(
        "point_depart",
        ""
    ).strip()

    # -----------------------------------------------------
    # DONNÉES HED — OPTIONNELLES
    # -----------------------------------------------------

    dose_animale = request.form.get(
        "dose_animale",
        ""
    ).strip()

    espece = request.form.get(
        "espece",
        ""
    ).strip()

    contexte = request.form.get(
        "contexte",
        "MRSD_initiale"
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

        type_element
    )

    # -----------------------------------------------------
    # EXTRAPOLATION HED — DOSE DE REFERENCE
    # -----------------------------------------------------
    try:
        from extrapolation.hed_engine import calculer_dose_reference

        def valeur_positive_hed(valeur):
            if valeur is None or not str(valeur).strip():
                return None

            try:
                nombre = float(valeur)

                if nombre <= 0:
                    return None

                return nombre

            except (TypeError, ValueError):
                return None

        dose_val = valeur_positive_hed(dose_animale)

        evaluation_hed = {
            "dose_animale": dose_val,
            "espece": espece or None,
            "contexte": contexte or "MRSD_initiale",
            "HED": None,
            "Km_animal": None,
            "Km_humain": None,
            "facteur_securite": None,
            "dose_reference": None,
            "statut": "NON CALCULEE"
        }

        if dose_val is not None and espece:

            resultat_hed = calculer_dose_reference(
                dose_val,
                espece,
                contexte or "MRSD_initiale"
            )

            evaluation_hed["HED"] = resultat_hed.get("HED")
            evaluation_hed["Km_animal"] = resultat_hed.get("Km_animal")
            evaluation_hed["Km_humain"] = resultat_hed.get("Km_humain")
            evaluation_hed["facteur_securite"] = resultat_hed.get(
                "facteur_securite"
            )
            evaluation_hed["dose_reference"] = resultat_hed.get(
                "dose_reference"
            )
            evaluation_hed["statut"] = "CALCULEE"

        resultat["evaluation_hed"] = evaluation_hed

    except Exception as e:

        resultat["evaluation_hed"] = {
            "dose_animale": None,
            "espece": espece or None,
            "contexte": contexte or "MRSD_initiale",
            "HED": None,
            "Km_animal": None,
            "Km_humain": None,
            "facteur_securite": None,
            "dose_reference": None,
            "statut": "ERREUR",
            "erreur": str(e)
        }

    # -----------------------------------------------------
    # EVALUATION D'EXPOSITION — MOE / RQ
    # -----------------------------------------------------
    try:
        from risk.risk_engine import calculer_moe
        from risk.rq_engine import calculer_rq

        def valeur_positive(valeur):
            if valeur is None or not str(valeur).strip():
                return None

            try:
                nombre = float(valeur)

                if nombre <= 0:
                    return None

                return nombre

            except (TypeError, ValueError):
                return None

        pd_val = valeur_positive(point_depart)
        exp_val = valeur_positive(exposition_humaine)
        ref_val = valeur_positive(valeur_reference)

        evaluation = {
            "point_depart": pd_val,
            "exposition_humaine": exp_val,
            "valeur_reference": ref_val,
            "MOE": None,
            "RQ": None,
            "statut_MOE": "NON CALCULEE",
            "statut_RQ": "NON CALCULE",
        }

        # MOE = point de départ / exposition humaine
        if pd_val is not None and exp_val is not None:

            resultat_moe = calculer_moe(
                pd_val,
                exp_val
            )

            evaluation["MOE"] = resultat_moe.get("MOE")
            evaluation["statut_MOE"] = "CALCULEE"

        # RQ = exposition humaine / valeur de référence
        if exp_val is not None and ref_val is not None:

            resultat_rq = calculer_rq(
                exp_val,
                ref_val
            )

            evaluation["RQ"] = resultat_rq.get("RQ")
            evaluation["statut_RQ"] = "CALCULE"

        resultat["evaluation_exposition"] = evaluation

    except Exception as e:

        resultat["evaluation_exposition"] = {
            "point_depart": None,
            "exposition_humaine": None,
            "valeur_reference": None,
            "MOE": None,
            "RQ": None,
            "statut_MOE": "ERREUR",
            "statut_RQ": "ERREUR",
            "erreur": str(e)
        }

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
# LANCEMENT
# =========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False
    )
