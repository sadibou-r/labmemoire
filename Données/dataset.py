import os
import pandas as pd
import shutil

# --- 1. Charger le CSV ---
df = pd.read_csv("annotations.csv")

# --- 2. Créer le dossier principal du dataset ---
output_dir = "dataset"
os.makedirs(output_dir, exist_ok=True)

# --- 3. Parcourir les lignes du CSV ---
for _, row in df.iterrows():
    image_path = row["path"]
    grade = str(row["grade"])
    stade = row["stade"]

    # Créer le dossier de classe ex: "2_C"
    class_dir = os.path.join(output_dir, f"{grade}_{stade}")
    os.makedirs(class_dir, exist_ok=True)

    # Copier l'image dans le bon dossier
    if os.path.exists(image_path):
        shutil.copy(image_path, class_dir)
    else:
        print(f"⚠️ Image introuvable : {image_path}")