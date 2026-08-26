import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors

# ==============================
# SENTOX-QSAR : moteur de base
# ==============================

INPUT_FILE = r"C:\SENTOX\data\molecules.csv"
OUTPUT_FILE = r"C:\SENTOX\data\descripteurs_qsar.csv"


def calculer_descripteurs(smiles):
    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return {
            "Masse_molaire": None,
            "LogP": None,
            "HBD": None,
            "HBA": None,
            "Atomes": None,
            "TPSA": None,
            "Anneaux": None
        }

    return {
        "Masse_molaire": round(Descriptors.MolWt(mol), 3),
        "LogP": round(Crippen.MolLogP(mol), 3),
        "HBD": Lipinski.NumHDonors(mol),
        "HBA": Lipinski.NumHAcceptors(mol),
        "Atomes": mol.GetNumAtoms(),
        "TPSA": round(rdMolDescriptors.CalcTPSA(mol), 3),
        "Anneaux": rdMolDescriptors.CalcNumRings(mol)
    }


# Lecture de la base
df = pd.read_csv(INPUT_FILE)

print("\n===================================")
print("        SENTOX-QSAR")
print("===================================")
print(f"Nombre de molécules : {len(df)}")

# Calcul des descripteurs
resultats = df["SMILES"].apply(calculer_descripteurs)

descripteurs = pd.DataFrame(resultats.tolist())

# Remplacement des anciennes valeurs par les calculs RDKit
for colonne in descripteurs.columns:
    df[colonne] = descripteurs[colonne]

# Sauvegarde
df.to_csv(OUTPUT_FILE, index=False)

print("\nDescripteurs calculés avec RDKit.")
print(f"Fichier créé : {OUTPUT_FILE}")

print("\nAperçu :")
print(
    df[
        [
            "ID",
            "Nom",
            "SMILES",
            "Masse_molaire",
            "LogP",
            "HBD",
            "HBA",
            "Atomes",
            "TPSA",
            "Anneaux"
        ]
    ].head(10).to_string(index=False)
)

print("\n===================================")
print("SENTOX-QSAR : CALCUL TERMINE")
print("===================================")