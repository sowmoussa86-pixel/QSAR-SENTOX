
import time
from pathlib import Path

import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qsar.sentox_pubchem import rechercher_pubchem
from qsar.sentox_toxicity_search import rechercher_dl50_pubchem


FICHIER_SOURCE = Path("data/sentox_database_2000_enriched_noms.csv")
FICHIER_SORTIE = Path("data/test_dl50_10_substances.csv")
NOMBRE_TEST = 10


def rechercher_substance(nom):
    nom = str(nom).strip()

    if not nom or nom.lower() == "nan":
        return [{
            "nom_recherche": nom,
            "statut": "NOM_INDISPONIBLE",
        }]

    try:
        identification = rechercher_pubchem(nom)
    except Exception as exc:
        return [{
            "nom_recherche": nom,
            "statut": "ERREUR_IDENTIFICATION",
            "message": str(exc),
        }]

    cid = identification.get("CID")

    if identification.get("statut") != "DOCUMENTE" or not cid:
        return [{
            "nom_recherche": nom,
            "statut": "CID_NON_TROUVE",
            "source_identification": identification.get("source", ""),
            "message": identification.get("message", ""),
        }]

    try:
        resultats = rechercher_dl50_pubchem(cid)
    except Exception as exc:
        return [{
            "nom_recherche": nom,
            "CID": cid,
            "statut": "ERREUR_TOXICITE",
            "message": str(exc),
        }]

    for resultat in resultats:
        resultat["nom_recherche"] = nom
        resultat["source_identification"] = identification.get("source", "")

    return resultats


def main():
    if not FICHIER_SOURCE.exists():
        print(f"Fichier source introuvable : {FICHIER_SOURCE}")
        return

    df = pd.read_csv(FICHIER_SOURCE)

    if "Nom_PubChem" not in df.columns:
        print("Colonne Nom_PubChem absente de la base.")
        return

    noms = (
        df["Nom_PubChem"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    noms = noms[noms != ""].drop_duplicates().head(NOMBRE_TEST)

    if noms.empty:
        print("Aucun nom chimique disponible pour le test.")
        return

    toutes_les_lignes = []

    for numero, nom in enumerate(noms, start=1):
        print(f"[{numero}/{len(noms)}] Recherche : {nom}")
        lignes = rechercher_substance(nom)
        toutes_les_lignes.extend(lignes)

        nb_dl50 = sum(
            1 for ligne in lignes
            if ligne.get("DL50_brute")
        )
        print(f"    Valeurs DL50 extraites : {nb_dl50}")

        # Pause entre les substances pour limiter les requêtes.
        time.sleep(1)

    resultat = pd.DataFrame(toutes_les_lignes)
    resultat.to_csv(
        FICHIER_SORTIE,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n--- BILAN DU TEST ---")
    print(f"Substances testées : {len(noms)}")
    print(f"Lignes enregistrées : {len(resultat)}")
    print(
        "Substances avec DL50 extraite : "
        f"{resultat.loc[resultat.get('DL50_brute', pd.Series(index=resultat.index, dtype=object)).notna(), 'nom_recherche'].nunique()}"
        if "DL50_brute" in resultat.columns
        else "Substances avec DL50 extraite : 0"
    )
    print(f"Fichier créé : {FICHIER_SORTIE}")


if __name__ == "__main__":
    main()
