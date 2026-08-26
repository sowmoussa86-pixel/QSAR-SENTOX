import os
import time
import requests
import pandas as pd

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski


# ============================================================
# SENTOX DATABASE BUILDER 2000
# Construction automatique d'une base de 2000 molécules
# Source chimique : PubChem
# Descripteurs : RDKit
# ============================================================

BASE_DIR = r"C:\SENTOX"
DATA_DIR = os.path.join(BASE_DIR, "data")

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000.csv"
)

os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# MOLECULES DE REFERENCE
# ============================================================

SEEDS = [
    "ethanol",
    "methanol",
    "acetone",
    "benzene",
    "toluene",
    "phenol",
    "aspirin",
    "paracetamol",
    "ibuprofen",
    "caffeine",
    "isoniazid",
    "glycine",
    "alanine",
    "valine",
    "leucine",
    "quercetin",
    "kaempferol",
    "rutin",
    "catechin",
    "epicatechin"
]


# ============================================================
# PUBCHEM
# ============================================================

PUBCHEM_BASE = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
)


HEADERS = {
    "User-Agent": "SENTOX-QSAR/2.0"
}


def requete_json(url, params=None, timeout=30):

    try:

        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=timeout
        )

        if response.status_code != 200:
            return None

        return response.json()

    except Exception as e:

        print(f"Erreur réseau : {e}")

        return None


# ============================================================
# RECHERCHE CID
# ============================================================

def trouver_cid(nom):

    url = (
        PUBCHEM_BASE
        + "/compound/name/"
        + requests.utils.quote(nom)
        + "/cids/JSON"
    )

    data = requete_json(url)

    if not data:
        return None

    try:
        return int(data["IdentifierList"]["CID"][0])
    except Exception:
        return None


# ============================================================
# RECHERCHE PAR SIMILARITE
# ============================================================

def trouver_molecules_similaires(cid, maximum=300):

    url = (
        PUBCHEM_BASE
        + f"/compound/fastsimilarity_2d/cid/"
        + f"{cid}/cids/JSON"
    )

    params = {
        "Threshold": 80,
        "MaxRecords": maximum
    }

    data = requete_json(url, params=params)

    if not data:
        return []

    try:
        return data["IdentifierList"]["CID"]
    except Exception:
        return []


# ============================================================
# PROPRIETES PUBCHEM
# ============================================================

def recuperer_proprietes(cids):

    if not cids:
        return []

    cid_string = ",".join(
        str(cid) for cid in cids
    )

    properties = (
        "MolecularFormula,"
        "MolecularWeight,"
        "XLogP,"
        "TPSA,"
        "HBondDonorCount,"
        "HBondAcceptorCount,"
        "CanonicalSMILES,"
        "IsomericSMILES"
    )

    url = (
        PUBCHEM_BASE
        + "/compound/cid/"
        + cid_string
        + "/property/"
        + properties
        + "/JSON"
    )

    data = requete_json(url, timeout=60)

    if not data:
        return []

    try:
        return data["PropertyTable"]["Properties"]
    except Exception:
        return []


# ============================================================
# DESCRIPTEURS RDKit
# ============================================================

def calculer_rdkit(smiles):

    if not smiles:
        return {}

    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return {}

    try:

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
                int(
                    Lipinski.NumHDonors(mol)
                ),

            "RDKit_HBA":
                int(
                    Lipinski.NumHAcceptors(mol)
                ),

            "RDKit_TPSA":
                round(
                    Descriptors.TPSA(mol),
                    4
                ),

            "Atomes_lourds":
                int(
                    Lipinski.HeavyAtomCount(mol)
                ),

            "Anneaux":
                int(
                    Lipinski.RingCount(mol)
                ),

            "Liaisons_rotatables":
                int(
                    Lipinski.NumRotatableBonds(mol)
                )
        }

    except Exception:
        return {}


# ============================================================
# CATEGORISATION
# ============================================================

def categorie_molecule(nom):

    nom = str(nom).lower()

    if nom in [
        "aspirin",
        "paracetamol",
        "ibuprofen",
        "isoniazid"
    ]:
        return "Drug"

    if nom in [
        "quercetin",
        "kaempferol",
        "rutin",
        "catechin",
        "epicatechin"
    ]:
        return "Medicinal_plant_compound"

    if nom in [
        "glycine",
        "alanine",
        "valine",
        "leucine"
    ]:
        return "Amino_acid"

    return "Industrial"


# ============================================================
# CONSTRUCTION
# ============================================================

