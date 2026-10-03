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
from pathlib import Path
import pandas as pd
import joblib
from rdkit import Chem
import unicodedata
import re
import math
import json
from qsar.qsar_engine import calculer_descripteurs

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
    Recherche un élément dans les bases SENTOX.

    Les molécules et médicaments sont recherchés en priorité
    dans les bases moléculaires SENTOX.

    Les autres éléments continuent d'utiliser la base
    constituants_enrichis.csv.
    """

    nom_original = str(nom).strip()

    if not nom_original:
        return []

    type_normalise = str(type_element).strip().lower()

    # =====================================================
    # RECHERCHE MOLECULAIRE
    # =====================================================

    if type_normalise in (
        "auto",
        "molecule",
        "molécule",
        "medicament",
        "médicament"
    ):

        resultat_molecule = rechercher_molecule_multibase(
            nom_original
        )

        if resultat_molecule:
            return [resultat_molecule]

    # =====================================================
    # RECHERCHE CLASSIQUE
    # =====================================================

    nom_normalise = nom_original.lower()

    base = charger_base()

    resultats = []

    for ligne in base:

        texte = " ".join(
            str(v).lower()
            for v in ligne.values()
        )

        if nom_normalise in texte:

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

    Priorité :
    1. utiliser les données documentées dans la base ;
    2. si elles sont absentes ou invalides, les calculer avec RDKit
       à partir du SMILES.
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

    # ---------------------------------------------------------
    # DONNÉES DOCUMENTÉES
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # FORMULE
    # ---------------------------------------------------------

    if formule:
        formule_str = str(formule).strip()

        if formule_str.lower() not in (
            "nan",
            "none",
            "null",
            ""
        ):
            structure["formule_brute"] = formule_str

    # ---------------------------------------------------------
    # MASSE MOLAIRE
    # ---------------------------------------------------------

    if masse is not None:
        try:
            valeur_masse = float(
                str(masse).replace(",", ".")
            )

            if valeur_masse == valeur_masse:
                structure["masse_molaire"] = valeur_masse

        except Exception:
            pass

    # ---------------------------------------------------------
    # SMILES
    # ---------------------------------------------------------

    if smiles:
        smiles_str = str(smiles).strip()

        if smiles_str.lower() not in (
            "nan",
            "none",
            "null",
            ""
        ):
            structure["smiles"] = smiles_str

    # ---------------------------------------------------------
    # INCHI DOCUMENTÉ
    # ---------------------------------------------------------

    if inchi:
        inchi_str = str(inchi).strip()

        if inchi_str.lower() not in (
            "nan",
            "none",
            "null",
            ""
        ):
            structure["inchi"] = inchi_str

    # =========================================================
    # COMPLÉTION AUTOMATIQUE PAR RDKit
    # =========================================================

    if structure["smiles"]:

        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors
            from rdkit.Chem import rdMolDescriptors

            mol = Chem.MolFromSmiles(
                structure["smiles"]
            )

            if mol is not None:

                # -------------------------------------------------
                # FORMULE BRUTE
                # -------------------------------------------------

                if not structure["formule_brute"]:
                    try:
                        structure["formule_brute"] = (
                            rdMolDescriptors.CalcMolFormula(mol)
                        )

                        structure[
                            "formule_brute_statut"
                        ] = "calculé — RDKit"

                    except Exception:
                        pass

                # -------------------------------------------------
                # MASSE MOLÉCULAIRE
                # -------------------------------------------------

                if structure["masse_molaire"] is None:
                    try:
                        structure["masse_molaire"] = round(
                            Descriptors.MolWt(mol),
                            4
                        )

                        structure[
                            "masse_molaire_statut"
                        ] = "calculé — RDKit"

                    except Exception:
                        pass

                # -------------------------------------------------
                # INCHI
                # -------------------------------------------------

                if not structure["inchi"]:
                    try:
                        inchi_calcule = Chem.MolToInchi(mol)

                        if inchi_calcule:
                            structure["inchi"] = inchi_calcule

                            structure[
                                "inchi_statut"
                            ] = "calculé — RDKit"

                    except Exception:
                        pass

                # -------------------------------------------------
                # SMILES CANONIQUE
                # -------------------------------------------------

                try:
                    structure[
                        "smiles_canonique"
                    ] = Chem.MolToSmiles(mol)

                except Exception:
                    pass

                # -------------------------------------------------
                # VALIDATION
                # -------------------------------------------------

                structure[
                    "structure_smiles_statut"
                ] = "valide — RDKit"

            else:
                structure[
                    "structure_smiles_statut"
                ] = "SMILES invalide"

        except Exception as e:

            structure[
                "rdkit_erreur"
            ] = str(e)

    # ---------------------------------------------------------
    # FALLBACK ANCIEN : CALCUL À PARTIR DE LA FORMULE
    # ---------------------------------------------------------

    if (
        structure["masse_molaire"] is None
        and structure["formule_brute"]
    ):

        try:
            masse_calculee = calculer_masse_molaire(
                structure["formule_brute"]
            )

            if masse_calculee:
                structure["masse_molaire"] = masse_calculee

                structure[
                    "masse_molaire_statut"
                ] = "calculé — formule"

        except Exception:
            pass

    return structure
def analyser_structure_2d(smiles):
    """
    Génération de la structure 2D avec RDKit.
    """
    from web.qsar.structure_engine import generer_structure_2d
    return generer_structure_2d(smiles)


def analyser_structure_3d(smiles):
    """
    Génération de la structure 3D avec RDKit.
    """
    from web.qsar.structure_engine import generer_structure_3d
    return generer_structure_3d(smiles)


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
            "ld50",
            "ld50_mg_kg",
            "ld50 mg kg",
            "ld50 (mg/kg)",
            "dl50_mg_kg",
            "dl50 mg kg"
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

    # NaN / valeurs vides = donnée non disponible
    toxicite_valide = False

    if toxicite is not None:
        try:
            toxicite_valide = (
                str(toxicite).strip().lower()
                not in ("", "nan", "none", "null")
            )
        except Exception:
            toxicite_valide = False

    if toxicite_valide:

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
    resultats_base,
    smiles=None
):
    """
    Analyse ADME.

    Priorité :
    1. données ADME documentées dans la base ;
    2. profil ADME structurel calculé par RDKit si un SMILES
       est disponible.

    Les résultats RDKit sont des indicateurs structurels.
    Ils ne constituent pas des données pharmacocinétiques
    expérimentales.
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

    # ========================================================
    # 1. RECHERCHE DES DONNÉES ADME DOCUMENTÉES
    # ========================================================

    if resultats_base:

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

    # ========================================================
    # 2. PROFIL ADME STRUCTUREL RDKit
    # ========================================================

    if smiles:

        try:

            from web.qsar.adme_engine import (
                analyser_adme_structure
            )

            profil = analyser_adme_structure(
                smiles
            )

            if profil.get(
                "statut_global"
            ) == "CALCULÉ — PROFIL STRUCTUREL":

                for parametre in [
                    "absorption",
                    "distribution",
                    "metabolisme",
                    "excretion"
                ]:

                    # Une donnée documentée reste prioritaire.
                    # RDKit complète uniquement les paramètres
                    # encore indisponibles.

                    if adme[parametre].get(
                        "statut"
                    ) == "non disponible":

                        adme[parametre] = (
                            profil[parametre]
                        )

                adme["descripteurs_support"] = (
                    profil.get(
                        "descripteurs_support",
                        {}
                    )
                )

                adme["statut_global"] = (
                    "CALCULÉ — PROFIL STRUCTUREL"
                )

                adme["moteur"] = "RDKit"

                adme["type_resultat"] = (
                    "INDICATEUR STRUCTUREL"
                )

        except Exception as e:

            adme["erreur_structurelle"] = str(e)

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
# 17 BIS. ANALYSE DES CONSTITUANTS
# =========================================================

