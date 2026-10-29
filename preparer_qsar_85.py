
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski, rdMolDescriptors

base_file = "data/sentox_database_2000_enriched_noms.csv"
dl50_file = "data/dl50_pubchem_2000_resultats.csv"
output_file = "data/qsar_preparation_85_smiles_descripteurs.csv"

base = pd.read_csv(base_file)
dl50 = pd.read_csv(dl50_file)

dl50["valeur_normalisee_mg_kg"] = pd.to_numeric(
    dl50["valeur_normalisee_mg_kg"], errors="coerce"
)
dl50["CID_base"] = pd.to_numeric(dl50["CID_base"], errors="coerce")

valid = dl50.dropna(
    subset=["valeur_normalisee_mg_kg", "CID_base"]
).copy()
valid["CID_base"] = valid["CID_base"].astype(int)

base["CID"] = pd.to_numeric(base["CID"], errors="coerce")
cids = set(valid["CID_base"])
selected = base[base["CID"].isin(cids)].copy()
selected = selected.drop_duplicates(subset=["CID"]).copy()

results = []
invalid = []

for _, row in selected.iterrows():
    smiles = row.get("SMILES_PubChem")
    molecule = Chem.MolFromSmiles(str(smiles)) if pd.notna(smiles) else None

    if molecule is None:
        invalid.append(row.get("Nom_PubChem", row["CID"]))
        results.append([None] * 7)
        continue

    results.append([
        Descriptors.MolWt(molecule),
        Crippen.MolLogP(molecule),
        Lipinski.NumHDonors(molecule),
        Lipinski.NumHAcceptors(molecule),
        rdMolDescriptors.CalcTPSA(molecule),
        molecule.GetNumHeavyAtoms(),
        rdMolDescriptors.CalcNumRings(molecule),
    ])

columns = [
    "Masse_molaire_RDKit",
    "LogP_RDKit",
    "HBD_RDKit",
    "HBA_RDKit",
    "TPSA_RDKit",
    "Atomes_lourds_RDKit_calc",
    "Anneaux_RDKit_calc",
]

descriptors = pd.DataFrame(results, columns=columns, index=selected.index)
prepared = pd.concat([selected, descriptors], axis=1)

prepared.to_csv(output_file, index=False, encoding="utf-8-sig")

print("Fichier créé :", output_file)
print("Substances :", len(prepared))
print("SMILES valides :", len(prepared) - len(invalid))
print("SMILES invalides :", len(invalid))
print("Descripteurs calculés :", len(columns))
print("\nAperçu :")
print(prepared[
    ["Nom_PubChem", "CID", "Masse_molaire_RDKit", "LogP_RDKit", "TPSA_RDKit"]
].head(10).to_string(index=False))

if invalid:
    print("\nSubstances avec SMILES invalide ou absent :")
    print(invalid)
