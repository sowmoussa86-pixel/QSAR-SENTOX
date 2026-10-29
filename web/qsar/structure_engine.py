# ============================================================
# SENTOX - MOTEUR DE STRUCTURE MOLECULAIRE 2D / 3D
# ============================================================

from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from rdkit.Chem.Draw import rdMolDraw2D
import base64


# ============================================================
# 1. VALIDATION DU SMILES
# ============================================================

def charger_molecule(smiles):
    """
    Transforme un SMILES en molécule RDKit.
    """
    if not smiles:
        return None

    try:
        mol = Chem.MolFromSmiles(str(smiles).strip())

        if mol is None:
            return None

        return mol

    except Exception:
        return None


# ============================================================
# 2. STRUCTURE 2D
# ============================================================

def generer_structure_2d(smiles, largeur=600, hauteur=400):
    """
    Génère une représentation moléculaire 2D au format SVG.

    Retourne un dictionnaire exploitable directement
    par SENTOX.
    """

    mol = charger_molecule(smiles)

    if mol is None:
        return {
            "disponible": False,
            "statut": "ERREUR",
            "message": "SMILES invalide ou non reconnu",
            "svg": None
        }

    try:

        # Génération des coordonnées 2D
        Chem.rdDepictor.Compute2DCoords(mol)

        drawer = rdMolDraw2D.MolDraw2DSVG(
            largeur,
            hauteur
        )

        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()

        svg = drawer.GetDrawingText()

        return {
            "disponible": True,
            "statut": "CALCULÉ — RDKit",
            "moteur": "RDKit",
            "format": "SVG",
            "svg": svg
        }

    except Exception as e:

        return {
            "disponible": False,
            "statut": "ERREUR",
            "message": str(e),
            "svg": None
        }


# ============================================================
# 3. STRUCTURE 3D
# ============================================================

def generer_structure_3d(smiles):
    """
    Génère un conformère moléculaire 3D à partir du SMILES.

    La structure obtenue est un modèle COMPUTATIONNEL,
    et non une structure expérimentale.
    """

    mol = charger_molecule(smiles)

    if mol is None:
        return {
            "disponible": False,
            "statut": "ERREUR",
            "message": "SMILES invalide ou non reconnu"
        }

    try:

        # Ajout des hydrogènes
        mol3d = Chem.AddHs(mol)

        # Génération du conformère 3D
        resultat = AllChem.EmbedMolecule(
            mol3d,
            randomSeed=42
        )

        if resultat != 0:

            return {
                "disponible": False,
                "statut": "ÉCHEC",
                "message": "Impossible de générer le conformère 3D"
            }

        # Optimisation géométrique
        try:
            AllChem.UFFOptimizeMolecule(mol3d)
        except Exception:
            pass

        conformer = mol3d.GetConformer()

        atomes = []

        for atom in mol3d.GetAtoms():

            position = conformer.GetAtomPosition(
                atom.GetIdx()
            )

            atomes.append({
                "index": atom.GetIdx(),
                "element": atom.GetSymbol(),
                "x": float(position.x),
                "y": float(position.y),
                "z": float(position.z)
            })

        liaisons = []

        for bond in mol3d.GetBonds():

            liaisons.append({
                "source": bond.GetBeginAtomIdx(),
                "target": bond.GetEndAtomIdx(),
                "type": str(bond.GetBondType())
            })

        # ====================================================
        # FORMAT PDB POUR LE VISUALISEUR 3D
        # ====================================================

        lignes_pdb = []

        for atom in mol3d.GetAtoms():

            idx = atom.GetIdx()

            position = conformer.GetAtomPosition(idx)

            element = atom.GetSymbol()

            nom_atome = element[:2].upper()

            # Format PDB ATOM
            ligne = (
                f"ATOM  "
                f"{idx + 1:5d} "
                f"{nom_atome:^4s}"
                f" MOL A   1    "
                f"{position.x:8.3f}"
                f"{position.y:8.3f}"
                f"{position.z:8.3f}"
                f"  1.00  0.00          "
                f"{element:>2s}"
            )

            lignes_pdb.append(ligne)

        # Connexions atomiques
        for bond in mol3d.GetBonds():

            a = bond.GetBeginAtomIdx() + 1
            b = bond.GetEndAtomIdx() + 1

            lignes_pdb.append(
                f"CONECT{a:5d}{b:5d}"
            )

        lignes_pdb.append("END")

        pdb_block = "\n".join(lignes_pdb)

        return {

            "disponible": True,

            "statut": "CALCULÉ — RDKit",

            "moteur": "RDKit",

            "mode": "conformère 3D calculé",

            "experimental": False,

            "nombre_atomes": len(atomes),

            "atomes": atomes,

            "liaisons": liaisons,

            # Données 3D destinées au visualiseur
            "mol_block": pdb_block,

            "viewer_format": "pdb",

            "smiles": smiles

        }

    except Exception as e:

        return {

            "disponible": False,

            "statut": "ERREUR",

            "message": str(e)

        }


# ============================================================
# 4. STRUCTURE COMPLETE 2D + 3D
# ============================================================

def analyser_structure(smiles):

    if not smiles:

        return {

            "statut": "NON DISPONIBLE",

            "structure_2d": None,

            "structure_3d": None

        }

    structure_2d = generer_structure_2d(smiles)

    structure_3d = generer_structure_3d(smiles)

    return {

        "statut": "CALCULÉ — RDKit",

        "smiles": smiles,

        "structure_2d": structure_2d,

        "structure_3d": structure_3d

    }
