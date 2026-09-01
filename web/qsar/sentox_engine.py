# =========================================================
# SENTOX ENGINE
# Moteur central d'analyse toxicologique, pharmacologique
# QSAR, ADME et interactions moléculaires
# =========================================================

"""
SENTOX ENGINE

Niveaux de données :

DOCUMENTÉ
    Donnée provenant d'une base ou d'une source scientifique.

CALCULÉ
    Résultat obtenu à partir d'une formule déterministe.

PRÉDIT
    Résultat issu d'un modèle prédictif ou d'une estimation.

NON DISPONIBLE
    Aucune donnée exploitable trouvée.

IMPORTANT
    Une prédiction SENTOX-QSAR ne constitue pas une preuve
    expérimentale.
"""

import os
import re
import math
import json


# =========================================================
# 1. CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")

FICHIER_CONSTITUANTS = os.path.join(
    DATA_DIR,
    "constituants_enrichis.csv"
)


# =========================================================
# 2. STRUCTURE STANDARD SENTOX
# =========================================================

def resultat_sentox(
    valeur=None,
    statut="non disponible",
    source=None,
    confiance=None,
    unite=None,
    commentaire=None
):
    """
    Structure standardisée d'une donnée SENTOX.
    """

    return {
        "valeur": valeur,
        "statut": statut,
        "source": source,
        "confiance": confiance,
        "unite": unite,
        "commentaire": commentaire
    }


def documente(
    valeur=None,
    source=None,
    unite=None,
    commentaire=None
):
    return resultat_sentox(
        valeur=valeur,
        statut="documenté",
        source=source,
        unite=unite,
        commentaire=commentaire
    )


def calcule(
    valeur=None,
    source="Formule SENTOX",
    unite=None,
    commentaire=None
):
    return resultat_sentox(
        valeur=valeur,
        statut="calculé",
        source=source,
        unite=unite,
        commentaire=commentaire
    )


def predit(
    valeur=None,
    source="SENTOX-QSAR",
    confiance=None,
    unite=None,
    commentaire=None
):
    return resultat_sentox(
        valeur=valeur,
        statut="prédit",
        source=source,
        confiance=confiance,
        unite=unite,
        commentaire=commentaire
    )


# =========================================================
# 3. CHARGEMENT DE LA BASE
# =========================================================

