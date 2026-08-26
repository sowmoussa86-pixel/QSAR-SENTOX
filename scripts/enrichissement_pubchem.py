# ============================================================
# SENTOX - ENRICHISSEMENT PUBCHEM
# VERSION ROBUSTE
# ============================================================

import os
import time
import shutil
import requests
import pandas as pd

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"C:\SENTOX"
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000_enriched.csv"
)

BACKUP_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000_backup.csv"
)

os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================
# PUBCHEM
# ============================================================

PUBCHEM_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    "compound/name/{}/property/"
    "MolecularFormula,"
    "MolecularWeight,"
    "XLogP,"
    "HBondDonorCount,"
    "HBondAcceptorCount,"
    "TPSA,"
    "HeavyAtomCount,"
    "RotatableBondCount,"
    "CanonicalSMILES,"
    "IsomericSMILES,"
    "IUPACName,"
    "Title/JSON"
)


HEADERS = {
    "User-Agent": "SENTOX-QSAR/2.0"
}


# ============================================================
# AFFICHAGE
# ============================================================

def afficher_titre(texte):
    print()
    print("=" * 70)
    print(texte)
    print("=" * 70)


# ============================================================
# RECHERCHE PUBCHEM
# ============================================================
def rechercher_plante(nom):
    import pandas as pd

    fichier = r"C:\SENTOX\data\plantes.csv"

    try:
        plantes = pd.read_csv(fichier)

        resultat = plantes[
            plantes["Nom_scientifique"]
            .astype(str)
            .str.strip()
            .str.lower()
            == str(nom).strip().lower()
        ]

        if resultat.empty:
            return None

        return resultat.iloc[0].to_dict()

    except Exception as e:
        print("Erreur :", e)
        return None
def nom_pubchem(nom):
    correspondances = {
        "Quercétine": "quercetin",
        "Rutine": "rutin",
        "Kaempférol": "kaempferol",
        "Naringénine": "naringenin",
        "Catéchine": "catechin",
        "Épicatéchine": "epicatechin",
        "Acide gallique": "gallic acid",
        "Acide ellagique": "ellagic acid"
    }

    if nom is None:
        return None

    nom = str(nom).strip()

    return correspondances.get(nom, nom)
def rechercher_pubchem(nom):

    if nom is None:
        return None

    nom = str(nom).strip()

    if not nom:
        return None

    url = PUBCHEM_URL.format(
        requests.utils.quote(nom)
    )

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code != 200:
            return None

        data = response.json()

        properties = (
            data
            .get("PropertyTable", {})
            .get("Properties", [])
        )

        if not properties:
            return None

        return properties[0]

    except Exception:
        return None

def rechercher_constituants(plant_id):
    try:
        df = pd.read_csv(
            r"C:\SENTOX\data\constituants_plantes.csv"
        )

        resultat = df[
            df["Plant_ID"]
            .astype(str)
            .str.strip()
            .str.lower()
            == str(plant_id).strip().lower()
        ]

        if resultat.empty:
            return []

        return resultat.to_dict(orient="records")

    except Exception as e:
        print("Erreur recherche constituants :", e)
        return []

def enrichir_constituants(plant_id):
    """
    Récupère les constituants d'une plante et
    ajoute automatiquement les données PubChem.
    """

    resultats = rechercher_constituants(plant_id)

    if not resultats:
        print("Aucun constituant trouvé.")
        return []

    enrichis = []

    for constituant in resultats:

        nom = constituant.get("Constituant")

        if not nom:
            continue

        print(f"\nRecherche PubChem : {nom}")

        nom_pub = nom_pubchem(nom)

        if not nom_pub:
            print("  Nom PubChem introuvable")
            continue

        donnees = rechercher_pubchem(nom_pub)

        if donnees:
            ligne = constituant.copy()
            ligne["Nom_PubChem"] = nom_pub
            ligne.update(donnees)

            enrichis.append(ligne)

            print(f"  ✓ Trouvé : {nom_pub}")
            print(f"  CID : {donnees.get('CID')}")
            print(f"  Formule : {donnees.get('MolecularFormula')}")
            print(f"  Masse : {donnees.get('MolecularWeight')}")
        else:
            print(f"  ✗ PubChem ne trouve pas : {nom_pub}")

    return enrichis
