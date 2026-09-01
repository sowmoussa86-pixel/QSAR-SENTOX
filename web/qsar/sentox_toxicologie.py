# =========================================================
# SENTOX — MODULE TOXICOLOGIE
# Toxicité • DL50 • Organes cibles • Voies d'exposition
# Documenté • Calculé • Prédit
# =========================================================

"""
SENTOX — Toxicologie prédictive

Ce module centralise les informations toxicologiques
disponibles pour un élément ou un mélange.

Les résultats sont distingués en :

DOCUMENTÉ :
    information provenant d'une source scientifique.

CALCULÉ :
    résultat obtenu mathématiquement à partir de données.

PRÉDIT :
    résultat issu d'un modèle ou d'une estimation.

IMPORTANT :
Une prédiction ne constitue pas une preuve expérimentale.
"""


from typing import Any, Dict, List, Optional


# =========================================================
# 1. NIVEAUX DE DONNÉES
# =========================================================

STATUT_DOCUMENTE = "documenté"
STATUT_CALCULE = "calculé"
STATUT_PREDIT = "prédit"
STATUT_NON_DISPONIBLE = "non disponible"


# =========================================================
# 2. STRUCTURE TOXICOLOGIQUE
# =========================================================

def creer_resultat_toxicologique(
    nom: str,
    donnees: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    donnees = donnees or {}

    return {
        "nom": nom,

        "statut": donnees.get(
            "statut",
            STATUT_NON_DISPONIBLE
        ),

        "niveau_risque": donnees.get(
            "niveau_risque",
            "Non déterminé"
        ),

        "toxicite_aigue": donnees.get(
            "toxicite_aigue"
        ),

        "toxicite_chronique": donnees.get(
            "toxicite_chronique"
        ),

        "dl50": donnees.get(
            "dl50"
        ),

        "dl50_unite": donnees.get(
            "dl50_unite",
            "mg/kg"
        ),

        "voie_exposition": donnees.get(
            "voie_exposition",
            []
        ),

        "organes_cibles": donnees.get(
            "organes_cibles",
            []
        ),

        "effets": donnees.get(
            "effets",
            []
        ),

        "source": donnees.get(
            "source"
        )
    }


# =========================================================
# 3. DL50
# =========================================================

def analyser_dl50(
    dl50: Optional[float],
    unite: str = "mg/kg",
    espece: Optional[str] = None,
    voie: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyse une valeur de DL50 lorsqu'elle est disponible.

    La classification ci-dessous est volontairement
    présentée comme une interprétation indicative.
    """

    resultat = {
        "valeur": dl50,
        "unite": unite,
        "espece": espece,
        "voie": voie,
        "statut": STATUT_DOCUMENTE if dl50 is not None
                  else STATUT_NON_DISPONIBLE,
        "interpretation": "Non déterminée"
    }

    if dl50 is None:
        return resultat

    if dl50 <= 5:
        resultat["interpretation"] = "Très forte toxicité aiguë"

    elif dl50 <= 50:
        resultat["interpretation"] = "Forte toxicité aiguë"

    elif dl50 <= 300:
        resultat["interpretation"] = "Toxicité aiguë importante"

    elif dl50 <= 2000:
        resultat["interpretation"] = "Toxicité aiguë modérée"

    elif dl50 <= 5000:
        resultat["interpretation"] = "Faible toxicité aiguë"

    else:
        resultat["interpretation"] = (
            "Très faible toxicité aiguë selon la valeur fournie"
        )

    return resultat


# =========================================================
# 4. VOIES D'EXPOSITION
# =========================================================

def analyser_voies_exposition(
    voies: Optional[List[str]] = None
) -> Dict[str, Any]:

    voies = voies or []

    voies_connues = [
        "orale",
        "cutanée",
        "inhalation",
        "oculaire",
        "intraveineuse",
        "intramusculaire",
        "intraperitoneale"
    ]

    reconnues = [
        voie for voie in voies
        if voie.lower() in voies_connues
    ]

    return {
        "statut": (
            STATUT_DOCUMENTE
            if reconnues
            else STATUT_NON_DISPONIBLE
        ),
        "voies": reconnues
    }


# =========================================================
# 5. ORGANES CIBLES
# =========================================================

ORGANES_SENTOX = [
    "Foie",
    "Reins",
    "Intestin",
    "Estomac",
    "Système nerveux",
    "Système cardiovasculaire",
    "Poumons",
    "Peau",
    "Système immunitaire",
    "Système reproducteur",
    "Système endocrinien"
]


def analyser_organes_cibles(
    organes: Optional[List[str]] = None
) -> Dict[str, Any]:

    organes = organes or []

    organes_reconnus = []

    for organe in organes:

        for organe_sentox in ORGANES_SENTOX:

            if organe.lower() == organe_sentox.lower():

                if organe_sentox not in organes_reconnus:
                    organes_reconnus.append(organe_sentox)

    return {
        "statut": (
            STATUT_DOCUMENTE
            if organes_reconnus
            else STATUT_NON_DISPONIBLE
        ),
        "organes": organes_reconnus
    }


# =========================================================
# 6. EFFETS TOXICOLOGIQUES
# =========================================================

EFFETS_TOXICOLOGIQUES = [
    "hépatotoxicité",
    "néphrotoxicité",
    "neurotoxicité",
    "cardiotoxicité",
    "génotoxicité",
    "mutagénicité",
    "cancérogénicité",
    "immunotoxicité",
    "reprotoxicité",
    "toxicité digestive",
    "toxicité cutanée",
    "toxicité respiratoire"
]


def analyser_effets(
    effets: Optional[List[str]] = None
) -> Dict[str, Any]:

    effets = effets or []

    effets_reconnus = []

    for effet in effets:

        effet_normalise = effet.lower().strip()

        if effet_normalise in EFFETS_TOXICOLOGIQUES:

            effets_reconnus.append(
                effet_normalise
            )

    return {
        "statut": (
            STATUT_DOCUMENTE
            if effets_reconnus
            else STATUT_NON_DISPONIBLE
        ),
        "effets": effets_reconnus
    }


# =========================================================
# 7. ANALYSE TOXICOLOGIQUE INDIVIDUELLE
# =========================================================

def analyser_toxicologie(
    nom: str,
    donnees: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    donnees = donnees or {}

    resultat = creer_resultat_toxicologique(
        nom,
        donnees
    )

    # -----------------------------------------------------
    # DL50
    # -----------------------------------------------------

    dl50 = analyser_dl50(
        donnees.get("dl50"),
        donnees.get(
            "dl50_unite",
            "mg/kg"
        ),
        donnees.get("espece"),
        donnees.get("voie")
    )

    # -----------------------------------------------------
    # VOIES
    # -----------------------------------------------------

    voies = analyser_voies_exposition(
        donnees.get(
            "voie_exposition",
            []
        )
    )

    # -----------------------------------------------------
    # ORGANES
    # -----------------------------------------------------

    organes = analyser_organes_cibles(
        donnees.get(
            "organes_cibles",
            []
        )
    )

    # -----------------------------------------------------
    # EFFETS
    # -----------------------------------------------------

    effets = analyser_effets(
        donnees.get(
            "effets",
            []
        )
    )

    resultat["dl50_analyse"] = dl50
    resultat["voies_analyse"] = voies
    resultat["organes_analyse"] = organes
    resultat["effets_analyse"] = effets

    # -----------------------------------------------------
    # SI AUCUNE DONNÉE
    # -----------------------------------------------------

    if not donnees:

        resultat["statut"] = STATUT_PREDIT

        resultat["niveau_risque"] = (
            "À déterminer par SENTOX-QSAR"
        )

        resultat["interpretation"] = (
            "Aucune donnée toxicologique documentée "
            "n'est actuellement disponible dans les "
            "données fournies."
        )

    else:

        resultat["interpretation"] = (
            "Les informations toxicologiques disponibles "
            "ont été structurées par SENTOX."
        )

    return resultat


# =========================================================
# 8. PRÉDICTION TOXICOLOGIQUE
# =========================================================

def prediction_toxicologique(
    nom: str,
    proprietes: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    proprietes = proprietes or {}

    return {

        "element": nom,

        "statut": STATUT_PREDIT,

        "toxicite_aigue": {
            "resultat": "À prédire",
            "variables": [
                "poids moléculaire",
                "logP",
                "polarité",
                "structure moléculaire"
            ]
        },

        "toxicite_chronique": {
            "resultat": "À prédire"
        },

        "organes_cibles": {
            "resultat": "À prédire"
        },

        "genotoxicite": {
            "resultat": "À prédire"
        },

        "hepatotoxicite": {
            "resultat": "À prédire"
        },

        "nephrotoxicite": {
            "resultat": "À prédire"
        },

        "neurotoxicite": {
            "resultat": "À prédire"
        },

        "proprietes_utilisees": proprietes,

        "avertissement": (
            "Résultat prédictif : ne constitue pas une "
            "preuve expérimentale."
        )
    }


# =========================================================
# 9. ANALYSE TOXICOLOGIQUE D'UN MÉLANGE
# =========================================================

def analyser_toxicologie_melange(
    elements: List[Dict[str, Any]]
) -> Dict[str, Any]:

    resultats = []

    organes_potentiels = set()

    for element in elements:

        nom = element.get(
            "nom",
            "Élément inconnu"
        )

        donnees = element.get(
            "toxicologie",
            {}
        )

        analyse = analyser_toxicologie(
            nom,
            donnees
        )

        resultats.append(analyse)

        for organe in analyse.get(
            "organes_analyse",
            {}
        ).get(
            "organes",
            []
        ):

            organes_potentiels.add(
                organe
            )

    # -----------------------------------------------------
    # NIVEAU GLOBAL
    # -----------------------------------------------------

    niveaux = [
        resultat.get(
            "niveau_risque",
            ""
        )
        for resultat in resultats
    ]

    if any(
        "fort" in niveau.lower()
        or "élev" in niveau.lower()
        for niveau in niveaux
        if niveau
    ):

        niveau_global = "À surveiller"

    elif resultats:

        niveau_global = "À déterminer"

    else:

        niveau_global = "Non disponible"

    return {

        "nombre_elements": len(resultats),

        "elements": resultats,

        "niveau_risque_global": niveau_global,

        "organes_potentiels": sorted(
            organes_potentiels
        ),

        "statut": STATUT_PREDIT,

        "interpretation": (
            "Le profil toxicologique global du mélange "
            "doit être interprété en tenant compte de "
            "chaque constituant et de leurs interactions "
            "potentielles."
        )
    }


# =========================================================
# 10. RÉSUMÉ POUR L'INTERFACE WEB
# =========================================================

def resume_toxicologie(
    resultat: Dict[str, Any]
) -> Dict[str, Any]:

    return {

        "niveau_risque": resultat.get(
            "niveau_risque",
            "Non déterminé"
        ),

        "dl50": resultat.get(
            "dl50"
        ),

        "statut": resultat.get(
            "statut",
            STATUT_NON_DISPONIBLE
        ),

        "organes_cibles": resultat.get(
            "organes_cibles",
            []
        ),

        "effets": resultat.get(
            "effets",
            []
        ),

        "source": resultat.get(
            "source"
        )
    }


# =========================================================
# 11. TEST DU MODULE
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SENTOX — TEST DU MODULE TOXICOLOGIE")
    print("=" * 60)

    resultat = analyser_toxicologie(
        "Élément test"
    )

    print("\nÉlément :")
    print(resultat["nom"])

    print("\nStatut :")
    print(resultat["statut"])

    print("\nNiveau de risque :")
    print(resultat["niveau_risque"])

    print("\nDL50 :")
    print(resultat["dl50_analyse"]["interpretation"])

    print("\nOrganes cibles :")
    print(resultat["organes_analyse"]["organes"])

    print("\nEffets :")
    print(resultat["effets_analyse"]["effets"])

    print("\nModule toxicologique SENTOX opérationnel.")
