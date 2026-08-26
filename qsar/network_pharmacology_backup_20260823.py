# ============================================================
# SENTOX - NETWORK PHARMACOLOGY ENGINE
# QSAR MULTICOMPOSES / PHARMACOLOGIE DE RESEAU
# ============================================================

import os
import math
import pandas as pd
import numpy as np

# ------------------------------------------------------------
# CHEMISTRY
# ------------------------------------------------------------

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors
    RDKIT_OK = True
except ImportError:
    RDKIT_OK = False


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = r"C:\SENTOX"

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

INPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000_enriched.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_network_results.csv"
)


# ------------------------------------------------------------
# TARGET DATABASE
# ------------------------------------------------------------
# Première version : cibles fonctionnelles.
# Elles seront ensuite remplacées/enrichies par les données
# expérimentales ou les prédictions de SwissTargetPrediction.

TARGETS = {

    "diabete": [
        "alpha-glucosidase",
        "alpha-amylase",
        "DPP-4",
        "PPAR-gamma",
        "AMPK",
        "GLUT4"
    ],

    "inflammation": [
        "COX-1",
        "COX-2",
        "5-LOX",
        "NF-kB",
        "TNF-alpha",
        "IL-6"
    ],

    "oxydation": [
        "Nrf2",
        "ROS",
        "SOD",
        "CAT",
        "GPx"
    ],

    "foie": [
        "CYP3A4",
        "CYP2D6",
        "CYP2C9",
        "Nrf2"
    ]
}


# ------------------------------------------------------------
# KEYWORDS / COMPOUND FAMILIES
# ------------------------------------------------------------

COMPOUND_FAMILIES = {

    "flavonoide": [
        "quercetin",
        "kaempferol",
        "rutin",
        "catechin",
        "epicatechin"
    ],

    "polyphenol": [
        "phenol",
        "gallic",
        "caffeic",
        "chlorogenic",
        "ferulic"
    ],

    "acide_organique": [
        "acid"
    ],

    "amine": [
        "amine"
    ]
}


# ------------------------------------------------------------
# UTILITIES
# ------------------------------------------------------------

def safe_float(value):

    try:

        if pd.isna(value):
            return np.nan

        return float(value)

    except:

        return np.nan


def normalize_column_names(df):

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    return df


# ------------------------------------------------------------
# MOLECULAR VALIDATION
# ------------------------------------------------------------

def validate_smiles(smiles):

    if not RDKIT_OK:
        return False

    if pd.isna(smiles):
        return False

    try:

        mol = Chem.MolFromSmiles(
            str(smiles)
        )

        return mol is not None

    except:

        return False


# ------------------------------------------------------------
# QSAR DESCRIPTOR SCORE
# ------------------------------------------------------------

def calculate_molecular_score(row):

    """
    Score moléculaire indicatif.

    ATTENTION :
    Ce score n'est pas une preuve pharmacologique.
    Il sert de couche de priorisation.
    """

    score = 0.0

    # Lipophilie
    logp = safe_float(
        row.get("LogP")
    )

    if not np.isnan(logp):

        if 1 <= logp <= 4:
            score += 20

        elif 0 <= logp < 1:
            score += 12

        else:
            score += 5

    # HBD
    hbd = safe_float(
        row.get("HBD")
    )

    if not np.isnan(hbd):

        if 1 <= hbd <= 5:
            score += 15

        elif hbd == 0:
            score += 5

    # HBA
    hba = safe_float(
        row.get("HBA")
    )

    if not np.isnan(hba):

        if 1 <= hba <= 10:
            score += 15

        else:
            score += 5

    # TPSA
    tpsa = safe_float(
        row.get("TPSA")
    )

    if not np.isnan(tpsa):

        if 20 <= tpsa <= 140:
            score += 15

        else:
            score += 5

    # Anneaux
    rings = safe_float(
        row.get("Anneaux")
    )

    if not np.isnan(rings):

        if rings <= 8:
            score += 10

        else:
            score += 5

    # LD50
    ld50 = safe_float(
        row.get("LD50_mg_kg")
    )

    if not np.isnan(ld50):

        if ld50 >= 2000:
            score += 25

        elif ld50 >= 300:
            score += 15

        else:
            score += 5

    return round(
        min(score, 100),
        2
    )


# ------------------------------------------------------------
# FAMILY DETECTION
# ------------------------------------------------------------

