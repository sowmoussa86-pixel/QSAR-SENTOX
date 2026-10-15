import json
from pathlib import Path

fichier = Path("data/test_pubchem_toxicologie.json")

if not fichier.exists():
    raise SystemExit("Fichier de test introuvable.")

with fichier.open("r", encoding="utf-8") as f:
    resultats = json.load(f)

mots_cles = (
    "toxic", "lethal", "ld50", "acute exposure",
    "absorption", "distribution", "metabolism",
    "excretion", "pharmacokinetic", "bioavailability"
)

def textes_information(section):
    textes = []
    for info in section.get("Information", []) or []:
        for valeur in info.get("Value", {}).get("StringWithMarkup", []) or []:
            texte = valeur.get("String", "")
            if texte:
                textes.append(texte)
        valeur = info.get("Value", {})
        if valeur.get("Number") is not None:
            textes.append(str(valeur["Number"]))
    return textes

def parcourir(sections, sortie):
    for section in sections or []:
        titre = section.get("TOCHeading", "Section sans titre")
        textes = textes_information(section)
        contenu = " | ".join(textes)

        if any(mot in titre.lower() for mot in mots_cles):
            sortie.append((titre, contenu[:350]))

        parcourir(section.get("Section", []), sortie)

for element in resultats:
    cid = element.get("CID")
    print(f"\n{'=' * 55}\nCID : {cid}")

    if element.get("statut") != "Réponse reçue":
        print("Fiche non récupérée :", element.get("erreur", "erreur inconnue"))
        continue

    rapport = element.get("donnees", {}).get("Record", {})
    sections = rapport.get("Section", [])
    trouvailles = []
    parcourir(sections, trouvailles)

    if not trouvailles:
        print("Aucune section ciblée détectée.")
    else:
        for titre, contenu in trouvailles[:15]:
            print(f"\n[{titre}]")
            print(contenu or "(Section trouvée, texte direct absent)")

print("\nExamen terminé : aucun fichier de données modifié.")
