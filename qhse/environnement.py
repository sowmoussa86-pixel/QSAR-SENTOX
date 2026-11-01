
# ============================================================
# SENTOX QHSE - MODULE ENVIRONNEMENT V1
# ============================================================

from datetime import datetime


CATEGORIES = [
    "DECHETS",
    "EAU",
    "AIR",
    "SOL",
    "ENERGIE",
    "BRUIT",
    "RESSOURCES NATURELLES"
]


def creer_impact(
    secteur,
    activite,
    aspect,
    impact,
    categorie,
    gravite,
    probabilite,
    mesures_maitrise=""
):
    if not secteur.strip():
        raise ValueError("Le secteur est obligatoire.")

    if not activite.strip():
        raise ValueError("L'activité est obligatoire.")

    if categorie not in CATEGORIES:
        raise ValueError("Catégorie environnementale invalide.")

    try:
        gravite = int(gravite)
        probabilite = int(probabilite)
    except (TypeError, ValueError):
        raise ValueError("Les niveaux doivent être numériques.")

    if not 1 <= gravite <= 5:
        raise ValueError("Gravité comprise entre 1 et 5.")

    if not 1 <= probabilite <= 5:
        raise ValueError("Probabilité comprise entre 1 et 5.")

    criticite = gravite * probabilite

    if criticite <= 4:
        niveau = "FAIBLE"
    elif criticite <= 9:
        niveau = "MODERE"
    elif criticite <= 16:
        niveau = "ELEVE"
    else:
        niveau = "CRITIQUE"

    return {
        "date_creation": datetime.now().isoformat(
            timespec="seconds"
        ),
        "secteur": secteur,
        "activite": activite,
        "aspect_environnemental": aspect,
        "impact_environnemental": impact,
        "categorie": categorie,
        "gravite": gravite,
        "probabilite": probabilite,
        "criticite": criticite,
        "niveau": niveau,
        "mesures_maitrise": mesures_maitrise
    }
