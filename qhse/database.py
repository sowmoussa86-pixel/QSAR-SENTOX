
# ============================================================
# SENTOX QHSE - BASE DE DONNEES SQLITE V1
# ============================================================

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sentox_qhse.db")


def obtenir_connexion():
    connexion = sqlite3.connect(DB_PATH)
    connexion.row_factory = sqlite3.Row
    return connexion


def initialiser_base():
    with obtenir_connexion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS risques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_creation TEXT NOT NULL,
                secteur TEXT NOT NULL,
                activite TEXT NOT NULL,
                danger TEXT NOT NULL,
                personnes_exposees TEXT NOT NULL,
                consequences TEXT NOT NULL,
                gravite INTEGER NOT NULL,
                probabilite INTEGER NOT NULL,
                criticite INTEGER NOT NULL,
                niveau_risque TEXT NOT NULL,
                action_recommandee TEXT,
                mesures_prevention TEXT,
                responsable TEXT,
                echeance TEXT,
                statut TEXT DEFAULT 'A TRAITER'
            )
        """)
        conn.commit()


def enregistrer_risque(fiche):
    with obtenir_connexion() as conn:
        curseur = conn.execute("""
            INSERT INTO risques (
                date_creation, secteur, activite, danger,
                personnes_exposees, consequences, gravite,
                probabilite, criticite, niveau_risque,
                action_recommandee, mesures_prevention,
                responsable, echeance, statut
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fiche["date_creation"],
            fiche["secteur"],
            fiche["activite"],
            fiche["danger"],
            fiche["personnes_exposees"],
            fiche["consequences"],
            fiche["gravite"],
            fiche["probabilite"],
            fiche["criticite"],
            fiche["niveau_risque"],
            fiche["action_recommandee"],
            fiche["mesures_prevention"],
            fiche["responsable"],
            fiche["echeance"],
            fiche["statut"]
        ))

        return curseur.lastrowid


def lister_risques():
    with obtenir_connexion() as conn:
        lignes = conn.execute("""
            SELECT * FROM risques ORDER BY id DESC
        """).fetchall()

        return [dict(ligne) for ligne in lignes]


def supprimer_risque(identifiant):
    with obtenir_connexion() as conn:
        curseur = conn.execute(
            "DELETE FROM risques WHERE id = ?",
            (identifiant,)
        )
        return curseur.rowcount > 0
