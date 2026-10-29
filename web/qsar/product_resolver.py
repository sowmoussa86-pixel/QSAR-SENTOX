
"""
QSAR-SENTOX — Résolution de l'identité d'un produit.
Recherche par nom commercial, substance active, SMILES ou CID PubChem.

Ce module recherche des correspondances candidates.
Il ne garantit pas l'identité d'un médicament et ne réalise pas de prédiction QSAR.
"""

import json
import re
import urllib.parse
import urllib.request
import urllib.error


PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


def normaliser_nom(nom):
    """Normalise un texte pour comparer des noms."""
    if not isinstance(nom, str):
        return ""
    return re.sub(r"\s+", " ", nom.strip()).casefold()


def requete_json(url, timeout=10):
    """Interroge une API HTTPS et retourne les données JSON."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "QSAR-SENTOX/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def rechercher_pubchem(nom):
    """
    Recherche une substance par nom dans PubChem.
    Retourne des candidats à vérifier, et non une identification garantie.
    """
    nom = (nom or "").strip()
    if not nom:
        return {
            "statut": "saisie_manquante",
            "nom_saisi": nom,
            "candidats": []
        }

    nom_url = urllib.parse.quote(nom, safe="")
    url = f"{PUBCHEM_BASE}/compound/name/{nom_url}/cids/JSON"
    resultat = requete_json(url)

    if not resultat:
        return {
            "statut": "aucune_correspondance_confirmee",
            "nom_saisi": nom,
            "candidats": [],
            "message": (
                "Aucun résultat récupéré. Vérifier la connexion, "
                "le nom ou les sources."
            )
        }

    cids = resultat.get("IdentifierList", {}).get("CID", [])
    cids = cids[:5]
    candidats = []

    for cid in cids:
        details_url = (
            f"{PUBCHEM_BASE}/compound/cid/{cid}/property/"
            "Title,IUPACName,CanonicalSMILES,IsomericSMILES,"
            "MolecularFormula,MolecularWeight/JSON"
        )
        details = requete_json(details_url)
        if not details:
            continue

        proprietes = details.get("PropertyTable", {}).get("Properties", [])
        if not proprietes:
            continue

        p = proprietes[0]
        candidats.append({
            "nom_recherche": nom,
            "cid": p.get("CID"),
            "nom_pubchem": p.get("Title"),
            "nom_iupac": p.get("IUPACName"),
            "smiles_canonique": p.get("ConnectivitySMILES"),
            "smiles_isomerique": p.get("SMILES"),
            "formule": p.get("MolecularFormula"),
            "masse_molaire": p.get("MolecularWeight"),
            "source": "PubChem",
            "statut_identite": "candidat_a_verifier"
        })

    return {
        "statut": (
            "candidats_trouves" if candidats
            else "aucun_candidat_exploitable"
        ),
        "nom_saisi": nom,
        "candidats": candidats,
        "avertissement": (
            "Vérifier l'identité, la forme et la substance active. "
            "Un nom commercial n'identifie pas toujours une molécule unique."
        )
    }


def resoudre_produit(
    nom_connu,
    nom_substance=None,
    smiles=None,
    pubchem_cid=None
):
    """
    Point d'entrée de SENTOX.
    Accepte une seule information connue. Le nom commercial doit être
    confirmé par une source de médicaments avant de conclure sur la composition.
    """
    nom = (nom_substance or "").strip() or (nom_connu or "").strip()

    if pubchem_cid:
        cid = str(pubchem_cid).strip()
        if cid.isdigit():
            details_url = (
                f"{PUBCHEM_BASE}/compound/cid/{cid}/property/"
                "Title,IUPACName,CanonicalSMILES,IsomericSMILES,"
                "MolecularFormula,MolecularWeight/JSON"
            )
            resultat = requete_json(details_url)
            if resultat:
                proprietes = resultat.get("PropertyTable", {}).get(
                    "Properties", []
                )
                if proprietes:
                    p = proprietes[0]
                    return {
                        "statut": "identifiant_retrouve_a_verifier",
                        "nom_saisi": nom_connu,
                        "candidats": [{
                            "cid": p.get("CID"),
                            "nom_pubchem": p.get("Title"),
                            "nom_iupac": p.get("IUPACName"),
                            "smiles_canonique": p.get("ConnectivitySMILES"),
                            "smiles_isomerique": p.get("SMILES"),
                            "formule": p.get("MolecularFormula"),
                            "masse_molaire": p.get("MolecularWeight"),
                            "source": "PubChem",
                            "statut_identite": "candidat_a_verifier"
                        }]
                    }

    if smiles and not nom:
        return {
            "statut": "verification_smiles_requise",
            "nom_saisi": nom_connu,
            "smiles_fourni": smiles,
            "candidats": [],
            "message": "La structure doit être validée avant l'analyse."
        }

    return rechercher_pubchem(nom)
