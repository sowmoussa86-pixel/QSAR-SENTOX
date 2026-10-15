import json
import time
import urllib.request
import urllib.error
from pathlib import Path

cids = [102, 125, 180, 241, 289]
sortie = Path("data/test_pubchem_toxicologie.json")
resultats = []

for cid in cids:
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/"
        f"rest/pug_view/data/compound/{cid}/JSON"
    )
    requete = urllib.request.Request(
        url,
        headers={"User-Agent": "QSAR-SENTOX/1.0"}
    )

    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            donnees = json.loads(reponse.read().decode("utf-8"))

        resultats.append({
            "CID": cid,
            "statut": "Réponse reçue",
            "donnees": donnees
        })
        print(f"CID {cid} : réponse reçue")

    except (urllib.error.URLError, TimeoutError, ValueError) as erreur:
        resultats.append({
            "CID": cid,
            "statut": "Échec de récupération",
            "erreur": str(erreur)
        })
        print(f"CID {cid} : erreur - {erreur}")

    time.sleep(1.2)

sortie.parent.mkdir(parents=True, exist_ok=True)
with sortie.open("w", encoding="utf-8") as f:
    json.dump(resultats, f, ensure_ascii=False)

print("\nRésultats enregistrés dans :", sortie)
print("Réponses reçues :", sum(
    r["statut"] == "Réponse reçue" for r in resultats
), "/", len(cids))
print("Ce test ne valide aucune DL50 et ne modifie pas la base.")
