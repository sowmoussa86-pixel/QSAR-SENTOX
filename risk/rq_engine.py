# ============================================================
# SENTOX - MOTEUR DE QUOTIENT DE RISQUE (RQ) V1
# ============================================================
import math

def valider_valeur(valeur, nom):
    """
    Vérifie qu'une valeur est numérique, finie et positive.
    """
    try:
        valeur = float(valeur)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{nom} doit être un nombre fini.")

    if not math.isfinite(valeur):
        raise ValueError(f"{nom} doit être un nombre fini.")

    if valeur <= 0:
        raise ValueError(
            f"{nom} doit être strictement supérieure à zéro."
        )

    return valeur



def calculer_rq(exposition_humaine, valeur_reference):
    """
    Calcule le Quotient de Risque (RQ).

    Formule :
        RQ = exposition humaine / valeur de référence

    L'interprétation du RQ dépend du contexte toxicologique,
    de la voie, de la durée et de la valeur de référence utilisée.
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
            "l'exposition humaine à une valeur de référence. "
            "Son interprétation nécessite le contexte toxicologique "
            "et réglementaire approprié."
        )
    }