# =========================================================
# SENTOX — MODULE ADME
# Absorption • Distribution • Métabolisme • Excrétion
# =========================================================

"""
SENTOX ADME

Ce module organise les informations ADME selon trois niveaux :

1. DOCUMENTÉ
   Donnée provenant d'une source scientifique ou d'une base.

2. CALCULÉ
   Valeur obtenue par un calcul à partir de données disponibles.

3. PRÉDIT
   Résultat provenant d'un modèle prédictif.

IMPORTANT :
Ce module constitue une architecture de travail pour SENTOX.
Une prédiction n'est pas une preuve expérimentale.
"""

from typing import Any, Dict, List, Optional


# =========================================================
# 1. STRUCTURE ADME
# =========================================================

def creer_resultat_adme(
    absorption: Optional[Dict[str, Any]] = None,
    distribution: Optional[Dict[str, Any]] = None,
    metabolisme: Optional[Dict[str, Any]] = None,
    excretion: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crée une structure standardisée pour les données ADME.
    """

    return {
        "absorption": absorption or {},
        "distribution": distribution or {},
        "metabolisme": metabolisme or {},
        "excretion": excretion or {}
    }


# =========================================================
# 2. ABSORPTION
# =========================================================

def analyser_absorption(donnees: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyse les informations disponibles concernant
    l'absorption d'une substance.
    """

    donnees = donnees or {}

    resultat = {
        "niveau": "Non déterminé",
        "statut": "non_disponible",
        "voie": donnees.get("voie"),
        "biodisponibilite": donnees.get("biodisponibilite"),
        "permeabilite": donnees.get("permeabilite"),
        "pH_dependance": donnees.get("pH_dependance"),
        "source": donnees.get("source"),
        "interpretation": ""
    }

    if donnees:
        resultat["statut"] = "documente"
        resultat["niveau"] = "Donnée documentée"
        resultat["interpretation"] = (
            "Des données d'absorption sont disponibles "
            "dans les données fournies."
        )
    else:
        resultat["statut"] = "a_predire"
        resultat["niveau"] = "À prédire"
        resultat["interpretation"] = (
            "Aucune donnée d'absorption documentée n'a été "
            "fournie pour cet élément."
        )

    return resultat


# =========================================================
# 3. DISTRIBUTION
# =========================================================

def analyser_distribution(donnees: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyse les informations disponibles concernant
    la distribution d'une substance dans l'organisme.
    """

    donnees = donnees or {}

    resultat = {
        "niveau": "Non déterminé",
        "statut": "non_disponible",
        "liaison_proteines": donnees.get("liaison_proteines"),
        "volume_distribution": donnees.get("volume_distribution"),
        "barriere_hemato_encephalique": donnees.get(
            "barriere_hemato_encephalique"
        ),
        "distribution_tissulaire": donnees.get(
            "distribution_tissulaire"
        ),
        "source": donnees.get("source"),
        "interpretation": ""
    }

    if donnees:
        resultat["statut"] = "documente"
        resultat["niveau"] = "Donnée documentée"
        resultat["interpretation"] = (
            "Des informations de distribution sont disponibles."
        )
    else:
        resultat["statut"] = "a_predire"
        resultat["niveau"] = "À prédire"
        resultat["interpretation"] = (
            "Les paramètres de distribution devront être "
            "déterminés à partir de données expérimentales "
            "ou de modèles prédictifs."
        )

    return resultat


# =========================================================
# 4. MÉTABOLISME
# =========================================================

def analyser_metabolisme(donnees: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyse les informations concernant le métabolisme.
    """

    donnees = donnees or {}

    resultat = {
        "niveau": "Non déterminé",
        "statut": "non_disponible",
        "organe_principal": donnees.get(
            "organe_principal",
            "Foie"
        ),
        "enzymes": donnees.get("enzymes", []),
        "cyp": donnees.get("cyp", []),
        "metabolites": donnees.get("metabolites", []),
        "induction": donnees.get("induction"),
        "inhibition": donnees.get("inhibition"),
        "source": donnees.get("source"),
        "interpretation": ""
    }

    if donnees:
        resultat["statut"] = "documente"
        resultat["niveau"] = "Donnée documentée"
        resultat["interpretation"] = (
            "Des informations concernant le métabolisme "
            "sont disponibles."
        )
    else:
        resultat["statut"] = "a_predire"
        resultat["niveau"] = "À prédire"
        resultat["interpretation"] = (
            "Le métabolisme devra être étudié à partir "
            "des données disponibles et, si possible, "
            "par des modèles prédictifs."
        )

    return resultat


# =========================================================
# 5. EXCRÉTION
# =========================================================

def analyser_excretion(donnees: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyse les informations concernant l'excrétion.
    """

    donnees = donnees or {}

    resultat = {
        "niveau": "Non déterminé",
        "statut": "non_disponible",
        "voie_principale": donnees.get("voie_principale"),
        "urinaire": donnees.get("urinaire"),
        "biliaire": donnees.get("biliaire"),
        "fecale": donnees.get("fecale"),
        "demi_vie": donnees.get("demi_vie"),
        "clairance": donnees.get("clairance"),
        "source": donnees.get("source"),
        "interpretation": ""
    }

    if donnees:
        resultat["statut"] = "documente"
        resultat["niveau"] = "Donnée documentée"
        resultat["interpretation"] = (
            "Des données d'excrétion sont disponibles."
        )
    else:
        resultat["statut"] = "a_predire"
        resultat["niveau"] = "À prédire"
        resultat["interpretation"] = (
            "Aucune donnée d'excrétion documentée n'a été "
            "fournie pour cet élément."
        )

    return resultat


# =========================================================
# 6. ANALYSE ADME COMPLÈTE
# =========================================================

def analyser_adme(
    donnees: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Fonction principale du module ADME.

    Elle accepte éventuellement un dictionnaire contenant
    des données documentées et construit une analyse ADME
    standardisée.
    """

    donnees = donnees or {}

    absorption = analyser_absorption(
        donnees.get("absorption")
    )

    distribution = analyser_distribution(
        donnees.get("distribution")
    )

    metabolisme = analyser_metabolisme(
        donnees.get("metabolisme")
    )

    excretion = analyser_excretion(
        donnees.get("excretion")
    )

    return creer_resultat_adme(
        absorption=absorption,
        distribution=distribution,
        metabolisme=metabolisme,
        excretion=excretion
    )


# =========================================================
# 7. MODE PRÉDICTIF
# =========================================================

def prediction_adme(
    nom: str,
    proprietes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prépare une structure de prédiction ADME.

    Cette fonction ne prétend pas remplacer un modèle QSAR.
    Elle sert d'interface pour connecter ultérieurement
    les véritables modèles prédictifs SENTOX-QSAR.
    """

    proprietes = proprietes or {}

    return {
        "element": nom,

        "absorption": {
            "statut": "predit",
            "resultat": "À déterminer par modèle ADME",
            "proprietes_utilisees": [
                "logP",
                "poids_moleculaire",
                "polarite",
                "liaisons_hydrogene"
            ],
            "valeurs": {
                "logP": proprietes.get("logP"),
                "poids_moleculaire": proprietes.get(
                    "poids_moleculaire"
                ),
                "polarite": proprietes.get("polarite")
            }
        },

        "distribution": {
            "statut": "predit",
            "resultat": "À déterminer par modèle ADME"
        },

        "metabolisme": {
            "statut": "predit",
            "resultat": "À déterminer par modèle ADME",
            "enzymes_potentielles": []
        },

        "excretion": {
            "statut": "predit",
            "resultat": "À déterminer par modèle ADME"
        },

        "avertissement": (
            "Les résultats prédictifs nécessitent une validation "
            "scientifique et expérimentale appropriée."
        )
    }


# =========================================================
# 8. ADME POUR UN MÉLANGE
# =========================================================

def analyser_adme_melange(
    elements: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyse ADME de plusieurs éléments.

    Exemple :

    elements = [
        {"nom": "miel"},
        {"nom": "ail"},
        {"nom": "paracetamol"}
    ]
    """

    resultats = []

    for element in elements:

        nom = element.get(
            "nom",
            "Élément inconnu"
        )

        donnees = element.get(
            "adme",
            {}
        )

        analyse = analyser_adme(donnees)

        resultats.append({
            "nom": nom,
            "adme": analyse
        })

    return {
        "nombre_elements": len(resultats),
        "elements": resultats,

        "interpretation": (
            "L'analyse ADME du mélange doit tenir compte "
            "des propriétés propres à chaque constituant "
            "et des interactions pharmacocinétiques "
            "potentielles."
        )
    }


# =========================================================
# 9. RÉSUMÉ POUR L'INTERFACE SENTOX
# =========================================================

def resume_adme(adme: Dict[str, Any]) -> Dict[str, str]:
    """
    Transforme les résultats ADME en résumé simple
    pour l'affichage dans analyse.html.
    """

    return {
        "absorption": adme.get(
            "absorption",
            {}
        ).get(
            "niveau",
            "Non disponible"
        ),

        "distribution": adme.get(
            "distribution",
            {}
        ).get(
            "niveau",
            "Non disponible"
        ),

        "metabolisme": adme.get(
            "metabolisme",
            {}
        ).get(
            "niveau",
            "Non disponible"
        ),

        "excretion": adme.get(
            "excretion",
            {}
        ).get(
            "niveau",
            "Non disponible"
        )
    }


# =========================================================
# 10. TEST DU MODULE
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SENTOX — TEST DU MODULE ADME")
    print("=" * 60)

    resultat = analyser_adme()

    print("\nABSORPTION :")
    print(resultat["absorption"]["niveau"])

    print("\nDISTRIBUTION :")
    print(resultat["distribution"]["niveau"])

    print("\nMÉTABOLISME :")
    print(resultat["metabolisme"]["niveau"])

    print("\nEXCRÉTION :")
    print(resultat["excretion"]["niveau"])

    print("\nModule ADME SENTOX opérationnel.")