def detect_family(row):

    # Compatible avec une ligne pandas OU avec un simple nom de molécule
    if hasattr(row, "get"):
        nom = str(row.get("Nom", ""))
        iupac = str(row.get("IUPAC_Name", ""))
        formule = str(row.get("Formule", ""))
    else:
        nom = str(row)
        iupac = ""
        formule = ""

    texte = f"{nom} {iupac} {formule}".lower()

    # ==============================
    # FLAVONOÏDES
    # ==============================

    flavonoides = [
        "quercetin",
        "quercétine",
        "kaempferol",
        "rutin",
        "rutine",
        "catechin",
        "catéchine",
        "epicatechin",
        "naringenin",
        "hesperetin",
        "apigenin",
        "luteolin",
        "myricetin"
    ]

    if any(x in texte for x in flavonoides):
        return "flavonoide"

    # ==============================
    # POLYPHÉNOLS
    # ==============================

    polyphenols = [
        "gallic acid",
        "acide gallique",
        "caffeic acid",
        "acide cafeique",
        "ferulic acid",
        "acide ferulique",
        "chlorogenic acid",
        "acide chlorogenique",
        "ellagic acid",
        "acide ellagique",
        "phenolic"
    ]

    if any(x in texte for x in polyphenols):
        return "polyphenol"

    # ==============================
    # ALCALOÏDES
    # ==============================

    alcaloides = [
        "alkaloid",
        "alcaloid",
        "caffeine",
        "caféine",
        "nicotine",
        "morphine",
        "quinine"
    ]

    if any(x in texte for x in alcaloides):
        return "alcaloide"

    # ==============================
    # TERPÉNOÏDES
    # ==============================

    terpenes = [
        "terpene",
        "terpenoid",
        "monoterpene",
        "sesquiterpene",
        "diterpene",
        "triterpene"
    ]

    if any(x in texte for x in terpenes):
        return "terpenoide"

    # ==============================
    # STÉROÏDES
    # ==============================

    steroids = [
        "steroid",
        "steroidal",
        "cholesterol"
    ]

    if any(x in texte for x in steroids):
        return "steroide"

    # ==============================
    # ACIDES ORGANIQUES
    # ==============================

    if "carboxylic acid" in texte:
        return "acide_organique"

    # ==============================
    # ACIDES AMINÉS
    # ==============================

    acides_amines = [
        "glycine",
        "alanine",
        "valine",
        "leucine",
        "isoleucine",
        "lysine",
        "arginine",
        "proline"
    ]

    if any(x in texte for x in acides_amines):
        return "acide_amini"

    # ==============================
    # PAR DÉFAUT
    # ==============================

    return "autre"

# ------------------------------------------------------------
# EFFECT PREDICTION
# ------------------------------------------------------------

def predict_effects(row):

    family = detect_family(row)

    effects = []

    if family == "flavonoide":

        effects.extend([
            "antioxydant",
            "anti_inflammatoire",
            "potentiel_metabolique"
        ])

    elif family == "polyphenol":

        effects.extend([
            "antioxydant",
            "anti_inflammatoire"
        ])

    elif family == "alcaloide":

        effects.append(
            "activité_biologique"
        )

    elif family == "acide_organique":

        effects.append(
            "activité_metabolique"
        )

    elif family == "acide_amini":

        effects.append(
            "métabolisme_amino_acides"
        )

    return list(
        dict.fromkeys(effects)
    )


# ------------------------------------------------------------
# TARGET MAPPING
# ------------------------------------------------------------

def map_targets(effects):

    targets = []

    for effect in effects:

        if effect == "antioxydant":

            targets.extend(
                TARGETS["oxydation"]
            )

        elif effect == "anti-inflammatoire":

            targets.extend(
                TARGETS["inflammation"]
            )

        elif effect == "potentiel_metabolique":

            targets.extend(
                TARGETS["diabete"]
            )

        elif effect == "stimulation_metabolique":

            targets.extend([
                "AMPK",
                "GLUT4"
            ])

    return list(
        dict.fromkeys(targets)
    )


# ------------------------------------------------------------
# SAFETY SCORE
# ------------------------------------------------------------

def calculate_safety(row):

    toxicity = str(
        row.get("Toxicite", "")
    ).lower()

    risk = str(
        row.get("Risque", "")
    ).lower()

    score = 50

    if "faible" in toxicity:
        score += 25

    elif "élev" in toxicity:
        score -= 25

    if "faible" in risk:
        score += 25

    elif "élev" in risk:
        score -= 25

    ld50 = safe_float(
        row.get("LD50_mg_kg")
    )

    if not np.isnan(ld50):

        if ld50 >= 2000:
            score += 10

        elif ld50 < 300:
            score -= 20

    return round(
        max(
            0,
            min(
                score,
                100
            )
        ),
        2
    )


