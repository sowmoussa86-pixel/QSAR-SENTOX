
# ============================================================
# SENTOX QHSE - MOTEUR D'EVALUATION DES RISQUES V1
# ============================================================

def evaluer_risque(gravite, probabilite):
    """
    Évalue un risque selon une matrice simple 5 x 5.

    Gravité : 1 à 5
    Probabilité : 1 à 5
    Criticité = Gravité x Probabilité
    """

    try:
        gravite = int(gravite)
        probabilite = int(probabilite)
    except (TypeError, ValueError):
        raise ValueError("Les valeurs doivent être numériques.")

    if not 1 <= gravite <= 5:
        raise ValueError("La gravité doit être comprise entre 1 et 5.")

    if not 1 <= probabilite <= 5:
        raise ValueError("La probabilité doit être comprise entre 1 et 5.")

    criticite = gravite * probabilite

    if criticite <= 4:
        niveau = "FAIBLE"
        action = "Maintenir les mesures de prévention."
    elif criticite <= 9:
        niveau = "MODERE"
        action = "Renforcer la surveillance et la prévention."
    elif criticite <= 16:
        niveau = "ELEVE"
        action = "Définir des actions correctives prioritaires."
    else:
        niveau = "CRITIQUE"
        action = "Mettre en place des mesures urgentes."

    return {
        "gravite": gravite,
        "probabilite": probabilite,
        "criticite": criticite,
        "niveau": niveau,
        "action_recommandee": action,
        "methode": "Matrice 5x5 - SENTOX QHSE V1"
    }
