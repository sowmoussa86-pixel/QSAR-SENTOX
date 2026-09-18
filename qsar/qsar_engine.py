import joblib
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors

# ==============================
# SENTOX-QSAR : moteur de base
# ==============================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "molecules.csv"
OUTPUT_FILE = BASE_DIR / "data" / "descripteurs_qsar.csv"


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
# =========================================================
# SENTOX-QSAR : PREDICTION LD50
# =========================================================

def predire_ld50_qsar(smiles):
    """
    Prédit la LD50 à partir d'un SMILES.

    IMPORTANT :
    Cette prédiction utilise le modèle QSAR prototype
    actuellement disponible dans SENTOX.
    Elle ne constitue pas une preuve expérimentale
    ni une donnée toxicologique réglementaire.
    """

    if not smiles:
        return {
            "statut": "non disponible",
            "raison": "SMILES absent"
        }

    # Calcul des descripteurs RDKit
    descripteurs = calculer_descripteurs(smiles)

    champs = [
        "Masse_molaire",
        "LogP",
        "HBD",
        "HBA",
        "Atomes",
        "TPSA",
        "Anneaux"
    ]

    if any(descripteurs.get(c) is None for c in champs):
        return {
            "statut": "non disponible",
            "raison": "Impossible de calculer les descripteurs RDKit"
        }

    # Chemin du modèle
    modele_path = BASE_DIR / "models" / "qsar_model.joblib"

    if not modele_path.exists():
        return {
            "statut": "non disponible",
            "raison": "Modèle QSAR introuvable"
        }

    # Chargement du modèle
    modele_data = joblib.load(modele_path)

    modele = modele_data["model"]
    features = modele_data["features"]

    # Vérification des variables attendues
    if not all(f in descripteurs for f in features):
        return {
            "statut": "non disponible",
            "raison": "Descripteurs requis par le modèle absents"
        }

    # Préparation des données
    X = pd.DataFrame(
        [[descripteurs[f] for f in features]],
        columns=features
    )

    # Prédiction
    prediction_log = float(
        modele.predict(X)[0]
    )

    prediction_ld50 = float(
        10 ** prediction_log
    )

    return {
        "statut": "PRÉDIT",
        "valeur": round(prediction_ld50, 3),
        "unite": "mg/kg",
        "log10_LD50": round(prediction_log, 4),
        "modele": type(modele).__name__,
        "cible": modele_data.get(
            "target",
            "log10_LD50_mg_kg"
        ),
        "n_training": modele_data.get(
            "n_training"
        ),
        "descripteurs": descripteurs,
        "commentaire": (
            "Prédiction QSAR prototype. "
            "Ne constitue pas une preuve expérimentale "
            "ou réglementaire."
        )
    }

