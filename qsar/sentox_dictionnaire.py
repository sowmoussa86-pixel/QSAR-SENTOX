"""
SENTOX - Dictionnaire de données
Gestion et validation du schéma scientifique SENTOX.
"""

import os
import pandas as pd


# ============================================================
# CHEMIN DU DICTIONNAIRE
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FICHIER_DICTIONNAIRE = os.path.join(
    BASE_DIR,
    "data",
    "dictionnaire_sentox.csv"
)


# ============================================================
# CHARGEMENT
# ============================================================

def charger_dictionnaire():
    """
    Charge le dictionnaire de données SENTOX.
    Le fichier CSV utilise le séparateur ';'.
    """

    if not os.path.exists(FICHIER_DICTIONNAIRE):
        raise FileNotFoundError(
            f"Dictionnaire SENTOX introuvable : {FICHIER_DICTIONNAIRE}"
        )

    return pd.read_csv(
        FICHIER_DICTIONNAIRE,
        sep=";",
        encoding="utf-8"
    )


# ============================================================
# VALIDATION
# ============================================================

COLONNES_OBLIGATOIRES = [
    "Domaine",
    "Table",
    "Champ",
    "Type",
    "Unite",
    "Description",
    "Source",
    "Statut_preuve",
    "Obligatoire",
    "Exemple"
]


def valider_dictionnaire(df=None):
    """
    Vérifie que le dictionnaire contient
    toutes les colonnes nécessaires.
    """

    if df is None:
        df = charger_dictionnaire()

    colonnes_manquantes = [
        colonne
        for colonne in COLONNES_OBLIGATOIRES
        if colonne not in df.columns
    ]

    if colonnes_manquantes:
        return {
            "valide": False,
            "message": "Colonnes manquantes",
            "colonnes_manquantes": colonnes_manquantes
        }

    return {
        "valide": True,
        "message": "Dictionnaire SENTOX valide",
        "nombre_champs": len(df)
    }


# ============================================================
# RECHERCHE D'UN CHAMP
# ============================================================

def rechercher_champ(champ):
    """
    Recherche un champ précis dans le dictionnaire.
    """

    df = charger_dictionnaire()

    resultat = df[
        df["Champ"]
        .astype(str)
        .str.lower()
        .eq(str(champ).lower())
    ]

    return resultat


# ============================================================
# RECHERCHE PAR DOMAINE
# ============================================================

def rechercher_domaine(domaine):
    """
    Retourne tous les champs appartenant
    à un domaine SENTOX.
    """

    df = charger_dictionnaire()

    resultat = df[
        df["Domaine"]
        .astype(str)
        .str.lower()
        .eq(str(domaine).lower())
    ]

    return resultat


# ============================================================
# RECHERCHE PAR TABLE
# ============================================================

def rechercher_table(table):
    """
    Retourne tous les champs appartenant
    à une table SENTOX.
    """

    df = charger_dictionnaire()

    resultat = df[
        df["Table"]
        .astype(str)
        .str.lower()
        .eq(str(table).lower())
    ]

    return resultat


# ============================================================
# LISTE DES DOMAINES
# ============================================================

def lister_domaines():
    """
    Retourne la liste des domaines SENTOX.
    """

    df = charger_dictionnaire()

    return sorted(
        df["Domaine"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


# ============================================================
# LISTE DES TABLES
# ============================================================

def lister_tables():
    """
    Retourne la liste des tables SENTOX.
    """

    df = charger_dictionnaire()

    return sorted(
        df["Table"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


# ============================================================
# TEST DU MODULE
# ============================================================

if __name__ == "__main__":

    print("======================================")
    print(" SENTOX - DICTIONNAIRE DE DONNÉES")
    print("======================================")

    try:

        dictionnaire = charger_dictionnaire()

        validation = valider_dictionnaire(dictionnaire)

        print(validation)

        print("\nDomaines disponibles :")

        for domaine in lister_domaines():
            print("-", domaine)

        print("\nNombre total de champs :")
        print(len(dictionnaire))

    except Exception as erreur:

        print("Erreur :", erreur)
