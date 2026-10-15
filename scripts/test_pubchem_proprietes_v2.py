import csv
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

SOURCE = Path("data/collecteur_multi_sources_v2_test.csv")
SORTIE = Path("data/collecteur_multi_sources_v2_proprietes_test.csv")

PROPRIETES = (
    "MolecularFormula,MolecularWeight,XLogP,"
    "HBondDonorCount,HBondAcceptorCount,TPSA,"
    "SMILES,ConnectivitySMILES,IUPACName"
)

CHAMPS = {
    "MolecularFormula": "Formule_PubChem",
    "MolecularWeight": "Masse_molaire_PubChem",
    "XLogP": "LogP_PubChem",
    "HBondDonorCount": "HBD_PubChem",
    "HBondAcceptorCount": "HBA_PubChem",
    "TPSA": "TPSA_PubChem",
    "SMILES": "SMILES_PubChem",
    "ConnectivitySMILES": "ConnectivitySMILES_PubChem",
    "IUPACName": "IUPAC_Name_PubChem",
}

def recuperer(cid):
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        f"compound/cid/{cid}/property/{PROPRIETES}/JSON"
    )
    req = urllib.request.Request(
        url, headers={"User-Agent": "QSAR-SENTOX research"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    records = data.get("PropertyTable", {}).get("Properties", [])
    return records[0] if records else {}

if not SOURCE.exists():
    raise SystemExit(f"Fichier source absent : {SOURCE}")

with SOURCE.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

if not lignes:
    raise SystemExit("Le fichier source ne contient aucune ligne.")

champs_sortie = list(lignes[0].keys())
for champ in CHAMPS.values():
    if champ not in champs_sortie:
        champs_sortie.append(champ)

if "PubChem_proprietes_statut" not in champs_sortie:
    champs_sortie.append("PubChem_proprietes_statut")

for i, ligne in enumerate(lignes, start=1):
    cid = (ligne.get("CID") or "").strip()
    print(f"[{i}/{len(lignes)}] CID {cid or 'absent'}")

    if not cid.isdigit():
        ligne["PubChem_proprietes_statut"] = "CID absent ou invalide"
        continue

    try:
        donnees = recuperer(cid)
        if not donnees:
            ligne["PubChem_proprietes_statut"] = "Aucune propriété"
        else:
            for cle_source, cle_sortie in CHAMPS.items():
                valeur = donnees.get(cle_source)
                ligne[cle_sortie] = "" if valeur is None else str(valeur)
            ligne["PubChem_proprietes_statut"] = "Propriétés récupérées"
    except Exception as erreur:
        ligne["PubChem_proprietes_statut"] = (
            "Erreur : " + str(erreur)[:150]
        )

    time.sleep(0.25)

with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs_sortie)
    writer.writeheader()
    writer.writerows(lignes)

print("\nFichier de test créé :", SORTIE)
print("Nombre de substances :", len(lignes))
print("Base originale modifiée : non")
print("Validation scientifique : toujours requise")
