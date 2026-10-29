
from pathlib import Path
import ast

fichier = Path("web/app.py")

if not fichier.exists():
    print("ERREUR : web/app.py introuvable.")
    raise SystemExit(1)

code = fichier.read_text(encoding="utf-8-sig")
ast.parse(code)

debut = 'MODELE_MODULE_SENTOX = """'
fin = '\n"""\n\n\n@app.route("/module/<nom_module>"'

i = code.find(debut)
j = code.find(fin, i + len(debut))

if i < 0 or j < 0:
    print("ERREUR : modèle du formulaire introuvable.")
    print("Aucune modification effectuée.")
    raise SystemExit(1)

nouveau_modele = r'''MODELE_MODULE_SENTOX = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ module.titre }} - SENTOX</title>
<style>
body{margin:0;font-family:Arial,sans-serif;background:#f1f5f9;color:#1e293b}
header{background:linear-gradient(135deg,#123b70,#087eaa);color:white;padding:22px}
main{max-width:950px;margin:25px auto;padding:18px}
.carte{background:white;padding:25px;border-radius:15px;box-shadow:0 3px 15px #0001}
h1,h2{color:#155e91}
label{display:block;margin-top:16px;font-weight:bold}
input,select,textarea{width:100%;padding:11px;margin-top:7px;box-sizing:border-box;border:1px solid #cbd5e1;border-radius:7px}
button,a{display:inline-block;margin-top:20px;padding:11px 16px;border-radius:7px}
button{background:#087eaa;color:white;border:0;cursor:pointer}
a{color:#087eaa}
.note{background:#fff7db;padding:14px;border-radius:8px;margin-top:20px;line-height:1.5}
.resultat{background:#e8f5ee;padding:15px;border-radius:8px;margin-top:20px;overflow-wrap:anywhere}
.erreur{background:#fdecec;padding:12px;border-radius:8px;margin-top:15px}
</style>
</head>
<body>
<header><strong>SENTOX</strong> — Espace scientifique et QHSE</header>
<main><div class="carte">
<h1>{{ module.titre }}</h1>
<p>{{ module.description }}</p>

{% if request.path.endswith("/qhse_rg") %}
<h2>Identification et évaluation préliminaire</h2>
<p>Commence par le nom indiqué sur l'emballage. Les informations inconnues peuvent rester vides.</p>
<form method="post">
<label>Nom du produit ou de la substance *</label>
<input name="produit" value="{{ request.form.get('produit', '') }}" required placeholder="Ex. eau de Javel, pesticide, acide chlorhydrique">

<label>Fabricant ou marque (facultatif)</label>
<input name="fabricant" value="{{ request.form.get('fabricant', '') }}" placeholder="Nom figurant sur l'emballage">

<label>Numéro CAS (si connu)</label>
<input name="cas" value="{{ request.form.get('cas', '') }}" placeholder="Laisser vide si inconnu">

<label>Classification de danger</label>
<select name="danger">
<option value="">Je ne sais pas / à vérifier</option>
<option value="indique">Danger indiqué sur l'étiquette ou la FDS</option>
<option value="aucune">Aucune classification trouvée — à vérifier</option>
</select>

<label>Voie d'exposition possible dans votre activité</label>
<select name="exposition">
<option value="">Je ne sais pas / à évaluer</option>
<option value="inhalation">Inhalation</option>
<option value="peau">Contact avec la peau</option>
<option value="yeux">Contact avec les yeux</option>
<option value="ingestion">Ingestion accidentelle</option>
<option value="plusieurs">Plusieurs voies possibles</option>
</select>

<label>Mesures de prévention déjà en place (facultatif)</label>
<textarea name="prevention" rows="3" placeholder="Ex. ventilation, gants adaptés, stockage sécurisé… Laisser vide si inconnu.">{{ request.form.get('prevention', '') }}</textarea>

<label>Fiche de données de sécurité disponible ?</label>
<select name="fds">
<option value="inconnue">Je ne sais pas</option>
<option value="oui">Oui</option>
<option value="non">Non</option>
</select>

<button type="submit">Évaluer les informations disponibles</button>
</form>

{% if resultat %}
<div class="resultat">
<h2>Résumé préliminaire</h2>
<p><strong>Produit saisi :</strong> {{ resultat.produit }}</p>
<p><strong>Fabricant :</strong> {{ resultat.fabricant or 'Non renseigné' }}</p>
<p><strong>Numéro CAS :</strong> {{ resultat.cas or 'Inconnu — identification nécessaire' }}</p>
<p><strong>Danger :</strong> {{ resultat.danger }}</p>
<p><strong>Voie d'exposition :</strong> {{ resultat.exposition }}</p>
<p><strong>Prévention :</strong> {{ resultat.prevention or 'Non renseignée — à définir après identification du produit et évaluation du risque' }}</p>
<p><strong>FDS :</strong> {{ resultat.fds }}</p>
<p><strong>Informations à compléter :</strong></p>
<ul>
{% for item in resultat.manquants %}
<li>{{ item }}</li>
{% endfor %}
</ul>
<strong>Statut : évaluation préliminaire, non validée.</strong>
</div>
{% endif %}

<div class="note">
<strong>Précaution :</strong> ce formulaire ne vérifie pas encore automatiquement les bases réglementaires et ne confirme pas l'identité du produit. Ne déduis pas l'absence de danger d'une information inconnue. Consulte l'étiquette et la FDS du fabricant avant de fixer les mesures de prévention.
</div>

{% else %}
{% if request.path.endswith("/molecules") %}
<form method="post">
<label>Nom commercial ou nom connu</label>
<input name="nom_connu" value="{{ request.form.get('nom_connu', '') }}" placeholder="Ex. Doliprane">
<label>Nom de la substance active (facultatif)</label>
<input name="nom_substance" value="{{ request.form.get('nom_substance', '') }}" placeholder="Ex. paracétamol">
<label>SMILES (facultatif)</label>
<input name="smiles" value="{{ request.form.get('smiles', '') }}" placeholder="Laisser vide si inconnu">
<label>Identifiant PubChem (facultatif)</label>
<input name="pubchem_cid" value="{{ request.form.get('pubchem_cid', '') }}" placeholder="Ex. 1983">
<button type="submit">Rechercher la substance</button>
</form>
{% else %}
<form method="get">
{% for champ in module.champs %}
<label>{{ champ }}</label>
<input name="champ{{ loop.index }}" placeholder="Facultatif : {{ champ }}">
{% endfor %}
<button type="submit">Afficher les informations saisies</button>
</form>
{% endif %}

{% if resultat %}
{% if resultat.get('erreur') %}
<div class="erreur">{{ resultat.get('erreur') }}</div>
{% else %}
<div class="resultat">
<h2>Résultat de la recherche</h2>
<p><strong>Statut :</strong> {{ resultat.get('statut', 'Non précisé') }}</p>
{% if resultat.get('message') %}<p>{{ resultat.get('message') }}</p>{% endif %}
{% for candidat in resultat.get('candidats', []) %}
<hr><h3>{{ candidat.get('nom_pubchem') or candidat.get('nom_recherche', 'Candidat') }}</h3>
<p><strong>CID PubChem :</strong> {{ candidat.get('cid') or 'Non disponible' }}</p>
<p><strong>Nom IUPAC :</strong> {{ candidat.get('nom_iupac') or 'Non disponible' }}</p>
<p><strong>Formule :</strong> {{ candidat.get('formule') or 'Non disponible' }}</p>
<p><strong>Source :</strong> {{ candidat.get('source', 'Non précisée') }}</p>
<p><strong>Identité :</strong> {{ candidat.get('statut_identite', 'À vérifier') }}</p>
{% endfor %}
{% if resultat.get('avertissement') %}<div class="note">{{ resultat.get('avertissement') }}</div>{% endif %}
</div>
{% endif %}
{% endif %}
{% endif %}

<a href="/dashboard">← Retour au tableau de bord</a>
</div></main>
</body>
</html>
"""'''

nouveau_code = code[:i] + nouveau_modele + code[j + len('\n"""'):]
ast.parse(nouveau_code)

# Enregistrer une copie distincte avant de modifier le fichier.
backup = Path("web/app_avant_formulaire_qhse.py")
if not backup.exists():
    backup.write_text(code, encoding="utf-8")

fichier.write_text(nouveau_code, encoding="utf-8")
print("Formulaire QHSE amélioré.")
print("Sauvegarde :", backup)
print("Le traitement du formulaire doit maintenant être ajouté à la route Flask.")
