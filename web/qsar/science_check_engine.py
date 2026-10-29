"""Moteur initial de Science Check pour SENTOX.

V1 : évaluation indicative fondée sur les informations déclarées.
Aucune recherche bibliographique automatique ni vérification des références.
"""

NIVEAUX_PREUVE = {
    "aucune": {
        "rang": 0,
        "libelle": "Aucune preuve fournie",
        "limite": "L'affirmation ne peut pas être validée avec les informations fournies."
    },
    "tradition": {
        "rang": 1,
        "libelle": "Usage traditionnel rapporté",
        "limite": "L'usage traditionnel ne démontre pas à lui seul l'efficacité ni l'innocuité."
    },
    "in_vitro": {
        "rang": 2,
        "libelle": "Données in vitro",
        "limite": "Un résultat en laboratoire ne démontre pas nécessairement un effet chez l'humain."
    },
    "animal": {
        "rang": 3,
        "libelle": "Données animales",
        "limite": "Les résultats animaux ne sont pas directement transposables à l'humain."
    },
    "observationnelle": {
        "rang": 4,
        "libelle": "Étude observationnelle humaine",
        "limite": "Une association observée ne démontre pas à elle seule un lien causal."
    },
    "essai_clinique": {
        "rang": 5,
        "libelle": "Essai clinique rapporté",
        "limite": "La qualité, la taille, les résultats et les biais de l'essai doivent être examinés."
    },
    "revue_systematique": {
        "rang": 6,
        "libelle": "Revue systématique rapportée",
        "limite": "La méthode, la qualité des études et la cohérence des résultats doivent être vérifiées."
    }
}


def evaluer_affirmation(
    affirmation,
    domaine="sante",
    niveau_preuve="aucune",
    preparation_exacte="",
    references=""
):
    """Produit une première évaluation prudente à partir des données déclarées."""

    affirmation = (affirmation or "").strip()
    domaine = (domaine or "sante").strip()
    preparation_exacte = (preparation_exacte or "").strip()
    references = (references or "").strip()
    niveau = (niveau_preuve or "aucune").strip().lower()

    if not affirmation:
        raise ValueError("Veuillez saisir une affirmation à évaluer.")

    if niveau not in NIVEAUX_PREUVE:
        raise ValueError("Niveau de preuve non reconnu.")

    preuve = NIVEAUX_PREUVE[niveau]

    if niveau == "aucune":
        verdict = "NON ÉTABLI — preuves non fournies"
    elif niveau == "tradition":
        verdict = "USAGE RAPPORTÉ — efficacité non démontrée par ce seul niveau"
    elif niveau in ("in_vitro", "animal"):
        verdict = "PREUVE PRÉCLINIQUE — confirmation humaine nécessaire"
    elif niveau == "observationnelle":
        verdict = "INDICE HUMAIN — causalité et biais à examiner"
    else:
        verdict = "PREUVE HUMAINE OU SYNTHÈSE RAPPORTÉE — qualité à vérifier"

    points_a_verifier = [
        "La source originale et sa date",
        "La méthode, les témoins et les limites de l'étude",
        "La dose, la voie d'administration et la durée",
        "La pertinence des résultats pour l'affirmation examinée",
        "Les effets indésirables et les populations à risque"
    ]

    if not preparation_exacte:
        points_a_verifier.insert(
            0,
            "Préciser la composition, la préparation et la dose étudiées"
        )

    if not references:
        statut_references = "Aucune référence fournie ; aucune vérification bibliographique effectuée."
    else:
        statut_references = (
            "Référence(s) déclarée(s) par l'utilisateur ; "
            "authenticité et contenu non vérifiés automatiquement."
        )

    return {
        "affirmation": affirmation,
        "domaine": domaine,
        "niveau_preuve": niveau,
        "niveau_preuve_libelle": preuve["libelle"],
        "verdict": verdict,
        "limite_principale": preuve["limite"],
        "preparation_exacte": preparation_exacte or "Non précisée",
        "references": references or "Non fournies",
        "statut_references": statut_references,
        "points_a_verifier": points_a_verifier,
        "avertissement": (
            "Cette évaluation préliminaire ne constitue pas une validation "
            "scientifique ni un avis médical. Ne pas retarder un diagnostic "
            "ou remplacer un traitement prescrit sur cette seule base."
        )
    }
