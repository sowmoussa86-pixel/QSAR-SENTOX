# ============================================================
# SENTOX — MOTEUR D'INTERACTIONS
# ============================================================

"""
SENTOX INTERACTION ENGINE

Analyse les interactions potentielles entre :
- plantes
- extraits
- aliments
- médicaments
- cosmétiques
- substances
- molécules
- produits complexes

IMPORTANT :
Ce module distingue :
    DOCUMENTÉ  -> interaction rapportée dans une source
    CALCULÉ    -> résultat obtenu par calcul/règle
    PRÉDIT     -> résultat issu d'un modèle prédictif

Une prédiction ne constitue pas une preuve expérimentale.
"""


# ============================================================
# 1. STRUCTURE STANDARD D'UNE INTERACTION
# ============================================================

def creer_interaction(
    element_a,
    element_b
):
    """
    Crée la structure standard d'une interaction.
    """

    return {

        "element_a": element_a,

        "element_b": element_b,

        "interaction_globale": {
            "valeur": None,
            "statut": "à analyser",
            "confiance": None
        },

        "potentialisation": {
            "valeur": None,
            "statut": "à analyser",
            "confiance": None
        },

        "antagonisme": {
            "valeur": None,
            "statut": "à analyser",
            "confiance": None
        },

        "inhibition": {
            "valeur": None,
            "statut": "à analyser",
            "confiance": None
        },

        "competition": {
            "valeur": None,
            "statut": "à analyser",
            "confiance": None
        },

        "synergie": {
            "valeur": None,
            "statut": "à analyser",
            "confiance": None
        },

        "interaction_pk": {
            "valeur": None,
            "statut": "à analyser",
            "confiance": None
        },

        "interaction_pd": {
            "valeur": None,
            "statut": "à analyser",
            "confiance": None
        },

        "cibles_communes": [],

        "enzymes_communes": [],

        "transporteurs_communs": [],

        "organes_potentiels": [],

        "sources": [],

        "conclusion": None
    }


# ============================================================
# 2. INTERACTION DOCUMENTÉE
# ============================================================

def interaction_documentee(
    element_a,
    element_b,
    type_interaction,
    description,
    source=None
):
    """
    Enregistre une interaction déjà rapportée
    dans la littérature ou une base scientifique.
    """

    interaction = creer_interaction(
        element_a,
        element_b
    )

    if type_interaction in interaction:

        interaction[type_interaction] = {

            "valeur": description,

            "statut": "documenté",

            "confiance": "source scientifique"
        }

    interaction["sources"] = []

    if source:

        interaction["sources"].append(source)

    interaction["conclusion"] = (
        "Interaction documentée dans les données disponibles."
    )

    return interaction


# ============================================================
# 3. INTERACTION CALCULÉE
# ============================================================

def interaction_calculee(
    element_a,
    element_b,
    type_interaction,
    valeur,
    methode="règle de calcul SENTOX"
):
    """
    Enregistre un résultat obtenu par calcul.
    """

    interaction = creer_interaction(
        element_a,
        element_b
    )

    if type_interaction in interaction:

        interaction[type_interaction] = {

            "valeur": valeur,

            "statut": "calculé",

            "confiance": methode
        }

    interaction["conclusion"] = (
        "Résultat obtenu par calcul. "
        "Il ne constitue pas une preuve expérimentale."
    )

    return interaction


# ============================================================
# 4. INTERACTION PRÉDITE
# ============================================================

def interaction_predite(
    element_a,
    element_b,
    type_interaction,
    prediction,
    confiance=None,
    modele="SENTOX-QSAR"
):
    """
    Enregistre une prédiction.
    """

    interaction = creer_interaction(
        element_a,
        element_b
    )

    if type_interaction in interaction:

        interaction[type_interaction] = {

            "valeur": prediction,

            "statut": "prédit",

            "confiance": confiance,

            "modele": modele
        }

    interaction["conclusion"] = (
        "Interaction prédite par SENTOX-QSAR. "
        "Cette prédiction doit être interprétée "
        "avec son niveau d'incertitude."
    )

    return interaction


# ============================================================
# 5. COMPARAISON DES CIBLES BIOLOGIQUES
# ============================================================

def comparer_cibles(
    cibles_a,
    cibles_b
):
    """
    Recherche les cibles biologiques communes.
    """

    if not cibles_a or not cibles_b:

        return []

    a = {
        str(x).strip().lower()
        for x in cibles_a
    }

    b = {
        str(x).strip().lower()
        for x in cibles_b
    }

    return sorted(
        list(a.intersection(b))
    )


