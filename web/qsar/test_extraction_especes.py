
import re

ESPECES = [
    "guinea pig", "mouse", "mice", "rat",
    "rabbit", "dog", "cat"
]

def extraire_espece(texte):
    texte = texte.lower()

    # Chercher les expressions les plus longues en premier.
    for espece in ESPECES:
        motif = r"\b" + re.escape(espece) + r"\b"
        if re.search(motif, texte):
            return espece

    return "A_VERIFIER"


exemples = [
    ("LD50 Rat oral 2400 mg/kg", "rat"),
    ("Oral LD50 (mouse) = 4550 mg/kg", "mouse"),
    ("oral LD50 values in rat have been reported to be 3608 mg/kg", "rat"),
    ("oral LD50 was calculated to be 3000 mg/kg", "A_VERIFIER"),
    ("LD50 Rabbit dermal 800 mg/kg", "rabbit"),
    ("LD50 Guinea pig oral 500 mg/kg", "guinea pig"),
]

erreurs = 0

for texte, attendu in exemples:
    obtenu = extraire_espece(texte)
    ok = obtenu == attendu
    print(
        ("OK" if ok else "ECHEC"),
        "| attendu:", attendu,
        "| obtenu:", obtenu,
        "|", texte
    )
    if not ok:
        erreurs += 1

print("Bilan :", len(exemples) - erreurs, "/", len(exemples), "tests réussis")

if erreurs:
    raise SystemExit(1)
