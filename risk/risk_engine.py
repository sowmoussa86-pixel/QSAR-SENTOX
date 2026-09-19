# ============================================================
# SENTOX - MOTEUR D'EVALUATION DU RISQUE V1
# ============================================================


def valider_valeur(valeur, nom):
    """
    Vérifie qu'une valeur est numérique et positive.
    """

    try:
        valeur = float(valeur)
    except (TypeError, ValueError):
        raise ValueError(
            f"{nom} doit être numérique."
        )

    if valeur <= 0:
        raise ValueError(
            f"{nom} doit être supérieure à zéro."
        )

    return valeur


def calculer_moe(point_depart, exposition_humaine):
    """
    Calcule la marge d'exposition (MOE).

    Formule :
        MOE = point de départ / exposition humaine

    L'interprétation dépend du contexte toxicologique,
    de l'endpoint, de la voie et de la durée d'exposition.
    """

    point_depart = valider_valeur(
        point_depart,
        "Le point de départ"
    )

    exposition_humaine = valider_valeur(
        exposition_humaine,
        "L'exposition humaine"
    )

    moe = point_depart / exposition_humaine

    return {
        "point_depart": point_depart,
        "exposition_humaine": exposition_humaine,
        "MOE": moe,
        "unite": "sans unité",
        "statut": "Calculée",
    }


def evaluer_moe(moe):
    """
    Retourne une description de la MOE sans attribuer
    automatiquement un niveau de risque.

    Les seuils d'interprétation doivent être définis
    selon le contexte toxicologique et réglementaire.
    """

    moe = valider_valeur(moe, "La MOE")

    return {
        "MOE": moe,
        "statut": "Calculée",
        "interpretation": (
            "La MOE est un indicateur quantitatif de comparaison "
            "entre un point de départ toxicologique et une "
            "exposition humaine. Son interprétation nécessite "
            "le contexte toxicologique et réglementaire approprié."
        ),
    }


def calculer_exposition(dose, frequence, duree=None):
    """
    Structure une estimation d'exposition humaine.

    dose :
        dose ou quantité d'exposition par événement.

    frequence :
        nombre d'événements par unité de temps.

    Cette fonction ne transforme pas automatiquement
    les unités et ne constitue pas une estimation
    toxicologique complète.
    """

    dose = valider_valeur(dose, "La dose")
    frequence = valider_valeur(frequence, "La fréquence")

    exposition = dose * frequence

    return {
        "dose": dose,
        "frequence": frequence,
        "duree": duree,
        "exposition_calculee": exposition,
        "statut": "Calculée",
    }
