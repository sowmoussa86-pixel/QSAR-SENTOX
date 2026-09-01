# ============================================================
# SENTOX — GESTION DES NIVEAUX DE PREUVE
# ============================================================

from typing import Any, Dict, List


DOCUMENTE = "documenté"
CALCULE = "calculé"
PREDIT = "prédit"
NON_DISPONIBLE = "non disponible"


def creer_resultat(
    valeur: Any = None,
    statut: str = NON_DISPONIBLE,
    source: str = "",
    methode: str = "",
    confiance: Any = None,
) -> Dict[str, Any]:

    return {
        "valeur": valeur,
        "statut": statut,
        "source": source,
        "methode": methode,
        "confiance": confiance,
    }


def documente(
    valeur: Any,
    source: str = "",
) -> Dict[str, Any]:

    return creer_resultat(
        valeur=valeur,
        statut=DOCUMENTE,
        source=source,
    )


def calcule(
    valeur: Any,
    methode: str = "",
) -> Dict[str, Any]:

    return creer_resultat(
        valeur=valeur,
        statut=CALCULE,
        methode=methode,
    )


def predit(
    valeur: Any,
    methode: str = "",
    confiance: Any = None,
) -> Dict[str, Any]:

    return creer_resultat(
        valeur=valeur,
        statut=PREDIT,
        methode=methode,
        confiance=confiance,
    )


def non_disponible() -> Dict[str, Any]:

    return creer_resultat()


# ============================================================
# FICHE SCIENTIFIQUE SENTOX
# ============================================================

def creer_fiche_scientifique(
    nom: str,
) -> Dict[str, Any]:

    return {

        "identification": {
            "nom": nom
        },

        "constituants": [],

        "pharmacologie": [],

        "toxicologie": [],

        "dl50": [],

        "organes_cibles": [],

        "adme": {

            "absorption": None,

            "distribution": None,

            "metabolisme": None,

            "excretion": None
        },

        "interactions": [],

        "structures": {

            "2D": None,

            "3D": None
        },

        "sources": [],

        "resume": {

            "documente": [],

            "calcule": [],

            "predit": [],

            "non_disponible": []
        }
    }


# ============================================================
# AJOUTER UNE DONNÉE
# ============================================================

def ajouter_donnee(
    fiche: Dict[str, Any],
    categorie: str,
    donnee: Dict[str, Any],
) -> Dict[str, Any]:

    if categorie not in fiche:
        fiche[categorie] = []

    if isinstance(
        fiche[categorie],
        list
    ):

        fiche[categorie].append(
            donnee
        )

    else:

        fiche[categorie] = donnee

    return fiche


# ============================================================
# CLASSIFICATION DES DONNÉES
# ============================================================

def classifier_donnees(
    fiche: Dict[str, Any]
) -> Dict[str, List]:

    resultat = {

        "documente": [],

        "calcule": [],

        "predit": [],

        "non_disponible": []
    }

    def parcourir(
        objet,
        chemin=""
    ):

        if isinstance(objet, dict):

            if "statut" in objet:

                statut = objet.get(
                    "statut"
                )

                element = {

                    "champ": chemin,

                    "valeur": objet.get(
                        "valeur"
                    ),

                    "source": objet.get(
                        "source"
                    ),

                    "methode": objet.get(
                        "methode"
                    ),

                    "confiance": objet.get(
                        "confiance"
                    )
                }

                if statut == DOCUMENTE:

                    resultat[
                        "documente"
                    ].append(element)

                elif statut == CALCULE:

                    resultat[
                        "calcule"
                    ].append(element)

                elif statut == PREDIT:

                    resultat[
                        "predit"
                    ].append(element)

                else:

                    resultat[
                        "non_disponible"
                    ].append(element)

            else:

                for cle, valeur in objet.items():

                    nouveau_chemin = (
                        f"{chemin}.{cle}"
                        if chemin
                        else cle
                    )

                    parcourir(
                        valeur,
                        nouveau_chemin
                    )

        elif isinstance(objet, list):

            for index, valeur in enumerate(
                objet
            ):

                nouveau_chemin = (
                    f"{chemin}[{index}]"
                )

                parcourir(
                    valeur,
                    nouveau_chemin
                )

    parcourir(fiche)

    return resultat


# ============================================================
# RÉSUMÉ POUR L'INTERFACE
# ============================================================

def resume_preuve(
    fiche: Dict[str, Any]
) -> Dict[str, Any]:

    classes = classifier_donnees(
        fiche
    )

    return {

        "nombre_documente": len(
            classes["documente"]
        ),

        "nombre_calcule": len(
            classes["calcule"]
        ),

        "nombre_predit": len(
            classes["predit"]
        ),

        "nombre_non_disponible": len(
            classes["non_disponible"]
        ),

        "donnees": classes
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    fiche = creer_fiche_scientifique(
        "Paracétamol"
    )

    ajouter_donnee(
        fiche,
        "toxicologie",
        documente(
            "Données toxicologiques disponibles",
            "Source scientifique"
        )
    )

    ajouter_donnee(
        fiche,
        "dl50",
        documente(
            "Valeur documentée",
            "Base scientifique"
        )
    )

    ajouter_donnee(
        fiche,
        "pharmacologie",
        predit(
            "Effet potentiel",
            "SENTOX-QSAR",
            0.82
        )
    )

    ajouter_donnee(
        fiche,
        "organes_cibles",
        calcule(
            ["foie", "reins"],
            "Analyse SENTOX"
        )
    )

    resume = resume_preuve(
        fiche
    )

    print("=" * 60)
    print("SENTOX — NIVEAUX DE PREUVE")
    print("=" * 60)

    print(
        "Documenté :",
        resume["nombre_documente"]
    )

    print(
        "Calculé :",
        resume["nombre_calcule"]
    )

    print(
        "Prédit :",
        resume["nombre_predit"]
    )

    print(
        "Non disponible :",
        resume["nombre_non_disponible"]
    )