# ------------------------------------------------------------
# MAIN ANALYSIS
# ------------------------------------------------------------

def analyze_database():

    print()
    print("=" * 70)
    print("SENTOX NETWORK PHARMACOLOGY ENGINE")
    print("=" * 70)
    print()

    if not os.path.exists(INPUT_FILE):

        print(
            "ERREUR : fichier introuvable :"
        )

        print(INPUT_FILE)

        return

    # --------------------------------------------------------
    # READ DATABASE
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            INPUT_FILE,
            encoding="utf-8-sig",
            low_memory=False
        )

    except UnicodeDecodeError:

        df = pd.read_csv(
            INPUT_FILE,
            encoding="latin1",
            low_memory=False
        )

    df = normalize_column_names(
        df
    )

    print(
        f"Molecules chargees : {len(df)}"
    )

    print()

    # --------------------------------------------------------
    # REQUIRED COLUMNS
    # --------------------------------------------------------

    print("Colonnes detectees :")

    for col in df.columns:

        print(
            " -",
            col
        )

    print()

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    molecular_scores = []
    safety_scores = []
    families = []
    effects_list = []
    targets_list = []
    target_counts = []

    for index, row in df.iterrows():

        effects = predict_effects(
            row
        )

        targets = map_targets(
            effects
        )

        molecular_score = (
            calculate_molecular_score(
                row
            )
        )

        safety_score = (
            calculate_safety(
                row
            )
        )

        family = detect_family(
            row.get(
                "Nom",
                ""
            )
        )

        molecular_scores.append(
            molecular_score
        )

        safety_scores.append(
            safety_score
        )

        families.append(
            family
        )

        effects_list.append(
            ";".join(effects)
        )

        targets_list.append(
            ";".join(targets)
        )

        target_counts.append(
            len(targets)
        )

        if (
            index + 1
        ) % 100 == 0:

            print(
                f"Analyse : {index + 1}/{len(df)}"
            )

    # --------------------------------------------------------
    # ADD RESULTS
    # --------------------------------------------------------

    df["SENTOX_Famille"] = families

    df["SENTOX_Effets"] = (
        effects_list
    )

    df["SENTOX_Cibles"] = (
        targets_list
    )

    df["SENTOX_Nombre_Cibles"] = (
        target_counts
    )

    df["SENTOX_QSAR_Score"] = (
        molecular_scores
    )

    df["SENTOX_Securite_Score"] = (
        safety_scores
    )

    # --------------------------------------------------------
    # MULTI-TARGET SCORE
    # --------------------------------------------------------

    max_targets = max(
        max(target_counts),
        1
    )

    df["SENTOX_Multicible_Score"] = (
        df["SENTOX_Nombre_Cibles"]
        / max_targets
        * 100
    ).round(2)

    # --------------------------------------------------------
    # GLOBAL PRIORITY
    # --------------------------------------------------------

    df["SENTOX_Priorite"] = (
        df["SENTOX_QSAR_Score"] * 0.4
        +
        df["SENTOX_Securite_Score"] * 0.3
        +
        df["SENTOX_Multicible_Score"] * 0.3
    ).round(2)

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("ANALYSE TERMINEE")
    print("=" * 70)

    print(
        f"Molecules analysees : {len(df)}"
    )

    print(
        f"Resultat : {OUTPUT_FILE}"
    )

    print()

    print(
        "Top 10 molecules prioritaires :"
    )

    cols = [
        "Nom",
        "CID",
        "SENTOX_Famille",
        "SENTOX_QSAR_Score",
        "SENTOX_Securite_Score",
        "SENTOX_Multicible_Score",
        "SENTOX_Priorite"
    ]

    available_cols = [
        c for c in cols
        if c in df.columns
    ]

    top = df.sort_values(
        "SENTOX_Priorite",
        ascending=False
    ).head(10)

    print(
        top[
            available_cols
        ].to_string(
            index=False
        )
    )

    print()
    print(
        "=" * 70
    )
    print(
        "SENTOX NETWORK PHARMACOLOGY : OK"
    )
    print(
        "=" * 70
    )


# ------------------------------------------------------------
# EXECUTION
# ------------------------------------------------------------

if __name__ == "__main__":

    analyze_database()