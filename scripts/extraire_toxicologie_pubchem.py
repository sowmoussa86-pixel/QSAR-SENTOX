import json
import re
from pathlib import Path

source = Path("data/test_pubchem_toxicologie.json")
sortie = Path("data/toxicologie_extraite_a_verifier.json")

with source.open(encoding="utf-8") as f:
    donnees = json.load(f)

motif = re.compile(
    r".{0,100}\b(?:LD50|LC50|NOAEL|LOAEL)\b.{0,220}",
    re.IGNORECASE
)

def textes(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for valeur in obj.values():
            yield from textes(valeur)
    elif isinstance(obj, list):
        for valeur in obj:
            yield from textes(valeur)

resultats = []

for entree in donnees:
    cid = entree.get("CID")
    statut = entree.get("statut", "")
    trouve = set()

    for texte in textes(entree.get("donnees", {})):
        for extrait in motif.findall(texte):
            extrait = " ".join(extrait.split())
            if re.search(r"\d", extrait):
                trouve.add(extrait)

    for extrait in sorted(trouve):
        resultats.append({
            "CID": cid,
            "extrait_brut": extrait,
            "statut_validation": "A vérifier",
            "source_recuperation": "PubChem PUG View",
            "statut_requete": statut
        })

sortie.parent.mkdir(parents=True, exist_ok=True)
with sortie.open("w", encoding="utf-8") as f:
    json.dump(resultats, f, ensure_ascii=False, indent=2)

print("Extraits enregistrés :", len(resultats))
print("Fichier :", sortie)
print("Statut : tous les extraits restent à vérifier.")
