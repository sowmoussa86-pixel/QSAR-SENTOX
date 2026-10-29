
import csv
import re
import time
from pathlib import Path

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import requests
from sentox_normalisation import normaliser_dl50
BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"
HEADERS = {"User-Agent": "QSAR-SENTOX/1.1 (toxicology research)"}

# Format : LD50 Rat oral 2400 mg/kg
LD50_PATTERN = re.compile(
    r"\bLD\s*50\b\s*[:=\-]?\s*"
    r"([A-Za-z][A-Za-z -]*?)\s+"
    r"(oral|ip|iv|sc|dermal|inhalation|intraperitoneal|"
    r"intravenous|subcutaneous)\s*"
    r"[:=\-]?\s*"
    r"([<>]?\s*\d+(?:[.,]\d+)?)\s*"
    r"(mg/kg|g/kg|ug/kg|µg/kg|μg/kg)",
    re.IGNORECASE,
)

# Format : Oral LD50 (mouse) = 4550 mg/kg
LD50_REVERSE_PATTERN = re.compile(
    r"\b(oral|ip|iv|sc|dermal|inhalation|intraperitoneal|"
    r"intravenous|subcutaneous)\b"
    r"\s*(?:LD\s*50|LD50)\s*"
    r"\(?\s*([A-Za-z][A-Za-z -]*?)\s*\)?\s*"
    r"[:=]?\s*"
    r"([<>]?\s*\d+(?:[.,]\d+)?)\s*"
    r"(mg/kg|g/kg|ug/kg|µg/kg|μg/kg)",
    re.IGNORECASE,
)


def normaliser_voie(voie):
    voie = voie.lower().strip()
    correspondances = {
        "ip": "intraperitoneale",
        "iv": "intraveineuse",
        "sc": "sous-cutanee",
    }
    return correspondances.get(voie, voie)


def extraire_textes(value):
    """Extrait le texte des champs textuels PubChem."""
    textes = []

    if not isinstance(value, dict):
        return textes

    for item in value.get("StringWithMarkup", []):
        texte = item.get("String", "")
        if texte:
            textes.append(texte)

    return textes


def rechercher_dl50_pubchem(cid):
    """Recherche les DL50 dans la fiche complète PubChem."""
    url = f"{BASE_URL}/data/compound/{int(cid)}/JSON"
    source_url = (
        f"https://pubchem.ncbi.nlm.nih.gov/compound/{int(cid)}"
    )

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as exc:
        return [{
            "CID": cid,
            "statut": "ERREUR_REQUETE",
            "message": str(exc),
            "source_URL": source_url,
        }]

    record = data.get("Record", {})
    record_number = record.get("RecordNumber", cid)
    nom = record.get("RecordTitle", "")

    references = {
        item.get("ReferenceNumber"): item
        for item in record.get("Reference", [])
        if item.get("ReferenceNumber") is not None
    }

    results = []
    deja_vus = set()

    def ajouter_resultat(
        texte, espece, voie, valeur, unite,
        section, info
    ):
        espece = espece.strip(" ()\t")
        voie = normaliser_voie(voie)
        valeur = valeur.strip()
        unite = unite.replace("μ", "µ").strip()

        normalisation = normaliser_dl50(valeur, unite)
        ref_num = info.get("ReferenceNumber")
        ref = references.get(ref_num, {})
        source = ref.get("SourceName", "")
        reference_nom = ref.get("Name", "")

        cle = (
            str(record_number),
            texte.lower(),
            espece.lower(),
            voie.lower(),
            valeur,
            unite.lower(),
            str(ref_num),
        )

        if cle in deja_vus:
            return

        deja_vus.add(cle)

        results.append({
            "CID": record_number,
            "substance": nom,
            "DL50_brute": texte,
            "espece": espece,
            "voie": voie,
            "valeur": valeur,
            "unite": unite,
            "valeur_normalisee_mg_kg": normalisation["valeur_normalisee_mg_kg"],
            "operateur": normalisation["operateur"],
            "statut_normalisation": normalisation["statut_normalisation"],
            "message_normalisation": normalisation["message_normalisation"],
            "section": section,
            "reference": source,
            "reference_nom": reference_nom,
            "reference_numero": ref_num or "",
            "qualite_source": "A vérifier dans la source originale",
            "source_URL": source_url,
            "statut": "A_VERIFIER",
            "message": (
                "Valeur extraite automatiquement ; "
                "vérifier la référence, l'espèce, la voie "
                "et l'unité avant toute utilisation."
            ),
        })

    def parcourir(sections, chemin=""):
        for section in sections or []:
            titre = section.get("TOCHeading", "")
            nouveau_chemin = (
                f"{chemin} > {titre}" if chemin
                else titre
            )

            for info in section.get("Information", []):
                value = info.get("Value", {})
                textes = extraire_textes(value)

                for texte in textes:
                    for match in LD50_PATTERN.finditer(texte):
                        ajouter_resultat(
                            match.group(0),
                            match.group(1),
                            match.group(2),
                            match.group(3),
                            match.group(4),
                            nouveau_chemin,
                            info,
                        )

                    for match in LD50_REVERSE_PATTERN.finditer(texte):
                        ajouter_resultat(
                            match.group(0),
                            match.group(2),
                            match.group(1),
                            match.group(3),
                            match.group(4),
                            nouveau_chemin,
                            info,
                        )

            parcourir(
                section.get("Section", []),
                nouveau_chemin,
            )

    parcourir(record.get("Section", []))

    if not results:
        return [{
            "CID": record_number,
            "substance": nom,
            "statut": "NON_TROUVE",
            "message": (
                "Aucune DL50 extraite des champs textuels "
                "reconnus. Des données peuvent exister dans "
                "des tables externes ou d'autres sources."
            ),
            "source_URL": source_url,
        }]

    return results


def enregistrer_csv(lignes, chemin):
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    champs = sorted({
        cle for ligne in lignes for cle in ligne
    })

    with chemin.open(
        "w", newline="", encoding="utf-8-sig"
    ) as fichier:
        writer = csv.DictWriter(
            fichier,
            fieldnames=champs,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(lignes)


if __name__ == "__main__":
    lignes = rechercher_dl50_pubchem(359)

    enregistrer_csv(
        lignes,
        "data/test_dl50_pubchem.csv",
    )

    print("Résultats :", len(lignes))

    for ligne in lignes:
        print(ligne)

    print("\nFichier créé : data/test_dl50_pubchem.csv")
