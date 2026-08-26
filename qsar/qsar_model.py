import os
import sys
import pandas as pd
import numpy as np

from joblib import dump
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# SENTOX-QSAR
# Module d'apprentissage automatique toxicologique
# ============================================================

BASE_DIR = r"C:\SENTOX"
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

INPUT_FILE = os.path.join(DATA_DIR, "descripteurs_qsar.csv")
OUTPUT_MODEL = os.path.join(MODEL_DIR, "qsar_model.joblib")

# Nombre minimum recommandé pour commencer un modèle
MIN_MOLECULES = 10


# ============================================================
# AFFICHAGE
# ============================================================

def titre():
    print("=" * 60)
    print("              SENTOX-QSAR : MODELE ML")
    print("=" * 60)


# ============================================================
# VERIFICATION DU FICHIER
# ============================================================

def verifier_fichier():

    if not os.path.exists(INPUT_FILE):

        print()
        print("ERREUR : fichier introuvable.")
        print(f"Fichier attendu : {INPUT_FILE}")
        print()

        return False

    return True


# ============================================================
# LECTURE DE LA BASE
# ============================================================

def charger_base():

    try:

        df = pd.read_csv(
            INPUT_FILE,
            sep=",",
            encoding="utf-8-sig"
        )

    except Exception as e:

        print()
        print("ERREUR lors de la lecture du fichier CSV :")
        print(e)
        print()

        return None

    # Nettoyage des noms de colonnes
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
    )

    return df


# ============================================================
# VERIFICATION DES COLONNES
# ============================================================

def verifier_colonnes(df):

    colonnes_requises = [
        "ID",
        "Nom",
        "SMILES",
        "LD50_mg_kg"
    ]

    print()
    print("Colonnes détectées :")

    for colonne in df.columns:
        print(" -", colonne)

    print()

    manquantes = [
        colonne
        for colonne in colonnes_requises
        if colonne not in df.columns
    ]

    if manquantes:

        print("ERREUR : colonnes manquantes :")

        for colonne in manquantes:
            print(" -", colonne)

        print()
        print("Le fichier doit contenir au minimum :")
        print(",".join(colonnes_requises))
        print()

        return False

    return True


# ============================================================
# PREPARATION DES DONNEES
# ============================================================

def preparer_donnees(df):

    # Conversion numérique robuste
    df["LD50_mg_kg"] = pd.to_numeric(
        df["LD50_mg_kg"],
        errors="coerce"
    )

    # Conversion des descripteurs
    descripteurs = [
        "Masse_molaire",
        "LogP",
        "HBD",
        "HBA",
        "Atomes",
        "TPSA",
        "Anneaux"
    ]

    for colonne in descripteurs:

        if colonne in df.columns:

            df[colonne] = pd.to_numeric(
                df[colonne],
                errors="coerce"
            )

    return df


# ============================================================
# SELECTION DES VARIABLES
# ============================================================

