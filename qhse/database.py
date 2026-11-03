
# ============================================================
# SENTOX QHSE - BASE DE DONNEES SQLITE V2
# Architecture multientreprise
# ============================================================

import sqlite3
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sentox_qhse.db")


def obtenir_connexion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialiser_base():
    with obtenir_connexion() as conn:

        # ENTREPRISES
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entreprises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                secteur TEXT,
                adresse TEXT,
                pays TEXT DEFAULT 'Senegal',
                email TEXT,
                telephone TEXT,
                date_creation TEXT NOT NULL,
                statut TEXT DEFAULT 'ACTIVE'
            )
        """)

        # UTILISATEURS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                nom TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                mot_de_passe_hash TEXT,
                date_creation TEXT NOT NULL,
                statut TEXT DEFAULT 'ACTIF',
                UNIQUE(entreprise_id, email),
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # REGISTRE DES RISQUES
        conn.execute("""
            CREATE TABLE IF NOT EXISTS risques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER,
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
                statut TEXT DEFAULT 'A TRAITER',
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # MIGRATION : compatibilite avec ancienne base V1
        colonnes = [
            ligne["name"]
            for ligne in conn.execute(
                "PRAGMA table_info(risques)"
            ).fetchall()
        ]

        if "entreprise_id" not in colonnes:
            conn.execute(
                "ALTER TABLE risques ADD COLUMN entreprise_id INTEGER"
            )

        # ACTIONS CORRECTIVES ET PREVENTIVES
        conn.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                risque_id INTEGER,
                description TEXT NOT NULL,
                responsable TEXT NOT NULL,
                echeance TEXT,
                priorite TEXT DEFAULT 'NORMALE',
                statut TEXT DEFAULT 'A FAIRE',
                date_creation TEXT NOT NULL,
                date_cloture TEXT,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id),
                FOREIGN KEY(risque_id)
                    REFERENCES risques(id)
            )
        """)

        # AUDITS ET INSPECTIONS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                secteur TEXT,
                type_audit TEXT NOT NULL,
                auditeur TEXT NOT NULL,
                reference TEXT,
                date_audit TEXT NOT NULL,
                statut TEXT DEFAULT 'PLANIFIE',
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # CONSTATS D'AUDIT
        conn.execute("""
            CREATE TABLE IF NOT EXISTS constats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL,
                exigence TEXT NOT NULL,
                constat TEXT NOT NULL,
                statut TEXT NOT NULL,
                recommandation TEXT,
                FOREIGN KEY(audit_id)
                    REFERENCES audits(id) ON DELETE CASCADE
            )
        """)

        # IMPACTS ENVIRONNEMENTAUX
        conn.execute("""
            CREATE TABLE IF NOT EXISTS impacts_environnementaux (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                secteur TEXT NOT NULL,
                activite TEXT NOT NULL,
                aspect TEXT,
                impact TEXT,
                categorie TEXT,
                gravite INTEGER,
                probabilite INTEGER,
                criticite INTEGER,
                niveau TEXT,
                mesures_maitrise TEXT,
                date_creation TEXT NOT NULL,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # ====================================================
        # COMPTES CENTRAUX ET ACCES AUX ENTREPRISES
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS comptes_utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                mot_de_passe_hash TEXT NOT NULL,
                role_global TEXT DEFAULT 'EXPERT',
                statut TEXT DEFAULT 'ACTIF',
                date_creation TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS acces_entreprises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilisateur_id INTEGER NOT NULL,
                entreprise_id INTEGER NOT NULL,
                role_entreprise TEXT NOT NULL,
                date_creation TEXT NOT NULL,
                UNIQUE(utilisateur_id, entreprise_id),
                FOREIGN KEY(utilisateur_id)
                    REFERENCES comptes_utilisateurs(id),
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # ====================================================
        # SITES DES ENTREPRISES
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                nom TEXT NOT NULL,
                adresse TEXT,
                secteur TEXT,
                responsable TEXT,
                effectif INTEGER DEFAULT 0,
                statut TEXT DEFAULT 'ACTIF',
                date_creation TEXT NOT NULL,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # ====================================================
        # MISSIONS D'EXPERTISE SENTOX
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                site_id INTEGER,
                reference TEXT UNIQUE,
                titre TEXT NOT NULL,
                description TEXT,
                type_prestation TEXT,
                date_debut TEXT,
                date_fin TEXT,
                responsable_sentox TEXT,
                statut TEXT DEFAULT 'PLANIFIEE',
                date_creation TEXT NOT NULL,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id),
                FOREIGN KEY(site_id)
                    REFERENCES sites(id)
            )
        """)

        # ====================================================
        # RAPPORTS ET VALIDATION PAR L'EXPERT
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS rapports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                mission_id INTEGER,
                titre TEXT NOT NULL,
                type_rapport TEXT,
                contenu TEXT,
                statut TEXT DEFAULT 'BROUILLON',
                redacteur_id INTEGER,
                validateur_id INTEGER,
                date_creation TEXT NOT NULL,
                date_validation TEXT,
                date_publication TEXT,
                observations_validation TEXT,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id),
                FOREIGN KEY(mission_id)
                    REFERENCES missions(id),
                FOREIGN KEY(redacteur_id)
                    REFERENCES comptes_utilisateurs(id),
                FOREIGN KEY(validateur_id)
                    REFERENCES comptes_utilisateurs(id)
            )
        """)

        # ====================================================
        # ABONNEMENTS DES ENTREPRISES
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS abonnements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                formule TEXT NOT NULL,
                montant REAL NOT NULL DEFAULT 0,
                devise TEXT DEFAULT 'XOF',
                periodicite TEXT,
                date_debut TEXT NOT NULL,
                date_fin TEXT,
                statut TEXT DEFAULT 'EN_ATTENTE',
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # ====================================================
        # FACTURES : ABONNEMENTS ET PRESTATIONS
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS factures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                mission_id INTEGER,
                abonnement_id INTEGER,
                numero_facture TEXT NOT NULL UNIQUE,
                objet TEXT NOT NULL,
                montant REAL NOT NULL,
                devise TEXT DEFAULT 'XOF',
                date_emission TEXT NOT NULL,
                date_echeance TEXT,
                statut TEXT DEFAULT 'IMPAYEE',
                date_paiement TEXT,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id),
                FOREIGN KEY(mission_id)
                    REFERENCES missions(id),
                FOREIGN KEY(abonnement_id)
                    REFERENCES abonnements(id)
            )
        """)

        # ====================================================
        # INDEX POUR LES RECHERCHES PAR ENTREPRISE
        # ====================================================

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sites_entreprise
            ON sites(entreprise_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_missions_entreprise
            ON missions(entreprise_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_rapports_entreprise
            ON rapports(entreprise_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_acces_utilisateur
            ON acces_entreprises(utilisateur_id)
        """)

        # HISTORIQUE
        conn.execute("""
            CREATE TABLE IF NOT EXISTS historique (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER,
                utilisateur_id INTEGER,
                module TEXT NOT NULL,
                operation TEXT NOT NULL,
                description TEXT,
                date_operation TEXT NOT NULL,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id),
                FOREIGN KEY(utilisateur_id)
                    REFERENCES utilisateurs(id)
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_risques_entreprise
            ON risques(entreprise_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_actions_entreprise
            ON actions(entreprise_id)
        """)

        conn.commit()