def analyser_constituants(resultats_base):
    """
    Extrait les constituants associés à un élément
    à partir de tous les résultats de la base SENTOX.
    """

    constituants = []

    if not resultats_base:
        return constituants

    for donnees in resultats_base:

        constituant, _ = extraire_valeur(
            donnees,
            [
                "constituant",
                "nom constituant",
                "compound",
                "molecule",
                "molécule"
            ]
        )

        if not constituant:
            continue

        classe, _ = extraire_valeur(
            donnees,
            [
                "classe chimique",
                "classe",
                "chemical class"
            ]
        )

        partie, _ = extraire_valeur(
            donnees,
            [
                "partie utilisée",
                "partie",
                "part used"
            ]
        )

        cid, _ = extraire_valeur(
            donnees,
            [
                "cid",
                "pubchem cid",
                "pubchem_cid"
            ]
        )

        formule, _ = extraire_valeur(
            donnees,
            [
                "formule",
                "formula",
                "molecularformula"
            ]
        )

        smiles, _ = extraire_valeur(
            donnees,
            [
                "smiles",
                "connectivitysmiles"
            ]
        )

        constituants.append({
            "nom": constituant,
            "classe_chimique": classe,
            "partie_utilisee": partie,
            "CID": cid,
            "formule": formule,
            "SMILES": smiles
        })

    return constituants


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
    # CONSTITUANTS
    # -----------------------------------------------------

    analyse[
        "constituants"
    ] = analyser_constituants(
        resultats_base
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
    # BASE TOXICOLOGIQUE V2
    # -----------------------------------------------------
    try:
        from web.qsar.toxicology_database_engine import rechercher_toxicologie

        nom_recherche = identification.get("nom_identifie") or nom

        analyse[
            "toxicologie_v2"
        ] = rechercher_toxicologie(
            nom_recherche
        )

        # -------------------------------------------------
        # CALCUL HED CONDITIONNEL
        # -------------------------------------------------
        if analyse["toxicologie_v2"].get("resultats"):
            from extrapolation.hed_engine import calculer_hed

            for tox in analyse["toxicologie_v2"]["resultats"]:
                espece = tox.get("Espece")
                valeur = tox.get("Valeur")
                unite = tox.get("Unite")

                # HED uniquement si l'espèce et la dose
                # sont suffisamment renseignées.
                if (
                    espece
                    and str(espece).strip().lower()
                    not in {
                        "non précisée",
                        "non precisee",
                        "non précisé",
                        "non precise",
                        "nan",
                        ""
                    }
                    and valeur is not None
                    and str(valeur).lower() != "nan"
                    and unite
                    and str(unite).strip().lower() == "mg/kg"
                ):
                    try:
                        resultat_hed = calculer_hed(
                            float(valeur),
                            str(espece).strip()
                        )

                        tox["HED"] = resultat_hed.get("HED")
                        tox["Km_animal"] = resultat_hed.get("Km_animal")
                        tox["Km_humain"] = resultat_hed.get("Km_humain")
                        tox["Point_depart"] = valeur

                    except Exception as hed_error:
                        tox["HED"] = None
                        tox["Commentaire_SENTOX"] = (
                            str(tox.get("Commentaire_SENTOX") or "")
                            + " HED non calculée : "
                            + str(hed_error)
                        )

                else:
                    tox["HED"] = None
                    tox["Commentaire_SENTOX"] = (
                        str(tox.get("Commentaire_SENTOX") or "")
                        + " HED non calculée : espèce ou dose insuffisamment documentée."
                    )

                # -------------------------------------------------
                # CALCUL MOE / RQ CONDITIONNEL
                # -------------------------------------------------
                from risk.risk_engine import calculer_moe
                from risk.rq_engine import calculer_rq

                exposition = tox.get("Exposition_humaine")
                point_depart = tox.get("Point_depart")
                valeur_reference = tox.get("Dose_reference_humaine")

                def valeur_valide(valeur):
                    if valeur is None:
                        return False
                    try:
                        nombre = float(valeur)
                        return nombre > 0
                    except (TypeError, ValueError):
                        return False

                # MOE :
                # point de départ / exposition humaine
                if (
                    valeur_valide(point_depart)
                    and valeur_valide(exposition)
                ):
                    try:
                        resultat_moe = calculer_moe(
                            float(point_depart),
                            float(exposition)
                        )
                        tox["MOE"] = resultat_moe.get("MOE")
                        tox["Statut_MOE"] = "Calculée"
                    except Exception as moe_error:
                        tox["MOE"] = None
                        tox["Statut_MOE"] = "NON CALCULÉE"
                        tox["Commentaire_SENTOX"] = (
                            str(tox.get("Commentaire_SENTOX") or "")
                            + " MOE non calculée : "
                            + str(moe_error)
                        )
                else:
                    tox["MOE"] = None
                    tox["Statut_MOE"] = "NON CALCULÉE"

                # RQ :
                # exposition humaine / valeur de référence
                if (
                    valeur_valide(exposition)
                    and valeur_valide(valeur_reference)
                ):
                    try:
                        resultat_rq = calculer_rq(
                            float(exposition),
                            float(valeur_reference)
                        )
                        tox["RQ"] = resultat_rq.get("RQ")
                        tox["Statut_RQ"] = "Calculée"
                    except Exception as rq_error:
                        tox["RQ"] = None
                        tox["Statut_RQ"] = "NON CALCULÉ"
                        tox["Commentaire_SENTOX"] = (
                            str(tox.get("Commentaire_SENTOX") or "")
                            + " RQ non calculé : "
                            + str(rq_error)
                        )
                else:
                    tox["RQ"] = None
                    tox["Statut_RQ"] = "NON CALCULÉ"

    except Exception as e:
        analyse[
            "toxicologie_v2"
        ] = {
            "statut": "ERREUR",
            "resultats": [],
            "erreur": str(e)
        }

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

    # -----------------------------------------------------
    # DESCRIPTEURS QSAR — RDKit
    # -----------------------------------------------------

    smiles = structure.get("smiles")

    if smiles:
        from web.qsar.descriptors_engine import calculer_descripteurs_rdkit

        analyse[
            "molecule"
        ][
            "descripteurs"
        ] = calculer_descripteurs_rdkit(smiles)

    else:
        analyse[
            "molecule"
        ][
            "descripteurs"
        ] = {
            "statut": "NON DISPONIBLE",
            "message": "SMILES absent"
        }

    # -----------------------------------------------------
    # SIMILARITÉ MOLÉCULAIRE
    # -----------------------------------------------------

    try:
        if smiles:
            from web.qsar.similarity_engine import (
                evaluer_domaine_applicabilite
            )

            analyse["molecule"]["similarite"] = (
                evaluer_domaine_applicabilite(
                    smiles,
                    chemin_base=os.path.join(
                        DATA_DIR,
                        "molecules.csv"
                    ),
                    top_n=5
                )
            )

        else:
            analyse["molecule"]["similarite"] = {
                "statut": "NON DISPONIBLE",
                "message": "SMILES absent",
                "voisins": []
            }

    except Exception as e:
        analyse["molecule"]["similarite"] = {
            "statut": "ERREUR",
            "message": str(e),
            "voisins": []
        }

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


# ============================================================
# SENTOX - RECHERCHE DANS LA BASE MOLECULAIRE 2000
# ============================================================

FICHIER_BASE_MOLECULES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "sentox_database_2000_enriched_noms.csv"
)


