import csv
import time
from pathlib import Path
from urllib.error import HTTPError

from scripts.enrichir_ld50_sources_v1 import (
    BASE, lire_base, interroger_pubchem, chercher_extraits
)

SORTIE = Path("data/ld50_candidats_pubchem_v2_a_verifier.csv")
JOURNAL = Path("data/ld50_requetes_pubchem_v2_log.csv")
MAX_SUBSTANCES = 5

CHAMPS = [
    "CID", "Nom_substance", "Rubrique_PubChem", "Extrait_brut",
    "LD50_mg_kg", "Espece", "Voie_exposition",
    "Source_toxicologie", "Statut_validation"
]
CHAMPS_LOG = ["CID", "Nom_substance", "Statut"]


def interroger_avec_reessais(cid, tentatives=3):
    """Réessaie les erreurs réseau temporaires, sans répéter les HTTP 4xx."""
    import urllib.error
    from scripts.enrichir_ld50_sources_v1 import interroger_pubchem
    for essai in range(1, tentatives + 1):
        try:
            return interroger_pubchem(cid)
        except urllib.error.HTTPError as erreur:
            if erreur.code in (400, 404, 422) or essai == tentatives:
                raise
        except (urllib.error.URLError, TimeoutError, OSError) as erreur:
            if essai == tentatives:
                raise
        time.sleep(2 ** essai)
    raise RuntimeError("Échec des tentatives PubChem")


def lire_csv(chemin, champs):
    if not chemin.exists():
        return []
    with chemin.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sauver_csv(chemin, champs, lignes):
    temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
    with temporaire.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(lignes)
    temporaire.replace(chemin)


def main():
    lignes, colonnes = lire_base()
    colonne_cid = "CID" if "CID" in colonnes else "PubChem_CID"

    candidats = lire_csv(SORTIE, CHAMPS)
    journal = lire_csv(JOURNAL, CHAMPS_LOG)

    deja_reussi = {
        r["CID"] for r in journal
        if r.get("Statut", "").startswith(
            ("0 extrait", "1 extrait", "2 extrait", "3 extrait",
             "4 extrait", "5 extrait", "6 extrait", "7 extrait",
             "8 extrait", "9 extrait")
        ) or r.get("Statut", "").startswith("Aucun extrait") or r.get("Statut", "") == "HTTP_404"
    }
    cids_journal = {r["CID"] for r in journal}
    cids_candidats = {
        (r["CID"], r["Rubrique_PubChem"], r["Extrait_brut"])
        for r in candidats
    }

    traites = 0
    for ligne in lignes:
        cid = (ligne.get(colonne_cid) or "").strip()
        nom = (ligne.get("Nom") or ligne.get("Nom_substance") or "").strip()

        if not cid.isdigit() or cid in deja_reussi:
            continue
        if traites >= MAX_SUBSTANCES:
            break

        print(f"Interrogation {cid} | {nom}")
        try:
            donnees = interroger_avec_reessais(cid)
            extraits = list(chercher_extraits(donnees))
            for rubrique, extrait in extraits:
                cle = (cid, rubrique, extrait)
                if cle in cids_candidats:
                    continue
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
                cids_candidats.add(cle)
            statut = (
                f"{len(extraits)} extrait(s) à vérifier"
                if extraits else "Aucun extrait LD50 détecté"
            )
        except HTTPError as e:
            statut = f"HTTP_{e.code}"
        except Exception as e:
            statut = f"ERREUR_{type(e).__name__}: {str(e)[:120]}"

        if cid in cids_journal:
            journal = [r for r in journal if r["CID"] != cid]
        journal.append({"CID": cid, "Nom_substance": nom, "Statut": statut})
        cids_journal.add(cid)

        sauver_csv(SORTIE, CHAMPS, candidats)
        sauver_csv(JOURNAL, CHAMPS_LOG, journal)
        print("  ", statut)
        traites += 1
        time.sleep(0.5)

    print("Lot terminé.")
    print("Substances interrogées pendant ce lancement :", traites)
    print("Candidats enregistrés :", len(candidats))
    print("Fichier candidats :", SORTIE)
    print("Journal :", JOURNAL)
    print("Toutes les valeurs restent à vérifier manuellement.")


if __name__ == "__main__":
    main()
