import pandas as pd
from pathlib import Path


# ============================================================
# SENTOX - MOTEUR D'EXTRAPOLATION ANIMAL → HUMAIN
# ============================================================

REFERENCE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sentox_extrapolation_reference.csv"
)


def charger_references():
    """
    Charge les paramètres d'extrapolation
    depuis le fichier CSV SENTOX.
    """

    if not REFERENCE_FILE.exists():
        raise FileNotFoundError(
            f"Fichier de référence introuvable : {REFERENCE_FILE}"
        )

    df = pd.read_csv(REFERENCE_FILE)

    colonnes_requises = {
        "Parametre",
        "Espece",
        "Valeur",
        "Unite",
        "Contexte",
        "Source",
        "Reference",
        "Statut",
    }

    colonnes_manquantes = colonnes_requises - set(df.columns)

    if colonnes_manquantes:
        raise ValueError(
            "Colonnes manquantes dans le fichier de référence : "
            + ", ".join(sorted(colonnes_manquantes))
        )

    return df


def obtenir_km(espece):
    """
    Retourne la valeur Km correspondant à l'espèce.
    """

    if not isinstance(espece, str) or not espece.strip():
        raise ValueError("L'espèce doit être renseignée.")

    df = charger_references()

    espece_normalisee = espece.strip().lower()

    ligne = df[
        (df["Parametre"].astype(str).str.lower() == "km")
        & (
            df["Espece"]
            .astype(str)
            .str.strip()
            .str.lower()
            == espece_normalisee
        )
    ]

    if ligne.empty:
        raise ValueError(
            f"Aucune valeur Km trouvée pour l'espèce : {espece}"
        )

    valeur = ligne.iloc[0]["Valeur"]

    try:
        km = float(valeur)
    except (TypeError, ValueError):
        raise ValueError(
            f"Valeur Km invalide pour l'espèce : {espece}"
        )

    if km <= 0:
        raise ValueError(
            f"La valeur Km doit être supérieure à zéro : {espece}"
        )

    return km


def valider_entrees(dose_animale, espece):
    """
    Vérifie que les données d'entrée sont valides.
    """

    try:
        dose = float(dose_animale)
    except (TypeError, ValueError):
        raise ValueError(
            "La dose animale doit être un nombre."
        )

    if dose <= 0:
        raise ValueError(
            "La dose animale doit être supérieure à zéro."
        )

    if not isinstance(espece, str) or not espece.strip():
        raise ValueError(
            "L'espèce doit être renseignée."
        )

    # Vérifie également que l'espèce existe dans la table Km.
    obtenir_km(espece)

    return True


def calculer_hed(dose_animale, espece):
    """
    Calcule la dose équivalente humaine (HED).

    Formule :

        HED = Dose animale × Km animal / Km humain

    Important :
        La HED est une conversion basée sur le facteur
        de surface corporelle. Elle ne constitue pas à elle
        seule une dose thérapeutique ni une dose sûre.
    """

    valider_entrees(dose_animale, espece)

    dose_animale = float(dose_animale)

    km_animal = obtenir_km(espece)
    km_humain = obtenir_km("humain_adulte")

    hed = dose_animale * km_animal / km_humain

    return {
        "dose_animale": dose_animale,
        "espece": espece.strip(),
        "Km_animal": km_animal,
        "Km_humain": km_humain,
        "HED": hed,
        "unite": "mg/kg",
    }


def obtenir_facteur_securite(contexte="MRSD_initiale"):
    """
    Retourne le facteur de sécurité de référence
    pour le contexte demandé.

    Attention :
        Ce facteur n'est pas une règle universelle.
        Il doit être interprété selon le contexte
        réglementaire et toxicologique approprié.
    """

    if not isinstance(contexte, str) or not contexte.strip():
        raise ValueError(
            "Le contexte doit être renseigné."
        )

    df = charger_references()

    contexte_normalise = contexte.strip().lower()

    ligne = df[
        (df["Parametre"].astype(str).str.lower() == "facteur_securite")
        & (
            df["Contexte"]
            .astype(str)
            .str.strip()
            .str.lower()
            == contexte_normalise
        )
    ]

    if ligne.empty:
        raise ValueError(
            f"Aucun facteur de sécurité trouvé pour le contexte : {contexte}"
        )

    valeur = ligne.iloc[0]["Valeur"]

    try:
        facteur = float(valeur)
    except (TypeError, ValueError):
        raise ValueError(
            f"Facteur de sécurité invalide pour le contexte : {contexte}"
        )

    if facteur <= 0:
        raise ValueError(
            "Le facteur de sécurité doit être supérieur à zéro."
        )

    return facteur


def calculer_dose_reference(
    dose_animale,
    espece,
    contexte="MRSD_initiale",
):
    """
    Calcule une dose de référence à partir de la HED
    et du facteur de sécurité correspondant au contexte.

    Cette valeur ne constitue pas automatiquement une dose
    thérapeutique ni une dose sûre chez l'humain.
    """

    resultat_hed = calculer_hed(
        dose_animale,
        espece,
    )

    facteur = obtenir_facteur_securite(
        contexte
    )

    dose_reference = (
        resultat_hed["HED"] / facteur
    )

    return {
        **resultat_hed,
        "facteur_securite": facteur,
        "contexte": contexte,
        "dose_reference": dose_reference,
        "unite_dose_reference": "mg/kg",
    }
