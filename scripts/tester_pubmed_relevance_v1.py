import csv
from pathlib import Path
from web.qsar.pubmed_relevance_engine import evaluer_pertinence

source = Path("data/audit_scientifique_preliminaire_23.csv")
sortie = Path("data/audit_pubmed_relevance_engine_v1.csv")

with source.open(encoding="utf-8-sig", newline="") as f:
    references = list(csv.DictReader(f))

if not references:
    raise SystemExit("Aucune référence trouvée.")

champs = list(references[0].keys())
ajouts = [
    "Synonymes_detectes_titre_v3",
    "Synonymes_detectes_resume_v3",
    "Classement_relevance_v3",
    "Preuve_toxicologique_etablie_v3",
    "Validation_scientifique_v3",
    "Avertissement_relevance_v3",
]
for champ in ajouts:
    if champ not in champs:
        champs.append(champ)

for ligne in references:
    resultat = evaluer_pertinence(
        substance=ligne.get("Substances_associees_dans_la_recherche", ""),
        titre=ligne.get("Titre", ""),
        resume=ligne.get("Abstract_integral", ""),
    )

    ligne["Synonymes_detectes_titre_v3"] = "; ".join(
        resultat["synonymes_detectes_titre"]
    )
    ligne["Synonymes_detectes_resume_v3"] = "; ".join(
        resultat["synonymes_detectes_resume"]
    )
    ligne["Classement_relevance_v3"] = resultat["classement"]
    ligne["Preuve_toxicologique_etablie_v3"] = str(
        resultat["preuve_toxicologique_etablie"]
    )
    ligne["Validation_scientifique_v3"] = resultat["validation_scientifique"]
    ligne["Avertissement_relevance_v3"] = resultat["avertissement"]

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(references)

print("Références analysées :", len(references))
print("Fichier créé :", sortie)
print("Fichier source modifié : non")
print("\nRésultats :")

for ligne in references:
    print(
        ligne.get("PMID", ""), "|",
        ligne.get("Substances_associees_dans_la_recherche", ""), "|",
        ligne["Classement_relevance_v3"], "|",
        ligne["Synonymes_detectes_resume_v3"] or "aucun synonyme détecté"
    )

print("\nValidation scientifique complète : non effectuée")