# ============================================================
# DESCRIPTEURS RDKit
# ============================================================

def calculer_rdkit(smiles):

    resultat = {
        "RDKit_Masse_molaire": "",
        "RDKit_LogP": "",
        "RDKit_HBD": "",
        "RDKit_HBA": "",
        "RDKit_TPSA": "",
        "RDKit_Atomes_lourds": "",
        "RDKit_Anneaux": "",
        "RDKit_Liaisons_rotatables": ""
    }

    if not smiles:
        return resultat

    try:

        mol = Chem.MolFromSmiles(str(smiles))

        if mol is None:
            return resultat

        resultat["RDKit_Masse_molaire"] = round(
            Descriptors.MolWt(mol), 4
        )

        resultat["RDKit_LogP"] = round(
            Crippen.MolLogP(mol), 4
        )

        resultat["RDKit_HBD"] = int(
            Lipinski.NumHDonors(mol)
        )

        resultat["RDKit_HBA"] = int(
            Lipinski.NumHAcceptors(mol)
        )

        resultat["RDKit_TPSA"] = round(
            Descriptors.TPSA(mol), 4
        )

        resultat["RDKit_Atomes_lourds"] = int(
            Lipinski.HeavyAtomCount(mol)
        )

        resultat["RDKit_Anneaux"] = int(
            Lipinski.RingCount(mol)
        )

        resultat["RDKit_Liaisons_rotatables"] = int(
            Lipinski.NumRotatableBonds(mol)
        )

    except Exception:
        pass

    return resultat


# ============================================================
# NORMALISATION DU NOM DES COLONNES
# ============================================================

def trouver_colonne_nom(df):

    candidats = [
        "Nom",
        "nom",
        "NAME",
        "Name",
        "Molecule",
        "Molecule_Name",
        "Molecular_Name"
    ]

    for colonne in candidats:

        if colonne in df.columns:
            return colonne

    return None


# ============================================================
# MAIN
# ============================================================
def rechercher_plante(nom):
    import pandas as pd

    fichier = r"C:\SENTOX\data\plantes.csv"

    try:
        plantes = pd.read_csv(fichier)

        resultat = plantes[
            plantes["Nom_scientifique"]
            .astype(str)
            .str.strip()
            .str.lower()
            == str(nom).strip().lower()
        ]

        if resultat.empty:
            return None

        return resultat.iloc[0].to_dict()

    except Exception as e:
        print("Erreur :", e)
        return None

