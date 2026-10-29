import requests
from urllib.parse import quote

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

def rechercher_pubchem(nom):
    nom = str(nom).strip()
    if not nom:
        return {"statut": "ERREUR", "message": "Nom vide"}
    url = f"{BASE_URL}/compound/name/{quote(nom, safe="")}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 404:
            return {"statut": "NON_TROUVE", "nom_recherche": nom, "source": url}
        r.raise_for_status()
        prop = r.json()["PropertyTable"]["Properties"][0]
        cid = prop.get("CID")
        return {"statut": "DOCUMENTE", "nom_recherche": nom, "CID": cid, "formule": prop.get("MolecularFormula"), "masse_moleculaire": prop.get("MolecularWeight"), "nom_IUPAC": prop.get("IUPACName"), "source": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}", "base": "PubChem"}
    except requests.Timeout:
        return {"statut": "ERREUR", "message": "Delai PubChem depasse"}
    except requests.RequestException as e:
        return {"statut": "ERREUR", "message": str(e)}
    except (ValueError, KeyError, IndexError, TypeError) as e:
        return {"statut": "ERREUR", "message": f"Reponse PubChem invalide : {e}"}
