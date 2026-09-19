from math import log10


# ============================================================
# SENTOX - MOTEUR TOXICOLOGIQUE V1
# ============================================================

ENDPOINTS_AUTORISES = {
    "LD50",
    "NOAEL",
    "LOAEL",
    "BMD",
    "BMDL",
}


def valider_endpoint(endpoint):
    """
    Vérifie que le type de point de départ est reconnu par SENTOX.
    """

    if not isinstance(endpoint, str):
        raise ValueError("L'endpoint doit être une chaîne de caractères.")

    endpoint_normalise = endpoint.strip().upper()

    if endpoint_normalise not in ENDPOINTS_AUTORISES:
        raise ValueError(
            f"Endpoint non reconnu : {endpoint}. "
            f"Valeurs autorisées : {', '.join(sorted(ENDPOINTS_AUTORISES))}"
        )

    return endpoint_normalise


def valider_dose(valeur):
    """
    Vérifie qu'une valeur toxicologique est numérique et positive.
    """

    try:
        dose = float(valeur)
    except (TypeError, ValueError):
        raise ValueError(
            "La valeur toxicologique doit être numérique."
        )

    if dose <= 0:
        raise ValueError(
            "La valeur toxicologique doit être supérieure à zéro."
        )

    return dose


def creer_donnee_toxicologique(
    endpoint,
    valeur,
    unite="mg/kg",
    espece=None,
    voie_exposition=None,
    type_exposition=None,
    duree=None,
    source=None,
    reference=None,
    statut="Documentée",
):
    """
    Crée une observation toxicologique structurée.

    Aucune valeur toxicologique n'est inventée par ce moteur.
    La valeur doit provenir d'une source fournie au système.
    """

    endpoint = valider_endpoint(endpoint)
    valeur = valider_dose(valeur)

    return {
        "Endpoint": endpoint,
        "Valeur": valeur,
        "Unite": unite,
        "Espece": espece,
        "Voie_exposition": voie_exposition,
        "Type_exposition": type_exposition,
        "Duree": duree,
        "Source": source,
        "Reference": reference,
        "Statut": statut,
    }


def calculer_log10_dose(valeur):
    """
    Calcule log10 d'une valeur toxicologique positive.

    Utilisé notamment pour les analyses de type LD50.
    """

    valeur = valider_dose(valeur)

    return log10(valeur)


def classer_point_depart(endpoint):
    """
    Classe le point de départ toxicologique selon sa nature.

    Cette fonction ne donne pas de niveau de danger.
    Elle identifie uniquement la nature de la donnée.
    """

    endpoint = valider_endpoint(endpoint)

    if endpoint == "LD50":
        return {
            "type": "toxicite_aigue",
            "interpretation": (
                "Indicateur de toxicité aiguë. "
                "Ne doit pas être assimilé automatiquement "
                "à une dose thérapeutique ou à un NOAEL."
            ),
        }

    if endpoint in {"NOAEL", "LOAEL", "BMD", "BMDL"}:
        return {
            "type": "point_depart_toxicologique",
            "interpretation": (
                "Point de départ toxicologique pouvant être "
                "utilisé pour une évaluation de risque selon "
                "le contexte, l'étude et la voie d'exposition."
            ),
        }

    raise ValueError(f"Endpoint non pris en charge : {endpoint}")


def preparer_point_depart(endpoint, valeur, unite="mg/kg"):
    """
    Prépare un point de départ pour les étapes ultérieures
    d'extrapolation et d'évaluation du risque.

    Le moteur conserve la distinction entre :
    - donnée documentée ;
    - calcul ;
    - prédiction.
    """

    endpoint = valider_endpoint(endpoint)
    valeur = valider_dose(valeur)

    resultat = {
        "Endpoint": endpoint,
        "Valeur": valeur,
        "Unite": unite,
        "Statut": "Documentée",
    }

    resultat["Classification"] = classer_point_depart(endpoint)

    if endpoint == "LD50":
        resultat["Log10_valeur"] = calculer_log10_dose(valeur)

    return resultat