def main():

    afficher_titre(
        "SENTOX - ENRICHISSEMENT PUBCHEM"
    )

    # --------------------------------------------------------
    # VERIFICATION DU FICHIER
    # --------------------------------------------------------

    if not os.path.exists(INPUT_FILE):

        print()
        print("ERREUR : fichier introuvable")
        print(INPUT_FILE)
        input("\nAppuyez sur Entree pour terminer...")
        return

    print()
    print("Base utilisée :")
    print(INPUT_FILE)

    # --------------------------------------------------------
    # SAUVEGARDE DE SECURITE
    # --------------------------------------------------------

    try:

        shutil.copy2(
            INPUT_FILE,
            BACKUP_FILE
        )

        print()
        print("Sauvegarde de sécurité créée :")
        print(BACKUP_FILE)

    except Exception as e:

        print()
        print("ERREUR lors de la sauvegarde :")
        print(e)
        input("\nAppuyez sur Entree pour terminer...")
        return

    # --------------------------------------------------------
    # LECTURE ROBUSTE DU CSV
    # --------------------------------------------------------

    try:

        try:

            df = pd.read_csv(
                INPUT_FILE,
                encoding="utf-8-sig",
                low_memory=False,
                dtype=object
            )

        except UnicodeDecodeError:

            df = pd.read_csv(
                INPUT_FILE,
                encoding="latin1",
                low_memory=False,
                dtype=object
            )

    except Exception as e:

        print()
        print("ERREUR lors de la lecture du CSV :")
        print(e)

        input("\nAppuyez sur Entree pour terminer...")
        return

    # --------------------------------------------------------
    # IMPORTANT :
    # TOUTES LES COLONNES RESTENT EN OBJECT
    # --------------------------------------------------------

    df = df.astype(object)

    print()
    print(
        "Molecules dans la base :",
        len(df)
    )

    # --------------------------------------------------------
    # IDENTIFICATION DE LA COLONNE NOM
    # --------------------------------------------------------

    colonne_nom = trouver_colonne_nom(df)

    if colonne_nom is None:

        print()
        print(
            "ERREUR : aucune colonne de nom de molecule trouvee."
        )

        print()
        print("Colonnes disponibles :")

        for col in df.columns:
            print("-", col)

        input("\nAppuyez sur Entree pour terminer...")
        return

    print()
    print(
        "Colonne utilisée pour PubChem :",
        colonne_nom
    )

    # --------------------------------------------------------
    # COLONNES SENTOX
    # --------------------------------------------------------

    colonnes_pubchem = [
        "PubChem_CID",
        "Formule_PubChem",
        "Masse_molaire_PubChem",
        "LogP_PubChem",
        "HBD_PubChem",
        "HBA_PubChem",
        "TPSA_PubChem",
        "Atomes_lourds_PubChem",
        "Anneaux_PubChem",
        "Liaisons_rotatables_PubChem",
        "SMILES",
        "SMILES_isomerique",
        "IUPAC_Name",
        "PubChem_Statut"
    ]

    colonnes_rdkit = [
        "RDKit_Masse_molaire",
        "RDKit_LogP",
        "RDKit_HBD",
        "RDKit_HBA",
        "RDKit_TPSA",
        "RDKit_Atomes_lourds",
        "RDKit_Anneaux",
        "RDKit_Liaisons_rotatables"
    ]

    # --------------------------------------------------------
    # CREATION DES COLONNES
    # --------------------------------------------------------

    for colonne in colonnes_pubchem + colonnes_rdkit:

        if colonne not in df.columns:

            df[colonne] = ""

    # IMPORTANT :
    # on reconvertit en object après création
    df = df.astype(object)

    # --------------------------------------------------------
    # TRAITEMENT
    # --------------------------------------------------------

    total = len(df)

    trouves = 0
    non_trouves = 0
    erreurs = 0

    afficher_titre(
        "RECHERCHE PUBCHEM"
    )

    for index in range(total):

        nom = df.at[
            index,
            colonne_nom
        ]

        print(
            f"[{index + 1}/{total}] {nom}"
        )

        if nom is None or str(nom).strip() == "":

            df.at[
                index,
                "PubChem_Statut"
            ] = "Nom_absent"

            non_trouves += 1

            continue

        try:

            data = rechercher_pubchem(nom)

            if data is None:

                df.at[
                    index,
                    "PubChem_Statut"
                ] = "Non_trouve"

                non_trouves += 1

                continue

            trouves += 1

            # ------------------------------------------------
            # PUBCHEM
            # ------------------------------------------------

            df.at[
                index,
                "PubChem_CID"
            ] = data.get("CID", "")

            df.at[
                index,
                "Formule_PubChem"
            ] = data.get(
                "MolecularFormula",
                ""
            )

            df.at[
                index,
                "Masse_molaire_PubChem"
            ] = data.get(
                "MolecularWeight",
                ""
            )

            df.at[
                index,
                "LogP_PubChem"
            ] = data.get(
                "XLogP",
                ""
            )

            df.at[
                index,
                "HBD_PubChem"
            ] = data.get(
                "HBondDonorCount",
                ""
            )

            df.at[
                index,
                "HBA_PubChem"
            ] = data.get(
                "HBondAcceptorCount",
                ""
            )

            df.at[
                index,
                "TPSA_PubChem"
            ] = data.get(
                "TPSA",
                ""
            )

            df.at[
                index,
                "Atomes_lourds_PubChem"
            ] = data.get(
                "HeavyAtomCount",
                ""
            )

            df.at[
                index,
                "Liaisons_rotatables_PubChem"
            ] = data.get(
                "RotatableBondCount",
                ""
            )

            df.at[
                index,
                "SMILES"
            ] = data.get(
                "ConnectivitySMILES",
                data.get(
                    "CanonicalSMILES",
                    ""
                )
            )

            df.at[
                index,
                "SMILES_isomerique"
            ] = data.get(
                "SMILES",
                data.get(
                    "IsomericSMILES",
                    ""
                )
            )

            df.at[
                index,
                "IUPAC_Name"
            ] = data.get(
                "IUPACName",
                ""
            )

            df.at[
                index,
                "PubChem_Statut"
            ] = "Trouve"

            # ------------------------------------------------
            # RDKit
            # ------------------------------------------------

            smiles = df.at[
                index,
                "SMILES_isomerique"
            ]

            if not smiles:

                smiles = df.at[
                    index,
                    "SMILES"
                ]

            rdkit_data = calculer_rdkit(
                smiles
            )

            for cle, valeur in rdkit_data.items():

                df.at[
                    index,
                    cle
                ] = valeur

        except Exception as e:

            erreurs += 1

            df.at[
                index,
                "PubChem_Statut"
            ] = "Erreur"

            print(
                "  ERREUR :",
                str(e)[:100]
            )

        # ----------------------------------------------------
        # PAUSE POUR RESPECTER L'API PUBCHEM
        # ----------------------------------------------------

        time.sleep(0.25)

        # ----------------------------------------------------
        # SAUVEGARDE INTERMEDIAIRE
        # ----------------------------------------------------

        if (index + 1) % 100 == 0:

            try:

                df.to_csv(
                    OUTPUT_FILE,
                    index=False,
                    encoding="utf-8-sig"
                )

                print()
                print(
                    "  Sauvegarde intermédiaire :",
                    index + 1,
                    "molécules"
                )

            except Exception as e:

                print(
                    "  Attention sauvegarde :",
                    e
                )

    # --------------------------------------------------------
    # SAUVEGARDE FINALE
    # --------------------------------------------------------

    try:

        df.to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

    except Exception as e:

        print()
        print(
            "ERREUR lors de la sauvegarde finale :"
        )
        print(e)

        input("\nAppuyez sur Entree pour terminer...")
        return

    # --------------------------------------------------------
    # RAPPORT
    # --------------------------------------------------------

    afficher_titre(
        "ENRICHISSEMENT TERMINE"
    )

    print()
    print(
        "Molecules initiales :",
        total
    )

    print(
        "Trouvées sur PubChem :",
        trouves
    )

    print(
        "Non trouvées :",
        non_trouves
    )

    print(
        "Erreurs :",
        erreurs
    )

    print()
    print(
        "Base enrichie :"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "Sauvegarde originale :"
    )

    print(
        BACKUP_FILE
    )

    print()
    print("=" * 70)
    print(
        "SENTOX DATABASE ENRICHIE : OK"
    )
    print("=" * 70)

    input(
        "\nAppuyez sur Entree pour terminer..."
    )