def obtenir_variables(df):

    variables = [
        "Masse_molaire",
        "LogP",
        "HBD",
        "HBA",
        "Atomes",
        "TPSA",
        "Anneaux"
    ]

    variables_disponibles = [
        colonne
        for colonne in variables
        if colonne in df.columns
    ]

    return variables_disponibles


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    titre()

    # --------------------------------------------------------
    # Vérification
    # --------------------------------------------------------

    if not verifier_fichier():
        return

    # --------------------------------------------------------
    # Lecture
    # --------------------------------------------------------

    df = charger_base()

    if df is None:
        return

    print(f"Nombre total de molécules : {len(df)}")

    # --------------------------------------------------------
    # Colonnes
    # --------------------------------------------------------

    if not verifier_colonnes(df):
        return

    # --------------------------------------------------------
    # Préparation
    # --------------------------------------------------------

    df = preparer_donnees(df)

    # --------------------------------------------------------
    # Compter les données toxicologiques
    # --------------------------------------------------------

    nb_tox = df["LD50_mg_kg"].notna().sum()

    print(
        f"Molécules avec données toxicologiques : {nb_tox}"
    )

    # --------------------------------------------------------
    # Données insuffisantes
    # --------------------------------------------------------

    if nb_tox < MIN_MOLECULES:

        print()
        print("ATTENTION : données insuffisantes")
        print(
            f"Minimum recommandé pour ce prototype : "
            f"{MIN_MOLECULES}"
        )

        print()
        print(
            "Le modèle n'est PAS entraîné afin d'éviter "
            "une prédiction artificiellement peu fiable."
        )

        print()
        print(
            "Ajoutez davantage de valeurs LD50_mg_kg "
            "documentées dans molecules.csv."
        )

        print()
        print("Le moteur SENTOX-QSAR reste opérationnel.")
        print()

        return

    # --------------------------------------------------------
    # Variables
    # --------------------------------------------------------

    variables = obtenir_variables(df)

    if len(variables) < 3:

        print()
        print(
            "ERREUR : pas assez de descripteurs disponibles."
        )

        return

    print()
    print("Descripteurs utilisés :")

    for variable in variables:
        print(" -", variable)

    # --------------------------------------------------------
    # Sous-base propre
    # --------------------------------------------------------

    colonnes = variables + ["LD50_mg_kg"]

    data = df[colonnes].dropna()

    print()
    print(
        f"Molécules utilisables pour le ML : {len(data)}"
    )

    if len(data) < MIN_MOLECULES:

        print()
        print(
            "ATTENTION : trop peu de lignes complètes "
            "après nettoyage."
        )

        return

    # --------------------------------------------------------
    # X et y
    # --------------------------------------------------------

    X = data[variables]

    # Transformation logarithmique de la LD50
    # afin de réduire l'effet des valeurs extrêmes
    y = np.log10(data["LD50_mg_kg"])

    # --------------------------------------------------------
    # Séparation apprentissage / test
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    print()
    print("Apprentissage du modèle...")
    
    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    modele = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    modele.fit(X_train, y_train)

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    prediction = modele.predict(X_test)

    mae = mean_absolute_error(y_test, prediction)
    rmse = np.sqrt(mean_squared_error(y_test, prediction))
    r2 = r2_score(y_test, prediction)

    print()
    print("=" * 60)
    print("RESULTATS DU MODELE")
    print("=" * 60)

    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

    # --------------------------------------------------------
    # Validation croisée
    # --------------------------------------------------------

    if len(data) >= 15:

        print()
        print("Validation croisée...")

        folds = min(5, len(data))

        cv = KFold(
            n_splits=folds,
            shuffle=True,
            random_state=42
        )

        scores = cross_val_score(
            modele,
            X,
            y,
            cv=cv,
            scoring="r2"
        )

        print(
            f"R² moyen CV : {scores.mean():.4f}"
        )

        print(
            f"Écart-type CV : {scores.std():.4f}"
        )

    # --------------------------------------------------------
    # Création du dossier modèle
    # --------------------------------------------------------

    os.makedirs(MODEL_DIR, exist_ok=True)

    # --------------------------------------------------------
    # Sauvegarde
    # --------------------------------------------------------

    package = {
        "model": modele,
        "features": variables,
        "target": "log10_LD50_mg_kg",
        "n_training": len(data)
    }

    dump(package, OUTPUT_MODEL)

    print()
    print("=" * 60)
    print("MODELE SENTOX-QSAR ENREGISTRE")
    print("=" * 60)

    print()
    print(f"Fichier : {OUTPUT_MODEL}")

    print()
    print("ATTENTION :")
    print(
        "Ce modèle est un prototype de recherche."
    )

    print(
        "Il ne doit pas être utilisé seul pour "
        "une décision clinique ou réglementaire."
    )

    print()
    print("FIN DU PROGRAMME")
    print("=" * 60)


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print("Programme interrompu par l'utilisateur.")

    except Exception as e:

        print()
        print("=" * 60)
        print("ERREUR NON PREVUE")
        print("=" * 60)
        print(type(e).__name__, ":", e)
        print()
        print(
            "Vérifiez molecules.csv et les colonnes "
            "descripteurs."
        )