# ============================================================
# SENTOX - MOTEUR D'INCERTITUDE V1
# ============================================================


def valider_facteur(facteur):
    """
    Vérifie qu'un facteur d'incertitude est numérique et positif.
    """

    try:
        facteur = float(facteur)
    except (TypeError, ValueError):
        raise ValueError(
            "Le facteur d'incertitude doit être numérique."
        )

    if facteur <= 0:
        raise ValueError(
            "Le facteur d'incertitude doit être supérieur à zéro."
        )

    return facteur


def calculer_dose_ajustee(valeur_reference, facteur_incertitude):
    """
    Calcule une valeur ajustée après application
    d'un facteur d'incertitude.

    Formule :
        Dose ajustée = valeur de référence / facteur

    Cette valeur ne constitue pas automatiquement
    une dose sûre ou thérapeutique.
    """

    try:
        valeur_reference = float(valeur_reference)
    except (TypeError, ValueError):
        raise ValueError(
            "La valeur de référence doit être numérique."
        )

    if valeur_reference <= 0:
        raise ValueError(
            "La valeur de référence doit être supérieure à zéro."
        )

    facteur = valider_facteur(facteur_incertitude)

    dose_ajustee = valeur_reference / facteur

    return {
        "valeur_reference": valeur_reference,
        "facteur_incertitude": facteur,
        "valeur_ajustee": dose_ajustee,
        "unite": "mg/kg",
        "statut": "Calculée",
        "interpretation": (
            "Valeur calculée après application du facteur "
            "d'incertitude. Elle ne constitue pas à elle seule "
            "une dose thérapeutique ou une garantie de sécurité."
        ),
    }


def calculer_moe(point_depart, exposition_humaine):
    """
    Calcule la marge d'exposition (MOE).

    Formule :
        MOE = point de départ / exposition humaine

    Les unités doivent être compatibles.
    """

    try:
        point_depart = float(point_depart)
        exposition_humaine = float(exposition_humaine)
    except (TypeError, ValueError):
        raise ValueError(
            "Le point de départ et l'exposition humaine "
            "doivent être numériques."
        )

    if point_depart <= 0:
        raise ValueError(
            "Le point de départ doit être supérieur à zéro."
        )

    if exposition_humaine <= 0:
        raise ValueError(
            "L'exposition humaine doit être supérieure à zéro."
        )

    moe = point_depart / exposition_humaine

    return {
        "point_depart": point_depart,
        "exposition_humaine": exposition_humaine,
        "MOE": moe,
        "statut": "Calculée",
        "interpretation": (
            "La MOE est un indicateur quantitatif de comparaison "
            "entre un point de départ toxicologique et une exposition. "
            "Son interprétation dépend du contexte toxicologique "
            "et réglementaire."
        ),
    }
