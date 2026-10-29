
from pathlib import Path
import shutil
import sys

FICHIER = Path("web/qsar/sentox_engine.py")

DEBUT = '    # EVALUATION MOE / RQ'
FIN = '    analyse["evaluation_risque"] = evaluation_risque'

def main():
    if not FICHIER.is_file():
        print(f"ERREUR : fichier introuvable : {FICHIER}")
        sys.exit(1)

    texte = FICHIER.read_text(encoding="utf-8")
    lignes = texte.splitlines(keepends=True)

    debuts = [
        i for i, ligne in enumerate(lignes)
        if DEBUT in ligne
    ]
    fins = [
        i for i, ligne in enumerate(lignes)
        if FIN in ligne
    ]

    if len(debuts) != 1 or len(fins) != 1:
        print("ERREUR : bloc non identifié de manière unique.")
        print("Aucune modification effectuée.")
        sys.exit(1)

    debut = debuts[0]
    fin = fins[0]

    if fin <= debut:
        print("ERREUR : limites du bloc incohérentes.")
        sys.exit(1)

    ancien_bloc = "".join(lignes[debut:fin + 1])

    if 'calculer_moe(' not in ancien_bloc:
        print("ERREUR : calcul MOE attendu introuvable.")
        sys.exit(1)

    if 'calculer_rq(' not in ancien_bloc:
        print("ERREUR : calcul RQ attendu introuvable.")
        sys.exit(1)

    nouveau_bloc = '''    # EVALUATION MOE / RQ
    # La DL50 reste un indicateur de toxicite aigue.
    # Elle n'est pas utilisee automatiquement comme
    # reference pour la MOE ou le RQ.

    evaluation_risque = {
        "statut": "reference_toxicologique_manquante",
        "exposition_humaine": None,
        "MOE": None,
        "RQ": None,
        "DL50": analyse.get("toxicologie", {}).get("dl50"),
        "avertissement": (
            "MOE et RQ non calcules : une reference "
            "toxicologique adaptee et documentee est requise."
        )
    }

    analyse["evaluation_risque"] = evaluation_risque'''

    sauvegarde = FICHIER.with_name(
        "sentox_engine_avant_correction_moe_rq.py"
    )

    if sauvegarde.exists():
        print(f"ERREUR : sauvegarde deja existante : {sauvegarde}")
        print("Aucune modification effectuee.")
        sys.exit(1)

    shutil.copy2(FICHIER, sauvegarde)

    lignes[debut:fin + 1] = [nouveau_bloc + "\n"]
    resultat = "".join(lignes)

    try:
        compile(resultat, str(FICHIER), "exec")
    except SyntaxError as exc:
        print(f"ERREUR de syntaxe : {exc}")
        print("Le fichier original n'a pas ete modifie.")
        sauvegarde.unlink(missing_ok=True)
        sys.exit(1)

    FICHIER.write_text(resultat, encoding="utf-8")

    print("Correction appliquee.")
    print(f"Sauvegarde : {sauvegarde}")
    print("MOE/RQ ne sont plus calcules automatiquement a partir de la DL50.")
    print("La syntaxe Python est valide.")

if __name__ == "__main__":
    main()
