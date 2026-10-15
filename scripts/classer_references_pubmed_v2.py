import csv
import re
from pathlib import Path
from collections import Counter

SOURCE = Path("data/references_pubmed_verification.csv")
SORTIE = Path("data/references_pubmed_classees_v2.csv")

MOTS_TOX = [
    "toxicity", "toxicology", "toxicological", "ld50",
    "lethal dose", "genotoxicity", "mutagenicity",
    "carcinogenicity", "neurotoxicity", "hepatotoxicity",
    "nephrotoxicity", "poisoning", "dose response",
    "adverse effects", "safety assessment"
]

MOTS_EXTRAIT = [
    "extract", "extracts", "mixture", "mixtures",
    "herbal", "plant extract", "essential oil",
    "botanical", "preparation"
]

MOTS_PHARMACO = [
    "mechanism", "mechanistic", "pharmacology",
    "therapeutic", "neuroprotective", "stroke protection",
    "receptor", "enzyme inhibition"
]


def normaliser(texte):
    texte = (texte or "").lower()
    texte = re.sub(r"[^a-z0-9]+", " ", texte)
    return " " + " ".join(texte.split()) + " "


def contient_expression(texte_normalise, expression):
    expression_normalisee = normaliser(expression)
    return expression_normalisee.strip() in texte_normalise.strip()


def expressions_trouvees(texte, liste):
    return [mot for mot in liste if contient_expression(texte, mot)]


def classer(ligne):
    titre_brut = ligne.get("Titre", "")
    resume_brut = ligne.get("Resume", "")
    titre = normaliser(titre_brut)
    resume = normaliser(resume_brut)

    substances = [
        s.strip()
        for s in ligne.get(
            "Substances_associees_dans_la_recherche", ""
        ).split(";")
        if s.strip()
    ]

    noms_titre = [
        s for s in substances if contient_expression(titre, s)
    ]
    noms_resume = [
        s for s in substances if contient_expression(resume, s)
    ]

    tox_titre = expressions_trouvees(titre, MOTS_TOX)
    tox_resume = expressions_trouvees(resume, MOTS_TOX)
    mots_extrait = expressions_trouvees(
        titre + resume, MOTS_EXTRAIT
    )
    mots_pharmaco = expressions_trouvees(
        titre + resume, MOTS_PHARMACO
    )

    if noms_titre:
        presence = "Titre"
    elif noms_resume:
        presence = "Résumé uniquement"
    else:
        presence = "Non retrouvé dans titre/résumé"

    if mots_extrait:
        type_etude = "Extrait, mélange ou préparation"
    elif tox_titre or tox_resume:
        type_etude = "Étude toxicologique potentielle"
    elif mots_pharmaco:
        type_etude = "Pharmacologie ou mécanisme"
    else:
        type_etude = "Autre ou pertinence incertaine"

    if noms_titre and tox_titre:
        niveau = "Élevé - à vérifier"
        classement = "Substance dans le titre + terme toxicologique"
    elif noms_titre:
        niveau = "Moyen - à vérifier"
        classement = "Substance dans le titre, toxicité non établie"
    elif noms_resume and (tox_titre or tox_resume):
        niveau = "Moyen - à vérifier"
        classement = "Substance dans le résumé + thème toxicologique"
    elif noms_resume:
        niveau = "Faible à moyen - à vérifier"
        classement = "Substance dans le résumé, pertinence à examiner"
    else:
        niveau = "Faible - à vérifier"
        classement = "Substance non retrouvée textuellement"

    nouvelle = dict(ligne)
    nouvelle["Substance_dans_titre"] = "Oui" if noms_titre else "Non"
    nouvelle["Substance_dans_resume"] = "Oui" if noms_resume else "Non"
    nouvelle["Substance_exacte_reconnue"] = "; ".join(
        sorted(set(noms_titre + noms_resume))
    )
    nouvelle["Type_etude_preliminaire"] = type_etude
    nouvelle["Niveau_pertinence"] = niveau
    nouvelle["Classement_v2"] = classement
    nouvelle["Indices_toxicologiques_titre"] = "; ".join(tox_titre)
    nouvelle["Indices_toxicologiques_resume"] = "; ".join(tox_resume)
    nouvelle["Indices_extrait_melange"] = "; ".join(mots_extrait)
    nouvelle["Indices_pharmacologie"] = "; ".join(mots_pharmaco)
    nouvelle["Justification_classement"] = (
        f"Présence du nom : {presence}. "
        f"Termes toxicologiques dans le titre : "
        f"{', '.join(tox_titre) or 'aucun détecté'}. "
        f"Validation scientifique humaine requise."
    )
    nouvelle["Validation_humaine_v2"] = "À faire"
    return nouvelle


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Fichier source introuvable : {SOURCE}")

    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f))

    if not lignes:
        raise SystemExit("Le fichier source ne contient aucune référence.")

    resultats = [classer(ligne) for ligne in lignes]
    colonnes = list(resultats[0].keys())

    with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(resultats)

    print("Classement v2 terminé.")
    print("Références traitées :", len(resultats))
    print("Fichier créé :", SORTIE)
    print("Fichier source modifié : non")
    print("\n=== CLASSEMENT V2 ===")
    for categorie, nombre in Counter(
        r["Classement_v2"] for r in resultats
    ).most_common():
        print(f"{categorie} : {nombre}")

    print("\n=== TYPES D'ETUDES PRELIMINAIRES ===")
    for categorie, nombre in Counter(
        r["Type_etude_preliminaire"] for r in resultats
    ).most_common():
        print(f"{categorie} : {nombre}")

    print("\nAttention : classement textuel préliminaire,")
    print("pas une validation scientifique des articles.")


if __name__ == "__main__":
    main()