def main():

    print()
    print("=" * 70)
    print("              SENTOX DATABASE BUILDER 2000")
    print("=" * 70)
    print()

    tous_cids = set()

    # --------------------------------------------------------
    # 1. Recherche des molécules de référence
    # --------------------------------------------------------

    print("RECHERCHE DES MOLECULES DE REFERENCE")
    print("-" * 70)

    for i, nom in enumerate(SEEDS, 1):

        print(
            f"[{i}/{len(SEEDS)}] Recherche : {nom}"
        )

        cid = trouver_cid(nom)

        if cid:

            print(f"       CID : {cid}")

            tous_cids.add(cid)

            similaires = trouver_molecules_similaires(
                cid,
                maximum=300
            )

            tous_cids.update(similaires)

            print(
                f"       CIDs collectes : "
                f"{len(similaires)}"
            )

        else:

            print("       NON TROUVE")

        # Respect de la politique PubChem
        time.sleep(0.25)

        if len(tous_cids) >= 2000:
            break


    # --------------------------------------------------------
    # 2. Limitation à 2000 molécules
    # --------------------------------------------------------

    cids = sorted(tous_cids)[:2000]

    print()
    print("=" * 70)
    print(
        f"CIDs uniques collectes : {len(cids)}"
    )
    print("=" * 70)
    print()


    if len(cids) < 2000:

        print(
            "ATTENTION : moins de 2000 CIDs ont ete "
            "collectes avec les recherches actuelles."
        )

        print(
            "Le fichier sera quand meme construit "
            "avec toutes les molécules disponibles."
        )


    # --------------------------------------------------------
    # 3. Recuperation des proprietes
    # --------------------------------------------------------

    toutes_les_donnees = []

    batch_size = 100

    total_batches = (
        (len(cids) + batch_size - 1)
        // batch_size
    )

    print()
    print("RECUPERATION DES PROPRIETES PUBCHEM")
    print("-" * 70)

    for debut in range(
        0,
        len(cids),
        batch_size
    ):

        batch = cids[
            debut:debut + batch_size
        ]

        numero = (
            debut // batch_size
        ) + 1

        print(
            f"Lot {numero}/{total_batches} "
            f"({len(batch)} molecules)"
        )

        data = recuperer_proprietes(batch)

        toutes_les_donnees.extend(data)

        time.sleep(0.5)


    # --------------------------------------------------------
    # 4. Construction des lignes SENTOX
    # --------------------------------------------------------

    lignes = []

    print()
    print("CALCUL DES DESCRIPTEURS RDKit")
    print("-" * 70)

    for i, item in enumerate(
        toutes_les_donnees,
        1
    ):

        cid = item.get("CID")

        smiles = (
            item.get("SMILES")
            or item.get("ConnectivitySMILES")
            or item.get("CanonicalSMILES")
            or item.get("IsomericSMILES")
        )

        if not smiles:
            continue

        rdkit_data = calculer_rdkit(
            smiles
        )

        nom = item.get(
            "Title",
            f"CID_{cid}"
        )

        ligne = {

            "Nom":
                nom,

            "Categorie":
                categorie_molecule(nom),

            "CID":
                cid,

            "Formule":
                item.get(
                    "MolecularFormula",
                    ""
                ),

            "Masse_molaire":
                item.get(
                    "MolecularWeight",
                    ""
                ),

            "LogP":
                item.get(
                    "XLogP",
                    ""
                ),

            "HBD":
                item.get(
                    "HBondDonorCount",
                    ""
                ),

            "HBA":
                item.get(
                    "HBondAcceptorCount",
                    ""
                ),

            "TPSA":
                item.get(
                    "TPSA",
                    ""
                ),

            "SMILES":
                smiles,

            "Source_structure":
                "PubChem",

            "Source_toxicologie":
                "",

            "Plante":
                "",

            "Partie_utilisee":
                "",

            "Statut_donnees":
                "Structure_PubChem",

            **rdkit_data,

            "LD50_mg_kg":
                "",

            "LogLD50":
                "",

            "Toxicite":
                "",

            "Risque":
                "",

            "RKdit_masse_molaire":
                rdkit_data.get(
                    "RDKit_Masse_molaire",
                    ""
                ),

            "RDKit_LogP":
                rdkit_data.get(
                    "RDKit_LogP",
                    ""
                ),

            "RDKit_HBD":
                rdkit_data.get(
                    "RDKit_HBD",
                    ""
                ),

            "RDKit_HBA":
                rdkit_data.get(
                    "RDKit_HBA",
                    ""
                ),

            "RDKit_TPSA":
                rdkit_data.get(
                    "RDKit_TPSA",
                    ""
                )
        }

        lignes.append(ligne)

        if i % 100 == 0:

            print(
                f"{i} molecules traitees..."
            )


    # --------------------------------------------------------
    # 5. DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(lignes)

    if df.empty:

        print()
        print(
            "ERREUR : aucune molecule n'a ete recuperee."
        )

        return


    # --------------------------------------------------------
    # 6. Suppression des doublons
    # --------------------------------------------------------

    if "CID" in df.columns:

        df = df.drop_duplicates(
            subset=["CID"]
        )


    # --------------------------------------------------------
    # 7. Maximum 2000 molecules
    # --------------------------------------------------------

    df = df.head(2000)


    # --------------------------------------------------------
    # 8. Sauvegarde
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # --------------------------------------------------------
    # 9. Rapport
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("              CONSTRUCTION TERMINEE")
    print("=" * 70)

    print(
        f"Molécules enregistrées : {len(df)}"
    )

    print(
        f"Fichier : {OUTPUT_FILE}"
    )

    print()
    print("Colonnes principales :")

    for colonne in df.columns:

        print(
            f"  - {colonne}"
        )

    print()
    print("Répartition par catégorie :")

    print(
        df["Categorie"]
        .value_counts()
        .to_string()
    )

    print()
    print("=" * 70)
    print("              SENTOX DATABASE 2000 : OK")
    print("=" * 70)


if __name__ == "__main__":
    main()