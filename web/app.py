from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

FICHIER = r"C:\SENTOX\data\constituants_enrichis.csv"


def charger_donnees():
    if not os.path.exists(FICHIER):
        return pd.DataFrame()

    try:
        df = pd.read_csv(FICHIER)
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna("")
    except Exception:
        return pd.DataFrame()


@app.route("/")
def accueil():

    df = charger_donnees()

    recherche = request.args.get("q", "").strip().lower()

    if recherche:
        masque = df.astype(str).apply(
            lambda ligne: ligne.str.lower().str.contains(
                recherche,
                na=False
            )
        ).any(axis=1)

        df = df[masque]

    constituants = df.to_dict(orient="records")

    return render_template(
        "index.html",
        constituants=constituants,
        recherche=recherche,
        nombre=len(constituants)
    )


@app.route("/constituant/<int:index>")
def constituant(index):

    df = charger_donnees()

    if index < 0 or index >= len(df):
        return "Constituant introuvable", 404

    donnees = df.iloc[index].to_dict()

    return render_template(
        "fiche.html",
        donnees=donnees
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )