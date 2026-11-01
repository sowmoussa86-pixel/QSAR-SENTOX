
# ============================================================
# SENTOX QHSE - APPLICATION WEB V1
# Registre des risques professionnels
# ============================================================

from flask import Flask, request, redirect, url_for, render_template_string, flash
from datetime import datetime

from database import (
    initialiser_base,
    enregistrer_risque,
    lister_risques,
    supprimer_risque
)

from risk_engine import evaluer_risque
from analyse_toxicologique import (
    analyser_substance,
    generer_prevention,
    generer_rapport_toxicologique
)

app = Flask(__name__)
app.secret_key = "sentox-qhse-demo-2026"


# ------------------------------------------------------------
# INITIALISATION
# ------------------------------------------------------------

initialiser_base()


# ------------------------------------------------------------
# INTERFACE HTML
# ------------------------------------------------------------

PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>SENTOX QHSE</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #172033;
}

header {
    background: linear-gradient(120deg, #082f49, #075985);
    color: white;
    padding: 25px;
}

header h1 {
    margin: 0;
    font-size: 28px;
}

header p {
    margin-bottom: 0;
    color: #dbeafe;
}

.container {
    max-width: 1200px;
    margin: 25px auto;
    padding: 0 18px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px #00000010;
}

.card h3 {
    margin: 0 0 12px;
    color: #475569;
    font-size: 14px;
}

.number {
    font-size: 30px;
    font-weight: bold;
    color: #0369a1;
}

.panel {
    background: white;
    padding: 22px;
    border-radius: 12px;
    margin-bottom: 22px;
    box-shadow: 0 2px 8px #00000010;
}

h2 {
    color: #075985;
    margin-top: 0;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 15px;
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 6px;
}

input, select, textarea {
    width: 100%;
    padding: 11px;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    font-size: 14px;
}

textarea {
    min-height: 75px;
}

button {
    background: #0369a1;
    color: white;
    border: 0;
    padding: 12px 20px;
    border-radius: 7px;
    cursor: pointer;
    font-weight: bold;
    margin-top: 15px;
}

button:hover {
    background: #075985;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 750px;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #e2e8f0;
    text-align: left;
    font-size: 13px;
}

th {
    background: #e0f2fe;
    color: #075985;
}

.table-container {
    overflow-x: auto;
}

.badge {
    padding: 5px 9px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 11px;
}

.FAIBLE { background: #dcfce7; color: #166534; }
.MODERE { background: #fef9c3; color: #854d0e; }
.ELEVE { background: #ffedd5; color: #9a3412; }
.CRITIQUE { background: #fee2e2; color: #991b1b; }

.modules {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
}

.module {
    padding: 17px;
    border-radius: 9px;
    background: #e0f2fe;
    color: #075985;
    font-weight: bold;
}

.notice {
    padding: 12px;
    background: #fef3c7;
    border-radius: 8px;
    color: #92400e;
    margin-bottom: 15px;
}

footer {
    text-align: center;
    padding: 25px;
    color: #64748b;
}
</style>
</head>

<body>

<header>
    <h1>SENTOX QHSE</h1>
    <p>Plateforme de gestion de la Qualité, de l'Hygiène,
    de la Sécurité et de l'Environnement</p>
</header>

<div class="container">

    <div class="notice">
        Version de démonstration : les fonctionnalités doivent
        être testées et validées avant utilisation professionnelle.
    </div>

    <div class="cards">
        <div class="card">
            <h3>Risques enregistrés</h3>
            <div class="number">{{ total }}</div>
        </div>

        <div class="card">
            <h3>Risques critiques</h3>
            <div class="number">{{ critiques }}</div>
        </div>

        <div class="card">
            <h3>Risques élevés</h3>
            <div class="number">{{ eleves }}</div>
        </div>

        <div class="card">
            <h3>Risques modérés</h3>
            <div class="number">{{ moderes }}</div>
        </div>
    </div>

    <section class="panel">
        <h2>Modules SENTOX QHSE</h2>

        <div class="modules">
            <div class="module">Registre des risques</div>
            <div class="module">Actions correctives</div>
            <div class="module">Audits et inspections</div>
            <div class="module">Gestion environnementale</div>
            <div class="module">Base de données</div>
            <div class="module">Tableau de bord</div>
        </div>
        <p>Les modules affichés ne sont pas tous encore raccordés.</p>
    </section>

    <section class="panel">
        <h2>Nouvelle évaluation des risques professionnels</h2>

        <form method="POST" action="/ajouter-risque">

            <div class="form-grid">

                <div>
                    <label>Secteur</label>
                    <input name="secteur" required
                    placeholder="Ex. Laboratoire">
                </div>

                <div>
                    <label>Activité</label>
                    <input name="activite" required
                    placeholder="Ex. Manipulation de produits">
                </div>

                <div>
                    <label>Danger identifié</label>
                    <input name="danger" required
                    placeholder="Ex. Exposition chimique">
                </div>

                <div>
                    <label>Personnes exposées</label>
                    <input name="personnes_exposees" required
                    placeholder="Ex. Techniciens">
                </div>

                <div>
                    <label>Conséquences possibles</label>
                    <textarea name="consequences" required
                    placeholder="Décrire les conséquences"></textarea>
                </div>

                <div>
                    <label>Gravité (1 à 5)</label>
                    <select name="gravite" required>
                        <option value="">Choisir</option>
                        <option value="1">1 - Très faible</option>
                        <option value="2">2 - Faible</option>
                        <option value="3">3 - Moyenne</option>
                        <option value="4">4 - Grave</option>
                        <option value="5">5 - Très grave</option>
                    </select>
                </div>

                <div>
                    <label>Probabilité (1 à 5)</label>
                    <select name="probabilite" required>
                        <option value="">Choisir</option>
                        <option value="1">1 - Très improbable</option>
                        <option value="2">2 - Peu probable</option>
                        <option value="3">3 - Possible</option>
                        <option value="4">4 - Probable</option>
                        <option value="5">5 - Très probable</option>
                    </select>
                </div>

                <div>
                    <label>Mesures de prévention</label>
                    <textarea name="mesures_prevention"
                    placeholder="Mesures existantes ou proposées"></textarea>
                </div>

                <div>
                    <label>Responsable</label>
                    <input name="responsable"
                    placeholder="Nom du responsable">
                </div>

                <div>
                    <label>Échéance</label>
                    <input type="date" name="echeance">
                </div>

            </div>

            <button type="submit">Calculer et enregistrer le risque</button>
        </form>
    </section>

    <section class="panel">
        <h2>Registre des risques professionnels</h2>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Date</th>
                        <th>Secteur</th>
                        <th>Danger</th>
                        <th>Gravité</th>
                        <th>Probabilité</th>
                        <th>Criticité</th>
                        <th>Niveau</th>
                        <th>Statut</th>
                    </tr>
                </thead>

                <tbody>
                {% for r in risques %}
                    <tr>
                        <td>{{ r.id }}</td>
                        <td>{{ r.date_creation }}</td>
                        <td>{{ r.secteur }}</td>
                        <td>{{ r.danger }}</td>
                        <td>{{ r.gravite }}</td>
                        <td>{{ r.probabilite }}</td>
                        <td>{{ r.criticite }}/25</td>
                        <td>
                            <span class="badge {{ r.niveau_risque }}">
                                {{ r.niveau_risque }}
                            </span>
                        </td>
                        <td>{{ r.statut }}</td>
                    </tr>
                {% else %}
                    <tr>
                        <td colspan="9">Aucun risque enregistré.</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </section>

</div>

<footer>
    SENTOX QHSE — Version 1 — Démonstration professionnelle
</footer>

</body>
</html>
"""


# ------------------------------------------------------------
# TABLEAU DE BORD
# ------------------------------------------------------------

@app.route("/")
def accueil():

    risques = lister_risques()

    total = len(risques)

    critiques = sum(
        1 for r in risques
        if r.get("niveau_risque") == "CRITIQUE"
    )

    eleves = sum(
        1 for r in risques
        if r.get("niveau_risque") == "ELEVE"
    )

    moderes = sum(
        1 for r in risques
        if r.get("niveau_risque") == "MODERE"
    )

    return render_template_string(
        PAGE,
        risques=risques,
        total=total,
        critiques=critiques,
        eleves=eleves,
        moderes=moderes
    )


# ------------------------------------------------------------
# ENREGISTREMENT D'UN RISQUE
# ------------------------------------------------------------

@app.route("/ajouter-risque", methods=["POST"])
def ajouter_risque():

    try:
        secteur = request.form.get("secteur", "").strip()
        activite = request.form.get("activite", "").strip()
        danger = request.form.get("danger", "").strip()
        personnes = request.form.get("personnes_exposees", "").strip()
        consequences = request.form.get("consequences", "").strip()

        gravite = int(request.form.get("gravite"))
        probabilite = int(request.form.get("probabilite"))

        mesures = request.form.get("mesures_prevention", "").strip()
        responsable = request.form.get("responsable", "").strip()
        echeance = request.form.get("echeance", "").strip()

        champs = [
            secteur, activite, danger, personnes, consequences
        ]

        if not all(champs):
            raise ValueError("Tous les champs obligatoires doivent être remplis.")

        if echeance:
            datetime.strptime(echeance, "%Y-%m-%d")

        evaluation = evaluer_risque(gravite, probabilite)

        fiche = {
            "date_creation": datetime.now().isoformat(timespec="seconds"),
            "secteur": secteur,
            "activite": activite,
            "danger": danger,
            "personnes_exposees": personnes,
            "consequences": consequences,
            "gravite": evaluation["gravite"],
            "probabilite": evaluation["probabilite"],
            "criticite": evaluation["criticite"],
            "niveau_risque": evaluation["niveau"],
            "action_recommandee": evaluation["action_recommandee"],
            "mesures_prevention": mesures,
            "responsable": responsable,
            "echeance": echeance,
            "statut": "A TRAITER"
        }

        enregistrer_risque(fiche)

        return redirect(url_for("accueil"))

    except (ValueError, TypeError) as erreur:
        return f"<h3>Erreur de saisie : {erreur}</h3><a href='/'>Retour</a>", 400

    except Exception as erreur:
        app.logger.exception("Erreur lors de l'enregistrement")
        return f"<h3>Erreur technique : {erreur}</h3><a href='/'>Retour</a>", 500


# ------------------------------------------------------------
# SUPPRESSION D'UN RISQUE
# ------------------------------------------------------------

@app.route("/supprimer-risque/<int:identifiant>", methods=["POST"])
def supprimer(identifiant):

    try:
        supprimer_risque(identifiant)
        return redirect(url_for("accueil"))

    except Exception as erreur:
        app.logger.exception("Erreur de suppression")
        return f"Erreur : {erreur}", 500


# ------------------------------------------------------------
# ANALYSE TOXICOLOGIQUE SENTOX
# ------------------------------------------------------------

@app.route("/analyse-toxicologique", methods=["GET", "POST"])
def page_analyse_toxicologique():

    rapport = None
    erreur = None

    if request.method == "POST":
        try:
            profil = analyser_substance(
                nom_substance=request.form.get("substance", ""),
                numero_cas=request.form.get("numero_cas", ""),
                voie_exposition=request.form.get(
                    "voie_exposition", "Non renseignée"
                ),
                duree_exposition=request.form.get(
                    "duree_exposition", ""
                ),
                effets_documentes=[
                    x.strip() for x in request.form.get(
                        "effets", ""
                    ).split(";") if x.strip()
                ],
                absorption=request.form.get(
                    "absorption", "Non renseignée"
                ),
                distribution=request.form.get(
                    "distribution", "Non renseignée"
                ),
                metabolisme=request.form.get(
                    "metabolisme", "Non renseigné"
                ),
                elimination=request.form.get(
                    "elimination", "Non renseignée"
                ),
                organes_cibles=[
                    x.strip() for x in request.form.get(
                        "organes", ""
                    ).split(";") if x.strip()
                ],
                effets_environnementaux=[
                    x.strip() for x in request.form.get(
                        "environnement", ""
                    ).split(";") if x.strip()
                ],
                references=[
                    x.strip() for x in request.form.get(
                        "references", ""
                    ).split(";") if x.strip()
                ],
                niveau_preuve=request.form.get(
                    "niveau_preuve", "DONNEES NON VERIFIEES"
                )
            )

            rapport = generer_rapport_toxicologique(profil)

        except (ValueError, TypeError) as exc:
            erreur = str(exc)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Analyse toxicologique - SENTOX</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f1f5f9;
                color: #172033;
                margin: 0;
                padding: 25px;
            }
            main {
                max-width: 1000px;
                margin: auto;
            }
            section {
                background: white;
                padding: 22px;
                margin-bottom: 20px;
                border-radius: 12px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(
                    auto-fit, minmax(240px, 1fr)
                );
                gap: 14px;
            }
            label {
                display: block;
                font-weight: bold;
                margin-bottom: 6px;
            }
            input, select, textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                box-sizing: border-box;
            }
            textarea { min-height: 75px; }
            button {
                background: #0369a1;
                color: white;
                border: 0;
                padding: 12px 20px;
                border-radius: 7px;
                cursor: pointer;
            }
            pre {
                white-space: pre-wrap;
                overflow-wrap: anywhere;
            }
            .erreur { color: #b91c1c; }
                        .rapport-header {
                border-bottom: 3px solid #087e8b;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }
            .rapport-section {
                border: 1px solid #dbe4ec;
                border-radius: 8px;
                padding: 16px;
                margin: 15px 0;
                background: #ffffff;
            }
            .rapport-section h3 {
                color: #075985;
                margin-top: 0;
            }
            .rapport-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 12px;
            }
            .rapport-item {
                background: #f1f5f9;
                padding: 12px;
                border-radius: 6px;
                overflow-wrap: anywhere;
            }
            .rapport-item strong {
                display: block;
                color: #334155;
                margin-bottom: 6px;
            }
            .rapport-liste {
                padding-left: 22px;
                line-height: 1.7;
            }
            .rapport-note {
                background: #fff7ed;
                border-left: 4px solid #ea580c;
                padding: 12px;
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
    <main>
        <section>
            <h1>SENTOX QHSE</h1>
            <h2>Analyse toxicologique d'une substance</h2>

            <form method="POST">
                <div class="grid">
                    <div>
                        <label>Nom de la substance *</label>
                        <input name="substance" required>
                    </div>
                    <div>
                        <label>Numéro CAS</label>
                        <input name="numero_cas">
                    </div>
                    <div>
                        <label>Voie d'exposition</label>
                        <select name="voie_exposition">
                            <option>Non renseignée</option>
                            <option>Inhalation</option>
                            <option>Cutanée</option>
                            <option>Ingestion</option>
                            <option>Oculaire</option>
                            <option>Multiple</option>
                        </select>
                    </div>
                    <div>
                        <label>Durée d'exposition</label>
                        <input name="duree_exposition"
                               placeholder="Ex. 4 heures/jour">
                    </div>
                    <div>
                        <label>Absorption</label>
                        <input name="absorption">
                    </div>
                    <div>
                        <label>Distribution</label>
                        <input name="distribution">
                    </div>
                    <div>
                        <label>Métabolisme</label>
                        <input name="metabolisme">
                    </div>
                    <div>
                        <label>Élimination</label>
                        <input name="elimination">
                    </div>
                </div>

                <p>
                    <label>Effets toxicologiques documentés</label>
                    <textarea name="effets"
                        placeholder="Séparer les éléments par des points-virgules"></textarea>
                </p>
                <p>
                    <label>Organes cibles potentiels</label>
                    <input name="organes"
                        placeholder="Ex. Foie ; Reins ; Poumons">
                </p>
                <p>
                    <label>Effets environnementaux</label>
                    <textarea name="environnement"></textarea>
                </p>
                <p>
                    <label>Références scientifiques</label>
                    <textarea name="references"></textarea>
                </p>
                <p>
                    <label>Niveau de preuve</label>
                    <select name="niveau_preuve">
                        <option>DONNEES NON VERIFIEES</option>
                        <option>DONNEES BIBLIOGRAPHIQUES</option>
                        <option>PREDICTION</option>
                        <option>DONNEES EXPERIMENTALES</option>
                    </select>
                </p>

                <button type="submit">
                    Générer l'analyse toxicologique
                </button>
            </form>
        </section>

        {% if erreur %}
        <section class="erreur">
            <h3>Erreur</h3>
            {{ erreur }}
        </section>
        {% endif %}

        {% if rapport %}
        <section>
            <h2>Résultat de l'analyse</h2>
            <p>
                Les informations affichées sont celles qui ont
                été renseignées. Elles ne constituent pas une
                validation toxicologique automatique.
            </p>
            <h3>Rapport structuré</h3>
            <pre>{{ rapport }}</pre>
        </section>
        {% endif %}

        <p><a href="/">Retour au tableau de bord</a></p>
    </main>
    </body>
    </html>
    """, rapport=rapport, erreur=erreur)

# ------------------------------------------------------------
# VERIFICATION DE SANTE DU SERVICE
# ------------------------------------------------------------

@app.route("/health")
def health():
    return {
        "application": "SENTOX QHSE",
        "version": "1.0",
        "status": "running"
    }


# ------------------------------------------------------------
# LANCEMENT LOCAL
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
