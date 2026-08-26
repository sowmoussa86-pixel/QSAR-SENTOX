# -*- coding: utf-8 -*-
"""
SENTOX Network Pharmacology V2
--------------------------------
Moteur de pharmacologie de réseau pour les molécules SENTOX.

IMPORTANT :
- Les associations famille chimique -> cibles sont des associations
  HEURISTIQUES/ANNOTATIVES pour prototypage.
- Elles ne constituent PAS des preuves expérimentales ni des probabilités
  pharmacologiques validées.
- Le module produit un "SENTOX_Network_Coverage_Score" et non une probabilité
  d'efficacité clinique.

Entrée :
    C:\\SENTOX\\data\\sentox_database_2000_enriched.csv

Sorties :
    C:\\SENTOX\\data\\sentox_network_results_v2.csv
    C:\\SENTOX\\data\\sentox_network_edges_v2.csv
"""

from pathlib import Path
import re
import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(r"C:\SENTOX")
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "sentox_database_2000_enriched.csv"
OUTPUT_FILE = DATA_DIR / "sentox_network_results_v2.csv"
EDGES_FILE = DATA_DIR / "sentox_network_edges_v2.csv"


# ============================================================
# FAMILLES CHIMIQUES
# ============================================================

FAMILY_KEYWORDS = {
    "flavonoide": [
        "quercetin", "quercétine", "kaempferol", "kaempférol",
        "rutin", "rutine", "catechin", "catéchine",
        "epicatechin", "naringenin", "hesperetin",
        "apigenin", "apigénine", "luteolin", "lutéoline",
        "myricetin", "myricétine"
    ],

    "polyphenol": [
        "gallic acid", "acide gallique",
        "caffeic acid", "acide caféique",
        "ferulic acid", "acide férulique",
        "chlorogenic acid", "acide chlorogénique",
        "ellagic acid", "acide ellagique",
        "phenolic", "polyphenol", "polyphénol"
    ],

    "alcaloide": [
        "alkaloid", "alcaloïde", "caffeine", "caféine",
        "nicotine", "quinine", "quinidine", "morphine"
    ],

    "terpenoide": [
        "terpene", "terpenoid", "monoterpene",
        "sesquiterpene", "diterpene", "triterpene"
    ],

    "steroide": [
        "steroid", "steroidal", "cholesterol"
    ],

    "acide_organique": [
        "carboxylic acid", "organic acid", "acide organique"
    ],

    "acide_amino": [
        "glycine", "alanine", "valine", "leucine",
        "isoleucine", "lysine", "arginine", "proline"
    ]
}


# ============================================================
# CIBLES / VOIES : ANNOTATION DE PROTOTYPAGE
# ============================================================
# Ces associations servent à construire le réseau logiciel.
# Elles doivent être remplacées/complétées par des données validées
# provenant de bases de cibles et de littérature avant toute conclusion
# pharmacologique.

FAMILY_TARGETS = {
    "flavonoide": {
        "targets": [
            "PTGS2",
            "AKT1",
            "PPARG",
            "EGFR",
            "MAPK1"
        ],
        "pathways": [
            "Inflammation",
            "PI3K-AKT",
            "MAPK",
            "Métabolisme"
        ]
    },

    "polyphenol": {
        "targets": [
            "PTGS2",
            "NFKB1",
            "AKT1",
            "AMPK",
            "PPARG"
        ],
        "pathways": [
            "Inflammation",
            "PI3K-AKT",
            "AMPK",
            "Métabolisme"
        ]
    },

    "alcaloide": {
        "targets": [
            "ACHE",
            "DRD2",
            "HTR2A",
            "ADRB2",
            "CYP3A4"
        ],
        "pathways": [
            "Neurotransmission",
            "Métabolisme des médicaments",
            "Signalisation"
        ]
    },

    "terpenoide": {
        "targets": [
            "PPARG",
            "PTGS2",
            "MAPK1",
            "NFKB1"
        ],
        "pathways": [
            "Inflammation",
            "MAPK",
            "Métabolisme"
        ]
    },

    "steroide": {
        "targets": [
            "NR3C1",
            "ESR1",
            "AR",
            "PPARG"
        ],
        "pathways": [
            "Récepteurs nucléaires",
            "Hormones",
            "Métabolisme"
        ]
    },

    "acide_organique": {
        "targets": [
            "SLC2A4",
            "AMPK",
            "PPARG"
        ],
        "pathways": [
            "Métabolisme",
            "AMPK",
            "Transport"
        ]
    },

    "acide_amino": {
        "targets": [
            "MTOR",
            "INSR",
            "GLUL"
        ],
        "pathways": [
            "Métabolisme",
            "Signalisation de l'insuline"
        ]
    },

    "autre": {
        "targets": [],
        "pathways": []
    }
}


