from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski


def calculer_descripteurs(smiles):
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return {}
    return {
        "Masse_molaire": Descriptors.MolWt(mol),
        "LogP": Crippen.MolLogP(mol),
        "HBD": Lipinski.NumHDonors(mol),
        "HBA": Lipinski.NumHAcceptors(mol),
        "Atomes": mol.GetNumHeavyAtoms(),
        "TPSA": Descriptors.TPSA(mol),
        "Anneaux": Lipinski.RingCount(mol)
    }
