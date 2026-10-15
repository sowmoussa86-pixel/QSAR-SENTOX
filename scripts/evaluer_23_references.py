import csv
from pathlib import Path

source = Path("data/analyse_pertinence_pubmed_23.csv")
sortie = Path("data/audit_scientifique_preliminaire_23.csv")

evaluations = {
"10839460": ("Mécanisme indirect", "Étude du mécanisme de la tyrosinase sur des monophenols hydroxylés ; toxicité non démontrée."),
"3516352": ("Mécanisme indirect", "Étude d'une enzyme du métabolisme secondaire ; preuve toxicologique non établie."),
"2019564": ("Pertinence faible", "Étude de la dégradation du p-crésol ; lien direct avec la substance cible à confirmer."),
"35086000": ("Pharmacologie indirecte", "Étude d'un composé glycosylé issu des graines de Moringa ; ne pas assimiler automatiquement ce composé à l'alcool p-hydroxybenzylique."),
"31805306": ("ADME / pharmacocinétique", "Étude du passage de l'alcool p-hydroxybenzylique à travers la barrière hémato-encéphalique ; ce n'est pas une étude de toxicité."),
"26563741": ("Pertinence faible", "Étude d'un promédicament antioxydant ; identité avec la substance cible non établie."),
"4890135": ("Indéterminée", "Titre ancien sur des préparations contre les coups de soleil ; résumé indisponible."),
"11465150": ("Non pertinente pour la cible", "Étude de dérivés de l'acide 2-arylpropionique ; pas de preuve spécifique sur la toxicité du benzène."),
"35787943": ("Non pertinente pour la cible", "Étude d'interactions médicamenteuses ; pas de preuve spécifique sur le benzène."),
"29504827": ("Contexte métabolique indirect", "Revue sur le métabolisme des flavonoïdes et le microbiote ; lien direct avec le catéchol à établir."),
"4307774": ("Non pertinente pour la cible", "Article sur le métabolisme du cuivre ; lien avec le catéchol non établi."),
"32692612": ("Non pertinente pour la cible", "Article sur la méthanogenèse ; aucun lien direct établi avec le o-crésol."),
"26087123": ("Non pertinente pour la cible", "Article sur des marqueurs fluorescents ; toxicité du o-crésol non étudiée d'après le titre."),
"33631048": ("Non pertinente pour la cible", "Article sur la fixation enzymatique du CO2 ; lien avec le o-crésol non établi."),
"30311986": ("Mécanisme indirect", "Revue sur les monooxygénases et les composés aromatiques ; ne prouve pas la toxicité du o-crésol."),
"28624475": ("Mécanisme indirect", "Revue sur les oxydoréductases et les biotransformations industrielles ; preuve spécifique non établie."),
"33245912": ("Pertinence faible", "Étude de réactions de déshalogénation ; lien direct avec le o-crésol non établi."),
"35073609": ("Pertinence faible", "Article sur les flavines prén ylées et leurs mécanismes ; toxicité du o-crésol non établie."),
"28515321": ("Contexte métabolique indirect", "Revue sur les monooxygénases flaviniques et les maladies ; lien direct avec le o-crésol à confirmer."),
"7140579": ("Toxicologie de classe", "Article sur l'intoxication par les salicylates ; utile pour le contexte de cette classe, mais à vérifier pour la substance précise et l'actualité des recommandations."),
"38992404": ("Non pertinente pour la cible", "Revue sur Peucedanum decursivum ; aucun lien direct établi avec le m-crésol."),
"34025642": ("Non pertinente pour la cible", "Étude sur l'hyperforine et un modèle de psoriasis ; ne démontre pas la toxicité du phloroglucinol."),
"28885074": ("Interaction / pharmacocinétique", "Revue sur le millepertuis et les interactions médicamenteuses ; ne démontre pas la toxicité du phloroglucinol.")
}

if not source.exists():
    raise SystemExit(f"Fichier introuvable : {source}")

with source.open(encoding="utf-8-sig", newline="") as f:
    lignes = list(csv.DictReader(f))

if not lignes:
    raise SystemExit("Aucune référence à examiner.")

champs = list(lignes[0].keys())
for champ in (
    "Evaluation_preliminaire",
    "Justification_preliminaire",
    "Utilisation_dans_SENTOX",
    "Validation_scientifique"
):
    if champ not in champs:
        champs.append(champ)

for ligne in lignes:
    pmid = ligne.get("PMID", "").strip()
    categorie, justification = evaluations.get(
        pmid,
        ("Indéterminée", "Évaluation manuelle nécessaire.")
    )
    ligne["Evaluation_preliminaire"] = categorie
    ligne["Justification_preliminaire"] = justification
    ligne["Utilisation_dans_SENTOX"] = (
        "Contexte uniquement ; ne pas utiliser comme preuve toxicologique spécifique."
    )
    ligne["Validation_scientifique"] = "À effectuer"

with sortie.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=champs)
    writer.writeheader()
    writer.writerows(lignes)

print("Références traitées :", len(lignes))
print("Fichier créé :", sortie)
print("Fichier source modifié : non")
print("Validation scientifique complète : non effectuée")
