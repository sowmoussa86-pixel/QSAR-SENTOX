import csv
from pathlib import Path

fichier = Path("data/registre_sources_toxicologie.csv")
fichier.parent.mkdir(parents=True, exist_ok=True)

lignes = [
    {
        "substance": "Acetone",
        "CID": 180,
        "endpoint": "LD50",
        "espece": "Rat",
        "voie": "Orale",
        "valeur": 5800,
        "unite": "mg/kg",
        "reference": "ATSDR, Toxicological Profile for Acetone",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK590387/",
        "statut": "Source repérée - étude originale à vérifier"
    },
    {
        "substance": "Acetone",
        "CID": 180,
        "endpoint": "LD50",
        "espece": "Rat",
        "voie": "Orale",
        "valeur": 9800,
        "unite": "mg/kg",
        "reference": "European Chemicals Bureau, IUCLID Dataset, via PubChem",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/180",
        "statut": "Source secondaire repérée - à vérifier"
    },
    {
        "substance": "Acetone",
        "CID": 180,
        "endpoint": "LD50",
        "espece": "Rat",
        "voie": "Orale",
        "valeur": 8450,
        "unite": "mg/kg",
        "reference": "European Chemicals Bureau, IUCLID Dataset, via PubChem",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/180",
        "statut": "Conversion publiée - à vérifier"
    },
    {
        "substance": "Benzene",
        "CID": 241,
        "endpoint": "LD50",
        "espece": "Rat",
        "voie": "Orale",
        "valeur": 3306,
        "unite": "mg/kg",
        "reference": "Sax, Dangerous Properties of Industrial Materials, 11e éd., 2004, p. 360",
        "url": "https://pubchem.ncbi.nlm.nih.gov/compound/241",
        "statut": "Référence bibliographique repérée - à vérifier"
    }
]

champs = list(lignes[0].keys())

with fichier.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(lignes)

print("Registre créé :", fichier)
print("Nombre de lignes :", len(lignes))
print("Aucune ligne n'est déclarée validée.")
