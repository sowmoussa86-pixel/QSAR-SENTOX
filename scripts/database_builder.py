import os
import time
import requests
import pandas as pd

# ============================================================
# SENTOX DATABASE BUILDER
# Première version : récupération de structures PubChem
# ============================================================

BASE_DIR = r"C:\SENTOX"
DATA_DIR = os.path.join(BASE_DIR, "data")

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_molecules.csv"
)

PUBCHEM_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
    "name/{}/property/"
    "MolecularFormula,MolecularWeight,XLogP,HBondDonorCount,"
    "HBondAcceptorCount,TPSA,CanonicalSMILES,IsomericSMILES/"
    "JSON"
)

# ------------------------------------------------------------
# Première liste de test
# ------------------------------------------------------------

MOLECULES_TEST = [
    "ethanol",
    "methanol",
    "acetone",
    "benzene",
    "phenol",
    "caffeine",
    "aspirin",
    "paracetamol",
    "ibuprofen",
    "glycine"
]


def rechercher_pubchem(nom):

    url = PUBCHEM_URL.format(
        requests.utils.quote(nom)
    )

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "SENTOX-QSAR/1.0"
            }
        )

        if response.status_code != 200:

            print(
                f"[ERREUR] {nom} -> "
                f"HTTP {response.status_code}"
            )

            return None

        data = response.json()

        properties = data["PropertyTable"]["Properties"][0]

        return properties

    except Exception as e:

        print(
            f"[ERREUR] {nom} -> {e}"
        )

        return None


def main():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    resultats = []

    print()
    print("=" * 60)
    print("           SENTOX DATABASE BUILDER")
    print("=" * 60)
    print()

    for i, nom in enumerate(
        MOLECULES_TEST,
        start=1
    ):

        print(
            f"[{i}/{len(MOLECULES_TEST)}] "
            f"Recherche : {nom}"
        )

        data = rechercher_pubchem(nom)

        if data is not None:

            resultats.append({

                "Nom_recherche": nom,

                "CID": data.get(
                    "CID"
                ),

                "Formule": data.get(
                    "MolecularFormula"
                ),

                "Masse_molaire": data.get(
                    "MolecularWeight"
                ),

                "LogP": data.get(
                    "XLogP"
                ),

                "HBD": data.get(
                    "HBondDonorCount"
                ),

                "HBA": data.get(
                    "HBondAcceptorCount"
                ),

                "TPSA": data.get(
                    "TPSA"
                ),

                "SMILES": data.get(
                    "ConnectivitySMILES"
                ) or data.get(
                    "CanonicalSMILES"
                )
            })

        # Petite pause pour éviter
        # des requêtes trop rapprochées
        time.sleep(0.3)

    df = pd.DataFrame(
        resultats
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 60)
    print("COLLECTE TERMINEE")
    print("=" * 60)

    print(
        f"Molécules récupérées : {len(df)}"
    )

    print(
        f"Fichier : {OUTPUT_FILE}"
    )

    print()

    if len(df) > 0:

        print(
            df[
                [
                    "Nom_recherche",
                    "CID",
                    "Formule",
                    "Masse_molaire",
                    "LogP",
                    "TPSA",
                    "SMILES"
                ]
            ].to_string(
                index=False
            )
        )


if __name__ == "__main__":

    main()