def normaliser_recherche(texte):
    """Normalise un texte pour faciliter la recherche."""
    if texte is None:
        return ""

    texte = str(texte).strip().lower()

    texte = unicodedata.normalize(
        "NFKD",
        texte
    ).encode(
        "ascii",
        "ignore"
    ).decode(
        "ascii"
    )

    return texte


def rechercher_molecule_sentox(nom_recherche):
    """Recherche une molécule dans la base SENTOX 2000."""

    if not nom_recherche:
        return None

    if not os.path.exists(FICHIER_BASE_MOLECULES):
        return None

    try:
        df = pd.read_csv(
            FICHIER_BASE_MOLECULES,
            low_memory=False
        )

        recherche = normaliser_recherche(nom_recherche)

        colonnes = [
            "Nom",
            "Nom_PubChem",
            "IUPAC_Name_PubChem",
            "CID"
        ]

        colonnes = [
            c for c in colonnes
            if c in df.columns
        ]

        # Correspondance exacte
        for colonne in colonnes:
            valeurs = (
                df[colonne]
                .fillna("")
                .astype(str)
                .map(normaliser_recherche)
            )

            masque = valeurs == recherche

            if masque.any():
                return df.loc[masque].iloc[0].to_dict()

        # Correspondance partielle
        for colonne in colonnes:
            valeurs = (
                df[colonne]
                .fillna("")
                .astype(str)
                .map(normaliser_recherche)
            )

            masque = valeurs.str.contains(
                recherche,
                regex=False,
                na=False
            )

            if masque.any():
                return df.loc[masque].iloc[0].to_dict()

        return None

    except Exception as e:
        print(f"[SENTOX] Erreur recherche molecule : {e}")
        return None



