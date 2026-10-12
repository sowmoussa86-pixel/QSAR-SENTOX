import csv
from pathlib import Path

FICHIER = Path("data/registre_sources_toxicologie.csv")

def controler_donnee(d):
    erreurs = []
    alertes = []

    obligatoires = [
        "substance", "endpoint", "espece", "voie",
        "valeur", "unite", "reference", "statut"
    ]

    for champ in obligatoires:
        if not d.get(champ, "").strip():
            erreurs.append(f"Champ manquant : {champ}")

    try:
        valeur = float(d.get("valeur", ""))
        if valeur <= 0:
            erreurs.append("La valeur doit être positive.")
    except (ValueError, TypeError):
        valeur = None
        erreurs.append("Valeur numérique invalide.")

    endpoint = d.get("endpoint", "").strip().upper()
    voie = d.get("voie", "").strip().lower()
    unite = d.get("unite", "").strip().lower()

    if endpoint == "LD50" and voie == "orale":
        if unite not in ("mg/kg", "mg/kg bw", "mg/kg pc"):
            alertes.append("Unité à examiner pour une DL50 orale.")
    elif endpoint == "LC50":
        alertes.append(
            "CL50 : vérifier le milieu, la durée et l'unité avant comparaison."
        )
    elif endpoint not in ("LD50", "LC50", "NOAEL", "LOAEL"):
        alertes.append("Endpoint non reconnu par ce contrôle simple.")

    statut = d.get("statut", "").lower()
    if "vérifier" in statut or "verifier" in statut:
        alertes.append("Source non validée : exclure des calculs définitifs.")

    return erreurs, alertes

def main():
    if not FICHIER.exists():
        print("Fichier introuvable :", FICHIER)
        return

    with FICHIER.open(encoding="utf-8-sig", newline="") as f:
        donnees = list(csv.DictReader(f))

    print("Données examinées :", len(donnees))
    print("=" * 60)

    for i, d in enumerate(donnees, 1):
        erreurs, alertes = controler_donnee(d)
        print(f"\n{i}. {d.get('substance')} | {d.get('endpoint')} | "
              f"{d.get('valeur')} {d.get('unite')}")
        print("ERREURS :", erreurs if erreurs else "Aucune détectée")
        print("ALERTES :", alertes if alertes else "Aucune")

    print("\nContrôle terminé : aucun résultat n'est automatiquement validé.")

if __name__ == "__main__":
    main()
