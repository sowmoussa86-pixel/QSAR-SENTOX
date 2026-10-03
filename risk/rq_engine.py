# ============================================================
# SENTOX - MOTEUR DE QUOTIENT DE RISQUE (RQ) V1
# ============================================================

def valider_valeur(valeur, nom):
    """
    Vérifie qu'une valeur est numérique et strictement positive.
    """
    try:
        valeur = float(valeur)
    except (TypeError, ValueError):
        raise ValueError(f"{nom} doit être numérique.")

    if valeur <= 0:
        raise ValueError(f"{nom} doit être supérieure à zéro.")

    return valeur


def calculer_rq(exposition_humaine, valeur_reference):
    """
    Calcule le quotient de risque (RQ).

    Formule :
        RQ = exposition humaine / valeur de référence

    Les deux valeurs doivent être exprimées
    dans des unités compatibles.

    Attention :
        L'interprétation du RQ dépend du contexte
        toxicologique, de l'endpoint, de la voie
        d'exposition et de la valeur de référence utilisée.
    """

    exposition_humaine = valider_valeur(
        exposition_humaine,
        "L'exposition humaine"
    )

    valeur_reference = valider_valeur(
        valeur_reference,
        "La valeur de référence"
    )

    rq = exposition_humaine / valeur_reference

    return {
        "exposition_humaine": exposition_humaine,
        "valeur_reference": valeur_reference,
        "RQ": rq,
        "unite": "sans unité",
        "statut": "Calculée",
        "interpretation": (
            "Le RQ est un indicateur quantitatif comparant "
            "une exposition humaine à une valeur de référence. "
            "Son interprétation nécessite le contexte "
            "toxicologique et réglementaire approprié."
        )
    }
