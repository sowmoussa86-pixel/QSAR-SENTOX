# ============================================================
# SENTOX ENGINE
# Moteur central d'analyse toxicologique et pharmacologique
# ============================================================

import re


# ============================================================
# CLASSIFICATION DES DONNÉES
# ============================================================

def classer_donnee(valeur, source=None):
    """
    Classe une information selon son origine :
    - documenté
    - calculé
    - prédit
    """

    if valeur is None or valeur == "":
        return "non disponible"

    if source:
        return "documenté"

    if isinstance(valeur, (int, float)):
        return "calculé"

    return "prédit"


# ============================================================
# NETTOYAGE
# ============================================================

def nettoyer_nom(nom):
    if not nom:
        return ""

    nom = str(nom).strip()
    nom = re.sub(r"\s+", " ", nom)

    return nom


# ============================================================
# IDENTIFICATION
# ============================================================

def identification(nom, donnees=None):

    nom = nettoyer_nom(nom)

    resultat = {
        "nom_recherche": nom,
        "identification": nom,
        "statut": "non disponible"
    }

    if donnees:
        resultat["statut"] = "documenté"

        for cle in [
            "nom_scientifique",
            "synonymes",
            "CAS",
            "CID",
            "SMILES",
            "InChI"
        ]:

            if cle in donnees and donnees[cle]:
                resultat[cle] = donnees[cle]

    return resultat


# ============================================================
# CONSTITUANTS / PRINCIPES ACTIFS
# ============================================================

def extraire_constituants(donnees):

    if not donnees:
        return []

    champs_possibles = [
        "constituants",
        "principes_actifs",
        "composes",
        "constituants_principaux"
    ]

    for champ in champs_possibles:

        if champ in donnees and donnees[champ]:

            valeur = donnees[champ]

            if isinstance(valeur, list):
                return valeur

            if isinstance(valeur, str):
                return [
                    x.strip()
                    for x in valeur.split(",")
                    if x.strip()
                ]

    return []


# ============================================================
# PHARMACOLOGIE
# ============================================================

def analyser_pharmacologie(donnees):

    resultat = {
        "activite": None,
        "mecanisme": None,
        "cibles": [],
        "statut": "non disponible"
    }

    if not donnees:
        return resultat

    champs = [
        "pharmacologie",
        "activite_pharmacologique",
        "mecanisme",
        "cible",
        "cibles"
    ]

    trouve = False

    for champ in champs:

        if champ in donnees and donnees[champ]:

            trouve = True

            if champ == "mecanisme":
                resultat["mecanisme"] = donnees[champ]

            elif champ in ["cible", "cibles"]:

                if isinstance(donnees[champ], list):
                    resultat["cibles"] = donnees[champ]
                else:
                    resultat["cibles"] = [donnees[champ]]

            else:
                resultat["activite"] = donnees[champ]

    if trouve:
        resultat["statut"] = "documenté"

    return resultat


# ============================================================
# TOXICOLOGIE
# ============================================================

def analyser_toxicologie(donnees):

    resultat = {
        "toxicite": None,
        "DL50": None,
        "voie": None,
        "espece": None,
        "organes_cibles": [],
        "statut": "non disponible"
    }

    if not donnees:
        return resultat

    mapping = {
        "toxicite": "toxicite",
        "niveau_toxicite": "toxicite",
        "DL50": "DL50",
        "dl50": "DL50",
        "voie": "voie",
        "espece": "espece",
        "organes_cibles": "organes_cibles"
    }

    trouve = False

    for champ, destination in mapping.items():

        if champ in donnees and donnees[champ] not in [None, ""]:

            trouve = True
            valeur = donnees[champ]

            if destination == "organes_cibles":

                if isinstance(valeur, list):
                    resultat[destination] = valeur
                else:
                    resultat[destination] = [valeur]

            else:
                resultat[destination] = valeur

    if trouve:
        resultat["statut"] = "documenté"

    return resultat


# ============================================================
# ADME
# ============================================================

