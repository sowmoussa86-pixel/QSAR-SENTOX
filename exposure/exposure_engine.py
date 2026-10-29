# ============================================================
# SENTOX - MOTEUR D EXPOSITION PARAMETRABLE V1
# ============================================================
import math

def valider(valeur, nom):
    """
    Vérifie qu'une valeur est numérique, finie et positive.
    """
    try:
        valeur = float(valeur)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{nom} doit être un nombre fini.")

    if not math.isfinite(valeur):
        raise ValueError(f"{nom} doit être un nombre fini.")

    if valeur <= 0:
        raise ValueError(
            f"{nom} doit être strictement supérieure à zéro."
        )

    return valeur



def calculer_exposition(concentration_mg_g, quantite_g_jour, poids_kg, frequence=1):
    concentration_mg_g = valider(concentration_mg_g, "La concentration")
    quantite_g_jour = valider(quantite_g_jour, "La quantite")
    poids_kg = valider(poids_kg, "Le poids corporel")
    frequence = valider(frequence, "La frequence")

    dose_mg_jour = concentration_mg_g * quantite_g_jour * frequence
    exposition_mg_kg_jour = dose_mg_jour / poids_kg

    return {
        "concentration_mg_g": concentration_mg_g,
        "quantite_g_jour": quantite_g_jour,
        "frequence": frequence,
        "poids_kg": poids_kg,
        "dose_mg_jour": dose_mg_jour,
        "exposition_mg_kg_jour": exposition_mg_kg_jour,
        "unite": "mg/kg/jour",
        "statut": "Calculee"
    }