# ============================================================
# GESTION DES ENTREPRISES
# ============================================================

def creer_entreprise(nom, secteur="", adresse="",
                     email="", telephone="", pays="Senegal"):

    if not nom or not nom.strip():
        raise ValueError("Le nom de l'entreprise est obligatoire.")

    with obtenir_connexion() as conn:
        curseur = conn.execute("""
            INSERT INTO entreprises (
                nom, secteur, adresse, email,
                telephone, pays, date_creation
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nom.strip(), secteur, adresse, email,
            telephone, pays,
            datetime.now().isoformat(timespec="seconds")
        ))
        return curseur.lastrowid


def lister_entreprises():
    with obtenir_connexion() as conn:
        lignes = conn.execute("""
            SELECT * FROM entreprises ORDER BY nom
        """).fetchall()
        return [dict(ligne) for ligne in lignes]


# ============================================================
# GESTION DES UTILISATEURS
# ============================================================

def creer_utilisateur(entreprise_id, nom, email, role,
                      mot_de_passe_hash=None):

    if not nom or not email or not role:
        raise ValueError("Nom, email et rôle obligatoires.")

    with obtenir_connexion() as conn:
        curseur = conn.execute("""
            INSERT INTO utilisateurs (
                entreprise_id, nom, email, role,
                mot_de_passe_hash, date_creation
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entreprise_id, nom, email, role,
            mot_de_passe_hash,
            datetime.now().isoformat(timespec="seconds")
        ))
        return curseur.lastrowid


# ============================================================
# GESTION DES RISQUES
# ============================================================

