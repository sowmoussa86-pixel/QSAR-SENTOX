import csv
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from risk.controle_compatibilite import controler_donnee

source = RACINE / "data" / "registre_sources_toxicologie.csv"
sortie = RACINE / "data" / "rapport_controle_toxicologie.csv"

with source.open(encoding="utf-8-sig", newline="") as f:
    donnees = list(csv.DictReader(f))

champs = [
    "substance", "CID", "endpoint", "espece", "voie",
    "valeur", "unite", "reference", "statut",
    "erreurs_controle", "alertes_controle", "decision"
]

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()

    for d in donnees:
        erreurs, alertes = controler_donnee(d)
        ligne = dict(d)
        ligne["erreurs_controle"] = " ; ".join(erreurs)
        ligne["alertes_controle"] = " ; ".join(alertes)
        ligne["decision"] = "A VERIFIER - NON VALIDEE"
        writer.writerow({k: ligne.get(k, "") for k in champs})

print("Rapport créé :", sortie.relative_to(RACINE))
print("Données examinées :", len(donnees))
print("Décision : toutes les données restent non validées.")
