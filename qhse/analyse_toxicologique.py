
# ============================================================
# SENTOX QHSE - MOTEUR D'ANALYSE TOXICOLOGIQUE V1
# Analyse sanitaire, ADME-Tox et environnementale
# ============================================================

from datetime import datetime


def verifier_texte(valeur):
    return str(valeur or "").strip()


def analyser_substance(
    nom_substance,
    numero_cas="",
    voie_exposition="",
    duree_exposition="",
    effets_documentes=None,
    absorption="Non renseignée",
    distribution="Non renseignée",
    metabolisme="Non renseigné",
    elimination="Non renseignée",
    organes_cibles=None,
    effets_environnementaux=None,
    references=None,
    niveau_preuve="DONNEES NON VERIFIEES"
):
    """
    Construit un profil toxicologique à partir des données fournies.
    Ne fabrique pas de résultats ADME ou de toxicité.
    """

    if not verifier_texte(nom_substance):
        raise ValueError("Le nom de la substance est obligatoire.")

    effets_documentes = effets_documentes or []
    organes_cibles = organes_cibles or []
    effets_environnementaux = effets_environnementaux or []
    references = references or []

    voies_valides = [
        "Inhalation",
        "Cutanée",
        "Ingestion",
        "Oculaire",
        "Multiple",
        "Non renseignée"
    ]

    if voie_exposition and voie_exposition not in voies_valides:
        raise ValueError("Voie d'exposition non reconnue.")

    return {
        "date_analyse": datetime.now().isoformat(
            timespec="seconds"
        ),
        "substance": verifier_texte(nom_substance),
        "numero_cas": verifier_texte(numero_cas),
        "voie_exposition": voie_exposition or "Non renseignée",
        "duree_exposition": duree_exposition,

        "consequences_potentielles": effets_documentes,

        "adme_tox": {
            "absorption": absorption,
            "distribution": distribution,
            "metabolisme": metabolisme,
            "elimination": elimination
        },

        "organes_cibles": organes_cibles,
        "effets_environnementaux": effets_environnementaux,

        "niveau_preuve": niveau_preuve,
        "references": references,

        "avertissement": (
            "Les effets et données ADME dépendent des informations "
            "documentaires fournies. Les données absentes ne sont "
            "pas considérées comme négatives. Une prédiction ne "
            "constitue pas une preuve d'effet chez l'être humain."
        )
    }


def generer_prevention(profil):
    """
    Propose des mesures générales selon la voie d'exposition.
    À adapter par l'expert QHSE après étude du poste.
    """

    voie = profil.get("voie_exposition", "")

    mesures = [
        "Substituer la substance par une solution moins dangereuse "
        "lorsque cela est techniquement possible.",
        "Consulter la fiche de données de sécurité.",
        "Limiter les quantités manipulées et les durées d'exposition.",
        "Former les travailleurs aux risques et aux procédures.",
        "Mettre en place une procédure de gestion des incidents."
    ]

    if voie in ["Inhalation", "Multiple"]:
        mesures.extend([
            "Évaluer la ventilation et le captage à la source.",
            "Contrôler les concentrations dans l'air.",
            "Définir une protection respiratoire adaptée si nécessaire."
        ])

    if voie in ["Cutanée", "Multiple"]:
        mesures.extend([
            "Éviter le contact direct avec la substance.",
            "Choisir des gants compatibles avec le produit.",
            "Prévoir un dispositif de lavage adapté."
        ])

    if voie in ["Ingestion", "Multiple"]:
        mesures.extend([
            "Interdire de manger et boire dans la zone de manipulation.",
            "Assurer le lavage des mains avant les pauses."
        ])

    mesures.extend([
        "Collecter et éliminer les déchets selon leur classification.",
        "Prévenir les rejets vers les eaux et les sols.",
        "Évaluer les risques résiduels après mise en place des mesures."
    ])

    return mesures


def generer_rapport_toxicologique(profil):
    """
    Prépare les données structurées destinées au rapport PDF.
    """

    if not isinstance(profil, dict):
        raise ValueError("Le profil toxicologique est invalide.")

    return {
        "titre": "SENTOX QHSE - Rapport toxicologique",
        "date": profil.get("date_analyse"),
        "substance": profil.get("substance"),
        "numero_cas": profil.get("numero_cas"),
        "voie_exposition": profil.get("voie_exposition"),
        "consequences": profil.get("consequences_potentielles", []),
        "adme_tox": profil.get("adme_tox", {}),
        "organes_cibles": profil.get("organes_cibles", []),
        "risques_environnementaux": profil.get(
            "effets_environnementaux", []
        ),
        "mesures_prevention": generer_prevention(profil),
        "niveau_preuve": profil.get("niveau_preuve"),
        "references": profil.get("references", []),
        "limites": profil.get("avertissement")
    }
