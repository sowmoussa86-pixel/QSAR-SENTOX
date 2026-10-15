import csv
from web.qsar.pubmed_scientific_classifier import classer_article

source = "data/audit_pubmed_relevance_engine_v1.csv"
destination = "data/audit_pubmed_classement_scientifique_v1.csv"

with open(source, encoding="utf-8-sig", newline="") as f:
    lecteur = csv.DictReader(f)
    lignes = list(lecteur)
    champs = list(lecteur.fieldnames or [])

ajouts = [
    "Categorie_scientifique_preliminaire",
    "Libelle_scientifique_preliminaire",
    "Justification_scientifique_preliminaire",
    "Validation_scientifique",
    "Preuve_toxicologique_etablie",
]

for champ in ajouts:
    if champ not in champs:
        champs.append(champ)

with open(destination, "w", encoding="utf-8-sig", newline="") as f:
    ecrivain = csv.DictWriter(f, fieldnames=champs)
    ecrivain.writeheader()

    for ligne in lignes:
        substance = ligne.get("Substances_associees_dans_la_recherche", "")
        titre = ligne.get("Titre", "")
        resume = ligne.get("Abstract_integral", "") or ligne.get("Resume_PubMed", "")

        syn_titre = ligne.get("Synonymes_detectes_titre_v3", "")
        syn_resume = ligne.get("Synonymes_detectes_resume_v3", "")
        synonymes = [
            terme.strip()
            for terme in (syn_titre + ";" + syn_resume).split(";")
            if terme.strip()
        ]

        resultat = classer_article(
            substance, titre, resume, synonymes
        )

        ligne["Categorie_scientifique_preliminaire"] = resultat["categorie"]
        ligne["Libelle_scientifique_preliminaire"] = resultat["libelle"]
        ligne["Justification_scientifique_preliminaire"] = resultat["justification"]
        ligne["Validation_scientifique"] = resultat["validation_scientifique"]
        ligne["Preuve_toxicologique_etablie"] = str(
            resultat["preuve_toxicologique_etablie"]
        ).lower()

        ecrivain.writerow(ligne)

print("Articles traités :", len(lignes))
print("Nouveau fichier :", destination)
print("Fichier source modifié : non")
