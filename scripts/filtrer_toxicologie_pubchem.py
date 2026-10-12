import json
import re
from pathlib import Path

source = Path("data/toxicologie_extraite_a_verifier.json")
sortie = Path("data/toxicologie_filtrees_a_verifier.json")

with source.open(encoding="utf-8") as f:
    donnees = json.load(f)

candidats = []
exclus = []

for ligne in donnees:
    extrait = ligne.get("extrait_brut", "")
    texte = extrait.lower()

    # Écarter les définitions générales sans valeur expérimentale
    if not re.search(r"\b(ld50|lc50|noael|loael)\b", texte):
        exclus.append({**ligne, "motif_filtre": "Aucun indicateur toxicologique reconnu"})
        continue

    # Repérer les données destinées aux organismes aquatiques
    aquatique = bool(re.search(
        r"rainbow trout|fish|fish species|aquatic|daphnia|algae|"
        r"oncorhynchus|mg/l|µg/l|ug/l",
        texte
    ))

    # Repérer les valeurs apparemment associées à un mammifère
    mammifere = bool(re.search(
        r"\b(rat|mouse|mice|rabbit|guinea pig|monkey|dog)\b",
        texte
    ))

    statut = (
        "Candidat mammifère à vérifier"
        if mammifere and not aquatique
        else "À examiner manuellement"
    )

    candidats.append({
        **ligne,
        "indication_mammifere": mammifere,
        "indication_aquatique": aquatique,
        "classement_automatique": statut,
        "statut_validation": "A vérifier"
    })

with sortie.open("w", encoding="utf-8") as f:
    json.dump(candidats, f, ensure_ascii=False, indent=2)

print("Extraits initiaux :", len(donnees))
print("Candidats conservés :", len(candidats))
print("Définitions écartées :", len(exclus))
print("Fichier créé :", sortie)
print("ATTENTION : classement automatique, aucune donnée validée.")
