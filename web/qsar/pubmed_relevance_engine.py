"""Évaluation préliminaire de la pertinence des articles PubMed pour SENTOX.

Ce module effectue un tri lexical explicable.
Il ne valide ni la qualité d'un article ni une conclusion toxicologique.
"""

import re
import unicodedata


SYNONYMES = {
    "3-hydroxybenzyl alcohol": [
        "3-hydroxybenzyl alcohol",
        "m-hydroxybenzyl alcohol",
        "m-hydroxybenzylalcohol",
        "3-hydroxybenzylalcohol",
    ],
    "4-hydroxybenzyl alcohol": [
        "4-hydroxybenzyl alcohol",
        "p-hydroxybenzyl alcohol",
        "4-hydroxybenzylalcohol",
        "p-hydroxybenzylalcohol",
    ],
    "acetone": ["acetone", "propanone", "dimethyl ketone"],
    "benzene": ["benzene", "benzol"],
    "catechol": ["catechol", "1,2-benzenediol", "pyrocatechol"],
    "o-cresol": ["o-cresol", "ortho-cresol", "2-methylphenol"],
    "m-cresol": ["m-cresol", "meta-cresol", "3-methylphenol"],
    "salicylic acid": ["salicylic acid", "2-hydroxybenzoic acid"],
    "phloroglucinol": ["phloroglucinol", "1,3,5-benzenetriol"],
}

MOTS_TOXICOLOGIE = (
    "toxicity", "toxicology", "toxicological", "poisoning",
    "intoxication", "adverse effects", "safety", "lethal dose",
    "acute toxicity", "chronic toxicity"
)


def normaliser(texte):
    """Normalise casse, accents et espaces."""
    texte = unicodedata.normalize("NFKD", str(texte or ""))
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texte).lower().strip()


def contient_expression(texte, expression):
    """Recherche une expression entière, sans confondre une sous-chaîne."""
    texte_normalise = normaliser(texte)
    expression_normalisee = normaliser(expression)
    motif = (
        r"(?<![a-z0-9])"
        + re.escape(expression_normalisee)
        + r"(?![a-z0-9])"
    )
    return bool(re.search(motif, texte_normalise))


def evaluer_pertinence(substance, titre="", resume=""):
    """Retourne une évaluation lexicale explicable pour une substance.

    Le résultat ne constitue pas une validation scientifique.
    """
    substance = str(substance or "").strip()
    titre = str(titre or "")
    resume = str(resume or "")

    if not substance:
        return {
            "substance": "",
            "synonymes_detectes_titre": [],
            "synonymes_detectes_resume": [],
            "mots_toxicologie_detectes": [],
            "classement": "Substance manquante",
            "preuve_toxicologique_etablie": False,
            "validation_scientifique": "Non effectuée",
            "avertissement": "La substance cible doit être précisée.",
        }

    cles = {
        normaliser(cle): valeurs
        for cle, valeurs in SYNONYMES.items()
    }
    synonymes = cles.get(normaliser(substance), [substance])

    trouves_titre = [
        terme for terme in synonymes
        if contient_expression(titre, terme)
    ]
    trouves_resume = [
        terme for terme in synonymes
        if contient_expression(resume, terme)
    ]

    texte_complet = normaliser(titre + " " + resume)
    termes_tox = [
        mot for mot in MOTS_TOXICOLOGIE
        if contient_expression(texte_complet, mot)
    ]

    if trouves_titre:
        classement = "Nom ou synonyme détecté dans le titre"
    elif trouves_resume:
        classement = "Nom ou synonyme détecté dans le résumé"
    else:
        classement = "Correspondance lexicale non détectée"

    return {
        "substance": substance,
        "synonymes_detectes_titre": trouves_titre,
        "synonymes_detectes_resume": trouves_resume,
        "mots_toxicologie_detectes": termes_tox,
        "classement": classement,
        "preuve_toxicologique_etablie": False,
        "validation_scientifique": "Non effectuée",
        "avertissement": (
            "Tri lexical uniquement. Une mention de la substance ou de mots "
            "toxicologiques ne démontre pas que l'article évalue sa toxicité. "
            "Vérifier le contenu, le modèle étudié, l'effet et les conclusions."
        ),
    }


def evaluer_article(article, substance):
    """Adapte un article retourné par pubmed_engine.py."""
    return evaluer_pertinence(
        substance=substance,
        titre=article.get("titre", ""),
        resume=article.get("resume", ""),
    )
