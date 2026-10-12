"""
SENTOX - Garde-fous toxicologiques
Cette couche vérifie les métadonnées avant un calcul.
Elle ne valide pas elle-même les études scientifiques.
"""

from risk.risk_engine import calculer_moe
from risk.rq_engine import calculer_rq


def verifier_donnee(donnee, role):
    erreurs = []

    statut = str(donnee.get("statut_validation", "")).strip().lower()
    source = str(donnee.get("source", "")).strip()
    voie = str(donnee.get("voie", "")).strip().lower()
    unite = str(donnee.get("unite", "")).strip().lower()
    endpoint = str(donnee.get("endpoint", "")).strip().upper()

    if statut != "validee":
        erreurs.append("Donnée non validée scientifiquement.")

    if not source:
        erreurs.append("Source bibliographique absente.")

    if not voie:
        erreurs.append("Voie d'exposition absente.")

    if not unite:
        erreurs.append("Unité absente.")

    if role == "reference_rq":
        if endpoint not in ("RFD", "RFC"):
            erreurs.append(
                "Pour ce contrôle RQ, la référence doit être "
                "une RfD ou une RfC documentée."
            )

    if role == "point_depart_moe":
        if endpoint not in ("NOAEL", "LOAEL", "BMDL", "POD"):
            erreurs.append(
                "Le point de départ doit être identifié "
                "comme NOAEL, LOAEL, BMDL ou POD."
            )

    return erreurs


def calculer_rq_securise(
    exposition, reference, meta_exposition, meta_reference
):
    erreurs = []
    erreurs += verifier_donnee(meta_exposition, "exposition")
    erreurs += verifier_donnee(meta_reference, "reference_rq")

    if meta_exposition.get("voie", "").strip().lower() != \
       meta_reference.get("voie", "").strip().lower():
        erreurs.append("Voies d'exposition incompatibles.")

    if meta_exposition.get("unite", "").strip().lower() != \
       meta_reference.get("unite", "").strip().lower():
        erreurs.append("Unités incompatibles : conversion à vérifier.")

    if erreurs:
        return {
            "statut": "BLOQUE",
            "RQ": None,
            "motifs": erreurs,
        }

    resultat = calculer_rq(exposition, reference)
    resultat["statut"] = "Calcul autorisé - métadonnées contrôlées"
    resultat["avertissement"] = (
        "Ce contrôle logiciel ne remplace pas la validation "
        "scientifique indépendante."
    )
    return resultat


def calculer_moe_securisee(
    point_depart, exposition, meta_point, meta_exposition
):
    erreurs = []
    erreurs += verifier_donnee(meta_point, "point_depart_moe")
    erreurs += verifier_donnee(meta_exposition, "exposition")

    if meta_point.get("voie", "").strip().lower() != \
       meta_exposition.get("voie", "").strip().lower():
        erreurs.append("Voies d'exposition incompatibles.")

    if meta_point.get("unite", "").strip().lower() != \
       meta_exposition.get("unite", "").strip().lower():
        erreurs.append("Unités incompatibles : conversion à vérifier.")

    if erreurs:
        return {
            "statut": "BLOQUE",
            "MOE": None,
            "motifs": erreurs,
        }

    resultat = calculer_moe(point_depart, exposition)
    resultat["statut"] = "Calcul autorisé - métadonnées contrôlées"
    resultat["avertissement"] = (
        "Ce contrôle logiciel ne remplace pas la validation "
        "scientifique indépendante."
    )
    return resultat
