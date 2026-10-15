import csv
import re
from pathlib import Path

SOURCE = Path("data/references_pubmed_verification.csv")
SORTIE = Path("data/references_pubmed_classees.csv")

MOTS_TOX = [
    "toxicity", "toxicology", "toxicological", "ld50",
    "lethal dose", "acute toxicity", "adme",
    "absorption", "metabolism", "metabolite",
    "pharmacokinetic", "distribution", "excretion",
    "toxicokinetic", "poisoning", "dose-response"
]

def normaliser(texte):
    return re.sub(r"[^a-z0-9]+", " ", (texte or "").lower()).strip()

with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

resultats = []

for ligne in lignes:
    titre = ligne.get("Titre", "")
    resume = ligne.get("Resume", "")
    texte = normaliser(titre + " " + resume)
    noms = [
        normaliser(n)
        for n in ligne.get(
            "Substances_associees_dans_la_recherche", ""
        ).split(";")
        if n.strip()
    ]

    nom_trouve = any(
        nom and nom in texte
        for nom in noms
    )
    mots_trouves = [
        mot for mot in MOTS_TOX
        if normaliser(mot) in texte
    ]

    if nom_trouve and mots_trouves:
        classement = "Priorité de vérification"
    elif nom_trouve:
        classement = "Substance mentionnée - thème à vérifier"
    elif mots_trouves:
        classement = "Thème toxicologique - substance à confirmer"
    else:
        classement = "Pertinence incertaine"

    nouvelle = dict(ligne)
    nouvelle["Substance_reconnue_dans_titre_resume"] = (
        "Oui" if nom_trouve else "Non"
    )
    nouvelle["Mots_cles_detectes"] = "; ".join(mots_trouves)
    nouvelle["Classement_automatique"] = classement
    nouvelle["Validation_humaine"] = "À faire"
    resultats.append(nouvelle)

if resultats:
    colonnes = list(resultats[0].keys())
    with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(resultats)

from collections import Counter
compte = Counter(r["Classement_automatique"] for r in resultats)

print("Références classées :", len(resultats))
for categorie, nombre in compte.items():
    print(f"{categorie} : {nombre}")
print("Fichier créé :", SORTIE)
print("Attention : classement automatique, pas validation scientifique.")
