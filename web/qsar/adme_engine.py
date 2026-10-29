# ============================================================
# SENTOX — MOTEUR ADME STRUCTUREL
# V1.0
# ============================================================
#
# Ce module produit un profil ADME à partir des descripteurs
# moléculaires calculés par RDKit.
#
# IMPORTANT :
# Les résultats sont des INDICATEURS STRUCTURELS.
# Ils ne remplacent pas des données expérimentales ni
# un modèle ADME validé.
# ============================================================

from web.qsar.descriptors_engine import calculer_descripteurs_rdkit


def resultat_adme():
    return {
        "valeur": None,
        "statut": "NON DISPONIBLE",
        "source": None,
        "confiance": None,
        "unite": None,
        "commentaire": None,
    }


def analyser_adme_structure(smiles):
    """
    Génère un profil ADME structurel à partir d'un SMILES.

    Les résultats sont calculés à partir des descripteurs RDKit.
    Ils constituent des indicateurs et non des données
    pharmacocinétiques expérimentales.
    """

    adme = {
        "absorption": resultat_adme(),
        "distribution": resultat_adme(),
        "metabolisme": resultat_adme(),
        "excretion": resultat_adme(),
        "descripteurs_support": {},
        "statut_global": "NON DISPONIBLE",
        "moteur": "RDKit",
        "type_resultat": "INDICATEUR STRUCTUREL",
    }

    if not smiles:
        return adme

    descripteurs = calculer_descripteurs_rdkit(smiles)

    if descripteurs.get("statut") != "CALCULÉ — RDKit":
        adme["statut_global"] = "ERREUR"
        adme["message"] = descripteurs.get(
            "message",
            "Impossible de calculer les descripteurs."
        )
        return adme

    # --------------------------------------------------------
    # DESCRIPTEURS UTILISÉS PAR LE PROFIL ADME
    # --------------------------------------------------------

    champs = [
        "masse_molaire",
        "logP",
        "tpsa",
        "HBD",
        "HBA",
        "liaisons_rotatables",
        "fraction_CSP3",
        "charge_formelle",
        "nombre_anneaux",
        "anneaux_aromatiques",
        "nombre_atomes_lourds",
    ]

    adme["descripteurs_support"] = {
        champ: descripteurs.get(champ)
        for champ in champs
    }

    # --------------------------------------------------------
    # ABSORPTION
    # --------------------------------------------------------

    adme["absorption"] = {
        "valeur": {
            "masse_molaire": descripteurs["masse_molaire"],
            "logP": descripteurs["logP"],
            "tpsa": descripteurs["tpsa"],
            "HBD": descripteurs["HBD"],
            "HBA": descripteurs["HBA"],
            "liaisons_rotatables": descripteurs[
                "liaisons_rotatables"
            ],
        },
        "statut": "CALCULÉ — INDICATEUR STRUCTUREL",
        "source": "RDKit",
        "confiance": "À interpréter",
        "unite": None,
        "commentaire": (
            "Profil structurel pouvant contribuer à l'évaluation "
            "de l'absorption. Ne constitue pas une mesure "
            "expérimentale de biodisponibilité ou de perméabilité."
        ),
    }

    # --------------------------------------------------------
    # DISTRIBUTION
    # --------------------------------------------------------

    adme["distribution"] = {
        "valeur": {
            "masse_molaire": descripteurs["masse_molaire"],
            "logP": descripteurs["logP"],
            "tpsa": descripteurs["tpsa"],
            "charge_formelle": descripteurs["charge_formelle"],
            "fraction_CSP3": descripteurs["fraction_CSP3"],
        },
        "statut": "CALCULÉ — INDICATEUR STRUCTUREL",
        "source": "RDKit",
        "confiance": "À interpréter",
        "unite": None,
        "commentaire": (
            "Profil structurel pertinent pour l'analyse de la "
            "distribution. Ne constitue pas une mesure "
            "expérimentale du volume de distribution ou de la "
            "liaison aux protéines plasmatiques."
        ),
    }

    # --------------------------------------------------------
    # METABOLISME
    # --------------------------------------------------------

    adme["metabolisme"] = {
        "valeur": {
            "logP": descripteurs["logP"],
            "HBD": descripteurs["HBD"],
            "HBA": descripteurs["HBA"],
            "tpsa": descripteurs["tpsa"],
            "anneaux_aromatiques": descripteurs[
                "anneaux_aromatiques"
            ],
            "liaisons_rotatables": descripteurs[
                "liaisons_rotatables"
            ],
        },
        "statut": "CALCULÉ — INDICATEUR STRUCTUREL",
        "source": "RDKit",
        "confiance": "À interpréter",
        "unite": None,
        "commentaire": (
            "Descripteurs structurels associés à l'analyse "
            "du devenir métabolique. Aucun métabolite ni "
            "enzyme métabolique n'est prédit par cette V1."
        ),
    }

    # --------------------------------------------------------
    # EXCRETION
    # --------------------------------------------------------

    adme["excretion"] = {
        "valeur": {
            "masse_molaire": descripteurs["masse_molaire"],
            "tpsa": descripteurs["tpsa"],
            "charge_formelle": descripteurs["charge_formelle"],
            "HBD": descripteurs["HBD"],
            "HBA": descripteurs["HBA"],
        },
        "statut": "CALCULÉ — INDICATEUR STRUCTUREL",
        "source": "RDKit",
        "confiance": "À interpréter",
        "unite": None,
        "commentaire": (
            "Profil structurel pouvant contribuer à l'analyse "
            "du devenir et de l'élimination. Ne constitue pas "
            "une mesure expérimentale de clairance ou de demi-vie."
        ),
    }

    adme["statut_global"] = "CALCULÉ — PROFIL STRUCTUREL"

    return adme


def verifier_adme(smiles):
    """
    Vérifie que le moteur ADME fonctionne correctement.
    """

    resultat = analyser_adme_structure(smiles)

    return (
        resultat.get("statut_global")
        == "CALCULÉ — PROFIL STRUCTUREL"
    )
