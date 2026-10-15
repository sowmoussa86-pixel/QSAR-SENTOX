import csv
from pathlib import Path

source = Path("data/audit_pertinence_directe_pubmed_v2.csv")
sortie = Path("data/controle_associations_pubmed_v1.csv")

if not source.exists():
    raise SystemExit(f"Fichier introuvable : {source}")

with source.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

if not lignes:
    raise SystemExit("Aucune référence à contrôler.")

# Signalements manuels préliminaires : ils ne remplacent pas
# une vérification de l'article intégral.
signalements = {
    "2019564": (
        "À vérifier",
        "L'article porte sur la dégradation du p-crésol ; "
        "l'association à la substance cible doit être justifiée."
    ),
    "35086000": (
        "À vérifier",
        "Le composé étudié est un dérivé glycosylé issu de Moringa ; "
        "ne pas l'assimiler automatiquement à la substance cible."
    ),
    "35787943": (
        "Association probablement non pertinente",
        "L'article porte sur des interactions entre médicaments ; "
        "aucune preuve spécifique sur le benzène n'est établie par le titre."
    ),
    "4307774": (
        "À vérifier",
        "Le titre porte sur le métabolisme du cuivre ; "
        "le lien avec le catéchol n'est pas établi."
    ),
    "32692612": (
        "Association probablement non pertinente",
        "Le titre porte sur la méthanogenèse ; "
        "le lien avec le o-crésol n'est pas établi."
    ),
    "26087123": (
        "Association probablement non pertinente",
        "Le titre porte sur l'imagerie par fluorescence ; "
        "le lien avec le o-crésol n'est pas établi."
    ),
    "33631048": (
        "Association probablement non pertinente",
        "Le titre porte sur la fixation enzymatique du CO2 ; "
        "le lien avec le o-crésol n'est pas établi."
    ),
    "11465150": (
        "Association probablement non pertinente",
        "Le titre porte sur des dérivés d'acides arylpropioniques ; "
        "une pertinence pour la toxicité du benzène n'est pas établie."
    )
}

champs = list(lignes[0].keys())
for nom in ("Controle_association", "Motif_controle", "Validation_humaine_association"):
    if nom not in champs:
        champs.append(nom)

for ligne in lignes:
    pmid = ligne.get("PMID", "").strip()
    statut, motif = signalements.get(
        pmid,
        (
            "À examiner",
            "Vérifier la substance réellement étudiée, le modèle, "
            "l'effet et la conclusion dans le résumé ou l'article intégral."
        )
    )
    ligne["Controle_association"] = statut
    ligne["Motif_controle"] = motif
    ligne["Validation_humaine_association"] = "Non effectuée"

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(lignes)

print("Références contrôlées :", len(lignes))
print("Fichier créé :", sortie)
print("Fichier source modifié : non")
print("Validation scientifique complète : non effectuée")
