# ============================================================
# SENTOX — STRUCTURE MOLÉCULAIRE 2D / 3D
# ============================================================

"""
SENTOX — Module de structure moléculaire

Fonctions :
- identification moléculaire
- CID PubChem
- SMILES
- InChI
- formule moléculaire
- poids moléculaire
- structure 2D
- structure 3D
- préparation à l'analyse de liaison

IMPORTANT :
La présence d'une structure 3D ne signifie pas qu'une
interaction biologique est démontrée.

Une analyse de liaison réelle nécessitera ensuite un
module de docking / interaction moléculaire.
"""

from typing import Any, Dict, Optional


# ============================================================
# 1. CRÉATION D'UNE FICHE MOLÉCULAIRE
# ============================================================

def creer_structure_molecule(
    nom: str,
    cid: Optional[int] = None,
    smiles: Optional[str] = None,
    inchi: Optional[str] = None,
    formule: Optional[str] = None,
    poids_moleculaire: Optional[float] = None,
) -> Dict[str, Any]:

    return {
        "nom": nom,

        "cid_pubchem": cid,

        "smiles": smiles,

        "inchi": inchi,

        "formule_moleculaire": formule,

        "poids_moleculaire": poids_moleculaire,

        "structure_2d": {
            "disponible": cid is not None,
            "source": "PubChem" if cid else None,
            "url": (
                f"https://pubchem.ncbi.nlm.nih.gov/image/"
                f"imagefly.cgi?cid={cid}&width=600&height=600"
                if cid else None
            )
        },

        "structure_3d": {
            "disponible": cid is not None,
            "source": "PubChem" if cid else None,
            "url": (
                f"https://pubchem.ncbi.nlm.nih.gov/compound/"
                f"{cid}#section=3D-Conformer"
                if cid else None
            )
        },

        "statut": (
            "documenté"
            if cid is not None
            else "non disponible"
        )
    }


# ============================================================
# 2. INFORMATIONS MOLÉCULAIRES
# ============================================================

def informations_moleculaires(
    nom: str,
    cid: Optional[int] = None,
    smiles: Optional[str] = None,
    formule: Optional[str] = None,
    poids_moleculaire: Optional[float] = None,
) -> Dict[str, Any]:

    return {
        "nom": nom,

        "identification": {
            "CID": cid,
            "SMILES": smiles,
            "formule": formule
        },

        "proprietes": {
            "poids_moleculaire": poids_moleculaire
        },

        "statut": (
            "documenté"
            if any([
                cid is not None,
                smiles is not None,
                formule is not None,
                poids_moleculaire is not None
            ])
            else "non disponible"
        )
    }


# ============================================================
# 3. PRÉPARATION À L'ANALYSE DE LIAISON
# ============================================================

def preparer_analyse_liaison(
    molecule_a: Dict[str, Any],
    molecule_b: Dict[str, Any]
) -> Dict[str, Any]:

    nom_a = molecule_a.get(
        "nom",
        "Molécule A"
    )

    nom_b = molecule_b.get(
        "nom",
        "Molécule B"
    )

    return {

        "molecule_a": nom_a,

        "molecule_b": nom_b,

        "smiles_a": molecule_a.get(
            "smiles"
        ),

        "smiles_b": molecule_b.get(
            "smiles"
        ),

        "structure_3d_a": molecule_a.get(
            "structure_3d"
        ),

        "structure_3d_b": molecule_b.get(
            "structure_3d"
        ),

        "analyse": {

            "liaison_possible": "À déterminer",

            "type": "À déterminer",

            "affinite": "À déterminer",

            "energie_liaison": "À déterminer",

            "sites_potentiels": [],

            "statut": "préparation"
        },

        "avertissement": (
            "La possibilité d'une liaison moléculaire ne "
            "peut pas être confirmée uniquement à partir "
            "d'une structure 2D ou 3D."
        )
    }


# ============================================================
# 4. ANALYSE DES ÉLÉMENTS D'UN MÉLANGE
# ============================================================

def preparer_melange_moleculaire(
    molecules: list
) -> Dict[str, Any]:

    fiches = []

    for molecule in molecules:

        fiche = creer_structure_molecule(
            nom=molecule.get(
                "nom",
                "Inconnu"
            ),
            cid=molecule.get(
                "cid"
            ),
            smiles=molecule.get(
                "smiles"
            ),
            inchi=molecule.get(
                "inchi"
            ),
            formule=molecule.get(
                "formule"
            ),
            poids_moleculaire=molecule.get(
                "poids_moleculaire"
            )
        )

        fiches.append(
            fiche
        )

    return {

        "nombre_molecules": len(fiches),

        "molecules": fiches,

        "statut": "documenté / calculé / prédit",

        "analyse_liaison": (
            "Préparation des paires moléculaires"
        )
    }


# ============================================================
# 5. GÉNÉRATION DES PAIRES
# ============================================================

def generer_paires_moleculaires(
    molecules: list
) -> list:

    paires = []

    for i in range(len(molecules)):

        for j in range(i + 1, len(molecules)):

            molecule_a = molecules[i]
            molecule_b = molecules[j]

            paires.append({

                "molecule_a": molecule_a.get(
                    "nom",
                    f"Molecule_{i + 1}"
                ),

                "molecule_b": molecule_b.get(
                    "nom",
                    f"Molecule_{j + 1}"
                ),

                "analyse": "À effectuer",

                "liaison": "À déterminer",

                "affinite": "À déterminer",

                "statut": "préparation"
            })

    return paires


# ============================================================
# 6. RÉSUMÉ POUR L'INTERFACE SENTOX
# ============================================================

def resume_structure(
    molecule: Dict[str, Any]
) -> Dict[str, Any]:

    return {

        "nom": molecule.get(
            "nom"
        ),

        "CID": molecule.get(
            "cid_pubchem"
        ),

        "SMILES": molecule.get(
            "smiles"
        ),

        "formule": molecule.get(
            "formule_moleculaire"
        ),

        "poids_moleculaire": molecule.get(
            "poids_moleculaire"
        ),

        "structure_2d": molecule.get(
            "structure_2d"
        ),

        "structure_3d": molecule.get(
            "structure_3d"
        ),

        "statut": molecule.get(
            "statut"
        )
    }


# ============================================================
# 7. TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SENTOX — TEST STRUCTURE MOLÉCULAIRE")
    print("=" * 60)

    paracetamol = creer_structure_molecule(
        nom="Paracétamol",
        cid=1983,
        smiles="CC(=O)NC1=CC=C(O)C=C1",
        formule="C8H9NO2",
        poids_moleculaire=151.16
    )

    print("\nNom :")
    print(paracetamol["nom"])

    print("\nCID PubChem :")
    print(paracetamol["cid_pubchem"])

    print("\nSMILES :")
    print(paracetamol["smiles"])

    print("\nFormule :")
    print(paracetamol["formule_moleculaire"])

    print("\nStructure 2D :")
    print(paracetamol["structure_2d"]["url"])

    print("\nStructure 3D :")
    print(paracetamol["structure_3d"]["url"])

    print("\nModule structure moléculaire SENTOX opérationnel.")
