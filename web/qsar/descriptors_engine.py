
# ============================================================
# SENTOX — MOTEUR DE DESCRIPTEURS MOLÉCULAIRES RDKit
# V2.1
# ============================================================

from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors


def charger_molecule(smiles):
    """
    Transforme un SMILES en objet moléculaire RDKit.
    """

    if not smiles:
        return None

    try:
        mol = Chem.MolFromSmiles(
            str(smiles).strip()
        )

        return mol

    except Exception:
        return None


def calculer_descripteurs_rdkit(smiles):
    """
    Calcule un ensemble de descripteurs moléculaires
    standards à partir d'un SMILES.

    Les valeurs sont calculées par RDKit.
    Elles ne constituent pas à elles seules
    une prédiction toxicologique.
    """

    mol = charger_molecule(smiles)

    if mol is None:

        return {
            "statut": "ERREUR",
            "message": "SMILES invalide ou non reconnu",
            "smiles": smiles
        }

    try:

        resultats = {

            # ------------------------------------------------
            # IDENTIFICATION STRUCTURALE
            # ------------------------------------------------

            "formule_brute":
                rdMolDescriptors.CalcMolFormula(mol),

            "masse_molaire":
                round(
                    Descriptors.MolWt(mol),
                    4
                ),

            # ------------------------------------------------
            # PROPRIETES PHYSICO-CHIMIQUES
            # ------------------------------------------------

            "logP":
                round(
                    Crippen.MolLogP(mol),
                    4
                ),

            "tpsa":
                round(
                    rdMolDescriptors.CalcTPSA(mol),
                    4
                ),

            # ------------------------------------------------
            # LIAISONS HYDROGENE
            # ------------------------------------------------

            "HBD":
                int(
                    Lipinski.NumHDonors(mol)
                ),

            "HBA":
                int(
                    Lipinski.NumHAcceptors(mol)
                ),

            # ------------------------------------------------
            # TOPOLOGIE
            # ------------------------------------------------

            "nombre_atomes_lourds":
                int(
                    Lipinski.HeavyAtomCount(mol)
                ),

            "nombre_anneaux":
                int(
                    Lipinski.RingCount(mol)
                ),

            "anneaux_aromatiques":
                int(
                    rdMolDescriptors.CalcNumAromaticRings(mol)
                ),

            "liaisons_rotatables":
                int(
                    Lipinski.NumRotatableBonds(mol)
                ),

            # ------------------------------------------------
            # HYBRIDATION / STRUCTURE
            # ------------------------------------------------

            "fraction_CSP3":
                round(
                    rdMolDescriptors.CalcFractionCSP3(mol),
                    4
                ),

            "charge_formelle":
                int(
                    Chem.GetFormalCharge(mol)
                ),

            
            # ------------------------------------------------
            # COMPTAGE ATOMIQUE
            # ------------------------------------------------

            "nombre_carbone":
                sum(
                    1
                    for atom in mol.GetAtoms()
                    if atom.GetSymbol() == "C"
                ),

            "nombre_hydrogene":
                sum(
                    int(atom.GetTotalNumHs())
                    for atom in mol.GetAtoms()
                ),

            "nombre_azote":
                sum(
                    1
                    for atom in mol.GetAtoms()
                    if atom.GetSymbol() == "N"
                ),

            "nombre_oxygene":
                sum(
                    1
                    for atom in mol.GetAtoms()
                    if atom.GetSymbol() == "O"
                ),

            # Nombre total d'atomes, hydrogènes implicites inclus
                        "nombre_atomes":
                int(
                    mol.GetNumAtoms()
                    + sum(
                        atom.GetTotalNumHs()
                        for atom in mol.GetAtoms()
                    )
                ),


            # ------------------------------------------------
            # INFORMATION RDKit
            # ------------------------------------------------

            "nombre_liaisons":
                int(
                    mol.GetNumBonds()
                ),

            "smiles":
                Chem.MolToSmiles(mol),

            "statut":
                "CALCULÉ — RDKit",

            "moteur":
                "RDKit"

        }

        return resultats

    except Exception as e:

        return {
            "statut": "ERREUR",
            "message": str(e),
            "smiles": smiles
        }


def verifier_descripteurs(smiles):

    resultat = calculer_descripteurs_rdkit(smiles)

    if resultat.get("statut") != "CALCULÉ — RDKit":

        return False

    champs_obligatoires = [
        "masse_molaire",
        "logP",
        "tpsa",
        "HBD",
        "HBA",
        "nombre_anneaux",
        "liaisons_rotatables",
        "fraction_CSP3"
    ]

    return all(
        champ in resultat
        for champ in champs_obligatoires
    )