def enregistrer_risque(fiche, entreprise_id=None):

    with obtenir_connexion() as conn:
        curseur = conn.execute("""
            INSERT INTO risques (
                entreprise_id, date_creation, secteur,
                activite, danger, personnes_exposees,
                consequences, gravite, probabilite,
                criticite, niveau_risque,
                action_recommandee, mesures_prevention,
                responsable, echeance, statut
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?)
        """, (
            entreprise_id,
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


def lister_risques(entreprise_id=None):

    with obtenir_connexion() as conn:
        if entreprise_id is None:
            lignes = conn.execute("""
                SELECT * FROM risques ORDER BY id DESC
            """).fetchall()
        else:
            lignes = conn.execute("""
                SELECT * FROM risques
                WHERE entreprise_id = ?
                ORDER BY id DESC
            """, (entreprise_id,)).fetchall()

        return [dict(ligne) for ligne in lignes]


def supprimer_risque(identifiant):
    with obtenir_connexion() as conn:
        curseur = conn.execute(
            "DELETE FROM risques WHERE id = ?",
            (identifiant,)
        )
        return curseur.rowcount > 0


        # ====================================================
        # COMPTES CENTRAUX ET ACCES MULTI-ENTREPRISES
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS comptes_utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                mot_de_passe_hash TEXT NOT NULL,
                role_global TEXT DEFAULT 'EXPERT',
                statut TEXT DEFAULT 'ACTIF',
                date_creation TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS acces_entreprises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilisateur_id INTEGER NOT NULL,
                entreprise_id INTEGER NOT NULL,
                role_entreprise TEXT NOT NULL,
                date_creation TEXT NOT NULL,
                UNIQUE(utilisateur_id, entreprise_id),
                FOREIGN KEY(utilisateur_id)
                    REFERENCES comptes_utilisateurs(id),
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # ====================================================
        # SITES DES ENTREPRISES
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                nom TEXT NOT NULL,
                adresse TEXT,
                secteur TEXT,
                responsable TEXT,
                effectif INTEGER DEFAULT 0,
                statut TEXT DEFAULT 'ACTIF',
                date_creation TEXT NOT NULL,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # ====================================================
        # MISSIONS D'EXPERTISE
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                site_id INTEGER,
                reference TEXT UNIQUE,
                titre TEXT NOT NULL,
                description TEXT,
                type_prestation TEXT,
                date_debut TEXT,
                date_fin TEXT,
                responsable_sentox TEXT,
                statut TEXT DEFAULT 'PLANIFIEE',
                date_creation TEXT NOT NULL,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id),
                FOREIGN KEY(site_id)
                    REFERENCES sites(id)
            )
        """)

        # ====================================================
        # RAPPORTS ET VALIDATION
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS rapports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                mission_id INTEGER,
                titre TEXT NOT NULL,
                type_rapport TEXT,
                contenu TEXT,
                statut TEXT DEFAULT 'BROUILLON',
                redacteur_id INTEGER,
                validateur_id INTEGER,
                date_creation TEXT NOT NULL,
                date_validation TEXT,
                date_publication TEXT,
                observations_validation TEXT,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id),
                FOREIGN KEY(mission_id)
                    REFERENCES missions(id),
                FOREIGN KEY(redacteur_id)
                    REFERENCES comptes_utilisateurs(id),
                FOREIGN KEY(validateur_id)
                    REFERENCES comptes_utilisateurs(id)
            )
        """)

        # ====================================================
        # ABONNEMENTS
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS abonnements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                formule TEXT NOT NULL,
                montant REAL NOT NULL DEFAULT 0,
                devise TEXT DEFAULT 'XOF',
                periodicite TEXT,
                date_debut TEXT NOT NULL,
                date_fin TEXT,
                statut TEXT DEFAULT 'EN_ATTENTE',
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id)
            )
        """)

        # ====================================================
        # FACTURES
        # ====================================================

        conn.execute("""
            CREATE TABLE IF NOT EXISTS factures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entreprise_id INTEGER NOT NULL,
                mission_id INTEGER,
                abonnement_id INTEGER,
                numero_facture TEXT NOT NULL UNIQUE,
                objet TEXT NOT NULL,
                montant REAL NOT NULL,
                devise TEXT DEFAULT 'XOF',
                date_emission TEXT NOT NULL,
                date_echeance TEXT,
                statut TEXT DEFAULT 'IMPAYEE',
                date_paiement TEXT,
                FOREIGN KEY(entreprise_id)
                    REFERENCES entreprises(id),
                FOREIGN KEY(mission_id)
                    REFERENCES missions(id),
                FOREIGN KEY(abonnement_id)
                    REFERENCES abonnements(id)
            )
        """)

        # INDEX DE RECHERCHE
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sites_entreprise
            ON sites(entreprise_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_missions_entreprise
            ON missions(entreprise_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_rapports_entreprise
            ON rapports(entreprise_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_acces_utilisateur
            ON acces_entreprises(utilisateur_id)
        """)

# ============================================================
# HISTORIQUE DES OPERATIONS
# ============================================================

def enregistrer_historique(
    module, operation, description="",
    entreprise_id=None, utilisateur_id=None
):
    with obtenir_connexion() as conn:
        conn.execute("""
            INSERT INTO historique (
                entreprise_id, utilisateur_id,
                module, operation, description,
                date_operation
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entreprise_id,
            utilisateur_id,
            module,
            operation,
            description,
            datetime.now().isoformat(timespec="seconds")
        ))


# ============================================================
# INITIALISATION
# ============================================================

if __name__ == "__main__":
    initialiser_base()
    print("SENTOX QHSE V2 : base SQLite initialisee.")
