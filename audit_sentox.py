import csv
from collections import Counter

csv.field_size_limit(10_000_000)

fichiers = [
    "data/sentox_database_2000_enriched_noms.csv",
    "data/sentox_lot_toxicologie_001_a_verifier.csv",
]

for chemin in fichiers:
    print(f"\n=== {chemin} ===")
    try:
        with open(chemin, encoding="utf-8-sig", newline="") as f:
            lecteur = csv.DictReader(f)
            lignes = list(lecteur)

        print("Nombre de lignes :", len(lignes))
        print("Colonnes :", lecteur.fieldnames)

        if "Statut_donnees" in (lecteur.fieldnames or []):
            print("Statuts :", Counter(
                ligne.get("Statut_donnees", "")
                for ligne in lignes
            ))

        colonnes = [
            "Nom", "CID", "SMILES", "LD50_mg_kg",
            "LogLD50", "Source_toxicologie",
            "Nom_base_SENTOX", "Valeur", "Unite",
            "Point_depart_POD", "Facteur_incertitude",
            "Source_organisme", "Statut_SENTOX"
        ]

        for colonne in colonnes:
            if colonne in (lecteur.fieldnames or []):
                remplis = sum(
                    bool((ligne.get(colonne) or "").strip())
                    for ligne in lignes
                )
                print(f"{colonne} : {remplis}/{len(lignes)} renseignées")

    except Exception as e:
        print("Erreur :", e)