# ============================================================
# OUTILS
# ============================================================

def clean_text(value):
    """Convertit n'importe quelle valeur en texte propre."""
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value).strip()


def detect_family(row):
    """
    Détection robuste de famille.
    Accepte une ligne pandas ou une chaîne.
    """

    if hasattr(row, "get"):
        nom = clean_text(row.get("Nom", ""))
        iupac = clean_text(row.get("IUPAC_Name", ""))
        formule = clean_text(row.get("Formule", ""))
        smiles = clean_text(row.get("SMILES", ""))
    else:
        nom = clean_text(row)
        iupac = ""
        formule = ""
        smiles = ""

    text = f"{nom} {iupac} {formule} {smiles}".lower()

    # priorité aux familles spécifiques
    for family, keywords in FAMILY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return family

    return "autre"


def split_items(value):
    """
    Transforme une cellule de type :
    'A;B;C' / 'A, B, C' / 'A|B'
    en liste unique.
    """
    text = clean_text(value)

    if not text:
        return []

    parts = re.split(r"[;|]", text)

    result = []
    for item in parts:
        item = item.strip()
        if item and item not in result:
            result.append(item)

    return result


def get_family_targets(family):
    data = FAMILY_TARGETS.get(family, FAMILY_TARGETS["autre"])

    targets = data.get("targets", [])
    pathways = data.get("pathways", [])

    return targets, pathways


# ============================================================
# SCORE RESEAU
# ============================================================

def calculate_network_scores(family, targets, pathways, row):
    """
    Calcule des scores de couverture du réseau.

    Ce ne sont PAS des probabilités d'efficacité.
    """

    target_count = len(targets)
    pathway_count = len(pathways)

    # Score QSAR existant s'il existe
    existing_qsar = np.nan

    for col in [
        "SENTOX_QSAR_Score",
        "QSAR_Score",
        "QSAR"
    ]:
        if col in row.index:
            try:
                existing_qsar = float(row[col])
                break
            except Exception:
                pass

    if pd.isna(existing_qsar):
        # Valeur neutre de prototypage.
        # Elle ne doit pas être interprétée comme une prédiction validée.
        existing_qsar = 50.0

    # Sécurité existante
    security = np.nan

    for col in [
        "SENTOX_Securite_Score",
        "SENTOX_Sécurité_Score",
        "Securite_Score",
        "Sécurité_Score"
    ]:
        if col in row.index:
            try:
                security = float(row[col])
                break
            except Exception:
                pass

    if pd.isna(security):
        security = 50.0

    # --------------------------------------------------------
    # Couverture multicible
    # --------------------------------------------------------
    # 5 cibles de référence -> 100
    multicible = min(100.0, (target_count / 5.0) * 100.0)

    # Diversité des voies
    pathway_score = min(100.0, (pathway_count / 4.0) * 100.0)

    # Priorité SENTOX :
    # couverture du réseau + sécurité + QSAR existant
    priority_score = (
        0.45 * multicible
        + 0.25 * pathway_score
        + 0.20 * float(existing_qsar)
        + 0.10 * float(security)
    )

    priority_score = round(max(0.0, min(100.0, priority_score)), 2)

    return {
        "SENTOX_QSAR_Score": round(float(existing_qsar), 2),
        "SENTOX_Securite_Score": round(float(security), 2),
        "SENTOX_Target_Count": target_count,
        "SENTOX_Pathway_Count": pathway_count,
        "SENTOX_Multicible_Coverage": round(multicible, 2),
        "SENTOX_Pathway_Coverage": round(pathway_score, 2),
        "SENTOX_Network_Priority": priority_score
    }


# ============================================================
# CONSTRUCTION DU RESEAU
# ============================================================

