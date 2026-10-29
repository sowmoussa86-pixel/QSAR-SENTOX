
import re


def normaliser_dl50(valeur_brute, unite_brute):
    """
    Normalise une DL50 en mg/kg sans modifier la donnée originale.
    Les valeurs ambiguës restent à valider.
    """
    resultat = {
        "valeur_brute": valeur_brute,
        "unite_brute": unite_brute,
        "operateur": "",
        "valeur_normalisee_mg_kg": None,
        "statut_normalisation": "A_VALIDER",
        "message_normalisation": "",
    }

    if not valeur_brute or not unite_brute:
        resultat["message_normalisation"] = "Valeur ou unité absente."
        return resultat

    texte = str(valeur_brute).strip()
    unite = str(unite_brute).strip().lower()
    unite = unite.replace("μ", "µ")

    # Récupération du signe éventuel : >, < ou =
    match = re.search(r"([<>]=?|=)?\s*([\d][\d.,]*)", texte)

    if not match:
        resultat["message_normalisation"] = (
            "Format numérique non reconnu."
        )
        return resultat

    operateur = match.group(1) or "="
    nombre = match.group(2)
    resultat["operateur"] = operateur

    # Ne pas interpréter automatiquement les séparateurs ambigus.
    if re.fullmatch(r"\d{1,3},\d{3}", nombre):
        resultat["message_normalisation"] = (
            "Virgule ambiguë : vérifier la source originale."
        )
        return resultat

    # Les nombres avec une virgule décimale simple sont acceptés.
    if "," in nombre and "." not in nombre:
        nombre = nombre.replace(",", ".")

    # Plusieurs séparateurs : format non traité automatiquement.
    if nombre.count(".") > 1 or nombre.count(",") > 0:
        resultat["message_normalisation"] = (
            "Format numérique ambigu ou non pris en charge."
        )
        return resultat

    try:
        valeur = float(nombre)
    except ValueError:
        resultat["message_normalisation"] = (
            "Conversion numérique impossible."
        )
        return resultat

    facteurs = {
        "mg/kg": 1.0,
        "g/kg": 1000.0,
        "ug/kg": 0.001,
        "µg/kg": 0.001,
    }

    if unite not in facteurs:
        resultat["message_normalisation"] = (
            f"Unité non reconnue : {unite_brute}"
        )
        return resultat

    resultat["valeur_normalisee_mg_kg"] = (
        valeur * facteurs[unite]
    )
    resultat["statut_normalisation"] = "OK"
    resultat["message_normalisation"] = (
        "Conversion mathématique effectuée. "
        "La donnée source reste à vérifier."
    )

    return resultat


if __name__ == "__main__":
    tests = [
        ("1,470", "mg/kg"),
        ("1,100", "mg/kg"),
        ("1.35", "g/kg"),
        ("> 2", "g/kg"),
        ("2890", "ug/kg"),
        ("4550", "mg/kg"),
    ]

    for valeur, unite in tests:
        print(normaliser_dl50(valeur, unite))
