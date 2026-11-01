
# ============================================================
# SENTOX QHSE - GESTION DES ACTIONS CORRECTIVES V1
# ============================================================

from datetime import datetime


STATUTS_AUTORISES = [
    "A FAIRE",
    "EN COURS",
    "TERMINEE",
    "EN RETARD"
]


def creer_action(
    risque_id,
    description,
    responsable,
    echeance,
    priorite="NORMALE"
):
    if not description.strip():
        raise ValueError("La description est obligatoire.")

    if not responsable.strip():
        raise ValueError("Le responsable est obligatoire.")

    return {
        "risque_id": risque_id,
        "description": description,
        "responsable": responsable,
        "echeance": echeance,
        "priorite": priorite,
        "statut": "A FAIRE",
        "date_creation": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def modifier_statut(action, nouveau_statut):
    if nouveau_statut not in STATUTS_AUTORISES:
        raise ValueError("Statut non autorisé.")

    action["statut"] = nouveau_statut
    return action


def verifier_echeance(action):
    if action.get("statut") == "TERMINEE":
        return False

    echeance = action.get("echeance")

    if not echeance:
        return False

    try:
        date_limite = datetime.strptime(
            echeance,
            "%Y-%m-%d"
        ).date()

        if date_limite < datetime.now().date():
            action["statut"] = "EN RETARD"
            return True

    except ValueError:
        raise ValueError(
            "L'échéance doit être au format AAAA-MM-JJ."
        )

    return False
