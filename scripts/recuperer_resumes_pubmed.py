import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

source = Path("data/audit_23_references_pubmed_v2.csv")
sortie = Path("data/audit_23_references_avec_resumes.csv")

if not source.exists():
    raise SystemExit(f"Fichier introuvable : {source}")

with source.open(encoding="utf-8-sig", newline="") as f:
    references = list(csv.DictReader(f))

if not references:
    raise SystemExit("Aucune référence dans le fichier source.")

champs = list(references[0].keys())
for champ in ("Resume_PubMed", "Statut_recuperation_resume"):
    if champ not in champs:
        champs.append(champ)

for i, ligne in enumerate(references, start=1):
    pmid = ligne.get("PMID", "").strip()
    ligne["Resume_PubMed"] = ""
    ligne["Statut_recuperation_resume"] = "PMID absent"

    if pmid:
        params = urllib.parse.urlencode({
            "db": "pubmed",
            "id": pmid,
            "retmode": "json"
        })
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + params

        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "QSAR-SENTOX/1.0"}
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                donnees = json.loads(response.read().decode("utf-8"))

            article = donnees.get("result", {}).get(pmid, {})
            titre = article.get("title", "")
            journal = article.get("fulljournalname", "")
            annee = article.get("pubdate", "")

            ligne["Resume_PubMed"] = (
                f"Titre : {titre}\n"
                f"Revue : {journal}\n"
                f"Date : {annee}\n"
                "Note : métadonnées bibliographiques récupérées ; "
                "le résumé intégral n'est pas fourni par cette requête."
            )
            ligne["Statut_recuperation_resume"] = (
                "Métadonnées récupérées" if titre else "Article non trouvé"
            )
        except Exception as e:
            ligne["Statut_recuperation_resume"] = (
                "Erreur réseau/API : " + str(e)[:120]
            )

    print(
        f"{i}/{len(references)} — PMID {pmid} : "
        f"{ligne['Statut_recuperation_resume']}"
    )
    time.sleep(0.4)

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(references)

print("\nFichier créé :", sortie)
print("Fichier source modifié : non")
