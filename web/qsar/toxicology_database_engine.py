import os
import pandas as pd


DATA_FILE = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    ),
    "data",
    "sentox_toxicology_v2.csv"
)


def charger_base_toxicologique():
    """
    Charge la base toxicologique SENTOX V2.
    """

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Base toxicologique introuvable : {DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


def rechercher_toxicologie(nom):
    """
    Recherche une substance par nom principal
    ou par synonyme.
    """

    if not isinstance(nom, str) or not nom.strip():
        return {
            "statut": "NON DISPONIBLE",
            "resultats": []
        }

    recherche = nom.strip().lower()

    df = charger_base_toxicologique()

    resultats = []

    for _, ligne in df.iterrows():

        nom_principal = str(
            ligne.get("Nom", "")
        ).strip().lower()

        synonymes = str(
            ligne.get("Synonymes", "")
        ).lower().split(";")

        synonymes = [
            s.strip()
            for s in synonymes
            if s.strip()
        ]

        if (
            recherche == nom_principal
            or recherche in synonymes
        ):

            resultats.append(
                ligne.to_dict()
            )

    if not resultats:
        return {
            "statut": "NON DISPONIBLE",
            "resultats": []
        }

    return {
        "statut": "DOCUMENTÉ",
        "resultats": resultats
    }


if __name__ == "__main__":

    for substance in [
        "Paracetamol",
        "Acetaminophen",
        "Methanol",
        "Substance_inconnue"
    ]:

        resultat = rechercher_toxicologie(
            substance
        )

        print("")
        print("===", substance, "===")
        print(resultat)
