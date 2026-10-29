
import sys
import time
from pathlib import Path

import pandas as pd

# Permet d'importer les modules du dossier web/qsar
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qsar.sentox_toxicity_search import rechercher_dl50_pubchem


FICHIER_SOURCE = Path("data/sentox_database_2000_enriched_noms.csv")
FICHIER_SORTIE = Path("data/dl50_pubchem_2000_resultats.csv")
FICHIER_ERREURS = Path("data/dl50_pubchem_2000_erreurs.csv")

# Premier essai : 50 entrées. Nous augmenterons ensuite si le test est fiable.
NOMBRE_MAX = 200
PAUSE_SECONDES = 1


def main():
    if not FICHIER_SOURCE.exists():
        print("ERREUR : fichier source introuvable :", FICHIER_SOURCE)
        return

    source = pd.read_csv(FICHIER_SOURCE)

    colonnes_requises = {"Nom_PubChem", "CID"}
    if not colonnes_requises.issubset(source.columns):
        print("ERREUR : colonnes Nom_PubChem et/ou CID manquantes.")
        return

    # Chargement des résultats précédents pour permettre la reprise.
    if FICHIER_SORTIE.exists():
        anciens = pd.read_csv(FICHIER_SORTIE)
        deja_traites = set(
            pd.to_numeric(anciens.get("CID_base"), errors="coerce")
            .dropna()
            .astype(int)
        )
        lignes = anciens.to_dict("records")
        print("Résultats existants chargés :", len(lignes))
    else:
        deja_traites = set()
        lignes = []

    # Sélection des entrées dont le CID n'a pas encore été traité.
    candidats = source[source["CID"].notna()].copy()
    candidats["CID"] = pd.to_numeric(candidats["CID"], errors="coerce")
    candidats = candidats[candidats["CID"].notna()]
    candidats["CID"] = candidats["CID"].astype(int)
    candidats = candidats[~candidats["CID"].isin(deja_traites)]

    candidats = candidats.head(NOMBRE_MAX)

    if candidats.empty:
        print("Aucune nouvelle entrée à traiter dans ce lot.")
        print("Les CID présents dans le fichier de résultats sont déjà traités.")
        return

    erreurs = []

    print("Entrées à traiter dans ce lot :", len(candidats))

    for numero, (_, ligne) in enumerate(candidats.iterrows(), start=1):
        nom = str(ligne["Nom_PubChem"])
        cid = int(ligne["CID"])

        print(f"[{numero}/{len(candidats)}] {nom} | CID {cid}")

        try:
            resultats = rechercher_dl50_pubchem(cid)

            if resultats:
                for resultat in resultats:
                    resultat["nom_recherche"] = nom
                    resultat["CID_base"] = cid
                    resultat["statut_recherche"] = (
                        "RESULTATS_EXTRAITS"
                        if resultat.get("DL50_brute")
                        else "AUCUNE_DL50_EXTRAITE"
                    )
                    lignes.append(resultat)

                print("    Lignes extraites :", len(resultats))

            else:
                lignes.append({
                    "nom_recherche": nom,
                    "CID_base": cid,
                    "statut": "NON_TROUVE",
                    "statut_recherche": "AUCUNE_DL50_EXTRAITE",
                    "message": (
                        "Aucune DL50 extraite par les règles actuelles. "
                        "Cela ne prouve pas l'absence de données ailleurs."
                    ),
                })
                print("    Aucune DL50 extraite")

        except Exception as erreur:
            enregistrement_erreur = {
                "nom_recherche": nom,
                "CID_base": cid,
                "statut_recherche": "ERREUR",
                "message_erreur": str(erreur),
            }
            erreurs.append(enregistrement_erreur)

            # Une erreur est enregistrée séparément pour permettre une reprise.
            lignes.append(enregistrement_erreur)
            print("    ERREUR :", erreur)

        # Sauvegarde après chaque entrée pour limiter la perte de données.
        pd.DataFrame(lignes).to_csv(
            FICHIER_SORTIE,
            index=False,
            encoding="utf-8-sig",
        )

        if erreurs:
            pd.DataFrame(erreurs).to_csv(
                FICHIER_ERREURS,
                index=False,
                encoding="utf-8-sig",
            )

        time.sleep(PAUSE_SECONDES)

    resultat_final = pd.DataFrame(lignes)

    print("\n--- BILAN DU LOT ---")
    print("Entrées traitées dans ce lancement :", len(candidats))
    print("Lignes dans le fichier :", len(resultat_final))
    print("Erreurs de recherche dans ce lancement :", len(erreurs))
    print("Fichier de résultats :", FICHIER_SORTIE)

    if "statut_recherche" in resultat_final.columns:
        print("\nRépartition des statuts :")
        print(resultat_final["statut_recherche"].value_counts().to_string())


if __name__ == "__main__":
    main()