# ============================================================
# 6. COMPARAISON DES ENZYMES
# ============================================================

def comparer_enzymes(
    enzymes_a,
    enzymes_b
):
    """
    Recherche les enzymes communes.
    """

    if not enzymes_a or not enzymes_b:

        return []

    a = {
        str(x).strip().lower()
        for x in enzymes_a
    }

    b = {
        str(x).strip().lower()
        for x in enzymes_b
    }

    return sorted(
        list(a.intersection(b))
    )


# ============================================================
# 7. COMPARAISON DES TRANSPORTEURS
# ============================================================

def comparer_transporteurs(
    transporteurs_a,
    transporteurs_b
):
    """
    Recherche les transporteurs communs.
    """

    if not transporteurs_a or not transporteurs_b:

        return []

    a = {
        str(x).strip().lower()
        for x in transporteurs_a
    }

    b = {
        str(x).strip().lower()
        for x in transporteurs_b
    }

    return sorted(
        list(a.intersection(b))
    )


# ============================================================
# 8. ORGANES POTENTIELLEMENT CONCERNÉS
# ============================================================

def comparer_organes(
    organes_a,
    organes_b
):
    """
    Recherche les organes communs.
    """

    if not organes_a or not organes_b:

        return []

    a = {
        str(x).strip().lower()
        for x in organes_a
    }

    b = {
        str(x).strip().lower()
        for x in organes_b
    }

    return sorted(
        list(a.intersection(b))
    )


# ============================================================
# 9. ANALYSE STRUCTURALE
# ============================================================

def analyser_similarite_moleculaire(
    molecule_a,
    molecule_b
):
    """
    Prépare la comparaison de deux molécules.

    La similarité structurale ne signifie PAS
    automatiquement qu'une interaction biologique existe.
    """

    if not molecule_a or not molecule_b:

        return {

            "statut": "non disponible",

            "similarite": None,

            "interpretation":
                "Structures insuffisantes pour comparaison."
        }

    smiles_a = molecule_a.get(
        "SMILES",
        molecule_a.get("smiles")
    )

    smiles_b = molecule_b.get(
        "SMILES",
        molecule_b.get("smiles")
    )

    if not smiles_a or not smiles_b:

        return {

            "statut": "non disponible",

            "similarite": None,

            "interpretation":
                "SMILES manquants."
        }

    return {

        "statut": "à calculer",

        "similarite": None,

        "smiles_a": smiles_a,

        "smiles_b": smiles_b,

        "interpretation":
            "Une comparaison structurale peut être effectuée."
    }


# ============================================================
# 10. ANALYSE D'UNE PAIRE
# ============================================================

def analyser_paire(
    element_a,
    element_b,
    donnees_a=None,
    donnees_b=None
):
    """
    Analyse deux éléments.
    """

    donnees_a = donnees_a or {}
    donnees_b = donnees_b or {}

    interaction = creer_interaction(
        element_a,
        element_b
    )

    # --------------------------------------------------------
    # CIBLES
    # --------------------------------------------------------

    cibles_a = donnees_a.get(
        "cibles",
        donnees_a.get("targets", [])
    )

    cibles_b = donnees_b.get(
        "cibles",
        donnees_b.get("targets", [])
    )

    interaction["cibles_communes"] = comparer_cibles(
        cibles_a,
        cibles_b
    )

    # --------------------------------------------------------
    # ENZYMES
    # --------------------------------------------------------

    enzymes_a = donnees_a.get(
        "enzymes",
        donnees_a.get("enzymes_cibles", [])
    )

    enzymes_b = donnees_b.get(
        "enzymes",
        donnees_b.get("enzymes_cibles", [])
    )

    interaction["enzymes_communes"] = comparer_enzymes(
        enzymes_a,
        enzymes_b
    )

    # --------------------------------------------------------
    # TRANSPORTEURS
    # --------------------------------------------------------

    transporteurs_a = donnees_a.get(
        "transporteurs",
        []
    )

    transporteurs_b = donnees_b.get(
        "transporteurs",
        []
    )

    interaction["transporteurs_communs"] = comparer_transporteurs(
        transporteurs_a,
        transporteurs_b
    )

    # --------------------------------------------------------
    # ORGANES
    # --------------------------------------------------------

    organes_a = donnees_a.get(
        "organes_cibles",
        []
    )

    organes_b = donnees_b.get(
        "organes_cibles",
        []
    )

    interaction["organes_potentiels"] = comparer_organes(
        organes_a,
        organes_b
    )

    # --------------------------------------------------------
    # STRUCTURES MOLECULAIRES
    # --------------------------------------------------------

    molecule_a = donnees_a.get(
        "molecule",
        {}
    )

    molecule_b = donnees_b.get(
        "molecule",
        {}
    )

    interaction["similarite_moleculaire"] = (
        analyser_similarite_moleculaire(
            molecule_a,
            molecule_b
        )
    )

    # --------------------------------------------------------
    # STATUT INITIAL
    # --------------------------------------------------------

    interaction["interaction_globale"] = {

        "valeur":
            "Analyse prédictive à effectuer",

        "statut":
            "prédit",

        "confiance":
            None
    }

    # --------------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------------

    interaction["conclusion"] = (
        "SENTOX a identifié les paramètres disponibles "
        "permettant d'étudier l'interaction entre les deux "
        "éléments. Une interaction prédite ne constitue "
        "pas une preuve expérimentale."
    )

    return interaction


