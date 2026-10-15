import csv
import re
from pathlib import Path

BASE = Path("data/sentox_database_2000_enriched_noms.csv")
TOX_FILES = [
    Path("data/sentox_toxicology_database.csv"),
    Path("data/sentox_toxicology_v2.csv"),
]
SORTIE = Path("data/sentox_2000_worklist_toxicologie_adme.csv")


def lire_csv(chemin):
    if not chemin.exists():
        return []
    with chemin.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normaliser(texte):
    return re.sub(r"[^a-z0-9]", "", (texte or "").lower())


def valeur(ligne, *champs):
    for champ in champs:
        v = (ligne.get(champ) or "").strip()
        if v:
            return v
    return ""


base = lire_csv(BASE)
if len(base) != 2000:
    raise SystemExit(
        f"ARRÊT : 2000 lignes attendues, {len(base)} trouvées. "
        "Aucun fichier de sortie créé."
    )

donnees_tox = []
for fichier in TOX_FILES:
    for ligne in lire_csv(fichier):
        if valeur(ligne, "Endpoint").upper() == "LD50":
            donnees_tox.append(ligne)

champs_ajoutes = [
    "LD50_valeur_candidate",
    "LD50_unite_candidate",
    "LD50_espece",
    "LD50_sexe",
    "LD50_voie",
    "LD50_duree",
    "LD50_effet",
    "LD50_source",
    "LD50_reference",
    "LD50_statut_validation",
    "ADME_absorption",
    "ADME_distribution",
    "ADME_metabolisme",
    "ADME_excretion",
    "ADME_source",
    "ADME_statut",
]

cles_existantes = set(base[0].keys()) if base else set()
for champ in champs_ajoutes:
    if champ in cles_existantes:
        raise SystemExit(
            f"ARRÊT : le champ {champ} existe déjà. "
            "Aucun fichier de sortie créé."
        )

compteur_dl50 = 0
compteur_adme = 0

for substance in base:
    cid = valeur(substance, "CID", "PubChem_CID")
    nom = valeur(substance, "Nom", "Nom_PubChem", "Nom_original")
    smiles = valeur(substance, "SMILES", "SMILES_PubChem")

    correspondances = []
    for tox in donnees_tox:
        cid_tox = valeur(tox, "CID")
        nom_tox = valeur(tox, "Nom", "Nom_base_SENTOX")
        smiles_tox = valeur(tox, "SMILES")

        # Privilégier l'identifiant PubChem quand il est disponible.
        meme_cid = bool(cid and cid_tox and cid == cid_tox)
        meme_smiles = bool(smiles and smiles_tox and smiles == smiles_tox)
        meme_nom = bool(
            nom and nom_tox
            and normaliser(nom) == normaliser(nom_tox)
        )

        if meme_cid or meme_smiles or meme_nom:
            correspondances.append(tox)

    # N'importer automatiquement une valeur que si une seule
    # entrée candidate est trouvée. Les autres cas nécessitent un contrôle.
    candidats = [
        t for t in correspondances
        if valeur(t, "Valeur")
    ]

    if len(candidats) == 1:
        tox = candidats[0]
        substance["LD50_valeur_candidate"] = valeur(tox, "Valeur")
        substance["LD50_unite_candidate"] = valeur(tox, "Unite")
        substance["LD50_espece"] = valeur(tox, "Espece")
        substance["LD50_sexe"] = valeur(tox, "Sexe")
        substance["LD50_voie"] = valeur(tox, "Voie_exposition")
        substance["LD50_duree"] = valeur(tox, "Duree")
        substance["LD50_effet"] = valeur(tox, "Effet")
        substance["LD50_source"] = valeur(tox, "Source")
        substance["LD50_reference"] = valeur(tox, "Reference")
        substance["LD50_statut_validation"] = (
            "À vérifier - valeur candidate importée"
        )
        compteur_dl50 += 1
    else:
        substance["LD50_valeur_candidate"] = ""
        substance["LD50_unite_candidate"] = ""
        substance["LD50_espece"] = ""
        substance["LD50_sexe"] = ""
        substance["LD50_voie"] = ""
        substance["LD50_duree"] = ""
        substance["LD50_effet"] = ""
        substance["LD50_source"] = ""
        substance["LD50_reference"] = ""
        substance["LD50_statut_validation"] = (
            "À contrôler - correspondances multiples"
            if len(candidats) > 1
            else "À rechercher"
        )

    # Aucun résultat ADME n'est inventé ou déduit des seules structures.
    substance["ADME_absorption"] = ""
    substance["ADME_distribution"] = ""
    substance["ADME_metabolisme"] = ""
    substance["ADME_excretion"] = ""
    substance["ADME_source"] = ""
    substance["ADME_statut"] = "À rechercher"

with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
    colonnes = list(base[0].keys()) + champs_ajoutes
    ecrivain = csv.DictWriter(f, fieldnames=colonnes)
    ecrivain.writeheader()
    ecrivain.writerows(base)

print("Fichier créé :", SORTIE)
print("Substances conservées :", len(base))
print("Entrées candidates de DL50 importées :", compteur_dl50)
print("Entrées sans valeur candidate :", len(base) - compteur_dl50)
print("Données ADME inventées : 0")
print("Base originale modifiée : non")
