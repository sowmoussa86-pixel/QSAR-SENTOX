
import csv
import json
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = Path("data/sentox_database_2000_enriched_noms.csv")
SORTIE = Path("data/ld50_candidats_pubchem_a_verifier.csv")
JOURNAL = Path("data/ld50_requetes_pubchem_log.csv")


def lire_base():
    if not BASE.exists():
        raise FileNotFoundError(f"Base introuvable : {BASE}")
    with BASE.open("r", encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.DictReader(fichier)
        lignes = list(lecteur)
        colonnes = lecteur.fieldnames or []
    if not lignes:
        raise ValueError("La base ne contient aucune ligne.")
    return lignes, colonnes


def chercher_extraits(objet):
    """Recherche des extraits mentionnant une LD50 dans les données PubChem."""
    if isinstance(objet, dict):
        rubrique = str(objet.get("TOCHeading", ""))
        informations = objet.get("Information", [])
        if isinstance(informations, list):
            for info in informations:
                texte = json.dumps(info.get("Value", {}), ensure_ascii=False)
                if re.search(r"\bLD\s*50\b|lethal dose", texte, re.I) and re.search(r"toxicity", rubrique, re.I):
                    yield rubrique, texte[:4000]
        for cle, valeur in objet.items():
            if cle != "Information" and isinstance(valeur, (dict, list)):
                yield from chercher_extraits(valeur)
    elif isinstance(objet, list):
        for element in objet:
            yield from chercher_extraits(element)


def interroger_pubchem(cid):
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/"
        f"data/compound/{cid}/JSON?heading=Toxicity"
    )
    requete = Request(
        url,
        headers={"User-Agent": "QSAR-SENTOX-toxicology-research/1.0"}
    )
    with urlopen(requete, timeout=25) as reponse:
        return json.loads(reponse.read().decode("utf-8"))


def main():
    lignes, colonnes = lire_base()
    print(f"Base lue : {len(lignes)} lignes")
    print("Colonnes disponibles :", ", ".join(colonnes))

    if "CID" in colonnes:
        colonne_cid = "CID"
    elif "PubChem_CID" in colonnes:
        colonne_cid = "PubChem_CID"
    else:
        raise ValueError("Aucune colonne CID ou PubChem_CID trouvée.")

    candidats = []
    journal = []
    cids_vus = set()

    for ligne in lignes:
        cid = (ligne.get(colonne_cid) or "").strip()
        nom = (
            ligne.get("Nom_substance")
            or ligne.get("Nom")
            or ligne.get("name")
            or ""
        ).strip()

        if not cid.isdigit() or cid in cids_vus:
            continue
        cids_vus.add(cid)

        try:
            donnees = interroger_pubchem(cid)
            extraits = list(chercher_extraits(donnees))
            for rubrique, extrait in extraits:
                candidats.append({
                    "CID": cid,
                    "Nom_substance": nom,
                    "Rubrique_PubChem": rubrique,
                    "Extrait_brut": extrait,
                    "LD50_mg_kg": "",
                    "Espece": "",
                    "Voie_exposition": "",
                    "Source_toxicologie": "PubChem PUG View",
                    "Statut_validation": "A_VERIFIER_MANUELLEMENT"
                })
            statut = (
                f"{len(extraits)} extrait(s) à vérifier"
                if extraits else "Aucun extrait LD50 détecté"
            )
        except HTTPError as erreur:
            statut = f"HTTP_{erreur.code}"
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as erreur:
            statut = f"ERREUR_RESEAU_OU_JSON: {str(erreur)[:150]}"

        journal.append({
            "CID": cid,
            "Nom_substance": nom,
            "Statut": statut
        })
        print(f"{cid} | {nom} | {statut}")
        time.sleep(0.4)

    champs_candidats = [
        "CID", "Nom_substance", "Rubrique_PubChem", "Extrait_brut",
        "LD50_mg_kg", "Espece", "Voie_exposition",
        "Source_toxicologie", "Statut_validation"
    ]
    with SORTIE.open("w", encoding="utf-8-sig", newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=champs_candidats)
        ecrivain.writeheader()
        ecrivain.writerows(candidats)

    with JOURNAL.open("w", encoding="utf-8-sig", newline="") as fichier:
        ecrivain = csv.DictWriter(
            fichier, fieldnames=["CID", "Nom_substance", "Statut"]
        )
        ecrivain.writeheader()
        ecrivain.writerows(journal)

    print("\nTerminé.")
    print(f"CID interrogés : {len(journal)}")
    print(f"Extraits candidats : {len(candidats)}")
    print(f"Fichier candidats : {SORTIE}")
    print(f"Journal : {JOURNAL}")
    print("Les résultats restent à vérifier : aucune LD50 n'est validée automatiquement.")
    print("La base originale n'a pas été modifiée.")


if __name__ == "__main__":
    main()
