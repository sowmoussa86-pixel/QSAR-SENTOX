"""
SENTOX
Enrichissement des constituants des plantes médicinales
à partir de PubChem.

Entrée :
    data/molecules_plantes.csv

Sortie :
    data/molecules_plantes_enrichies.csv
"""

import os
import time
import requests
import pandas as pd
# ============================================================
# SYNONYMES PUBCHEM VERIFIES
# ============================================================

SYNONYMES_PUBCHEM = {
    "Acide oléanolique": "oleanolic acid",
    "Bêta-amyrine": "beta-amyrin",
    "Cycloarténol": "cycloartenol",
    "Hédéragénine": "hederagenin",
    "Rhéine": "rhein",
    "Quercitrine": "quercitrin",
    "Isoquercitrine": "isoquercitrin",
    "Epiafzélechine": "epiafzelechin",
    "Épicatéchol": "epicatechin",
    "Leucopélargonidol": "leucopelargonidin",
}

# ============================================================
# CHEMINS DU PROJET
# ============================================================

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
    "molecules_plantes.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "molecules_plantes_enrichies.csv"
)


# ============================================================
# PUBCHEM
# ============================================================

PUBCHEM_URL = (
    "https://pubchem.ncbi.nlm.nih.gov"
    "/rest/pug/compound/name"
)


# ============================================================
# RECHERCHE D'UNE MOLECULE
# ============================================================

def rechercher_pubchem(nom_molecule):

    """
    Recherche une molécule par son nom dans PubChem.
    """

    nom = str(nom_molecule).strip()

    if not nom:
        return None

    url = (
        f"{PUBCHEM_URL}/"
        f"{requests.utils.quote(nom)}/"
        "property/"
        "MolecularFormula,"
        "MolecularWeight,"
        "CanonicalSMILES,"
        "IsomericSMILES,"
        "InChI,"
        "InChIKey/"
        "JSON"
    )

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "SENTOX/1.0"
            }
        )

        if response.status_code != 200:
            return None

        data = response.json()

        proprietes = (
            data
            .get("PropertyTable", {})
            .get("Properties", [])
        )

        if not proprietes:
            return None

        return proprietes[0]

    except Exception as erreur:

        print(
            f"   ERREUR : {erreur}"
        )

        return None


# ============================================================
# ENRICHISSEMENT
# ============================================================

def enrichir_base():

    print()
    print("=" * 65)
    print("SENTOX - ENRICHISSEMENT PUBCHEM")
    print("=" * 65)

    # --------------------------------------------------------
    # Vérification du fichier
    # --------------------------------------------------------

    if not os.path.exists(INPUT_FILE):

        print()
        print("ERREUR : fichier introuvable")
        print(INPUT_FILE)

        return

    # --------------------------------------------------------
    # Lecture CSV
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            INPUT_FILE,
            dtype=str
        )

    except Exception as erreur:

        print()
        print("ERREUR DE LECTURE CSV")
        print(erreur)

        return

    print()
    print(
        f"Nombre de molécules : {len(df)}"
    )

    # --------------------------------------------------------
    # Création des colonnes PubChem
    # --------------------------------------------------------

    nouvelles_colonnes = [

        "SMILES",
        "InChI",
        "InChIKey",
        "PubChem_CID",
        "Formule",
        "Masse_molaire",
        "PubChem_status"

    ]

    for colonne in nouvelles_colonnes:

        if colonne not in df.columns:

            df[colonne] = ""

    # --------------------------------------------------------
    # Recherche des molécules
    # --------------------------------------------------------

    total = len(df)

    trouvees = 0
    non_trouvees = 0

    for index, ligne in df.iterrows():

        nom = ligne.get(
            "Nom_molecule",
            ""
        )

        nom = str(nom).strip()

        print()
        print(
            f"[{index + 1}/{total}] {nom}"
        )

        resultat = rechercher_pubchem(
            nom
        )

        # ----------------------------------------------------
        # Molécule non trouvée
        # ----------------------------------------------------

        if resultat is None:

            df.at[
                index,
                "PubChem_status"
            ] = "NON_TROUVE"

            non_trouvees += 1

            print(
                "   -> Non trouvee dans PubChem"
            )

            time.sleep(0.3)

            continue

        # ----------------------------------------------------
        # Récupération des données
        # ----------------------------------------------------

        cid = resultat.get(
            "CID",
            ""
        )

        formule = resultat.get(
            "MolecularFormula",
            ""
        )

        masse = resultat.get(
            "MolecularWeight",
            ""
        )

        smiles = resultat.get(
            "IsomericSMILES",
            ""
        )

        if not smiles:

            smiles = resultat.get(
                "CanonicalSMILES",
                ""
            )

        inchi = resultat.get(
            "InChI",
            ""
        )

        inchikey = resultat.get(
            "InChIKey",
            ""
        )

        # ----------------------------------------------------
        # Enregistrement
        # ----------------------------------------------------

        df.at[
            index,
            "PubChem_CID"
        ] = str(cid)

        df.at[
            index,
            "Formule"
        ] = str(formule)

        df.at[
            index,
            "Masse_molaire"
        ] = str(masse)

        df.at[
            index,
            "SMILES"
        ] = str(smiles)

        df.at[
            index,
            "InChI"
        ] = str(inchi)

        df.at[
            index,
            "InChIKey"
        ] = str(inchikey)

        df.at[
            index,
            "PubChem_status"
        ] = "TROUVE"

        trouvees += 1

        print(
            f"   -> CID : {cid}"
        )

        print(
            f"   -> Formule : {formule}"
        )

        print(
            f"   -> Masse : {masse}"
        )

        print(
            f"   -> SMILES : {smiles}"
        )

        # Petite pause entre les requêtes
        time.sleep(0.3)

    # ========================================================
    # SAUVEGARDE
    # ========================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # RAPPORT
    # ========================================================

    print()
    print("=" * 65)
    print("ENRICHISSEMENT TERMINE")
    print("=" * 65)

    print(
        f"Molécules traitées : {total}"
    )

    print(
        f"Trouvées dans PubChem : {trouvees}"
    )

    print(
        f"Non trouvées : {non_trouvees}"
    )

    print()
    print(
        "Fichier de sortie :"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 65)


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    enrichir_base()