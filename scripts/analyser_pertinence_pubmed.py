import csv
from collections import Counter
from pathlib import Path

source = Path("data/audit_23_references_avec_abstracts.csv")
sortie = Path("data/analyse_pertinence_pubmed_23.csv")

with source.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

if not lignes:
    raise SystemExit("Le fichier ne contient aucune référence.")

def analyser(titre, resume):
    texte = (titre + " " + resume).lower()

    tox = [
        "toxicity", "toxicological", "toxicology", "poisoning",
        "intoxication", "toxic", "adverse effects", "safety"
    ]
    pharmaco = [
        "pharmacology", "pharmacological", "therapeutic",
        "drug interaction", "pharmacokinetic", "pharmacodynamics"
    ]
    mecanisme = [
        "enzyme", "metabolism", "metabolic", "biotransformation",
        "oxidoreductase", "monooxygenase", "mechanism"
    ]

    score_tox = sum(mot in texte for mot in tox)
    score_pharmaco = sum(mot in texte for mot in pharmaco)
    score_mecanisme = sum(mot in texte for mot in mecanisme)

    if score_tox:
        categorie = "Toxicologie ou sécurité : à examiner"
    elif score_pharmaco:
        categorie = "Pharmacologie : pertinence à vérifier"
    elif score_mecanisme:
        categorie = "Mécanisme ou métabolisme : pertinence à vérifier"
    else:
        categorie = "Pertinence toxicologique non établie"

    return categorie, score_tox, score_pharmaco, score_mecanisme

champs = list(lignes[0].keys())
for nom in (
    "Categorie_automatique",
    "Score_mots_toxicologie",
    "Score_mots_pharmacologie",
    "Score_mots_mecanismes",
    "Validation_humaine"
):
    if nom not in champs:
        champs.append(nom)

for ligne in lignes:
    titre = ligne.get("Titre", ligne.get("ArticleTitle", ""))
    resume = ligne.get("Abstract_integral", "")
    categorie, tox, pharma, mech = analyser(titre, resume)

    ligne["Categorie_automatique"] = categorie
    ligne["Score_mots_toxicologie"] = tox
    ligne["Score_mots_pharmacologie"] = pharma
    ligne["Score_mots_mecanismes"] = mech
    ligne["Validation_humaine"] = "À effectuer"

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(lignes)

print("Références analysées :", len(lignes))
print("\nClassement automatique préliminaire :")
for categorie, nombre in Counter(
    ligne["Categorie_automatique"] for ligne in lignes
).most_common():
    print(f"{categorie} : {nombre}")

print("\nFichier créé :", sortie)
print("Validation scientifique humaine : non effectuée")
print("Fichiers sources modifiés : non")
