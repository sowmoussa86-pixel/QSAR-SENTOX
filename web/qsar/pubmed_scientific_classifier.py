"""Préclassement scientifique des références PubMed pour SENTOX.

Ce module aide à trier les articles. Il ne remplace pas leur lecture
ni une validation toxicologique par un spécialiste.
"""

import re
import unicodedata


def normaliser(texte):
    texte = unicodedata.normalize("NFKD", str(texte or ""))
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texte).lower().strip()


def classer_article(substance, titre="", resume="", synonymes_detectes=None):
    substance = str(substance or "").strip()
    titre = str(titre or "")
    resume = str(resume or "")
    texte = normaliser(titre + " " + resume)

    if not substance:
        return {
            "categorie": "C",
            "libelle": "À vérifier",
            "validation_scientifique": "Non effectuée",
            "preuve_toxicologique_etablie": False,
            "justification": "Substance cible manquante.",
        }

    synonymes_detectes = synonymes_detectes or []
    contient_substance = bool(synonymes_detectes) or (
        normaliser(substance) in texte
    )

    termes_toxicite = (
        "toxicity", "toxicological", "toxicology", "poisoning",
        "lethal dose", "acute toxicity", "chronic toxicity",
        "genotoxicity", "cytotoxicity", "adverse effects"
    )
    termes_indirects = (
        "pharmacokinetic", "metabolism", "metabolite",
        "blood-brain barrier", "enzyme", "permeability",
        "mechanism", "antioxidant", "drug interaction"
    )

    toxicite_detectee = any(mot in texte for mot in termes_toxicite)
    contexte_indirect = any(mot in texte for mot in termes_indirects)

    if contient_substance and toxicite_detectee:
        categorie = "A"
        libelle = "Preuve directe potentielle — lecture requise"
        justification = (
            "La substance semble correspondre et des termes liés à la "
            "toxicité sont détectés. Vérifier que l'étude teste réellement "
            "la substance cible et examine un effet toxique."
        )
    elif contient_substance and contexte_indirect:
        categorie = "B"
        libelle = "Donnée indirecte potentielle"
        justification = (
            "La substance semble correspondre dans un contexte de mécanisme, "
            "métabolisme ou pharmacocinétique. Ce n'est pas une preuve de toxicité."
        )
    elif contient_substance:
        categorie = "C"
        libelle = "À vérifier"
        justification = (
            "Une correspondance lexicale est détectée, mais la pertinence "
            "scientifique n'est pas établie."
        )
    else:
        categorie = "D"
        libelle = "Correspondance non détectée — pertinence à vérifier"
        justification = (
            "Aucune correspondance directe détectée avec le nom fourni. "
            "Un synonyme absent du dictionnaire peut expliquer ce résultat."
        )

    return {
        "categorie": categorie,
        "libelle": libelle,
        "validation_scientifique": "Non effectuée",
        "preuve_toxicologique_etablie": False,
        "justification": justification,
    }
