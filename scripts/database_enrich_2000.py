import os
import shutil
import pandas as pd

# ============================================================
# SENTOX - ENRICHISSEMENT DE LA BASE 2000
# Version sécurisée : ne modifie jamais la base originale
# ============================================================

BASE_DIR = r"C:\SENTOX"
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000_enriched.csv"
)

BACKUP_FILE = os.path.join(
    DATA_DIR,
    "sentox_database_2000_backup.csv"
)


# ============================================================
# AFFICHAGE
# ============================================================

print()
print("=" * 70)
print("        SENTOX - ENRICHISSEMENT BASE 2000")
print("=" * 70)
print()


# ============================================================
# VERIFICATION DU FICHIER
# ============================================================

if not os.path.exists(INPUT_FILE):

    print("ERREUR : fichier introuvable")
    print(INPUT_FILE)
    print()
    input("Appuyez sur Entree...")
    raise SystemExit


# ============================================================
# SAUVEGARDE DE SECURITE
# ============================================================

if not os.path.exists(BACKUP_FILE):

    shutil.copy2(INPUT_FILE, BACKUP_FILE)

    print("Sauvegarde de securite creee :")
    print(BACKUP_FILE)

else:

    print("Sauvegarde de securite deja presente :")
    print(BACKUP_FILE)


# ============================================================
# LECTURE
# ============================================================

try:

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig",
        low_memory=False
    )

except UnicodeDecodeError:

    df = pd.read_csv(
        INPUT_FILE,
        encoding="latin1",
        low_memory=False
    )


print()
print("Nombre de molecules trouvees :", len(df))
print()


# ============================================================
# NETTOYAGE DES NOMS DE COLONNES
# ============================================================

df.columns = [
    str(col).strip()
    for col in df.columns
]


# ============================================================
# FONCTION POUR TROUVER UNE COLONNE
# ============================================================

def trouver_colonne(possibilites):

    for nom in possibilites:

        if nom in df.columns:
            return nom

    return None


col_nom = trouver_colonne([
    "Nom",
    "nom",
    "Name",
    "name",
    "nom_recherche"
])

col_categorie = trouver_colonne([
    "Categorie",
    "Catégorie",
    "category",
    "Category"
])

col_smiles = trouver_colonne([
    "SMILES",
    "smiles",
    "CanonicalSMILES",
    "IsomericSMILES"
])


# ============================================================
# CREATION DES COLONNES SENTOX
# ============================================================

colonnes_sentox = {

    "SENTOX_Categorie": "",

    "Plante": "",

    "Partie_utilisee": "",

    "Statut_donnees": "",

    "LD50_mg_kg": "",

    "LogLD50": "",

    "Toxicite": "",

    "Source_toxicologie": "",

    "Organisme": "",

    "Voie_exposition": "",

    "Confiance_toxicologique": ""
}


for colonne in colonnes_sentox:

    if colonne not in df.columns:
        df[colonne] = ""


# ============================================================
# CLASSIFICATION DE BASE
# ============================================================

def classifier(nom, categorie_existante):

    texte = (
        str(nom) + " " +
        str(categorie_existante)
    ).lower()

    # Composes connus de plantes medicinales
    plantes = [
        "quercetin",
        "kaempferol",
        "rutin",
        "catechin",
        "epicatechin",
        "apigenin",
        "luteolin",
        "naringenin",
        "hesperidin",
        "genistein",
        "daidzein",
        "tannic",
        "gallic acid",
        "caffeic acid",
        "ferulic acid",
        "chlorogenic acid",
        "ellagic acid",
        "resveratrol",
        "curcumin",
        "limonin",
        "saponin"
    ]

    for mot in plantes:

        if mot in texte:
            return "Medicinal_plant_compound"

    # Medicaments
    medicaments = [
        "aspirin",
        "paracetamol",
        "acetaminophen",
        "ibuprofen",
        "isoniazid",
        "metformin",
        "amoxicillin",
        "ciprofloxacin",
        "diclofenac",
        "naproxen",
        "warfarin",
        "caffeine"
    ]

    for mot in medicaments:

        if mot in texte:
            return "Drug"

    # Acides amines
    amino_acides = [
        "glycine",
        "alanine",
        "valine",
        "leucine",
        "isoleucine",
        "lysine",
        "arginine",
        "histidine",
        "phenylalanine",
        "tyrosine",
        "tryptophan",
        "methionine",
        "threonine"
    ]

    for mot in amino_acides:

        if mot in texte:
            return "Amino_acid"

    # Sinon, on conserve la categorie existante
    if (
        categorie_existante
        and str(categorie_existante).strip()
        and str(categorie_existante).lower() != "nan"
    ):
        return str(categorie_existante)

    return "Unclassified"