# ============================================================
# 11. ANALYSE DE PLUSIEURS PRODUITS
# ============================================================

def analyser_melange_interactions(
    elements
):
    """
    Analyse toutes les paires d'un mélange.

    Exemple :

        A + B + C

    produit :

        A × B
        A × C
        B × C
    """

    resultats = []

    if not elements:

        return resultats

    for i in range(len(elements)):

        for j in range(i + 1, len(elements)):

            element_a = elements[i]
            element_b = elements[j]

            if isinstance(element_a, dict):

                nom_a = element_a.get(
                    "nom",
                    element_a.get(
                        "name",
                        ""
                    )
                )

                donnees_a = element_a.get(
                    "donnees",
                    element_a.get(
                        "data",
                        {}
                    )
                )

            else:

                nom_a = str(element_a)
                donnees_a = {}

            if isinstance(element_b, dict):

                nom_b = element_b.get(
                    "nom",
                    element_b.get(
                        "name",
                        ""
                    )
                )

                donnees_b = element_b.get(
                    "donnees",
                    element_b.get(
                        "data",
                        {}
                    )
                )

            else:

                nom_b = str(element_b)
                donnees_b = {}

            resultats.append(
                analyser_paire(
                    nom_a,
                    nom_b,
                    donnees_a,
                    donnees_b
                )
            )

    return resultats


# ============================================================
# 12. RÉSUMÉ DU MÉLANGE
# ============================================================

def resume_interactions(
    interactions
):
    """
    Génère un résumé général.
    """

    if not interactions:

        return {

            "nombre_interactions": 0,

            "statut":
                "aucune interaction à analyser",

            "conclusion":
                "Aucune paire d'éléments disponible."
        }

    nombre = len(interactions)

    return {

        "nombre_interactions": nombre,

        "statut":
            "analyse prédictive",

        "conclusion":
            (
                f"{nombre} interaction(s) potentielle(s) "
                "ont été préparées pour l'analyse SENTOX-QSAR. "
                "Les résultats devront distinguer les données "
                "documentées des prédictions."
            )
    }


# ============================================================
# 13. TEST DU MODULE
# ============================================================

if __name__ == "__main__":

    elements_test = [

        {
            "nom": "Miel",

            "donnees": {

                "cibles": [
                    "Cible exemple A"
                ],

                "organes_cibles": [
                    "foie"
                ],

                "molecule": {}
            }
        },

        {
            "nom": "Ail",

            "donnees": {

                "cibles": [
                    "Cible exemple B"
                ],

                "organes_cibles": [
                    "foie",
                    "rein"
                ],

                "molecule": {}
            }
        },

        {
            "nom": "Paracétamol",

            "donnees": {

                "cibles": [
                    "Cible exemple A"
                ],

                "organes_cibles": [
                    "foie"
                ],

                "molecule": {}
            }
        }
    ]

    interactions = analyser_melange_interactions(
        elements_test
    )

    resume = resume_interactions(
        interactions
    )

    print(
        "=========================================="
    )

    print(
        "SENTOX — MOTEUR D'INTERACTIONS"
    )

    print(
        "=========================================="
    )

    print(
        "Nombre d'interactions :",
        resume["nombre_interactions"]
    )

    for interaction in interactions:

        print(
            interaction["element_a"],
            "×",
            interaction["element_b"]
        )

    print(
        resume["conclusion"]
    )
