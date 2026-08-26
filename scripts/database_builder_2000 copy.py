import os
import time
import requests
import pandas as pd

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski


# ============================================================
# SENTOX DATABASE BUILDER 2000
# ============================================================

BASE_DIR = r"C:\SENTOX"
DATA_DIR = os.path.join(BASE_DIR, "data")

MASTER_FILE = os.path.join(
    DATA_DIR,
    "molecules_master.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000.csv"
)


PUBCHEM_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
    "name/{}/property/"
    "MolecularFormula,MolecularWeight,XLogP,"
    "HBondDonorCount,HBondAcceptorCount,TPSA,"
    "CanonicalSMILES,IsomericSMILES/JSON"
)


# ============================================================
# PUBCHEM
# ============================================================

def rechercher_pubchem(nom):

    url = PUBCHEM_URL.format(
        requests.utils.quote(nom)
    )

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent":
                "SENTOX-QSAR/2.0"
            }
        )

        if response.status_code != 200:

            print(
                f"  [NON TROUVE] {nom}"
            )

            return None

        data = response.json()

        return data[
            "PropertyTable"
        ]["Properties"][0]

    except Exception as e:

        print(
            f"  [ERREUR] {nom} : {e}"
        )

        return None


# ============================================================
# RDKit
# ============================================================

def calculer_rdkit(smiles):

    if not smiles:
        return None

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return None

    return {

        "RDKit_Masse_molaire":
            round(
                Descriptors.MolWt(mol),
                4
            ),

        "RDKit_LogP":
            round(
                Crippen.MolLogP(mol),
                4
            ),

        "RDKit_HBD":
            Lipinski.NumHDonors(mol),

        "RDKit_HBA":
            Lipinski.NumHAcceptors(mol),

        "RDKit_TPSA":
            round(
                Descriptors.TPSA(mol),
                4
            ),

        "Atomes":
            mol.GetNumAtoms(),

        "Atomes_lourds":
            Lipinski.HeavyAtomCount(mol),

        "Anneaux":
            Lipinski.RingCount(mol),

        "Liaisons_rotatables":
            Lipinski.NumRotatableBonds(mol)
    }


# ============================================================
# CHARGEMENT DE LA LISTE
# ============================================================

def charger_master():

    if not os.path.exists(MASTER_FILE):

        print(
            "ERREUR : fichier master introuvable :"
        )

        print(MASTER_FILE)

        return None

    df = pd.read_csv(
        MASTER_FILE,
        encoding="utf-8-sig"
    )

    colonnes_obligatoires = [
        "Nom",
        "Categorie",
        "Plante",
        "Partie_utilisee"
    ]

    for colonne in colonnes_obligatoires:

        if colonne not in df.columns:

            print(
                f"ERREUR : colonne manquante : "
                f"{colonne}"
            )

            return None

    df = df.dropna(
        subset=["Nom"]
    )

    df["Nom"] = (
        df["Nom"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["Nom"] != ""
    ]

    df = df.drop_duplicates(
        subset=["Nom"]
    )

    return df


# ============================================================
# CONSTRUCTION
# ============================================================

def main():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    master = charger_master()

    if master is None:
        return

    print()
    print("=" * 70)
    print("          SENTOX DATABASE BUILDER 2000")
    print("=" * 70)

    print()
    print(
        f"Molécules dans la liste : "
        f"{len(master)}"
    )

    resultats = []

    for i, row in master.iterrows():

        nom = row["Nom"]
        categorie = row["Categorie"]

        print(
            f"[{i + 1}/{len(master)}] "
            f"{nom}"
        )

        pubchem = rechercher_pubchem(
            nom
        )

        if pubchem is None:

            continue

        smiles = (
            pubchem.get(
                "ConnectivitySMILES"
            )
            or
            pubchem.get(
                "CanonicalSMILES"
            )
            or
            pubchem.get(
                "IsomericSMILES"
            )
        )

        rdkit = calculer_rdkit(
            smiles
        )

        if rdkit is None:

            print(
                "  [ATTENTION] "
                "SMILES non exploitable"
            )

            continue

        resultat = {

            "Nom":
                nom,

            "Categorie":
                categorie,

            "CID":
                pubchem.get("CID"),

            "Formule":
                pubchem.get(
                    "MolecularFormula"
                ),

            "Masse_molaire":
                pubchem.get(
                    "MolecularWeight"
                ),

            "LogP":
                pubchem.get(
                    "XLogP"
                ),

            "HBD":
                pubchem.get(
                    "HBondDonorCount"
                ),

            "HBA":
                pubchem.get(
                    "HBondAcceptorCount"
                ),

            "TPSA":
                pubchem.get(
                    "TPSA"
                ),

            "SMILES":
                smiles,

            "Source_structure":
                "PubChem",

            "LD50_mg_kg":
                "",

            "LogLD50":
                "",

            "Toxicite":
                "",

            "Source_toxicologie":
                "",

            "Plante":
                row["Plante"],

            "Partie_utilisee":
                row["Partie_utilisee"],

            "Source_plante":
                "",

            "Statut_donnee":
                "Structure disponible"
        }

        resultat.update(
            rdkit
        )

        resultats.append(
            resultat
        )

        time.sleep(0.3)

    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        resultats
    )

    if len(df) == 0:

        print()
        print(
            "Aucune molécule récupérée."
        )

        return

    # --------------------------------------------------------
    # Suppression des doublons
    # --------------------------------------------------------

    if "CID" in df.columns:

        df = df.drop_duplicates(
            subset=["CID"],
            keep="first"
        )

    # --------------------------------------------------------
    # Tri
    # --------------------------------------------------------

    df = df.sort_values(
        by="Nom"
    )

    # --------------------------------------------------------
    # Sauvegarde
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # RAPPORT
    # ========================================================

    print()
    print("=" * 70)
    print("              CONSTRUCTION TERMINEE")
    print("=" * 70)

    print(
        f"Molécules récupérées : "
        f"{len(df)}"
    )

    print(
        f"Fichier : "
        f"{OUTPUT_FILE}"
    )

    print()

    print(
        "Répartition par catégorie :"
    )

    print(
        df["Categorie"]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "SENTOX DATABASE : OK"
    )


if __name__ == "__main__":

    main()