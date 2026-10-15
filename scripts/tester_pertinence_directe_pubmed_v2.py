import csv
import re
import unicodedata
from pathlib import Path

source = Path("data/audit_scientifique_preliminaire_23.csv")
sortie = Path("data/audit_pertinence_directe_pubmed_v2.csv")

SYNONYMES = {
    "3-Hydroxybenzyl alcohol": [
        "3-hydroxybenzyl alcohol",
        "m-hydroxybenzyl alcohol",
        "m-hydroxybenzylalcohol",
        "3-hydroxybenzylalcohol"
    ],
    "4-Hydroxybenzyl Alcohol": [
        "4-hydroxybenzyl alcohol",
        "p-hydroxybenzyl alcohol",
        "4-hydroxybenzylalcohol",
        "p-hydroxybenzylalcohol"
    ],
    "Acetone": ["acetone", "propanone", "dimethyl ketone"],
    "Benzene": ["benzene", "benzol"],
    "Catechol": ["catechol", "1,2-benzenediol", "pyrocatechol"],
    "O-Cresol": ["o-cresol", "ortho-cresol", "2-methylphenol"],
    "M-Cresol": ["m-cresol", "meta-cresol", "3-methylphenol"],
    "Salicylic Acid": ["salicylic acid", "2-hydroxybenzoic acid"],
    "Phloroglucinol": ["phloroglucinol", "1,3,5-benzenetriol"]
}

def normaliser(texte):
    texte = unicodedata.normalize("NFKD", texte or "")
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return texte.lower()

def contient_terme(texte, terme):
    texte = normaliser(texte)
    terme = normaliser(terme)
    motif = r"(?<![a-z0-9])" + re.escape(terme) + r"(?![a-z0-9])"
    return bool(re.search(motif, texte))

if not source.exists():
    raise SystemExit(f"Fichier introuvable : {source}")

with source.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

if not lignes:
    raise SystemExit("Aucune référence dans le fichier.")

champs = list(lignes[0].keys())
for nom in (
    "Synonymes_detectes_titre",
    "Synonymes_detectes_resume",
    "Resultat_lexical_v2",
    "Limite_synonymes_v2"
):
    if nom not in champs:
        champs.append(nom)

for ligne in lignes:
    substance = ligne.get("Substances_associees_dans_la_recherche", "").strip()
    titre = ligne.get("Titre", "")
    resume = ligne.get("Abstract_integral", "")

    synonymes = SYNONYMES.get(substance, [substance] if substance else [])
    titre_trouves = [s for s in synonymes if contient_terme(titre, s)]
    resume_trouves = [s for s in synonymes if contient_terme(resume, s)]

    ligne["Synonymes_detectes_titre"] = "; ".join(titre_trouves)
    ligne["Synonymes_detectes_resume"] = "; ".join(resume_trouves)

    if titre_trouves:
        resultat = "Terme ou synonyme détecté dans le titre"
    elif resume_trouves:
        resultat = "Terme ou synonyme détecté dans le résumé"
    else:
        resultat = "Aucun synonyme du dictionnaire détecté"

    ligne["Resultat_lexical_v2"] = resultat
    ligne["Limite_synonymes_v2"] = (
        "Dictionnaire préliminaire ; détection lexicale uniquement. "
        "La présence d'un nom ne prouve pas que l'article étudie sa toxicité."
    )

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(lignes)

print("Références analysées :", len(lignes))
for ligne in lignes:
    print(
        ligne.get("PMID", ""), "|",
        ligne.get("Substances_associees_dans_la_recherche", ""), "|",
        ligne["Resultat_lexical_v2"], "|",
        ligne["Synonymes_detectes_resume"] or "aucun terme détecté"
    )

print("\nFichier créé :", sortie)
print("Fichier source modifié : non")
print("Validation toxicologique : non effectuée")
