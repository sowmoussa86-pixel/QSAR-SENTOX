from datetime import datetime

STATUTS = [
    "CONFORME",
    "NON_CONFORME",
    "A_AMELIORER",
    "NON_APPLICABLE"
]


def creer_audit(
    entreprise,
    secteur,
    type_audit,
    auditeur,
    reference=""
):
    if not entreprise.strip():
        raise ValueError("L'entreprise est obligatoire.")

    if not auditeur.strip():
        raise ValueError("Le nom de l'auditeur est obligatoire.")

    return {
        "date": datetime.now().isoformat(timespec="seconds"),
        "entreprise": entreprise,
        "secteur": secteur,
        "type_audit": type_audit,
        "auditeur": auditeur,
        "reference": reference,
        "constats": []
    }


def ajouter_constat(
    audit,
    exigence,
    constat,
    statut,
    recommandation=""
):
    if statut not in STATUTS:
        raise ValueError("Statut de constat invalide.")

    if not exigence.strip() or not constat.strip():
        raise ValueError("Exigence et constat obligatoires.")

    audit["constats"].append({
        "exigence": exigence,
        "constat": constat,
        "statut": statut,
        "recommandation": recommandation
    })

    return audit


def calculer_resultats_audit(audit):
    constats = audit.get("constats", [])

    applicables = [
        c for c in constats
        if c["statut"] != "NON_APPLICABLE"
    ]

    total = len(applicables)

    conformes = sum(
        c["statut"] == "CONFORME"
        for c in applicables
    )

    non_conformes = sum(
        c["statut"] == "NON_CONFORME"
        for c in applicables
    )

    a_ameliorer = sum(
        c["statut"] == "A_AMELIORER"
        for c in applicables
    )

    return {
        "nombre_constats": len(constats),
        "exigences_applicables": total,
        "conformes": conformes,
        "non_conformes": non_conformes,
        "a_ameliorer": a_ameliorer,
        "taux_conformite": round(
            conformes / total * 100, 2
        ) if total else 0
    }
