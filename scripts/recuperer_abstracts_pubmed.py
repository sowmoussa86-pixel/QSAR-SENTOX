import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

source = Path("data/audit_23_references_avec_resumes.csv")
sortie = Path("data/audit_23_references_avec_abstracts.csv")

with source.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

champs = list(lignes[0].keys()) if lignes else []
for nom in ("Abstract_integral", "Statut_abstract"):
    if nom not in champs:
        champs.append(nom)

for i, ligne in enumerate(lignes, 1):
    pmid = ligne.get("PMID", "").strip()
    ligne["Abstract_integral"] = ""
    ligne["Statut_abstract"] = "PMID absent"

    if pmid:
        params = urllib.parse.urlencode({
            "db": "pubmed",
            "id": pmid,
            "rettype": "abstract",
            "retmode": "xml"
        })
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + params

        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "QSAR-SENTOX/1.0"}
            )
            with urllib.request.urlopen(req, timeout=25) as r:
                xml = r.read().decode("utf-8", errors="replace")

            import xml.etree.ElementTree as ET
            racine = ET.fromstring(xml)
            morceaux = [
                (element.text or "").strip()
                for element in racine.findall(".//Abstract/AbstractText")
            ]
            resume = " ".join(x for x in morceaux if x)

            ligne["Abstract_integral"] = resume
            ligne["Statut_abstract"] = (
                "Résumé récupéré" if resume else "Résumé non disponible"
            )
        except Exception as e:
            ligne["Statut_abstract"] = "Erreur : " + str(e)[:120]

    print(f"{i}/{len(lignes)} — PMID {pmid} : {ligne['Statut_abstract']}")
    time.sleep(0.4)

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(lignes)

print("\nFichier créé :", sortie)
print("Fichier source conservé :", source)
