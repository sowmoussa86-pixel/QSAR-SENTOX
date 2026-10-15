import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

BASE = Path("data/sentox_database_2000_enriched_noms.csv")
SORTIE = Path("data/collecteur_test_multi_sources_001.csv")

MOTS_CLES = (
    "toxicity", "toxicological", "lethal dose", "ld50",
    "absorption, distribution and excretion", "metabolism",
    "metabolites", "pharmacokinetic", "bioavailability",
    "acute toxicity", "non-human toxicity values",
    "toxicity data", "human toxicity values"
)


def requete_json(url, timeout=35):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "QSAR-SENTOX research contact: local project"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def texte_valeurs(informations):
    textes = []
    for info in informations or []:
        valeur = info.get("Value", {})
        for element in valeur.get("StringWithMarkup", []) or []:
            texte = element.get("String", "").strip()
            if texte:
                textes.append(texte)
        if valeur.get("Number") is not None:
            textes.append(str(valeur["Number"]))
    return textes


def extraire_sections(sections, resultat):
    for section in sections or []:
        titre = section.get("TOCHeading", "")
        if any(mot in titre.lower() for mot in MOTS_CLES):
            textes = texte_valeurs(section.get("Information", []))
            if textes:
                resultat.append(titre + ": " + " | ".join(textes[:5]))
        extraire_sections(section.get("Section", []), resultat)


def rechercher_pubmed(nom):
    termes = (
        f'"{nom}" AND '
        '(toxicology OR toxicity OR LD50 OR ADME OR '
        'absorption OR metabolism OR pharmacokinetics)'
    )
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": termes,
        "retmax": 8,
        "retmode": "json",
        "sort": "relevance"
    })
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + params
    data = requete_json(url)
    ids = data.get("esearchresult", {}).get("idlist", [])
    return ids, url


def charger_base():
    with BASE.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--start", type=int, default=0)
    args = parser.parse_args()

    substances = charger_base()
    if args.start < 0 or args.start >= len(substances):
        raise SystemExit("Position de départ hors limites.")
    if args.limit < 1:
        raise SystemExit("La limite doit être supérieure à zéro.")

    lot = substances[args.start:args.start + args.limit]
    lignes = []

    for index, substance in enumerate(lot, start=args.start + 1):
        cid = (substance.get("CID") or substance.get("PubChem_CID") or "").strip()
        nom = (substance.get("Nom") or substance.get("Nom_PubChem") or "").strip()
        print(f"[{index}/{len(substances)}] {nom} (CID {cid})")

        annotations = []
        statut_pubchem = "Non testé"
        url_pubchem = ""
        pmids = []
        url_pubmed = ""
        statut_pubmed = "Non testé"

        if cid.isdigit():
            url_pubchem = (
                "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/"
                f"data/compound/{cid}/JSON"
            )
            try:
                data = requete_json(url_pubchem)
                record = data.get("Record", {})
                extraire_sections(record.get("Section", []), annotations)
                statut_pubchem = "Réponse reçue"
            except Exception as erreur:
                statut_pubchem = "Erreur: " + str(erreur)[:180]
            time.sleep(1.2)
        else:
            statut_pubchem = "CID absent"

        if nom:
            try:
                pmids, url_pubmed = rechercher_pubmed(nom)
                statut_pubmed = "Résultats trouvés" if pmids else "Aucun résultat"
            except Exception as erreur:
                statut_pubmed = "Erreur: " + str(erreur)[:180]
            time.sleep(0.4)
        else:
            statut_pubmed = "Nom absent"

        lignes.append({
            "Nom": nom,
            "CID": cid,
            "PubChem_statut": statut_pubchem,
            "PubChem_URL": url_pubchem,
            "Annotations_toxicologie_ADME": "\n".join(annotations),
            "PubMed_statut": statut_pubmed,
            "PubMed_PMIDs": ";".join(pmids),
            "PubMed_URL_recherche": url_pubmed,
            "Statut_validation": "À vérifier manuellement"
        })

    colonnes = list(lignes[0].keys()) if lignes else []
    with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)

    print("\nFichier créé :", SORTIE)
    print("Substances traitées :", len(lignes))
    print("Réponses PubChem reçues :", sum(
        r["PubChem_statut"] == "Réponse reçue" for r in lignes
    ))
    print("Substances avec publications PubMed :", sum(
        r["PubMed_statut"] == "Résultats trouvés" for r in lignes
    ))
    print("Base originale modifiée : non")
    print("Les annotations extraites ne sont pas automatiquement validées.")


if __name__ == "__main__":
    main()
