
from pathlib import Path
import ast
import shutil

fichier = Path("web/app.py")
backup = Path("web/app_avant_traitement_qhse.py")

if not fichier.exists():
    print("ERREUR : web/app.py introuvable.")
    raise SystemExit(1)

code = fichier.read_text(encoding="utf-8-sig")
ast.parse(code)

repere = '    if nom_module == "molecules" and request.method == "POST":'

if 'if nom_module == "qhse_rg" and request.method == "POST":' in code:
    print("Le traitement QHSE existe déjà. Aucune modification.")
    raise SystemExit(0)

if repere not in code:
    print("ERREUR : point d'insertion introuvable.")
    print("Aucune modification effectuée.")
    raise SystemExit(1)

bloc = '''    if nom_module == "qhse_rg" and request.method == "POST":
        produit = request.form.get("produit", "").strip()
        fabricant = request.form.get("fabricant", "").strip()
        cas = request.form.get("cas", "").strip()
        danger = request.form.get("danger", "").strip()
        exposition = request.form.get("exposition", "").strip()
        prevention = request.form.get("prevention", "").strip()
        fds = request.form.get("fds", "inconnue").strip()

        if not produit:
            resultat = {
                "erreur": "Saisis le nom du produit pour commencer."
            }
        else:
            danger_textes = {
                "indique": "Danger indiqué : classification à vérifier dans la FDS.",
                "aucune": "Aucune classification trouvée : cela ne signifie pas absence de danger.",
                "": "Inconnu : consulter l’étiquette et la FDS."
            }
            exposition_textes = {
                "inhalation": "Inhalation (voie possible sélectionnée par l’utilisateur).",
                "peau": "Contact cutané (voie possible sélectionnée par l’utilisateur).",
                "yeux": "Contact oculaire (voie possible sélectionnée par l’utilisateur).",
                "ingestion": "Ingestion accidentelle (voie possible sélectionnée par l’utilisateur).",
                "plusieurs": "Plusieurs voies possibles, à évaluer selon l’activité.",
                "": "Inconnue : évaluer les conditions réelles d’utilisation."
            }
            fds_textes = {
                "oui": "Déclarée disponible par l’utilisateur ; contenu non vérifié.",
                "non": "Déclarée indisponible ; demander la FDS au fournisseur.",
                "inconnue": "Disponibilité inconnue."
            }

            manquants = []
            if not cas:
                manquants.append("Numéro CAS : identité chimique à confirmer.")
            if danger != "indique":
                manquants.append("Classification : vérifier les sources officielles et la FDS.")
            if not exposition:
                manquants.append("Voies d’exposition : évaluation à réaliser selon l’activité.")
            if not prevention:
                manquants.append("Prévention : à définir après identification des dangers et évaluation du risque.")
            if fds != "oui":
                manquants.append("FDS : obtenir la version applicable auprès du fournisseur.")

            resultat = {
                "produit": produit,
                "fabricant": fabricant,
                "cas": cas,
                "danger": danger_textes.get(danger, "À vérifier dans une source fiable."),
                "exposition": exposition_textes.get(exposition, "À évaluer."),
                "prevention": prevention,
                "fds": fds_textes.get(fds, "Disponibilité à confirmer."),
                "manquants": manquants
            }

'''

nouveau_code = code.replace(repere, bloc + repere, 1)
ast.parse(nouveau_code)

if not backup.exists():
    shutil.copy2(fichier, backup)

fichier.write_text(nouveau_code, encoding="utf-8")
print("SUCCÈS : traitement du formulaire QHSE ajouté.")
print("Sauvegarde :", backup)
print("Les données inconnues restent signalées comme à vérifier.")
