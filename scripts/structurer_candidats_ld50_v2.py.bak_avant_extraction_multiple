import csv
import json
import re
from pathlib import Path

SOURCE = Path("data/ld50_candidats_pubchem_v2_a_verifier.csv")
SORTIE = Path("data/ld50_candidats_structures_v2_a_verifier.csv")

def extraire_texte(extrait):
    try:
        obj = json.loads(extrait)
        textes = []

        def parcourir(x):
            if isinstance(x, dict):
                if isinstance(x.get("String"), str):
                    textes.append(x["String"])
                for v in x.values():
                    parcourir(v)
            elif isinstance(x, list):
                for v in x:
                    parcourir(v)

        parcourir(obj)
        return " ".join(dict.fromkeys(textes)) or extrait
    except (json.JSONDecodeError, TypeError):
        return extrait

def structurer(row):
    texte = extraire_texte(row.get("Extrait_brut", ""))
    rubrique = row.get("Rubrique_PubChem", "")
    valeur = ""
    unite = ""
    espece = ""
    voie = ""
    statut = "A_VERIFIER_MANUELLEMENT"

    if "Toxicity Summary" in rubrique:
        statut = "RESUME_GENERAL_NON_QUANTITATIF"
    else:
        # Compter les endpoints pour éviter de confondre LD50 et LC50.
        endpoints = re.findall(r"\b( LD\s*50 | LC\s*50 )\b".replace(" ", ""), texte, re.I)
        ld_matches = list(re.finditer(
            r"\bLD\s*50\b.{0,100}?((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s*[-–]\s*(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)?)\s*(mg/kg(?:\s*bw)?/day|mg/kg/day|mg/kg(?:\s*bw)?|(?:µg|ug)/kg|g/kg|mL/kg|g/L)\b",
            texte, re.I
        ))
        lc_present = re.search(r"\bLC\s*50\b", texte, re.I)

        if len(ld_matches) > 1 or (ld_matches and lc_present):
            statut = "EXTRAIT_MULTI_MESURES_A_VERIFIER"
        elif len(ld_matches) == 1:
            m = ld_matches[0]
            valeur = m.group(1).replace(" ", "").replace(",", "")
            unite = m.group(2)
            u = unite.lower().replace(" ", "")
            contexte = texte[m.start():m.start()+140]

            m_espece = re.search(r"\b(Rat|Mouse|Mice|Rabbit|Dog|Guinea pig)\b", contexte, re.I)
            if m_espece:
                espece = m_espece.group(1)

            m_voie = re.search(r"\b(oral|dermal|inhalation|intraperitoneal|intravenous|ip)\b", contexte, re.I)
            if m_voie:
                voie = {"ip": "intraperitoneal"}.get(m_voie.group(1).lower(), m_voie.group(1).lower())

            if "day" in u:
                statut = "QUARANTAINE_UNITE_A_VERIFIER"
            elif u in ("ug/kg", "µg/kg"):
                statut = "CONVERSION_UNITE_A_VERIFIER"
            elif u == "ml/kg":
                statut = "CONVERSION_DENSITE_A_VERIFIER"
            elif u == "g/l":
                statut = "UNITE_CONCENTRATION_A_VERIFIER"
            elif u == "g/kg":
                statut = "CONVERSION_UNITE_A_VERIFIER"
            elif not espece or not voie:
                statut = "CONTEXTE_INCOMPLET_A_VERIFIER"
            else:
                statut = "CANDIDAT_NUMERIQUE_A_VERIFIER"
        elif lc_present:
            statut = "LC50_NON_UTILISABLE_COMME_LD50"

    return {
        "CID": row.get("CID", ""),
        "Nom_substance": row.get("Nom_substance", ""),
        "Rubrique_PubChem": rubrique,
        "Valeur_extraite": valeur,
        "Unite_originale": unite,
        "Espece": espece,
        "Voie_exposition": voie,
        "Source_toxicologie": row.get("Source_toxicologie", ""),
        "Extrait_original": texte,
        "Statut_validation": statut,
    }

def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Fichier source introuvable : {SOURCE}")

    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f))

    resultats = [structurer(r) for r in lignes]
    champs = [
        "CID", "Nom_substance", "Rubrique_PubChem",
        "Valeur_extraite", "Unite_originale", "Espece",
        "Voie_exposition", "Source_toxicologie",
        "Extrait_original", "Statut_validation"
    ]

    with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(resultats)

    print("Candidats traités :", len(resultats))
    print("Fichier créé :", SORTIE)
    print("Aucune valeur n'a été automatiquement validée.")

if __name__ == "__main__":
    main()
