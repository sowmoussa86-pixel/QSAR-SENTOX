
import sqlite3
from pathlib import Path

# Base de données dédiée au module QHSE
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "qhse_sentox.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS risques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_creation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                domaine TEXT NOT NULL,
                titre TEXT NOT NULL,
                description TEXT DEFAULT '',
                gravite INTEGER NOT NULL CHECK(gravite BETWEEN 1 AND 5),
                probabilite INTEGER NOT NULL CHECK(probabilite BETWEEN 1 AND 5),
                mesures_prevention TEXT DEFAULT '',
                statut TEXT NOT NULL DEFAULT 'Ouvert',
                responsable TEXT DEFAULT '',
                echeance TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                risque_id INTEGER,
                date_creation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                description TEXT NOT NULL,
                responsable TEXT DEFAULT '',
                echeance TEXT DEFAULT '',
                statut TEXT NOT NULL DEFAULT 'À faire',
                FOREIGN KEY(risque_id)
                    REFERENCES risques(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS evaluations_chimiques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_creation TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                produit TEXT NOT NULL,
                fabricant TEXT DEFAULT '',
                numero_cas TEXT DEFAULT '',
                danger TEXT DEFAULT '',
                exposition TEXT DEFAULT '',
                prevention TEXT DEFAULT '',
                fds TEXT DEFAULT 'inconnue',
                statut TEXT NOT NULL DEFAULT 'Préliminaire'
            );
        """)


def ajouter_risque(
    domaine,
    titre,
    description="",
    gravite=1,
    probabilite=1,
    mesures_prevention="",
    responsable="",
    echeance=""
):
    domaine = domaine.strip()
    titre = titre.strip()

    if not domaine or not titre:
        raise ValueError("Le domaine et le titre sont obligatoires.")

    gravite = int(gravite)
    probabilite = int(probabilite)

    if not 1 <= gravite <= 5 or not 1 <= probabilite <= 5:
        raise ValueError("La gravité et la probabilité doivent être entre 1 et 5.")

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO risques (
                domaine, titre, description, gravite, probabilite,
                mesures_prevention, responsable, echeance
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            domaine, titre, description, gravite, probabilite,
            mesures_prevention, responsable, echeance
        ))
        return cursor.lastrowid


def lister_risques():
    with get_connection() as conn:
        return conn.execute("""
            SELECT *,
                   gravite * probabilite AS score
            FROM risques
            ORDER BY id DESC
        """).fetchall()


def ajouter_action(
    description,
    risque_id=None,
    responsable="",
    echeance=""
):
    description = description.strip()

    if not description:
        raise ValueError("La description de l'action est obligatoire.")

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO actions (
                risque_id, description, responsable, echeance
            )
            VALUES (?, ?, ?, ?)
        """, (risque_id, description, responsable, echeance))
        return cursor.lastrowid


def lister_actions():
    with get_connection() as conn:
        return conn.execute("""
            SELECT actions.*, risques.titre AS risque_titre
            FROM actions
            LEFT JOIN risques ON risques.id = actions.risque_id
            ORDER BY actions.id DESC
        """).fetchall()