# ============================================================
# SENTOX - RECHERCHE MULTI-BASES
# ============================================================

FICHIERS_BASES_SENTOX = [
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "molecules_master.csv"
    ),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "molecules.csv"
    ),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "sentox_database_2000_enriched_noms.csv"
    )
]


def rechercher_molecule_multibase(nom_recherche):
    """Recherche une molécule dans toutes les bases SENTOX.

    La fonction parcourt toutes les bases et conserve la fiche
    contenant le plus d'informations utiles.
    """

    recherche = normaliser_recherche(nom_recherche)

    if not recherche:
        return None

    meilleur_resultat = None
    meilleur_score = -1

    for fichier in FICHIERS_BASES_SENTOX:

        if not os.path.exists(fichier):
            continue

        try:
            df = pd.read_csv(
                fichier,
                low_memory=False
            )

            colonnes = [
                "Nom",
                "Nom_PubChem",
                "IUPAC_Name_PubChem",
                "CID"
            ]

            colonnes = [
                c for c in colonnes
                if c in df.columns
            ]

            if not colonnes:
                continue

            # Recherche exacte
            for colonne in colonnes:

                valeurs = (
                    df[colonne]
                    .fillna("")
                    .astype(str)
                    .map(normaliser_recherche)
                )

                masque = valeurs == recherche

                if masque.any():

                    for _, ligne_df in df.loc[masque].iterrows():

                        ligne = ligne_df.to_dict()

                        score = sum(
                            1
                            for valeur in ligne.values()
                            if pd.notna(valeur)
                            and str(valeur).strip()
                            and str(valeur).strip().lower() != "nan"
                        )

                        if score > meilleur_score:

                            ligne["_source_sentox"] = Path(
                                fichier
                            ).name

                            meilleur_resultat = ligne
                            meilleur_score = score

            # Recherche partielle uniquement si aucune
            # correspondance exacte n'a encore été trouvée
            if meilleur_resultat is None:

                for colonne in colonnes:

                    valeurs = (
                        df[colonne]
                        .fillna("")
                        .astype(str)
                        .map(normaliser_recherche)
                    )

                    masque = valeurs.str.contains(
                        recherche,
                        regex=False,
                        na=False
                    )

                    if masque.any():

                        for _, ligne_df in df.loc[masque].iterrows():

                            ligne = ligne_df.to_dict()

                            score = sum(
                                1
                                for valeur in ligne.values()
                                if pd.notna(valeur)
                                and str(valeur).strip()
                                and str(valeur).strip().lower() != "nan"
                            )

                            if score > meilleur_score:

                                ligne["_source_sentox"] = Path(
                                    fichier
                                ).name

                                meilleur_resultat = ligne
                                meilleur_score = score

        except Exception as e:

            print(
                f"[SENTOX] Erreur lecture {fichier}: {e}"
            )

    return meilleur_resultat


