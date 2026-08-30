from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

FICHIER = r"C:\SENTOX\data\constituants_enrichis.csv"


def charger_donnees():
    if not os.path.exists(FICHIER):
        return pd.DataFrame()

    try:
        df = pd.read_csv(FICHIER)
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna("")
    except Exception:
        return pd.DataFrame()


@app.route("/")
def accueil():

    df = charger_donnees()

    recherche = request.args.get("q", "").strip().lower()

    if recherche:
        masque = df.astype(str).apply(
            lambda ligne: ligne.str.lower().str.contains(
                recherche,
                na=False
            )
        ).any(axis=1)

        df = df[masque]

    constituants = df.to_dict(orient="records")

    return render_template(
        "index.html",
        constituants=constituants,
        recherche=recherche,
        nombre=len(constituants)
    )


@app.route("/constituant/<int:index>")
def constituant(index):

    df = charger_donnees()

    if index < 0 or index >= len(df):
        return "Constituant introuvable", 404

    donnees = df.iloc[index].to_dict()

    return render_template(
        "fiche.html",
        donnees=donnees
    )

@app.route("/molecule/<int:index>")
def molecule(index):
    df = charger_donnees()

    if index < 0 or index >= len(df):
        return "Molécule introuvable", 404

    donnees = df.iloc[index].to_dict()

    return render_template(
        "molecule.html",
        donnees=donnees
    )
# =========================================================
# SENTOX — ANALYSE INDIVIDUELLE
# =========================================================

@app.route("/analyse", methods=["POST"])
def analyse():

    element = request.form.get("element", "").strip()
    type_element = request.form.get("type", "auto")

    if not element:
        return "Aucun élément fourni", 400

    return render_template(
        "analyse.html",
        element=element,
        type_element=type_element,
        mode="individuel"
    )


# =========================================================
# SENTOX — ANALYSE MULTI-PRODUITS / MÉLANGE
# =========================================================

@app.route("/analyse-melange", methods=["POST"])
def analyse_melange():

    # -----------------------------------------------------
    # 1. RÉCUPÉRATION DES DONNÉES DU FORMULAIRE
    # -----------------------------------------------------

    elements = request.form.getlist("elements[]")
    types = request.form.getlist("types[]")

    donnees = []

    for i, element in enumerate(elements):

        element = element.strip()

        if not element:
            continue

        type_element = (
            types[i].strip()
            if i < len(types) and types[i].strip()
            else "auto"
        )

        donnees.append({
            "nom": element,
            "type": type_element
        })

    # -----------------------------------------------------
    # 2. VÉRIFICATION
    # -----------------------------------------------------

    if not donnees:
        return "Aucun élément fourni", 400

    # -----------------------------------------------------
    # 3. ANALYSE INDIVIDUELLE
    # -----------------------------------------------------

    df = charger_donnees()

    analyses_individuelles = []

    for element in donnees:

        nom = element["nom"].lower()

        constituants = []

        if not df.empty:

            # Recherche dans toutes les colonnes
            masque = df.astype(str).apply(
                lambda colonne:
                    colonne.str.lower().str.contains(
                        nom,
                        na=False,
                        regex=False
                    )
            ).any(axis=1)

            resultats = df[masque]

            constituants = resultats.to_dict(
                orient="records"
            )

        analyses_individuelles.append({
            "nom": element["nom"],
            "type": element["type"],
            "constituants": constituants
        })

    # -----------------------------------------------------
    # 4. CONSTITUANTS DU MÉLANGE
    # -----------------------------------------------------

    tous_constituants = []

    for analyse in analyses_individuelles:

        for constituant in analyse["constituants"]:

            tous_constituants.append({
                "produit": analyse["nom"],
                "donnees": constituant
            })

    # -----------------------------------------------------
    # 5. INTERACTIONS ENTRE LES ÉLÉMENTS
    # -----------------------------------------------------

    interactions = []

    for i in range(len(donnees)):

        for j in range(i + 1, len(donnees)):

            produit_a = donnees[i]["nom"]
            produit_b = donnees[j]["nom"]

            interactions.append({
                "produit_a": produit_a,
                "produit_b": produit_b,

                "interaction": "Analyse à effectuer",

                "potentialisation":
                    "Analyse à effectuer",

                "antagonisme":
                    "Analyse à effectuer",

                "inhibition":
                    "Analyse à effectuer",

                "competition":
                    "Analyse à effectuer",

                "synergie":
                    "Analyse à effectuer"
            })

    # -----------------------------------------------------
    # 6. ADME
    # -----------------------------------------------------

    adme = {
        "absorption": "Analyse à effectuer",
        "distribution": "Analyse à effectuer",
        "metabolisme": "Analyse à effectuer",
        "excretion": "Analyse à effectuer"
    }

    # -----------------------------------------------------
    # 7. ORGANES / CIBLES
    # -----------------------------------------------------

    organes = [
        "Foie",
        "Reins",
        "Intestin",
        "Système nerveux",
        "Système cardiovasculaire"
    ]

    # -----------------------------------------------------
    # 8. TOXICOLOGIE
    # -----------------------------------------------------

    toxicologie = {

        "niveau":
            "À déterminer par SENTOX-QSAR",

        "risque":
            "À déterminer par SENTOX-QSAR",

        "organes_cibles":
            organes
    }

    # -----------------------------------------------------
    # 9. CONCLUSION
    # -----------------------------------------------------

    conclusion = (
        "SENTOX a identifié les éléments introduits et recherché "
        "les données disponibles dans sa base. Les analyses "
        "d'interactions, ADME et toxicologiques doivent être "
        "interprétées selon les données disponibles et le niveau "
        "d'incertitude des modèles prédictifs."
    )

    # -----------------------------------------------------
    # 10. AFFICHAGE
    # -----------------------------------------------------

    return render_template(

        "analyse.html",

        # Liste simple pour l'affichage
        elements=donnees,

        # Analyse détaillée
        analyses_individuelles=analyses_individuelles,

        # Constituants
        tous_constituants=tous_constituants,

        # Interactions
        interactions=interactions,

        # ADME
        adme=adme,

        # Organes
        organes=organes,

        # Toxicologie
        toxicologie=toxicologie,

        # Conclusion
        conclusion=conclusion,

        # Mode
        mode="melange"
    )
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )