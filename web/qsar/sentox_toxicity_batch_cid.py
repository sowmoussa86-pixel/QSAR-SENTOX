
import time
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qsar.sentox_toxicity_search import rechercher_dl50_pubchem

FICHIER_SOURCE = Path("data/sentox_database_2000_enriched_noms.csv")
FICHIER_SORTIE = Path("data/test_dl50_10_cid.csv")
NOMBRE_TEST = 10


def main():
    df = pd.read_csv(FICHIER_SOURCE)

    if not {"Nom_PubChem", "CID"}.issubset(df.columns):
        print("Colonnes Nom_PubChem ou CID manquantes.")
        return

    echantillon = df[["Nom_PubChem", "CID"]].head(NOMBRE_TEST)
    lignes = []

    for numero, (_, ligne) in enumerate(echantillon.iterrows(), start=1):
        nom = str(ligne["Nom_PubChem"])
        cid = int(ligne["CID"])

        print(f"[{numero}/{len(echantillon)}] {nom} | CID {cid}")

        try:
            resultats = rechercher_dl50_pubchem(cid)

            if resultats:
                for resultat in resultats:
                    resultat["nom_recherche"] = nom
                    resultat["CID_base"] = cid
                    resultat["statut_recherche"] = "RESULTATS_EXTRAITS"
                    lignes.append(resultat)
                print(f"    Résultats extraits : {len(resultats)}")
            else:
                lignes.append({
                    "nom_recherche": nom,
                    "CID_base": cid,
                    "statut_recherche": "AUCUNE_DL50_EXTRAITE",
                })
                print("    Aucune DL50 extraite")

        except Exception as erreur:
            lignes.append({
                "nom_recherche": nom,
                "CID_base": cid,
                "statut_recherche": "ERREUR",
                "message_erreur": str(erreur),
            })
            print(f"    Erreur : {erreur}")

        time.sleep(1)

    resultat = pd.DataFrame(lignes)
    resultat.to_csv(FICHIER_SORTIE, index=False, encoding="utf-8-sig")

    print("\n--- BILAN ---")
    print("Substances testées :", len(echantillon))
    print("Lignes enregistrées :", len(resultat))
    print("Fichier créé :", FICHIER_SORTIE)

    if "statut_recherche" in resultat.columns:
        print(resultat["statut_recherche"].value_counts().to_string())


if __name__ == "__main__":
    main()