def charger_base():
    """
    Charge la base CSV si elle existe.

    Utilisation volontairement sans pandas afin que le moteur
    reste facilement déployable.
    """

    if not os.path.exists(FICHIER_CONSTITUANTS):
        return []

    try:

        import csv

        with open(
            FICHIER_CONSTITUANTS,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as fichier:

            lecteur = csv.DictReader(fichier)

            donnees = []

            for ligne in lecteur:

                ligne_nettoyee = {}

                for cle, valeur in ligne.items():

                    cle = str(cle).strip()

                    if valeur is None:
                        valeur = ""

                    ligne_nettoyee[cle] = str(
                        valeur
                    ).strip()

                donnees.append(ligne_nettoyee)

            return donnees

    except Exception:
        return []


# =========================================================
# 4. RECHERCHE DANS LA BASE
# =========================================================

def rechercher_element(
    nom,
    type_element="auto"
):
    """
    Recherche un élément dans la base SENTOX.

    La recherche est effectuée dans toutes les colonnes.
    """

    nom = str(nom).strip().lower()

    if not nom:
        return []

    base = charger_base()

    resultats = []

    for ligne in base:

        texte = " ".join(
            str(v).lower()
            for v in ligne.values()
        )

        if nom in texte:

            resultats.append(ligne)

    return resultats


# =========================================================
# 5. EXTRACTION INTELLIGENTE DES COLONNES
# =========================================================

def chercher_colonne(
    donnees,
    mots_cles
):
    """
    Cherche une colonne dont le nom contient l'un des mots-clés.
    """

    if not donnees:
        return None

    colonnes = list(donnees.keys())

    for colonne in colonnes:

        colonne_normalisee = (
            colonne.lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        for mot in mots_cles:

            if mot.lower() in colonne_normalisee:

                return colonne

    return None


def extraire_valeur(
    donnees,
    mots_cles
):
    """
    Retourne une valeur trouvée dans une ligne de base.
    """

    colonne = chercher_colonne(
        donnees,
        mots_cles
    )

    if colonne:

        valeur = donnees.get(
            colonne,
            ""
        )

        if str(valeur).strip():

            return valeur, colonne

    return None, None


# =========================================================
# 6. IDENTIFICATION
# =========================================================

def identifier_element(
    nom,
    type_element="auto"
):
    """
    Identifie un élément à partir de la base SENTOX.
    """

    resultats = rechercher_element(
        nom,
        type_element
    )

    if not resultats:

        return {
            "nom_recherche": nom,
            "nom_identifie": None,
            "type": type_element,
            "synonymes": [],
            "statut": "non disponible",
            "resultats_base": []
        }

    premier = resultats[0]

    valeur_nom, colonne_nom = extraire_valeur(
        premier,
        [
            "nom",
            "name",
            "produit",
            "substance",
            "molecule",
            "molécule",
            "constituant"
        ]
    )

    nom_identifie = (
        valeur_nom
        if valeur_nom
        else nom
    )

    return {
        "nom_recherche": nom,
        "nom_identifie": nom_identifie,
        "type": type_element,
        "synonymes": [],
        "statut": "documenté",
        "colonne_identification": colonne_nom,
        "resultats_base": resultats
    }


# =========================================================
# 7. MASSE MOLÉCULAIRE
# =========================================================

MASSES_ATOMIQUES = {

    "H": 1.008,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "P": 30.974,
    "S": 32.06,
    "Cl": 35.45,
    "Br": 79.904,
    "I": 126.904,
    "Na": 22.990,
    "K": 39.098,
    "Ca": 40.078,
    "Mg": 24.305,
    "Fe": 55.845,
    "Zn": 65.38,
    "Cu": 63.546,
    "Mn": 54.938,
    "Co": 58.933,
    "Cr": 51.996,
    "Si": 28.085
}


def calculer_masse_molaire(
    formule
):
    """
    Calcule la masse molaire à partir d'une formule brute.

    Exemple :
        C8H9NO2
    """

    if not formule:
        return None

    formule = str(formule).strip()

    pattern = r"([A-Z][a-z]?)(\d*)"

    elements = re.findall(
        pattern,
        formule
    )

    if not elements:
        return None

    masse = 0.0
    formule_reconstruite = ""

    for element, nombre in elements:

        if element not in MASSES_ATOMIQUES:
            return None

        quantite = (
            int(nombre)
            if nombre
            else 1
        )

        masse += (
            MASSES_ATOMIQUES[element]
            * quantite
        )

        formule_reconstruite += (
            element
            + str(quantite)
        )

    return round(
        masse,
        4
    )


# =========================================================
# 8. EXTRACTION DE LA STRUCTURE
# =========================================================

def extraire_structure(
    resultats_base
):
    """
    Recherche formule brute, masse molaire, SMILES et InChI.
    """

    structure = {

        "formule_brute": None,

        "masse_molaire": None,

        "smiles": None,

        "inchi": None,

        "structure_2d": None,

        "structure_3d": None
    }

    if not resultats_base:
        return structure

    donnees = resultats_base[0]

    formule, _ = extraire_valeur(
        donnees,
        [
            "formule",
            "formula",
            "formule brute"
        ]
    )

    masse, _ = extraire_valeur(
        donnees,
        [
            "masse molaire",
            "molecular weight",
            "molecular_weight",
            "poids moléculaire"
        ]
    )

    smiles, _ = extraire_valeur(
        donnees,
        [
            "smiles"
        ]
    )

    inchi, _ = extraire_valeur(
        donnees,
        [
            "inchi"
        ]
    )

    if formule:
        structure["formule_brute"] = formule

    if masse:
        try:
            structure["masse_molaire"] = float(
                str(masse).replace(",", ".")
            )
        except Exception:
            structure["masse_molaire"] = None

    if smiles:
        structure["smiles"] = smiles

    if inchi:
        structure["inchi"] = inchi

    # Si la masse n'est pas documentée,
    # SENTOX tente un calcul à partir de la formule.

    if (
        structure["masse_molaire"] is None
        and structure["formule_brute"]
    ):

        structure["masse_molaire"] = (
            calculer_masse_molaire(
                structure["formule_brute"]
            )
        )

        if structure["masse_molaire"]:

            structure[
                "masse_molaire_statut"
            ] = "calculé"

    return structure


# =========================================================
# 9. STRUCTURE 2D
# =========================================================

def analyser_structure_2d(
    smiles
):
    """
    Prépare la visualisation 2D.

    Le rendu graphique pourra être connecté à RDKit
    lorsque la bibliothèque sera disponible.
    """

    if not smiles:

        return {
            "statut": "non disponible",
            "smiles": None,
            "message":
                "SMILES non disponible"
        }

    return {

        "statut": "disponible",

        "smiles": smiles,

        "mode":
            "structure moléculaire 2D",

        "moteur":
            "RDKit recommandé pour le rendu graphique"
    }


# =========================================================
# 10. STRUCTURE 3D
# =========================================================

def analyser_structure_3d(
    smiles
):
    """
    Prépare la structure 3D.

    Une vraie géométrie 3D nécessite un moteur
    de chimio-informatique.
    """

    if not smiles:

        return {

            "statut": "non disponible",

            "smiles": None,

            "message":
                "SMILES non disponible"
        }

    return {

        "statut": "à générer",

        "smiles": smiles,

        "mode":
            "structure moléculaire 3D",

        "moteur":
            "RDKit / moteur 3D"
    }


# =========================================================
# 11. DESCRIPTEURS MOLÉCULAIRES SIMPLES
# =========================================================

def calculer_descripteurs_simples(
    formule
):
    """
    Calcule quelques paramètres simples à partir
    de la formule brute.
    """

    if not formule:
        return {}

    elements = dict(
        re.findall(
            r"([A-Z][a-z]?)(\d*)",
            formule
        )
    )

    def nombre(element):

        valeur = elements.get(
            element,
            ""
        )

        return int(valeur) if valeur else (
            1 if element in elements else 0
        )

    carbone = nombre("C")
    hydrogene = nombre("H")
    azote = nombre("N")
    oxygene = nombre("O")

    # Indice d'insaturation approximatif
    if carbone:

        DBE = (
            2 * carbone
            + 2
            + azote
            - hydrogene
        ) / 2

    else:

        DBE = None

    return {

        "carbone": carbone,

        "hydrogene": hydrogene,

        "azote": azote,

        "oxygene": oxygene,

        "indice_insaturation":
            DBE
    }


# =========================================================
# 12. POSSIBILITÉ DE LIAISON
# =========================================================

def analyser_possibilite_liaison(
    molecule_a,
    molecule_b
):
    """
    Analyse préliminaire de possibilité de liaison.

    ATTENTION :
    cette fonction ne constitue PAS un docking moléculaire.

    Elle prépare la structure pour des analyses futures :
    - similarité moléculaire
    - pharmacophore
    - docking
    - ligand-récepteur
    - interactions protéine-ligand
    """

    if not molecule_a or not molecule_b:

        return {

            "statut":
                "non analysable",

            "resultat": None,

            "confiance": None
        }

    smiles_a = molecule_a.get(
        "smiles"
    )

    smiles_b = molecule_b.get(
        "smiles"
    )

    if not smiles_a or not smiles_b:

        return {

            "statut":
                "non disponible",

            "resultat": None,

            "confiance": None,

            "message":
                "SMILES des deux molécules nécessaires"
        }

    # Pour l'instant, SENTOX indique que les molécules
    # sont prêtes pour une analyse de liaison.

    return {

        "statut":
            "prêt pour prédiction",

        "resultat":
            "Analyse structurale à effectuer",

        "molecule_a":
            smiles_a,

        "molecule_b":
            smiles_b,

        "methodes_prevues": [

            "similarité moléculaire",

            "pharmacophore",

            "docking moléculaire",

            "interaction ligand-récepteur"
        ],

        "confiance":
            None
    }


# =========================================================
# 13. ANALYSE PHARMACOLOGIQUE
# =========================================================

def analyser_pharmacologie(
    resultats_base
):
    """
    Recherche les informations pharmacologiques
    disponibles dans la base.
    """

    pharmacologie = {

        "principes_actifs": [],

        "mecanismes": [],

        "cibles": [],

        "statut": "non disponible"
    }

    if not resultats_base:
        return pharmacologie

    donnees = resultats_base[0]

    actif, _ = extraire_valeur(
        donnees,
        [
            "principe actif",
            "principes actifs",
            "active principle",
            "constituant"
        ]
    )

    mecanisme, _ = extraire_valeur(
        donnees,
        [
            "mecanisme",
            "mechanism",
            "mode d'action"
        ]
    )

    cible, _ = extraire_valeur(
        donnees,
        [
            "cible",
            "target",
            "receptor"
        ]
    )

    if actif:
        pharmacologie[
            "principes_actifs"
        ].append(actif)

    if mecanisme:
        pharmacologie[
            "mecanismes"
        ].append(mecanisme)

    if cible:
        pharmacologie[
            "cibles"
        ].append(cible)

    if (
        actif
        or mecanisme
        or cible
    ):
        pharmacologie[
            "statut"
        ] = "documenté"

    return pharmacologie


# =========================================================
# 14. TOXICOLOGIE
# =========================================================

def analyser_toxicologie(
    resultats_base
):
    """
    Recherche les données toxicologiques documentées.
    """

    toxicologie = {

        "toxicite_aigue":
            resultat_sentox(),

        "toxicite_chronique":
            resultat_sentox(),

        "dl50":
            resultat_sentox(),

        "noael":
            resultat_sentox(),

        "loael":
            resultat_sentox(),

        "organes_cibles": []
    }

    if not resultats_base:
        return toxicologie

    donnees = resultats_base[0]

    dl50, source_dl50 = extraire_valeur(
        donnees,
        [
            "dl50",
            "ld50"
        ]
    )

    toxicite, source_tox = extraire_valeur(
        donnees,
        [
            "toxicité aiguë",
            "acute toxicity",
            "toxicite"
        ]
    )

    organes, source_organes = extraire_valeur(
        donnees,
        [
            "organe cible",
            "organes cibles",
            "target organ"
        ]
    )

    if dl50:

        toxicologie[
            "dl50"
        ] = documente(
            dl50,
            source_dl50
        )

    if toxicite:

        toxicologie[
            "toxicite_aigue"
        ] = documente(
            toxicite,
            source_tox
        )

    if organes:

        toxicologie[
            "organes_cibles"
        ] = [
            x.strip()
            for x in str(organes).split(
                ","
            )
            if x.strip()
        ]

    return toxicologie


# =========================================================
# 15. ADME
# =========================================================

def analyser_adme(
    resultats_base
):
    """
    Recherche les paramètres ADME disponibles.
    """

    adme = {

        "absorption":
            resultat_sentox(),

        "distribution":
            resultat_sentox(),

        "metabolisme":
            resultat_sentox(),

        "excretion":
            resultat_sentox()
    }

    if not resultats_base:
        return adme

    donnees = resultats_base[0]

    correspondances = {

        "absorption": [
            "absorption"
        ],

        "distribution": [
            "distribution"
        ],

        "metabolisme": [
            "metabolisme",
            "metabolism"
        ],

        "excretion": [
            "excretion",
            "excrétion"
        ]
    }

    for parametre, mots in correspondances.items():

        valeur, source = extraire_valeur(
            donnees,
            mots
        )

        if valeur:

            adme[parametre] = documente(
                valeur,
                source
            )

    return adme


# =========================================================
# 16. SCORE DE RISQUE PRÉLIMINAIRE
# =========================================================

def calculer_score_risque(
    analyse
):
    """
    Produit un score préliminaire uniquement à partir
    des données disponibles.

    Ce score n'est PAS une classification réglementaire.
    """

    score = 0

    dl50 = analyse[
        "toxicologie"
    ][
        "dl50"
    ].get(
        "valeur"
    )

    toxicite = analyse[
        "toxicologie"
    ][
        "toxicite_aigue"
    ].get(
        "valeur"
    )

    if dl50:

        texte = str(
            dl50
        ).lower()

        nombres = re.findall(
            r"\d+(?:[.,]\d+)?",
            texte
        )

        if nombres:

            try:

                valeur = float(
                    nombres[0].replace(
                        ",",
                        "."
                    )
                )

                if valeur < 50:
                    score += 3

                elif valeur < 300:
                    score += 2

                elif valeur < 2000:
                    score += 1

            except Exception:
                pass

    if toxicite:

        texte = str(
            toxicite
        ).lower()

        if any(
            mot in texte
            for mot in [
                "élevée",
                "elevee",
                "high",
                "toxique"
            ]
        ):

            score += 2

    if score >= 4:

        niveau = "élevé"

    elif score >= 2:

        niveau = "modéré"

    else:

        niveau = "faible / données limitées"

    return {

        "score": score,

        "niveau": niveau,

        "statut": "calculé",

        "source":
            "Algorithme préliminaire SENTOX",

        "avertissement":
            "Ce score ne remplace pas une évaluation toxicologique réglementaire."
    }


# =========================================================
# 17. CRÉATION DE L'ANALYSE
# =========================================================

def creer_analyse_element(
    nom,
    type_element="auto"
):
    """
    Crée la structure complète d'analyse.
    """

    return {

        "identification": {

            "nom_recherche": nom,

            "nom_identifie": None,

            "type": type_element,

            "synonymes": [],

            "statut":
                "non disponible"
        },

        "constituants": [],

        "pharmacologie": {

            "principes_actifs": [],

            "mecanismes": [],

            "cibles": [],

            "statut":
                "non disponible"
        },

        "toxicologie": {

            "toxicite_aigue":
                resultat_sentox(),

            "toxicite_chronique":
                resultat_sentox(),

            "dl50":
                resultat_sentox(),

            "noael":
                resultat_sentox(),

            "loael":
                resultat_sentox(),

            "organes_cibles": []
        },

        "adme": {

            "absorption":
                resultat_sentox(),

            "distribution":
                resultat_sentox(),

            "metabolisme":
                resultat_sentox(),

            "excretion":
                resultat_sentox()
        },

        "interactions": [],

        "molecule": {

            "formule_brute": None,

            "masse_molaire": None,

            "masse_molaire_statut":
                None,

            "smiles": None,

            "inchi": None,

            "structure_2d": None,

            "structure_3d": None,

            "descripteurs": {}
        },

        "qsar": {

            "toxicite":
                resultat_sentox(),

            "adme":
                resultat_sentox(),

            "activite_biologique":
                resultat_sentox(),

            "cibles":
                resultat_sentox(),

            "similarite":
                resultat_sentox()
        },

        "score_risque": None,

        "sources": [],

        "conclusion": None
    }


# =========================================================
# 18. ANALYSE INDIVIDUELLE
# =========================================================

def analyser_element(
    nom,
    type_element="auto"
):
    """
    Fonction principale du moteur SENTOX.
    """

    analyse = creer_analyse_element(
        nom,
        type_element
    )

    # -----------------------------------------------------
    # IDENTIFICATION
    # -----------------------------------------------------

    identification = identifier_element(
        nom,
        type_element
    )

    analyse[
        "identification"
    ] = identification

    resultats_base = identification.get(
        "resultats_base",
        []
    )

    # -----------------------------------------------------
    # PHARMACOLOGIE
    # -----------------------------------------------------

    analyse[
        "pharmacologie"
    ] = analyser_pharmacologie(
        resultats_base
    )

    # -----------------------------------------------------
    # TOXICOLOGIE
    # -----------------------------------------------------

    analyse[
        "toxicologie"
    ] = analyser_toxicologie(
        resultats_base
    )

    # -----------------------------------------------------
    # ADME
    # -----------------------------------------------------

    analyse[
        "adme"
    ] = analyser_adme(
        resultats_base
    )

    # -----------------------------------------------------
    # STRUCTURE MOLÉCULAIRE
    # -----------------------------------------------------

    structure = extraire_structure(
        resultats_base
    )

    analyse[
        "molecule"
    ].update(
        structure
    )

    # -----------------------------------------------------
    # STRUCTURE 2D
    # -----------------------------------------------------

    analyse[
        "molecule"
    ][
        "structure_2d"
    ] = analyser_structure_2d(
        structure.get("smiles")
    )

    # -----------------------------------------------------
    # STRUCTURE 3D
    # -----------------------------------------------------

    analyse[
        "molecule"
    ][
        "structure_3d"
    ] = analyser_structure_3d(
        structure.get("smiles")
    )

    # -----------------------------------------------------
    # DESCRIPTEURS
    # -----------------------------------------------------

    analyse[
        "molecule"
    ][
        "descripteurs"
    ] = calculer_descripteurs_simples(
        structure.get(
            "formule_brute"
        )
    )

    # -----------------------------------------------------
    # SCORE DE RISQUE
    # -----------------------------------------------------

    analyse[
        "score_risque"
    ] = calculer_score_risque(
        analyse
    )

    # -----------------------------------------------------
    # SOURCES
    # -----------------------------------------------------

    for ligne in resultats_base:

        for cle, valeur in ligne.items():

            if (
                valeur
                and (
                    "source" in cle.lower()
                    or "reference" in cle.lower()
                    or "référence" in cle.lower()
                    or "doi" in cle.lower()
                )
            ):

                analyse[
                    "sources"
                ].append({
                    "source": valeur,
                    "statut": "documenté"
                })

    # -----------------------------------------------------
    # CONCLUSION
    # -----------------------------------------------------

    if resultats_base:

        analyse[
            "conclusion"
        ] = (
            "SENTOX a identifié des données documentées "
            "pour cet élément. Les résultats calculés sont "
            "distingués des données documentées. Les modules "
            "QSAR et de liaison moléculaire peuvent fournir "
            "des prédictions complémentaires."
        )

    else:

        analyse[
            "conclusion"
        ] = (
            "Aucune donnée correspondante n'a été retrouvée "
            "dans la base SENTOX actuellement disponible. "
            "Une recherche scientifique complémentaire sera "
            "nécessaire avant toute conclusion toxicologique."
        )

    return analyse


# =========================================================
# 19. ANALYSE D'UN MÉLANGE
# =========================================================

def analyser_melange(
    elements
):
    """
    Analyse plusieurs produits/substances.
    """

    analyses = []

    for element in elements:

        if isinstance(
            element,
            dict
        ):

            nom = element.get(
                "nom",
                ""
            )

            type_element = element.get(
                "type",
                "auto"
            )

        else:

            nom = str(
                element
            )

            type_element = "auto"

        nom = nom.strip()

        if not nom:
            continue

        analyses.append(
            analyser_element(
                nom,
                type_element
            )
        )

    # -----------------------------------------------------
    # INTERACTIONS
    # -----------------------------------------------------

    interactions = []

    for i in range(
        len(analyses)
    ):

        for j in range(
            i + 1,
            len(analyses)
        ):

            analyse_a = analyses[i]

            analyse_b = analyses[j]

            molecule_a = analyse_a[
                "molecule"
            ]

            molecule_b = analyse_b[
                "molecule"
            ]

            liaison = (
                analyser_possibilite_liaison(
                    molecule_a,
                    molecule_b
                )
            )

            interactions.append({

                "element_a":
                    analyse_a[
                        "identification"
                    ][
                        "nom_recherche"
                    ],

                "element_b":
                    analyse_b[
                        "identification"
                    ][
                        "nom_recherche"
                    ],

                "interaction":
                    "À évaluer",

                "potentialisation":
                    "À évaluer",

                "antagonisme":
                    "À évaluer",

                "inhibition":
                    "À évaluer",

                "competition":
                    "À évaluer",

                "synergie":
                    "À évaluer",

                "liaison_moleculaire":
                    liaison,

                "statut":
                    "prédit"
            })

    # -----------------------------------------------------
    # RISQUE GLOBAL
    # -----------------------------------------------------

    scores = []

    for analyse in analyses:

        score = analyse.get(
            "score_risque"
        )

        if score:

            scores.append(
                score.get(
                    "score",
                    0
                )
            )

    score_global = (
        sum(scores)
        if scores
        else 0
    )

    if score_global >= 7:

        niveau_global = "élevé"

    elif score_global >= 3:

        niveau_global = "modéré"

    else:

        niveau_global = "faible / données limitées"

    # -----------------------------------------------------
    # RETOUR
    # -----------------------------------------------------

    return {

        "elements":
            analyses,

        "interactions":
            interactions,

        "adme": {

            "absorption":
                "à évaluer",

            "distribution":
                "à évaluer",

            "metabolisme":
                "à évaluer",

            "excretion":
                "à évaluer"
        },

        "toxicologie": {

            "niveau":
                niveau_global,

            "score":
                score_global,

            "statut":
                "calculé",

            "message":
                "Score préliminaire SENTOX"
        },

        "conclusion": (
            "SENTOX a analysé les éléments du mélange "
            "et séparé les données documentées, calculées "
            "et les résultats destinés à la prédiction. "
            "Les interactions moléculaires nécessitent "
            "des modèles spécialisés pour être confirmées."
        )
    }


# =========================================================
# 20. EXPORT JSON
# =========================================================

def exporter_json(
    resultat,
    fichier="sentox_resultat.json"
):
    """
    Exporte un résultat SENTOX au format JSON.
    """

    with open(
        fichier,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            resultat,
            f,
            ensure_ascii=False,
            indent=2
        )

    return fichier


# =========================================================
# 21. TEST DU MOTEUR
# =========================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("        SENTOX ENGINE")
    print("======================================")
    print()

    test = analyser_element(
        "paracétamol",
        "medicament"
    )

    print(
        json.dumps(
            test,
            ensure_ascii=False,
            indent=2
        )
    )
