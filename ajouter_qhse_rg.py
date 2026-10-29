
from pathlib import Path
import ast
import shutil

fichier = Path("web/app.py")
sauvegarde = Path("web/app_avant_module_qhse_rg.py")

if not fichier.exists():
    print("ERREUR : web/app.py introuvable.")
    raise SystemExit(1)

code = fichier.read_text(encoding="utf-8-sig")

# Vérifier la syntaxe avant toute modification
ast.parse(code)

if '"qhse_rg": {' in code or "'qhse_rg': {" in code:
    print("Le module QHSE & RG existe déjà. Aucune modification.")
    raise SystemExit(0)

repere = '    "rapports": {'

if repere not in code:
    print("ERREUR : bloc rapports introuvable. Fichier non modifié.")
    raise SystemExit(1)

module = '''    "qhse_rg": {
        "titre": "QHSE & Réglementation",
        "description": (
            "Inventaire chimique, évaluation des risques, "
            "FDS, prévention et veille réglementaire."
        ),
        "champs": [
            "Nom du produit chimique",
            "Numéro CAS",
            "Classification de danger connue",
            "Voie d’exposition",
            "Mesures de prévention"
        ]
    },
'''

nouveau_code = code.replace(repere, module + repere, 1)

# Vérifier le nouveau code avant de l'enregistrer
ast.parse(nouveau_code)

if not sauvegarde.exists():
    shutil.copy2(fichier, sauvegarde)

fichier.write_text(nouveau_code, encoding="utf-8")

print("SUCCÈS : module QHSE & RG ajouté.")
print("Sauvegarde disponible :", sauvegarde)