def sauvegarder_enrichissement(plant_id):
    """
    Recherche les constituants d'une plante,
    récupère les données PubChem et les sauvegarde
    dans un fichier CSV enrichi.
    """
    import os
    import pandas as pd

    resultats = enrichir_constituants(plant_id)

    if not resultats:
        print(f"Aucun résultat à sauvegarder pour {plant_id}")
        return []

    fichier_sortie = r"C:\SENTOX\data\constituants_enrichis.csv"

    df_nouveau = pd.DataFrame(resultats)

    # Si le fichier existe déjà, on ajoute les nouveaux résultats
    if os.path.exists(fichier_sortie):
        df_existant = pd.read_csv(fichier_sortie)

        df_final = pd.concat(
            [df_existant, df_nouveau],
            ignore_index=True
        )

        # Évite les doublons
        if "Plant_ID" in df_final.columns and "Constituant" in df_final.columns:
            df_final = df_final.drop_duplicates(
                subset=["Plant_ID", "Constituant"],
                keep="last"
            )
    else:
        df_final = df_nouveau

    df_final.to_csv(
        fichier_sortie,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 70)
    print("SENTOX : SAUVEGARDE PUBCHEM TERMINÉE")
    print("=" * 70)
    print(f"Plante : {plant_id}")
    print(f"Résultats sauvegardés : {len(df_nouveau)}")
    print(f"Fichier : {fichier_sortie}")
    print("=" * 70)

    return resultats

# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()