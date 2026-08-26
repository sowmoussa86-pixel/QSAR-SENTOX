import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

FICHIER = r"C:\SENTOX\data\constituants_enrichis.csv"

def charger_donnees():
    if not os.path.exists(FICHIER):
        messagebox.showerror("Erreur", f"Fichier introuvable :\n{FICHIER}")
        return None
    try:
        df = pd.read_csv(FICHIER)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        messagebox.showerror("Erreur de lecture", str(e))
        return None

def afficher_donnees(df=None):
    if df is None:
        df = charger_donnees()
    if df is None:
        return
    for item in tableau.get_children():
        tableau.delete(item)
    colonnes = list(df.columns)
    tableau["columns"] = colonnes
    tableau["show"] = "headings"
    for colonne in colonnes:
        tableau.heading(colonne, text=colonne)
        tableau.column(colonne, width=150, minwidth=100, anchor="w")
    for _, ligne in df.iterrows():
        valeurs = []
        for colonne in colonnes:
            valeur = ligne[colonne]
            if pd.isna(valeur):
                valeur = ""
            valeurs.append(str(valeur))
        tableau.insert("", "end", values=valeurs)
    label_nombre.config(text=f"Constituants enrichis : {len(df)}")

def rechercher():
    recherche = entree_recherche.get().strip().lower()
    if not recherche:
        afficher_donnees()
        return
    df = charger_donnees()
    if df is None:
        return
    masque = df.astype(str).apply(
        lambda ligne: ligne.str.lower().str.contains(recherche, na=False)
    ).any(axis=1)
    afficher_donnees(df[masque])

def afficher_fiche():
    selection = tableau.selection()
    if not selection:
        messagebox.showinfo("SENTOX", "Veuillez sélectionner un constituant.")
        return
    item = selection[0]
    valeurs = tableau.item(item, "values")
    colonnes = tableau["columns"]
    donnees = {}
    for i, colonne in enumerate(colonnes):
        if i < len(valeurs):
            donnees[colonne] = valeurs[i]

    fiche = tk.Toplevel(fenetre)
    fiche.title("SENTOX - Fiche du constituant")
    fiche.geometry("900x700")
    fiche.minsize(700, 500)

    tk.Label(fiche, text="SENTOX", font=("Arial", 24, "bold")).pack(pady=(20, 0))
    nom = donnees.get("Constituant", donnees.get("Title", "Constituant"))
    tk.Label(fiche, text=str(nom), font=("Arial", 18, "bold")).pack(pady=5)
    tk.Label(fiche, text="Profil chimique enrichi par PubChem", font=("Arial", 11)).pack(pady=(0, 15))

    cadre = tk.Frame(fiche)
    cadre.pack(fill="both", expand=True, padx=20, pady=10)
    scrollbar = ttk.Scrollbar(cadre, orient="vertical")
    scrollbar.pack(side="right", fill="y")
    texte = tk.Text(cadre, font=("Consolas", 11), wrap="word", yscrollcommand=scrollbar.set)
    texte.pack(fill="both", expand=True)
    scrollbar.config(command=texte.yview)

    texte.insert("end", "=" * 60 + "\n")
    texte.insert("end", "             PROFIL DU CONSTITUANT\n")
    texte.insert("end", "=" * 60 + "\n\n")
    for colonne, valeur in donnees.items():
        texte.insert("end", f"{colonne}\n    {valeur}\n\n")
    texte.config(state="disabled")

    tk.Button(fiche, text="Fermer", command=fiche.destroy, font=("Arial", 10, "bold"), width=15).pack(pady=15)

def double_clic(event):
    afficher_fiche()

fenetre = tk.Tk()
fenetre.title("SENTOX - Profil chimique")
fenetre.geometry("1400x750")
fenetre.minsize(1000, 600)

tk.Label(fenetre, text="SENTOX", font=("Arial", 26, "bold")).pack(pady=(20, 0))
tk.Label(fenetre, text="PROFIL CHIMIQUE – CONSTITUANTS ENRICHIS PAR PUBCHEM", font=("Arial", 13)).pack(pady=(0, 15))

cadre_info = tk.Frame(fenetre)
cadre_info.pack(fill="x", padx=20, pady=5)
tk.Label(cadre_info, text="Acacia nilotica   |   ID : PL001", font=("Arial", 15, "bold"), anchor="w").pack(side="left")
label_nombre = tk.Label(cadre_info, text="Constituants enrichis : 0", font=("Arial", 12))
label_nombre.pack(side="right")

cadre_recherche = tk.Frame(fenetre)
cadre_recherche.pack(fill="x", padx=20, pady=10)
tk.Label(cadre_recherche, text="Rechercher :", font=("Arial", 11)).pack(side="left")
entree_recherche = tk.Entry(cadre_recherche, font=("Arial", 11), width=40)
entree_recherche.pack(side="left", padx=10)
tk.Button(cadre_recherche, text="Rechercher", command=rechercher, font=("Arial", 10, "bold")).pack(side="left", padx=5)
tk.Button(cadre_recherche, text="Actualiser", command=afficher_donnees, font=("Arial", 10, "bold")).pack(side="left", padx=5)
tk.Button(cadre_recherche, text="Voir la fiche", command=afficher_fiche, font=("Arial", 10, "bold")).pack(side="left", padx=5)

cadre_tableau = tk.Frame(fenetre)
cadre_tableau.pack(fill="both", expand=True, padx=20, pady=10)
scroll_vertical = ttk.Scrollbar(cadre_tableau, orient="vertical")
scroll_horizontal = ttk.Scrollbar(cadre_tableau, orient="horizontal")
tableau = ttk.Treeview(cadre_tableau, yscrollcommand=scroll_vertical.set, xscrollcommand=scroll_horizontal.set, selectmode="browse")
scroll_vertical.config(command=tableau.yview)
scroll_horizontal.config(command=tableau.xview)
scroll_vertical.pack(side="right", fill="y")
scroll_horizontal.pack(side="bottom", fill="x")
tableau.pack(fill="both", expand=True)
tableau.bind("<Double-1>", double_clic)

afficher_donnees()
fenetre.mainloop()