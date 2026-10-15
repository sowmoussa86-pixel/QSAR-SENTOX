import csv
import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE = Path("data/sentox_database_2000_enriched_noms.csv")
SORTIE = Path("data/sentox_dl50_adme_candidats.csv")
PROGRESSION = Path("data/progression_dl50_adme.json")

def requete(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "SENTOX toxicology research"}
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))

def texte_info(info):
    resultat = []
    for item in info or []:
        valeur = item.get("Value", {})
        for x in valeur.get("StringWithMarkup", []) or []:
            if x.get("String"):
                resultat.append(x["String"])
        if valeur.get("Number") is not None:
            unite = valeur.get("Unit", "")
            resultat.append(str(valeur["Number"]) + (" " + unite if unite else ""))
    return resultat

def parcourir(sections, sorties):
    for section in sections or []:
        titre = section.get("TOCHeading", "")
        for contenu in section.get("Information", []) or []:
            morceaux = texte_info([contenu])
            texte = " ".join(morceaux).strip()
            if not texte:
                continue
            if re.search(
                r"LD50|lethal dose|lethal concentration|LC50|"
                r"toxicity data|non-human toxicity|absorption|"
                r"distribution|metabolism|metabolite|excretion|"
                r"pharmacokinetic|toxicokinetic|bioavailability",
                titre + " " + texte, re.I
            ):
                sorties.append({
                    "Section": titre,
                    "Texte_source": texte,
                    "Reference_PubChem": ""
                })
        parcourir(section.get("Section", []), sorties)

def main():
    with BASE.open(encoding="utf-8-sig", newline="") as f:
        substances = list(csv.DictReader(f))

    deja = set()
    if SORTIE.exists():
        with SORTIE.open(encoding="utf-8-sig", newline="") as f:
            deja = {r["CID"] for r in csv.DictReader(f) if r.get("CID")}

    colonnes = [
        "Nom", "CID", "Section", "Texte_source",
        "Source_URL", "Statut_validation"
    ]
    if not SORTIE.exists():
        with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
            csv.DictWriter(f, fieldnames=colonnes).writeheader()

    total = len(substances)
    traites = len(deja)

    for numero, s in enumerate(substances, 1):
        cid = str(s.get("CID") or s.get("PubChem_CID") or "").strip()
        nom = str(s.get("Nom") or s.get("Nom_PubChem") or "").strip()
        if not cid.isdigit() or cid in deja:
            continue

        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
        lignes = []
        statut = "À vérifier"
        try:
            data = requete(url)
            record = data.get("Record", {})
            parcourir(record.get("Section", []), lignes)
            if not lignes:
                lignes = [{
                    "Section": "Aucune section cible extraite",
                    "Texte_source": "",
                    "Reference_PubChem": ""
                }]
            statut = "Annotations à vérifier"
        except Exception as e:
            lignes = [{
                "Section": "Erreur de collecte",
                "Texte_source": str(e)[:250],
                "Reference_PubChem": ""
            }]
            statut = "Erreur de collecte"

        with SORTIE.open("a", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=colonnes)
            for item in lignes:
                w.writerow({
                    "Nom": nom,
                    "CID": cid,
                    "Section": item["Section"],
                    "Texte_source": item["Texte_source"],
                    "Source_URL": url,
                    "Statut_validation": statut
                })

        deja.add(cid)
        traites += 1
        PROGRESSION.write_text(
            json.dumps({"substances_traitees": traites, "total": total},
                       ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        if numero % 10 == 0 or numero == total:
            print(f"Progression : {traites}/{total} substances")
        time.sleep(0.25)

    print("Collecte terminée ou interrompue.")
    print("Résultats :", SORTIE)
    print("Progression :", PROGRESSION)
    print("Les annotations doivent être validées avant usage toxicologique.")

if __name__ == "__main__":
    main()