# =========================================================
# SENTOX-QSAR : PREDICTION LD50
# =========================================================

def predire_ld50_qsar(smiles):
    """
    Prédit la LD50 orale à partir d'un SMILES.

    IMPORTANT :
    Cette fonction utilise le modèle QSAR expérimental
    actuellement disponible dans SENTOX.
    La prédiction ne constitue pas une preuve expérimentale
    ni une donnée toxicologique réglementaire.
    """

    if not smiles:
        return {
            "statut": "non disponible",
            "raison": "SMILES absent"
        }

    # Calcul des descripteurs RDKit
    descripteurs = calculer_descripteurs(smiles)

    if any(
        descripteurs.get(c) is None
        for c in [
            "Masse_molaire",
            "LogP",
            "HBD",
            "HBA",
            "Atomes",
            "TPSA",
            "Anneaux"
        ]
    ):
        return {
            "statut": "non disponible",
            "raison": "SMILES invalide ou descripteurs impossibles à calculer"
        }

    # Chargement du modèle
    modele_path = BASE_DIR / "models" / "qsar_model.joblib"

    if not modele_path.exists():
        return {
            "statut": "non disponible",
            "raison": "Modèle QSAR introuvable"
        }

    modele_data = joblib.load(modele_path)

    modele = modele_data["model"]
    features = modele_data["features"]

    # Construction du vecteur de prédiction
    X = pd.DataFrame(
        [[descripteurs[f] for f in features]],
        columns=features
    )

    # Prédiction
    prediction_log = float(
        modele.predict(X)[0]
    )

    prediction_ld50 = float(
        10 ** prediction_log
    )

    return {
        "statut": "PRÉDIT",
        "valeur": round(prediction_ld50, 3),
        "unite": "mg/kg",
        "log10_LD50": round(prediction_log, 4),
        "modele": "RandomForestRegressor",
        "cible": modele_data.get(
            "target",
            "log10_LD50_mg_kg"
        ),
        "n_training": modele_data.get(
            "n_training",
            None
        ),
        "descripteurs": descripteurs,
        "commentaire": (
            "Prédiction QSAR expérimentale/prototype. "
            "Ne constitue pas une preuve toxicologique "
            "expérimentale ou réglementaire."
        )
    }
        