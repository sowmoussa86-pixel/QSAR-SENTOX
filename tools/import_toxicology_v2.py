import pandas as pd
from pathlib import Path

SOURCE = Path("data/molecules.csv")
DESTINATION = Path("data/sentox_toxicology_v2.csv")

COLONNES_V2 = [
    "Tox_ID",
    "CID",
    "Nom",
    "Synonymes",
    "SMILES",
    "Type_element",
    "Plante_ou_produit",
    "Endpoint",
    "Valeur",
    "Unite",
    "Espece",
    "Sexe",
    "Voie_exposition",
    "Type_exposition",
    "Duree",
    "Effet",
    "Organe_cible",
    "Source",
    "Reference",
    "Qualite_donnee",
    "Statut",
    "Date_verification",
    "Point_depart",
    "Km_animal",
    "Km_humain",
    "HED",
    "Facteur_incertitude",
    "Dose_reference_humaine",
    "Exposition_humaine",
    "MOE",
    "RQ",
    "QSAR_prediction",
    "Unite_prediction",
    "Domaine_applicabilite",
    "Distance_modele",
    "Confiance_prediction",
    "Categorie_risque",
    "Organe_potentiel",
    "Commentaire_SENTOX",
]


def texte(valeur):
    if pd.isna(valeur):
        return ""
    return str(valeur).strip()


def main():

    df = pd.read_csv(SOURCE)

    df = df[
        df["LD50_mg_kg"].notna()
        & df["SMILES"].notna()
    ].copy()

    enregistrements = []

    for index, (smiles, groupe) in enumerate(
        df.groupby("SMILES", sort=False),
        start=1
    ):

        premier = groupe.iloc[0]

        noms = []

        for nom in groupe["Nom"]:
            nom = texte(nom)

            if nom and nom not in noms:
                noms.append(nom)

        nom_principal = noms[0]
        synonymes = [
            nom for nom in noms
            if nom != nom_principal
        ]

        enregistrements.append({
            "Tox_ID": f"TOX_{index:04d}",
            "CID": None,
            "Nom": nom_principal,
            "Synonymes": "; ".join(synonymes),
            "SMILES": texte(smiles),

            "Type_element": "molécule",
            "Plante_ou_produit": None,

            "Endpoint": "LD50",
            "Valeur": float(premier["LD50_mg_kg"]),
            "Unite": "mg/kg",

            "Espece": "Non précisée",
            "Sexe": "Non précisé",
            "Voie_exposition": "Non précisée",
            "Type_exposition": "aiguë",
            "Duree": "Non précisée",

            "Effet": None,
            "Organe_cible": None,

            "Source": texte(premier["Source"]),
            "Reference": None,
            "Qualite_donnee": "À vérifier",
            "Statut": "Documentée",

            "Date_verification": None,

            "Point_depart": None,
            "Km_animal": None,
            "Km_humain": None,
            "HED": None,

            "Facteur_incertitude": None,
            "Dose_reference_humaine": None,

            "Exposition_humaine": None,
            "MOE": None,
            "RQ": None,

            "QSAR_prediction": None,
            "Unite_prediction": None,
            "Domaine_applicabilite": None,
            "Distance_modele": None,
            "Confiance_prediction": None,

            "Categorie_risque": None,
            "Organe_potentiel": None,

            "Commentaire_SENTOX": (
                "LD50 importée depuis molecules.csv. "
                "Espèce, voie détaillée et contexte non précisés. "
                "HED, MOE et RQ non calculés automatiquement."
            ),
        })

    resultat = pd.DataFrame(
        enregistrements,
        columns=COLONNES_V2
    )

    resultat.to_csv(
        DESTINATION,
        index=False
    )

    print("=== IMPORT SENTOX V2 ===")
    print("Lignes source :", len(df))
    print("Structures uniques :", len(resultat))
    print("")
    print(
        resultat[
            [
                "Tox_ID",
                "Nom",
                "Synonymes",
                "Endpoint",
                "Valeur",
                "Unite",
                "Source",
                "Qualite_donnee",
                "HED",
                "MOE",
                "RQ"
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
