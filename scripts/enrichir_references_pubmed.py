import csv
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE = Path("data/collecteur_test_multi_sources_001.csv")
SORTIE = Path("data/references_pubmed_verification.csv")

with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

references = {}
for ligne in lignes:
    nom = ligne["Nom"]
    for pmid in ligne["PubMed_PMIDs"].split(";"):
        pmid = pmid.strip()
        if pmid:
            references.setdefault(pmid, set()).add(nom)

resultats = []

for pmid, substances in references.items():
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    })
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + params

    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "QSAR-SENTOX research"}
        )
        with urllib.request.urlopen(req, timeout=30) as reponse:
            racine = ET.fromstring(reponse.read())

        article = racine.find(".//PubmedArticle")
        if article is None:
            raise ValueError("Article introuvable")

        titre = " ".join(
            "".join(article.find(".//ArticleTitle").itertext()).split()
        ) if article.find(".//ArticleTitle") is not None else ""

        resume = " ".join(
            " ".join("".join(x.itertext()) for x in article.findall(".//Abstract/AbstractText")).split()
        )

        journal = article.findtext(".//Journal/Title", default="")
        annee = article.findtext(".//PubDate/Year", default="")
        doi = ""

        for identifiant in article.findall(".//ArticleId"):
            if identifiant.get("IdType") == "doi":
                doi = identifiant.text or ""
                break

        resultats.append({
            "PMID": pmid,
            "Substances_associees_dans_la_recherche": "; ".join(sorted(substances)),
            "Titre": titre,
            "Annee": annee,
            "Revue": journal,
            "DOI": doi,
            "Resume": resume,
            "URL": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "Validation_pertinence": "À vérifier"
        })

    except Exception as erreur:
        resultats.append({
            "PMID": pmid,
            "Substances_associees_dans_la_recherche": "; ".join(sorted(substances)),
            "Titre": "",
            "Annee": "",
            "Revue": "",
            "DOI": "",
            "Resume": "",
            "URL": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "Validation_pertinence": "Erreur de récupération : " + str(erreur)[:150]
        })

    time.sleep(0.4)

with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
    colonnes = [
        "PMID", "Substances_associees_dans_la_recherche", "Titre",
        "Annee", "Revue", "DOI", "Resume", "URL",
        "Validation_pertinence"
    ]
    ecrivain = csv.DictWriter(f, fieldnames=colonnes)
    ecrivain.writeheader()
    ecrivain.writerows(resultats)

print("Références traitées :", len(resultats))
print("Fichier créé :", SORTIE)
print("Les références restent à vérifier scientifiquement.")
