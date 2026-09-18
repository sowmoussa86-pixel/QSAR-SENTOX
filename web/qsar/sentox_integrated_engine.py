from web.qsar.sentox_toxicology_database import analyser_cid
from qsar.qsar_engine import predire_ld50_qsar


def analyser_cid_integre(cid):
    """Analyse intégrée SENTOX : données documentées + QSAR."""

    fiche = analyser_cid(cid)

    if fiche["statut"] != "TROUVE":
        return {
            "statut": "NON_TROUVE",
            "CID": cid,
            "molecule": None,
            "toxicologie_documentee": [],
            "prediction_qsar": {
                "statut": "NON_LANCE",
                "raison": "Molecule absente de la base structurelle"
            }
        }

    molecule = fiche["molecule"]
    smiles = molecule.get("SMILES_PubChem")

    if not smiles:
        prediction = {
            "statut": "NON_DISPONIBLE",
            "raison": "SMILES absent"
        }
    else:
        prediction = predire_ld50_qsar(smiles)

    return {
        "statut": "TROUVE",
        "CID": cid,
        "molecule": molecule,
        "toxicologie_documentee": fiche["toxicologie"],
        "prediction_qsar": prediction
    }
