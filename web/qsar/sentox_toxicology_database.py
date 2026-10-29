from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
STRUCTURE_FILE = BASE_DIR / "data" / "sentox_database_2000_enriched_noms.csv"
TOXICOLOGY_FILE = BASE_DIR / "data" / "sentox_toxicology_database.csv"


def charger_base_structurelle():
    return pd.read_csv(STRUCTURE_FILE)


def charger_base_toxicologique():
    return pd.read_csv(TOXICOLOGY_FILE)


def rechercher_toxicologie(cid):
    tox = charger_base_toxicologique()

    resultat = tox[
        tox["CID"].astype(str).str.strip()
        == str(cid).strip()
    ].copy()

    if resultat.empty:
        return []

    return resultat.to_dict(
        orient="records"
    )


def rechercher_molecule(cid):
    # 1. Recherche dans la base structurelle principale
    structure = charger_base_structurelle()
    resultat = structure[structure["CID"].astype(str) == str(cid)]

    if not resultat.empty:
        return resultat.iloc[0].to_dict()

    # 2. Recherche dans la base des constituants végétaux
    constituants_file = BASE_DIR / "data" / "constituants_enrichis.csv"

    if constituants_file.exists():
        constituants = pd.read_csv(constituants_file)
        resultat = constituants[
            constituants["CID"].astype(str) == str(cid)
        ]

        if not resultat.empty:
            return resultat.iloc[0].to_dict()

    return None


def analyser_cid(cid):
    molecule = rechercher_molecule(cid)
    if molecule is None:
        return {"statut": "NON_TROUVE", "CID": cid, "molecule": None, "toxicologie": []}
    toxicologie = rechercher_toxicologie(cid)
    return {"statut": "TROUVE", "CID": cid, "molecule": molecule, "toxicologie": toxicologie}
