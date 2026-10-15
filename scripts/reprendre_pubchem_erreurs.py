import argparse
import csv
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

SOURCE = Path("data/sentox_dl50_adme_candidats.csv")
SORTIE = Path("data/sentox_dl50_adme_candidats_corriges.csv")
DELAI_NORMAL = 2.0
CHAMPS = [
    "Nom", "CID", "Section", "Texte_source",
    "Source_URL", "Statut_validation"
]

def lire_csv(path):
    csv.field_size_limit(10_000_000)
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def requete(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "SENTOX research contact: local project"}
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))

def extraire_texte(infos):
    textes = []
    for info in infos or []:
        valeur = info.get("Value", {})
        for x in valeur.get("StringWithMarkup", []) or []:
            if x.get("String"):
                textes.append(x["String"])
        if valeur.get("Number") is not None:
            textes.append(str(valeur["Number"]))
    return textes

def parcourir(sections, resultats):
    mots = (
        "toxicity", "lethal dose", "ld50", "lc50",
        "absorption", "distribution", "metabolism",
        "metabolite", "excretion", "pharmacokinetic",
        "toxicokinetic", "bioavailability"
    )
    for section in sections or []:
        titre = section.get("TOCHeading", "")
        for info in section.get("Information", []) or []:
            texte = " | ".join(extraire_texte([info]))
            if texte and any(m in (titre + " " + texte).lower() for m in mots):
                resultats.append((titre, texte))
        parcourir(section.get("Section", []), resultats)

def ecrire(lignes, mode="a"):
    with SORTIE.open(mode, encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS)
        if mode == "w":
            w.writeheader()
        w.writerows(lignes)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=30)
    args = p.parse_args()

    lignes = lire_csv(SOURCE)
    erreurs = {}
    for r in lignes:
        if r.get("Section") == "Erreur de collecte" and r.get("CID"):
            erreurs.setdefault(r["CID"], r)

    # Créer la nouvelle sortie en conservant toutes les lignes non erronées.
    if not SORTIE.exists():
        ecrire([r for r in lignes if r.get("Section") != "Erreur de collecte"], "w")

    existantes = lire_csv(SORTIE) if SORTIE.exists() else []
    cid_ok = {
        r["CID"] for r in existantes
        if r.get("CID") and r.get("Section") != "Erreur de collecte"
    }
    a_traiter = [
        (cid, r) for cid, r in erreurs.items()
        if cid not in cid_ok
    ][:args.limit]

    print("CID en erreur à reprendre :", len(erreurs))
    print("CID déjà récupérés :", len(cid_ok))
    print("Tentatives dans ce lot :", len(a_traiter))

    for i, (cid, ancien) in enumerate(a_traiter, 1):
        nom = ancien.get("Nom", "")
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
        nouvelles = []
        statut = "Annotations à vérifier"
        erreur = ""

        for tentative in range(4):
            try:
                data = requete(url)
                parcourir(data.get("Record", {}).get("Section", []), nouvelles)
                break
            except urllib.error.HTTPError as e:
                erreur = f"HTTP {e.code}: {e.reason}"
                if e.code == 429:
                    attente = min(60, 10 * (2 ** tentative))
                    try:
                        attente = max(attente, int(e.headers.get("Retry-After", "0")))
                    except ValueError:
                        pass
                    print(f"Limite PubChem : pause de {attente} s")
                    time.sleep(attente)
                else:
                    break
            except Exception as e:
                erreur = str(e)[:200]
                time.sleep(5 * (tentative + 1))

        if nouvelles:
            sorties = [{
                "Nom": nom, "CID": cid, "Section": titre,
                "Texte_source": texte, "Source_URL": url,
                "Statut_validation": statut
            } for titre, texte in nouvelles]
        else:
            sorties = [{
                "Nom": nom, "CID": cid,
                "Section": "Aucune section cible extraite" if not erreur else "Erreur de collecte",
                "Texte_source": "" if not erreur else erreur,
                "Source_URL": url,
                "Statut_validation": "À vérifier"
            }]

        ecrire(sorties)
        print(f"{i}/{len(a_traiter)} : CID {cid} — {len(nouvelles)} annotations")
        time.sleep(DELAI_NORMAL)

    print("Fichier de sortie :", SORTIE)
    print("Ce lot est terminé. Relancer le script permet de poursuivre.")

if __name__ == "__main__":
    main()
