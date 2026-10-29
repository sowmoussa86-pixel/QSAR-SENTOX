from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski


def calculer_adme_structure(smiles):

    if not smiles:
        return {
            "statut": "non disponible",
            "source": None
        }

    mol = Chem.MolFromSmiles(str(smiles))

    if mol is None:
        return {
            "statut": "erreur",
            "source": "RDKit"
        }

    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    rot = Lipinski.NumRotatableBonds(mol)

    return {
        "statut": "calculé",
        "source": "RDKit",
        "mode": "indicateur structurel",
        "masse_molaire": round(mw, 3),
        "logP": round(logp, 3),
        "TPSA": round(tpsa, 3),
        "HBD": hbd,
        "HBA": hba,
        "liaisons_rotatables": rot
    }