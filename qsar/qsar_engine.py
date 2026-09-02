import os
import pandas as pd

from rdkit import Chem
from rdkit.Chem import (
    Descriptors,
    Crippen,
    Lipinski,
    rdMolDescriptors
)


# =========================================================
# SENTOX-QSAR
# MOTEUR DE CALCUL DES DESCRIPTEURS MOLÉCULAIRES
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

INPUT_FILE = os.path.join(
    DATA_DIR,
    "molecules.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "descripteurs_qsar.csv"
)


# =========================================================
# CALCUL DES DESCRIPTEURS
# =========================================================

def calculer_descripteurs(smiles):

    if not smiles:
        return {
            "Masse_molaire": None,
            "LogP": None,
            "HBD": None,
            "HBA": None,
            "Atomes": None,
            "TPSA": None,
            "Anneaux": None,
            "Bonds": None,
            "Fraction_CSP3": None
        }

    try:

        mol = Chem.MolFromSmiles(
            str(smiles)
        )

    except Exception:

        mol = None

    if mol is None:

        return {
            "Masse_molaire": None,
            "LogP": None,
            "HBD": None,
            "HBA": None,
            "Atomes": None,
            "TPSA": None,
            "Anneaux": None,
            "Bonds": None,
            "Fraction_CSP3": None
        }

    return {

        "Masse_molaire":
            round(
                Descriptors.MolWt(mol),
                3
            ),

        "LogP":
            round(
                Crippen.MolLogP(mol),
                3
            ),

        "HBD":
            Lipinski.NumHDonors(mol),

        "HBA":
            Lipinski.NumHAcceptors(mol),

        "Atomes":
            mol.GetNumAtoms(),

        "TPSA":
            round(
                rdMolDescriptors.CalcTPSA(mol),
                3
            ),

        "Anneaux":
            rdMolDescriptors.CalcNumRings(mol),

        "Bonds":
            mol.GetNumBonds(),

        "Fraction_CSP3":
            round(
                rdMolDescriptors.CalcFractionCSP3(mol),
                3
            )
    }


# =========================================================
# CALCUL POUR UNE MOLÉCULE
# =========================================================

def analyser_molecule(smiles):

    descripteurs = calculer_descripteurs(
        smiles
    )

    return {

        "smiles": smiles,

        "descripteurs": descripteurs,

        "statut":
            "calculé"
            if any(
                valeur is not None
                for valeur in descripteurs.values()
            )
            else "non disponible"
    }


# =========================================================
# CALCUL POUR UNE BASE DE MOLECULES
# =========================================================

def calculer_base_qsar(
    input_file=INPUT_FILE,
    output_file=OUTPUT_FILE
):

    if not os.path.exists(input_file):

        return {
            "statut": "erreur",
            "message":
                f"Fichier introuvable : {input_file}"
        }

    try:

        df = pd.read_csv(
            input_file
        )

    except Exception as e:

        return {
            "statut": "erreur",
            "message":
                f"Impossible de lire la base : {e}"
        }

    if "SMILES" not in df.columns:

        return {
            "statut": "erreur",
            "message":
                "La colonne SMILES est absente."
        }

    resultats = []

    for smiles in df["SMILES"]:

        resultats.append(
            calculer_descripteurs(
                smiles
            )
        )

    descripteurs = pd.DataFrame(
        resultats
    )

    for colonne in descripteurs.columns:

        df[colonne] = (
            descripteurs[colonne]
        )

    try:

        df.to_csv(
            output_file,
            index=False
        )

    except Exception as e:

        return {
            "statut": "erreur",
            "message":
                f"Impossible de sauvegarder : {e}"
        }

    return {

        "statut": "calculé",

        "nombre_molecules":
            len(df),

        "fichier":
            output_file,

        "descripteurs":
            list(
                descripteurs.columns
            )
    }


# =========================================================
# TEST DIRECT
# =========================================================

if __name__ == "__main__":

    resultat = calculer_base_qsar()

    print("")
    print("===================================")
    print("        SENTOX-QSAR")
    print("===================================")

    print(
        f"Statut : {resultat.get('statut')}"
    )

    if resultat.get("nombre_molecules"):

        print(
            "Nombre de molécules : "
            f"{resultat['nombre_molecules']}"
        )

    print(
        "Fichier : "
        f"{resultat.get('fichier', '')}"
    )

    print(
        "Descripteurs : "
        f"{resultat.get('descripteurs', [])}"
    )

    print("===================================")