# ============================================================
# APPLICATION DE LA CLASSIFICATION
# ============================================================

print("Classification des molecules...")
print()

for i in range(len(df)):

    if col_nom:

        nom = df.iloc[i][col_nom]

    else:

        nom = ""

    if col_categorie:

        ancienne_categorie = df.iloc[i][col_categorie]

    else:

        ancienne_categorie = ""

    nouvelle_categorie = classifier(
        nom,
        ancienne_categorie
    )

    df.at[
        df.index[i],
        "SENTOX_Categorie"
    ] = nouvelle_categorie


# ============================================================
# STATUT DES DONNEES TOXICOLOGIQUES
# ============================================================

def definir_statut(row):

    ld50 = row.get("LD50_mg_kg", "")

    toxicite = row.get("Toxicite", "")

    if (
        pd.notna(ld50)
        and str(ld50).strip() != ""
        and str(ld50).lower() != "nan"
    ):
        return "Donnee_toxicologique_presente"

    if (
        pd.notna(toxicite)
        and str(toxicite).strip() != ""
        and str(toxicite).lower() != "nan"
    ):
        return "Donnee_toxicologique_presente"

    return "A_enrichir"


df["Statut_donnees"] = df.apply(
    definir_statut,
    axis=1
)


# ============================================================
# INFORMATIONS PLANTES
# ============================================================

# IMPORTANT :
# Nous ne fabriquons aucune association plante/molecule.
# Ces champs resteront vides tant qu'une source scientifique
# ne permet pas de confirmer l'association.

if "Plante" not in df.columns:
    df["Plante"] = ""

if "Partie_utilisee" not in df.columns:
    df["Partie_utilisee"] = ""


# ============================================================
# SUPPRESSION DES DOUBLONS
# ============================================================

avant = len(df)

if col_smiles:

    df = df.drop_duplicates(
        subset=[col_smiles],
        keep="first"
    )

elif col_nom:

    df = df.drop_duplicates(
        subset=[col_nom],
        keep="first"
    )

apres = len(df)

print()
print("Doublons supprimes :", avant - apres)
print("Molecules finales :", apres)


# ============================================================
# SAUVEGARDE
# ============================================================

try:

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

except Exception as e:

    print()
    print("ERREUR lors de la sauvegarde :")
    print(e)
    input("Appuyez sur Entree...")
    raise SystemExit


# ============================================================
# RAPPORT
# ============================================================

print()
print("=" * 70)
print("          ENRICHISSEMENT TERMINE")
print("=" * 70)

print()
print("Base originale :")
print(INPUT_FILE)

print()
print("Nouvelle base :")
print(OUTPUT_FILE)

print()
print("Sauvegarde originale :")
print(BACKUP_FILE)

print()
print("Nombre final de molecules :", len(df))


print()
print("REPARTITION SENTOX")
print("-" * 40)

print(
    df["SENTOX_Categorie"]
    .value_counts()
    .to_string()
)


print()
print("STATUT DES DONNEES TOXICOLOGIQUES")
print("-" * 40)

print(
    df["Statut_donnees"]
    .value_counts()
    .to_string()
)


print()
print("=" * 70)
print("SENTOX DATABASE ENRICHIE : OK")
print("=" * 70)
print()

input("Appuyez sur Entree pour terminer...")