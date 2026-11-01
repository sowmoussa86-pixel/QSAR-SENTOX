
# ============================================================
# SENTOX QHSE - REGISTRE DES RISQUES PROFESSIONNELS V1
# ============================================================

from datetime import datetime
from risk_engine import evaluer_risque


def creer_risque(
    secteur,
    activite,
    danger,
    personnes_exposees,
    consequences,
    gravite,
    probabilite,
    mesures_prevention="",
    responsable="",
    echeance=""
):
    """
    Crée une fiche de risque professionnel
    et calcule automatiquement sa criticité.
    """

    champs_obligatoires = {
        "secteur": secteur,
        "activité": activite,
        "danger": danger,
        "personnes exposées": personnes_exposees,
        "conséquences": consequences
    }

    for nom, valeur in champs_obligatoires.items():
        if not str(valeur).strip():
            raise ValueError(f"Le champ {nom} est obligatoire.")

    evaluation = evaluer_risque(gravite, probabilite)

    fiche = {
        "id": datetime.now().strftime("QHSE-%Y%m%d%H%M%S"),
        "date_creation": datetime.now().isoformat(timespec="seconds"),
        "secteur": secteur,
        "activite": activite,
        "danger": danger,
        "personnes_exposees": personnes_exposees,
        "consequences": consequences,
        "gravite": evaluation["gravite"],
        "probabilite": evaluation["probabilite"],
        "criticite": evaluation["criticite"],
        "niveau_risque": evaluation["niveau"],
        "action_recommandee": evaluation["action_recommandee"],
        "mesures_prevention": mesures_prevention,
        "responsable": responsable,
        "echeance": echeance,
        "statut": "A TRAITER"
    }

    return fiche


def resume_risque(fiche):
    """
    Produit un résumé lisible d'une fiche de risque.
    """

    return (
        f"Risque : {fiche['danger']}\n"
        f"Secteur : {fiche['secteur']}\n"
        f"Activité : {fiche['activite']}\n"
        f"Personnes exposées : {fiche['personnes_exposees']}\n"
        f"Criticité : {fiche['criticite']}/25\n"
        f"Niveau : {fiche['niveau_risque']}\n"
        f"Action : {fiche['action_recommandee']}\n"
        f"Statut : {fiche['statut']}"
    )
