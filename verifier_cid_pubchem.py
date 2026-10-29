import pandas as pd
import requests

fichier = "data/sentox_database_2000_enriched_noms.csv"
df = pd.read_csv(fichier)

session = requests.Session()

print("Verification des 10 premiers CID\n")

for _, ligne in df[["Nom_PubChem", "CID"]].head(10).iterrows():
    nom = ligne["Nom_PubChem"]
    cid = int(ligne["CID"])

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        f"compound/cid/{cid}/property/Title,CanonicalSMILES/JSON"
    )

    try:
        reponse = session.get(url, timeout=20)

        if reponse.status_code == 200:
            donnees = reponse.json()
            proprietes = donnees["PropertyTable"]["Properties"][0]
            titre = proprietes.get("Title", "Titre absent")
            print(f"Base : {nom} | CID : {cid} | PubChem : {titre}")
        else:
            print(f"Base : {nom} | CID : {cid} | HTTP : {reponse.status_code}")

    except Exception as erreur:
        print(f"CID : {cid} | Erreur : {erreur}")