def build_network(df):

    result_rows = []
    edge_rows = []

    total = len(df)

    for index, (_, row) in enumerate(df.iterrows(), start=1):

        family = detect_family(row)

        targets, pathways = get_family_targets(family)

        scores = calculate_network_scores(
            family,
            targets,
            pathways,
            row
        )

        # ----------------------------------------------------
        # Informations molécule
        # ----------------------------------------------------

        nom = clean_text(row.get("Nom", f"Molecule_{index}"))
        cid = clean_text(row.get("CID", ""))

        result = row.to_dict()

        result["SENTOX_Famille_V2"] = family

        result["SENTOX_Cibles"] = ";".join(targets)
        result["SENTOX_Voies"] = ";".join(pathways)

        result.update(scores)

        # Score réseau final
        result["SENTOX_Network_Score"] = round(
            (
                0.50 * scores["SENTOX_Multicible_Coverage"]
                + 0.30 * scores["SENTOX_Pathway_Coverage"]
                + 0.20 * scores["SENTOX_Securite_Score"]
            ),
            2
        )

        result["SENTOX_Evidence_Level"] = (
            "HEURISTIC_FAMILY_MAPPING"
            if family != "autre"
            else "NO_TARGET_ANNOTATION"
        )

        result_rows.append(result)

        # ----------------------------------------------------
        # Arêtes du réseau
        # ----------------------------------------------------

        for target in targets:

            edge_rows.append({
                "Node_Type_A": "Molecule",
                "Node_A": nom,
                "CID": cid,
                "Node_Type_B": "Target",
                "Node_B": target,
                "Family": family,
                "Evidence": "heuristic_family_mapping"
            })

        for pathway in pathways:

            edge_rows.append({
                "Node_Type_A": "Molecule",
                "Node_A": nom,
                "CID": cid,
                "Node_Type_B": "Pathway",
                "Node_B": pathway,
                "Family": family,
                "Evidence": "heuristic_family_mapping"
            })

        if index % 100 == 0 or index == total:
            print(f"Analyse réseau : {index}/{total}")

    return pd.DataFrame(result_rows), pd.DataFrame(edge_rows)


# ============================================================
# RAPPORT CONSOLE
# ============================================================

def print_summary(result_df):

    print()
    print("=" * 75)
    print("SENTOX NETWORK PHARMACOLOGY V2")
    print("=" * 75)

    print(f"Molecules analysées : {len(result_df)}")

    if "SENTOX_Famille_V2" in result_df.columns:
        print()
        print("REPARTITION PAR FAMILLE")
        print("-" * 75)

        counts = result_df["SENTOX_Famille_V2"].value_counts()

        for family, count in counts.items():
            print(f"{family:<25} {count}")

    print()
    print("TOP 10 MOLECULES - PRIORITE RESEAU")
    print("-" * 75)

    columns = [
        "Nom",
        "CID",
        "SENTOX_Famille_V2",
        "SENTOX_Target_Count",
        "SENTOX_Pathway_Count",
        "SENTOX_Multicible_Coverage",
        "SENTOX_Pathway_Coverage",
        "SENTOX_Network_Score"
    ]

    available = [c for c in columns if c in result_df.columns]

    top = (
        result_df
        .sort_values("SENTOX_Network_Score", ascending=False)
        .head(10)
    )

    print(top[available].to_string(index=False))

    print()
    print("INTERPRETATION")
    print("-" * 75)
    print(
        "Les scores SENTOX_Network_Score et "
        "SENTOX_Multicible_Coverage sont des scores "
        "de priorisation informatique."
    )
    print(
        "Ils ne constituent pas une probabilité d'efficacité "
        "clinique et doivent être validés par des données "
        "pharmacologiques/expérimentales."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 75)
    print("SENTOX NETWORK PHARMACOLOGY V2")
    print("=" * 75)

    if not INPUT_FILE.exists():
        print()
        print("ERREUR : fichier introuvable :")
        print(INPUT_FILE)
        return

    print()
    print("Lecture de la base :")
    print(INPUT_FILE)

    # Lecture robuste
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

    print()
    print(f"Molecules chargées : {len(df)}")

    print()
    print("Colonnes détectées :")

    for col in df.columns:
        print(f"- {col}")

    print()
    print("Construction du réseau...")

    result_df, edges_df = build_network(df)

    # Sauvegarde
    result_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    edges_df.to_csv(
        EDGES_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print_summary(result_df)

    print()
    print("=" * 75)
    print("SENTOX NETWORK PHARMACOLOGY V2 : OK")
    print("=" * 75)

    print()
    print("Résultat molécules :")
    print(OUTPUT_FILE)

    print()
    print("Résultat réseau :")
    print(EDGES_FILE)


if __name__ == "__main__":
    main()