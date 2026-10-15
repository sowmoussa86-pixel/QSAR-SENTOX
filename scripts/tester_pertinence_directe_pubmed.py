import csv
import re
from pathlib import Path

source = Path("data/audit_scientifique_preliminaire_23.csv")
sortie = Path("data/audit_pertinence_directe_pubmed_v1.csv")

if not source.exists():
    raise SystemExit(f"Fichier introuvable : {source}")

with source.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

if not lignes:
    raise SystemExit("Le fichier ne contient aucune référence.")

def normaliser(texte):
    texte = (texte or "").lower()
    return re.sub(r"\s+", " ", texte).strip()

champs = list(lignes[0].keys())
for nom in (
    "Substance_recherchee",
    "Substance_dans_titre",
    "Substance_dans_resume",
    "Pertinence_directe_automatique",
    "Limite_evaluation"
):
    if nom not in champs:
        champs.append(nom)

for ligne in lignes:
    substance = ligne.get(
        "Substances_associees_dans_la_recherche", ""
    ).strip()
    titre = normaliser(ligne.get("Titre", ""))
    resume = normaliser(ligne.get("Abstract_integral", ""))

    cible = normaliser(substance)
    dans_titre = bool(cible and cible in titre)
    dans_resume = bool(cible and cible in resume)

    ligne["Substance_recherchee"] = substance
    ligne["Substance_dans_titre"] = "Oui" if dans_titre else "Non"
    ligne["Substance_dans_resume"] = "Oui" if dans_resume else "Non"

    if dans_titre:
        classement = "Nom exact dans le titre - vérifier le contenu"
    elif dans_resume:
        classement = "Nom exact dans le résumé - vérifier le contenu"
    else:
        classement = "Nom exact non retrouvé - synonymes à examiner"

    ligne["Pertinence_directe_automatique"] = classement
    ligne["Limite_evaluation"] = (
        "Test lexical uniquement : les synonymes, isomères et noms "
        "alternatifs peuvent ne pas être reconnus. Aucune validation "
        "scientifique automatique."
    )

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(lignes)

print("Références analysées :", len(lignes))
print("\nRésultats du test lexical :")

for ligne in lignes:
    print(
        ligne.get("PMID", ""), "|",
        ligne["Substance_recherchee"], "|",
        "Titre:", ligne["Substance_dans_titre"], "|",
        "Résumé:", ligne["Substance_dans_resume"], "|",
        ligne["Pertinence_directe_automatique"]
    )

print("\nFichier créé :", sortie)
print("Fichier source modifié : non")
print("Validation scientifique : non effectuée")
