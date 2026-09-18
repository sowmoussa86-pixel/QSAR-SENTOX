import os
import pandas as pd
import unicodedata
import pandas as pd
# ============================================================
# SENTOX - RECHERCHE DANS LA BASE MOLECULAIRE 2000
# ============================================================

FICHIER_BASE_MOLECULES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "sentox_database_2000_enriched_noms.csv"
)


def normaliser_recherche(texte):
    """Normalise un texte pour faciliter la recherche."""
    if texte is None:
        return ""

    texte = str(texte).strip().lower()

    texte = unicodedata.normalize(
        "NFKD",
        texte
    ).encode(
        "ascii",
        "ignore"
    ).decode(
        "ascii"
    )

    return texte


def rechercher_molecule_sentox(nom_recherche):
    """
    Recherche une molécule dans la base SENTOX 2000.
    
    Recherche dans :
    - Nom
    - Nom_PubChem
    - IUPAC_Name_PubChem
    - CID
    """

    if not nom_recherche:
        return None

    if not os.path.exists(FICHIER_BASE_MOLECULES):
        return None

    try:
        df = pd.read_csv(
            FICHIER_BASE_MOLECULES,
            low_memory=False
        )

        recherche = normaliser_recherche(nom_recherche)

        colonnes_recherche = [
            "Nom",
            "Nom_PubChem",
            "IUPAC_Name_PubChem",
            "CID"
        ]

        colonnes_recherche = [
            c for c in colonnes_recherche
            if c in df.columns
        ]

        for colonne in colonnes_recherche:

            valeurs = (
                df[colonne]
                .fillna("")
                .astype(str)
                .map(normaliser_recherche)
            )

            # Correspondance exacte
            masque = valeurs == recherche

            if masque.any():
                ligne = df.loc[masque].iloc[0]
                return ligne.to_dict()

        # ----------------------------------------------------
        # Recherche partielle si aucune correspondance exacte
        # ----------------------------------------------------

        for colonne in colonnes_recherche:

            valeurs = (
                df[colonne]
                .fillna("")
                .astype(str)
                .map(normaliser_recherche)
            )

            masque = valeurs.str.contains(
                recherche,
                regex=False,
                na=False
            )

            if masque.any():
                ligne = df.loc[masque].iloc[0]
                return ligne.to_dict()

        return None

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
# =========================================================
# SENTOX - PREDICTION QSAR AUTOMATIQUE
# SMILES -> RDKit -> 7 descripteurs -> Random Forest
# =========================================================

def predire_ld50_qsar(smiles):
    """
    Prédit la LD50 à partir d'un SMILES.

    Retourne :
        - statut
        - descripteurs utilisés
        - log10_LD50
        - LD50_mg_kg
    """

    try:
        import os
        import math
        import joblib
        import pandas as pd

        # -------------------------------------------------
        # Vérification du SMILES
        # -------------------------------------------------

        if not smiles:
            return {
                "statut": "erreur",
                "message": "SMILES absent."
            }

        # -------------------------------------------------
        # Calcul des descripteurs RDKit
        # -------------------------------------------------

        descripteurs = calculer_descripteurs(smiles)

        if not descripteurs:
            return {
                "statut": "erreur",
                "message": "Impossible de calculer les descripteurs."
            }

        # -------------------------------------------------
        # Chargement du modèle
        # -------------------------------------------------

        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        fichier_modele = os.path.join(
            base_dir,
            "models",
            "qsar_model.joblib"
        )

        if not os.path.exists(fichier_modele):
            return {
                "statut": "erreur",
                "message": "Modèle QSAR introuvable."
            }

        modele = joblib.load(fichier_modele)

        # -------------------------------------------------
        # Vérification du modèle
        # -------------------------------------------------

        model = modele["model"]
        features = modele["features"]

        # -------------------------------------------------
        # Construction du vecteur avec les mêmes noms
        # -------------------------------------------------

        valeurs = {}

        for feature in features:

            if feature not in descripteurs:
                return {
                    "statut": "erreur",
                    "message": (
                        f"Descripteur absent : {feature}"
                    )
                }

            valeurs[feature] = descripteurs[feature]

        X = pd.DataFrame(
            [valeurs],
            columns=features
        )

        # -------------------------------------------------
        # Prédiction
        # -------------------------------------------------

        prediction_log = float(
            model.predict(X)[0]
        )

        prediction_ld50 = float(
            10 ** prediction_log
        )

        # -------------------------------------------------
        # Résultat
        # -------------------------------------------------

        return {
            "statut": "succes",
            "smiles": smiles,
            "features": features,
            "descripteurs": valeurs,
            "log10_LD50_mg_kg": prediction_log,
            "LD50_mg_kg": prediction_ld50,
            "n_training": modele.get("n_training"),
            "type_modele": type(model).__name__,
            "avertissement": (
                "Prédiction QSAR expérimentale. "
                "Le modèle actuel doit être validé et "
                "renforcé avec davantage de données."
            )
        }

    except Exception as e:

        return {
            "statut": "erreur",
            "message": f"Erreur prédiction QSAR : {e}"
        }