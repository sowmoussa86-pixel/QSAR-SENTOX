import os
import time
import requests
import pandas as pd

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski


# ============================================================
# SENTOX - DATABASE BUILDER V2
# Base moléculaire pour SENTOX-QSAR
# ============================================================

BASE_DIR = r"C:\SENTOX"
DATA_DIR = os.path.join(BASE_DIR, "data")

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_v2.csv"
)

# ------------------------------------------------------------
# LISTE INITIALE
# Elle sera progressivement remplacée par la liste 2000
# ------------------------------------------------------------

MOLECULES = [

    # Solvants / industriels
    ("Ethanol", "Industrial"),
    ("Methanol", "Industrial"),
    ("Acetone", "Industrial"),
    ("Benzene", "Industrial"),
    ("Toluene", "Industrial"),
    ("Phenol", "Industrial"),

    # Médicaments
    ("Aspirin", "Drug"),
    ("Paracetamol", "Drug"),
    ("Ibuprofen", "Drug"),
    ("Caffeine", "Drug"),
    ("Isoniazid", "Drug"),

    # Acides aminés
    ("Glycine", "Amino_acid"),
    ("Alanine", "Amino_acid"),
    ("Valine", "Amino_acid"),
    ("Leucine", "Amino_acid"),

    # Plantes médicinales
    # Les composés seront ajoutés progressivement
    ("Quercetin", "Medicinal_plant_compound"),
    ("Kaempferol", "Medicinal_plant_compound"),
    ("Rutin", "Medicinal_plant_compound"),
    ("Catechin", "Medicinal_plant_compound"),
    ("Epicatechin", "Medicinal_plant_compound"),
]


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
                "User-Agent": "SENTOX-QSAR/2.0"
            }
        )

        if response.status_code != 200:

            print(
                f"  [ATTENTION] {nom} "
                f"non trouvé - HTTP {response.status_code}"
            )

            return None

        data = response.json()

        return data["PropertyTable"]["Properties"][0]

    except Exception as e:

        print(
            f"  [ERREUR] {nom} : {e}"
        )

        return None


# ============================================================
# RDKit
# ============================================================

def calculer_descripteurs(smiles):

    if not smiles:
        return None

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:

        return None

    try:

        return {

            "RDKit_Masse_molaire":
                round(Descriptors.MolWt(mol), 4),

            "RDKit_LogP":
                round(Crippen.MolLogP(mol), 4),

            "RDKit_HBD":
                Lipinski.NumHDonors(mol),

            "RDKit_HBA":
                Lipinski.NumHAcceptors(mol),

            "RDKit_TPSA":
                round(Descriptors.TPSA(mol), 4),

            "Atomes":
                mol.GetNumAtoms(),

            "Atomes_lourds":
                Lipinski.HeavyAtomCount(mol),

            "Anneaux":
                Lipinski.RingCount(mol),

            "Liaisons_rotatables":
                Lipinski.NumRotatableBonds(mol)
        }

    except Exception as e:

        print(
            f"  [RDKit ERREUR] {e}"
        )

        return None


# ============================================================
# CONSTRUCTION
# ============================================================

def main():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    resultats = []

    print()
    print("=" * 70)
    print("              SENTOX DATABASE BUILDER V2")
    print("=" * 70)
    print()

    print(
        f"Nombre de molécules à traiter : "
        f"{len(MOLECULES)}"
    )

    print()

    for index, (nom, categorie) in enumerate(
        MOLECULES,
        start=1
    ):

        print(
            f"[{index}/{len(MOLECULES)}] {nom}"
        )

        pubchem = rechercher_pubchem(
            nom
        )

        if pubchem is None:
            continue

        smiles = (
            pubchem.get("ConnectivitySMILES")
            or
            pubchem.get("CanonicalSMILES")
            or
            pubchem.get("IsomericSMILES")
        )

        rdkit_data = calculer_descripteurs(
            smiles
        )

        if rdkit_data is None:

            print(
                "  [ATTENTION] "
                "SMILES non exploitable par RDKit"
            )

            continue

        ligne = {

            "Nom": nom,

            "Categorie": categorie,

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
                "",

            "Partie_utilisee":
                "",

            "Source_plante":
                "",

            "Statut_donnee":
                "Structure disponible"
        }

        ligne.update(
            rdkit_data
        )

        resultats.append(
            ligne
        )

        time.sleep(0.3)

    # --------------------------------------------------------
    # SAUVEGARDE
    # --------------------------------------------------------

    df = pd.DataFrame(
        resultats
    )

    # Supprimer les doublons CID
    if "CID" in df.columns:

        df = df.drop_duplicates(
            subset=["CID"],
            keep="first"
        )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 70)
    print("             CONSTRUCTION TERMINEE")
    print("=" * 70)

    print(
        f"Molécules enregistrées : {len(df)}"
    )

    print(
        f"Fichier : {OUTPUT_FILE}"
    )

    print()

    print(
        "Colonnes disponibles :"
    )

    for colonne in df.columns:

        print(
            f" - {colonne}"
        )

    print()
    print(
        "SENTOX DATABASE V2 : OK"
    )


if __name__ == "__main__":

    main()