def analyser_adme(donnees):

    resultat = {
        "absorption": None,
        "distribution": None,
        "metabolisme": None,
        "excretion": None,
        "statut": "non disponible"
    }

    if not donnees:
        return resultat

    correspondances = {
        "absorption": "absorption",
        "distribution": "distribution",
        "metabolisme": "metabolisme",
        "excretion": "excretion",
        "ADME": "ADME"
    }

    trouve = False

    for champ, destination in correspondances.items():

        if champ in donnees and donnees[champ]:

            trouve = True
            resultat[destination] = donnees[champ]

    if trouve:
        resultat["statut"] = "documenté"

    return resultat


# ============================================================
# INTERACTIONS
# ============================================================

def analyser_interaction(produit_a, produit_b):

    return {
        "produit_a": produit_a,
        "produit_b": produit_b,
        "interaction": "À prédire",
        "potentialisation": "À évaluer",
        "antagonisme": "À évaluer",
        "inhibition": "À évaluer",
        "competition": "À évaluer",
        "synergie": "À évaluer",
        "statut": "prédit"
    }


# ============================================================
# STRUCTURE MOLÉCULAIRE
# ============================================================

def analyser_structure_moleculaire(donnees):

    resultat = {
        "SMILES": None,
        "InChI": None,
        "CID": None,
        "structure_2D": "Non disponible",
        "structure_3D": "Non disponible",
        "liaison_moleculaire": "À analyser",
        "statut": "non disponible"
    }

    if not donnees:
        return resultat

    for champ in ["SMILES", "smiles"]:
        if champ in donnees and donnees[champ]:
            resultat["SMILES"] = donnees[champ]
            resultat["statut"] = "documenté"

    for champ in ["InChI", "inchi"]:
        if champ in donnees and donnees[champ]:
            resultat["InChI"] = donnees[champ]

    for champ in ["CID", "cid", "PubChem_CID"]:
        if champ in donnees and donnees[champ]:
            resultat["CID"] = donnees[champ]

    if resultat["SMILES"]:
        resultat["structure_2D"] = "Disponible à partir du SMILES"
        resultat["structure_3D"] = "Génération possible à partir du SMILES"
        resultat["liaison_moleculaire"] = (
            "Étude de liaison moléculaire possible"
        )

    return resultat


# ============================================================
# SOURCE
# ============================================================

def analyser_source(donnees):

    if not donnees:
        return {
            "source": None,
            "statut": "non disponible"
        }

    sources = []

    for champ in [
        "source",
        "sources",
        "reference",
        "references",
        "doi",
        "pubmed"
    ]:

        if champ in donnees and donnees[champ]:

            valeur = donnees[champ]

            if isinstance(valeur, list):
                sources.extend(valeur)
            else:
                sources.append(valeur)

    return {
        "source": sources,
        "statut": "documenté" if sources else "non disponible"
    }


# ============================================================
# ANALYSE COMPLETE D'UNE SUBSTANCE
# ============================================================

def analyser_element(nom, donnees=None):

    nom = nettoyer_nom(nom)

    return {
        "identification": identification(
            nom,
            donnees
        ),

        "constituants": extraire_constituants(
            donnees
        ),

        "pharmacologie": analyser_pharmacologie(
            donnees
        ),

        "toxicologie": analyser_toxicologie(
            donnees
        ),

        "adme": analyser_adme(
            donnees
        ),

        "structure_moleculaire":
            analyser_structure_moleculaire(
                donnees
            ),

        "source":
            analyser_source(
                donnees
            )
    }


# ============================================================
# ANALYSE D'UN MÉLANGE
# ============================================================

def analyser_melange(elements):

    analyses = []

    for element in elements:

        if isinstance(element, dict):

            nom = element.get("nom", "")
            donnees = element.get("donnees", {})

        else:

            nom = str(element)
            donnees = {}

        analyses.append(
            analyser_element(
                nom,
                donnees
            )
        )

    interactions = []

    for i in range(len(elements)):

        for j in range(i + 1, len(elements)):

            nom_a = (
                elements[i].get("nom", "")
                if isinstance(elements[i], dict)
                else str(elements[i])
            )

            nom_b = (
                elements[j].get("nom", "")
                if isinstance(elements[j], dict)
                else str(elements[j])
            )

            interactions.append(
                analyser_interaction(
                    nom_a,
                    nom_b
                )
            )

    return {
        "elements": analyses,
        "interactions": interactions,
        "nombre_elements": len(analyses),
        "statut_global": "analyse prédictive"
    }
