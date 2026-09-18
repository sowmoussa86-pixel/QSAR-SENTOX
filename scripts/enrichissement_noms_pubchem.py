import os
import re
import time
import requests
import pandas as pd

# ============================================================
# SENTOX - ENRICHISSEMENT DES NOMS PAR PUBCHEM
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FICHIER_ENTREE = os.path.join(
    BASE_DIR,
    "data",
    "sentox_database_2000_enriched.csv"
)

FICHIER_SORTIE = os.path.join(
    BASE_DIR,
    "data",
    "sentox_database_2000_enriched_noms.csv"
)

TAILLE_LOT = 50
PAUSE = 0.5


def extraire_cid(valeur):
    """
    Transforme :
        CID_289 -> 289
        289    -> 289
    """
    if pd.isna(valeur):
        return None

    texte = str(valeur).strip()

    match = re.search(r"(\d+)$", texte)

    if match:
        return int(match.group(1))

    return None


def recuperer_pubchem(cids):
    """
    Récupère les propriétés PubChem pour une liste de CID.
    """
    if not cids:
        return {}

    cids_str = ",".join(str(cid) for cid in cids)

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        f"compound/cid/{cids_str}/property/"
        "Title,IUPACName,MolecularFormula,SMILES,InChI,InChIKey/JSON"
    )

    try:
        response = requests.get(url, timeout=60)

        if response.status_code != 200:
            print(
                f"⚠️ PubChem HTTP {response.status_code}"
            )
            return {}

        data = response.json()

        proprietes = data.get(
            "PropertyTable",
            {}
        ).get(
            "Properties",
            []
        )

        resultat = {}

        for item in proprietes:
            cid = item.get("CID")

            if cid is not None:
                resultat[int(cid)] = item

        return resultat

    except Exception as e:
        print(f"⚠️ Erreur PubChem : {e}")
        return {}


def main():

    print("=" * 60)
    print("SENTOX - ENRICHISSEMENT DES NOMS PUBCHEM")
    print("=" * 60)

    print(f"Fichier entrée : {FICHIER_ENTREE}")

    if not os.path.exists(FICHIER_ENTREE):
        print("❌ Fichier d'entrée introuvable.")
        return

    df = pd.read_csv(
        FICHIER_ENTREE,
        low_memory=False
    )

    print(f"Nombre de lignes : {len(df)}")

    if "CID" not in df.columns:
        print("❌ La colonne CID est absente.")
        return

    # --------------------------------------------------------
    # Sauvegarde du nom actuel
    # --------------------------------------------------------

    if "Nom_original" not in df.columns:
        df["Nom_original"] = df["Nom"].astype(str)

    # --------------------------------------------------------
    # Extraction des CID
    # --------------------------------------------------------

    df["_CID_NUM"] = df["CID"].apply(extraire_cid)

    cids = (
        df["_CID_NUM"]
        .dropna()
        .astype(int)
        .drop_duplicates()
        .tolist()
    )

    print(f"CID exploitables : {len(cids)}")

    # --------------------------------------------------------
    # Colonnes d'enrichissement
    # --------------------------------------------------------

    colonnes = [
        "Nom_PubChem",
        "IUPAC_Name_PubChem",
        "Formule_PubChem",
        "SMILES_PubChem",
        "InChI_PubChem",
        "InChIKey_PubChem",
        "PubChem_Statut"
    ]

    for colonne in colonnes:
        if colonne not in df.columns:
            df[colonne] = None

    # --------------------------------------------------------
    # Traitement par lots
    # --------------------------------------------------------

    total_lots = (len(cids) + TAILLE_LOT - 1) // TAILLE_LOT

    for numero_lot, debut in enumerate(
        range(0, len(cids), TAILLE_LOT),
        start=1
    ):

        lot = cids[
            debut: debut + TAILLE_LOT
        ]

        print(
            f"\nLot {numero_lot}/{total_lots}"
            f" - {len(lot)} CID"
        )

        donnees = recuperer_pubchem(lot)

        print(
            f"  → {len(donnees)} résultats PubChem"
        )

        for cid, infos in donnees.items():

            masque = df["_CID_NUM"] == cid

            titre = infos.get("Title")
            iupac = infos.get("IUPACName")
            formule = infos.get("MolecularFormula")
            smiles = infos.get("SMILES")
            inchi = infos.get("InChI")
            inchikey = infos.get("InChIKey")

            if titre:
                df.loc[
                    masque,
                    "Nom_PubChem"
                ] = titre

            if iupac:
                df.loc[
                    masque,
                    "IUPAC_Name_PubChem"
                ] = iupac

            if formule:
                df.loc[
                    masque,
                    "Formule_PubChem"
                ] = formule

            if smiles:
                df.loc[
                    masque,
                    "SMILES_PubChem"
                ] = smiles

            if inchi:
                df.loc[
                    masque,
                    "InChI_PubChem"
                ] = inchi

            if inchikey:
                df.loc[
                    masque,
                    "InChIKey_PubChem"
                ] = inchikey

            df.loc[
                masque,
                "PubChem_Statut"
            ] = "Trouvé"

            # ------------------------------------------------
            # Remplacement du nom artificiel CID_xxx
            # ------------------------------------------------

            if titre:
                noms_actuels = (
                    df.loc[masque, "Nom"]
                    .astype(str)
                    .str.strip()
                )

                masque_cid = (
                    noms_actuels
                    .str.match(r"^CID_\d+$", na=False)
                )

                index_cid = df.loc[masque].index[
                    masque_cid
                ]

                df.loc[
                    index_cid,
                    "Nom"
                ] = titre

        time.sleep(PAUSE)

    # --------------------------------------------------------
    # Nettoyage
    # --------------------------------------------------------

    df.drop(
        columns=["_CID_NUM"],
        inplace=True
    )

    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    df.to_csv(
        FICHIER_SORTIE,
        index=False
    )

    print("\n" + "=" * 60)
    print("✅ ENRICHISSEMENT TERMINÉ")
    print("=" * 60)

    print(
        f"Fichier créé : {FICHIER_SORTIE}"
    )

    print(
        "La base originale n'a pas été modifiée."
    )


if __name__ == "__main__":
    main()