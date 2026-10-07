# ============================================================
# SENTOX — MOTEUR DE SIMILARITÉ MOLÉCULAIRE V2
# MorganGenerator + Tanimoto
# Préparation du domaine d'applicabilité QSAR
# ============================================================

import os
import pandas as pd

from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator


# ------------------------------------------------------------
# 1. CHARGEMENT MOLÉCULE
# ------------------------------------------------------------

def charger_molecule(smiles):
    """Convertit un SMILES en molécule RDKit."""
    if not smiles:
        return None

    try:
        return Chem.MolFromSmiles(str(smiles).strip())
    except Exception:
        return None


# ------------------------------------------------------------
# 2. MORGAN FINGERPRINT MODERNE
# ------------------------------------------------------------

def calculer_fingerprint(smiles, radius=2, n_bits=2048):
    """
    Calcule une empreinte Morgan avec l'API moderne RDKit.

    radius=2 correspond à une empreinte de type ECFP4.
    """

    mol = charger_molecule(smiles)

    if mol is None:
        return {
            "statut": "ERREUR",
            "message": "SMILES invalide ou non reconnu"
        }

    try:
        generator = rdFingerprintGenerator.GetMorganGenerator(
            radius=radius,
            fpSize=n_bits
        )

        fp = generator.GetFingerprint(mol)

        return {
            "statut": "CALCULÉ — RDKit",
            "moteur": "RDKit",
            "type": "Morgan",
            "radius": radius,
            "n_bits": n_bits,
            "fingerprint": fp
        }

    except Exception as e:
        return {
            "statut": "ERREUR",
            "message": str(e)
        }


# ------------------------------------------------------------
# 3. SIMILARITÉ TANIMOTO
# ------------------------------------------------------------

def calculer_similarite_tanimoto(smiles_a, smiles_b):

    fp_a = calculer_fingerprint(smiles_a)
    fp_b = calculer_fingerprint(smiles_b)

    if fp_a.get("statut") != "CALCULÉ — RDKit":
        return None

    if fp_b.get("statut") != "CALCULÉ — RDKit":
        return None

    score = DataStructs.TanimotoSimilarity(
        fp_a["fingerprint"],
        fp_b["fingerprint"]
    )

    return round(float(score), 4)


# ------------------------------------------------------------
# 4. RECHERCHE DES MOLÉCULES SIMILAIRES
# ------------------------------------------------------------

def rechercher_similaires(
    smiles_recherche,
    chemin_base="data/molecules.csv",
    top_n=10,
    seuil_minimum=0.0
):
    """
    Recherche les molécules les plus similaires
    dans la base SENTOX.
    """

    mol_recherche = charger_molecule(smiles_recherche)

    if mol_recherche is None:
        return {
            "statut": "ERREUR",
            "message": "SMILES de recherche invalide",
            "resultats": []
        }

    generator = rdFingerprintGenerator.GetMorganGenerator(
        radius=2,
        fpSize=2048
    )

    fp_recherche = generator.GetFingerprint(
        mol_recherche
    )

    if not os.path.exists(chemin_base):
        return {
            "statut": "ERREUR",
            "message": f"Base introuvable : {chemin_base}",
            "resultats": []
        }

    try:
        df = pd.read_csv(chemin_base)
    except Exception as e:
        return {
            "statut": "ERREUR",
            "message": str(e),
            "resultats": []
        }

    resultats = []

    for _, ligne in df.iterrows():

        smiles = ligne.get("SMILES")

        if pd.isna(smiles) or not str(smiles).strip():
            continue

        mol = charger_molecule(smiles)

        if mol is None:
            continue

        try:

            fp = generator.GetFingerprint(mol)

            score = DataStructs.TanimotoSimilarity(
                fp_recherche,
                fp
            )

            score = round(float(score), 4)

            if score >= seuil_minimum:

                resultats.append({
                    "ID": ligne.get("ID"),
                    "Nom": ligne.get("Nom"),
                    "SMILES": str(smiles),
                    "similarite_tanimoto": score,
                    "LD50_mg_kg": ligne.get("LD50_mg_kg"),
                    "Toxicite": ligne.get("Toxicite"),
                    "Source": ligne.get("Source")
                })

        except Exception:
            continue

    resultats.sort(
        key=lambda x: x["similarite_tanimoto"],
        reverse=True
    )

    # --------------------------------------------------------
    # STATISTIQUES DE SIMILARITÉ
    # --------------------------------------------------------

    scores = [
        r["similarite_tanimoto"]
        for r in resultats
    ]

    if scores:
        meilleure = max(scores)
        moyenne_top = sum(scores[:min(5, len(scores))]) / min(5, len(scores))
    else:
        meilleure = None
        moyenne_top = None

    return {
        "statut": "CALCULÉ — RDKit",
        "moteur": "RDKit",
        "methode": "Morgan Fingerprint + Tanimoto",
        "radius": 2,
        "n_bits": 2048,

        "nombre_molecules_comparees": len(resultats),

        "meilleure_similarite": meilleure,

        "moyenne_top5": (
            round(moyenne_top, 4)
            if moyenne_top is not None
            else None
        ),

        "resultats": resultats[:top_n]
    }


# ------------------------------------------------------------
# 5. PROFIL DE DOMAINE D'APPLICABILITÉ
# ------------------------------------------------------------

def evaluer_domaine_applicabilite(
    smiles_recherche,
    chemin_base="data/molecules.csv",
    top_n=10
):
    """
    Produit un profil descriptif de similarité.

    IMPORTANT :
    aucun seuil toxicologique ou seuil de validité QSAR
    n'est imposé ici.

    Les valeurs doivent être interprétées en fonction
    du jeu de données et du modèle QSAR utilisé.
    """

    recherche = rechercher_similaires(
        smiles_recherche,
        chemin_base=chemin_base,
        top_n=top_n
    )

    if recherche.get("statut") != "CALCULÉ — RDKit":
        return recherche

    meilleure = recherche.get(
        "meilleure_similarite"
    )

    moyenne_top5 = recherche.get(
        "moyenne_top5"
    )

    nombre = recherche.get(
        "nombre_molecules_comparees",
        0
    )

    return {
        "statut": "CALCULÉ — RDKit",
        "moteur": "RDKit",

        "methode": (
            "Morgan Fingerprint + Tanimoto"
        ),

        "nombre_references": nombre,

        "meilleure_similarite": meilleure,

        "moyenne_top5": moyenne_top5,

        "interpretation": (
            "Profil de similarité calculé. "
            "La décision concernant le domaine "
            "d'applicabilité doit être définie "
            "en fonction du jeu d'apprentissage, "
            "du modèle QSAR et de sa validation."
        ),

        "avertissement": (
            "La similarité moléculaire ne constitue "
            "pas à elle seule une preuve de toxicité "
            "ou d'effet biologique."
        ),

        "voisins": recherche.get(
            "resultats",
            []
        )
    }


# ------------------------------------------------------------
# 6. TEST
# ------------------------------------------------------------

def verifier_similarity():

    smiles = "CC(=O)NC1=CC=C(C=C1)O"

    return evaluer_domaine_applicabilite(
        smiles,
        chemin_base="data/molecules.csv",
        top_n=5
    )
