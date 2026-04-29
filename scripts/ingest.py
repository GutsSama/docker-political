import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json

# --- CONFIGURATION DES CHEMINS ---
# Racine du projet (on remonte d'un cran depuis /scripts)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Chargement du .env à la racine (Utile uniquement pour le local)
# En Docker, les variables seront déjà dans l'environnement système via --env-file
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path)

def get_db_engine():
    """Récupère l'URL de la base depuis l'environnement."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Erreur : DATABASE_URL est introuvable dans l'environnement.")
        sys.exit(1)
    
    # Masquage du mot de passe pour le log
    safe_url = db_url.split('@')[-1] if '@' in db_url else "Hidden"
    print(f"🔗 Connexion à : {safe_url}")
    return create_engine(db_url)

def convert_columns_to_percentages(df, list_columns, divider_column):
    """Calcule les pourcentages de manière vectorisée."""
    df_conv = df.copy()
    mask = df_conv[divider_column] > 0
    df_conv.loc[mask, list_columns] = df_conv.loc[mask, list_columns].div(df_conv.loc[mask, divider_column], axis=0) * 100
    df_conv[list_columns] = df_conv[list_columns].fillna(0).replace([np.inf, -np.inf], 0)
    return df_conv

def run_ingestion():
    engine = get_db_engine()
    
    # 1. Vérification du CSV
    csv_path = ROOT_DIR / 'data' / 'df_stats.csv'
    if not csv_path.exists():
        print(f"❌ CSV introuvable à : {csv_path}")
        return
        
    print("📖 Lecture du CSV...")
    df_raw = pd.read_csv(csv_path, sep=';', dtype={'Code_INSEE': str})

    # --- PARTIE 1 : TRAINING ---
    print("📦 Préparation table 'training'...")
    df_train = df_raw[df_raw['Année'] == 2022].copy()
    
    cols_active = ['Hommes', 'Femmes', 'Agriculteurs', 'Artisans', 'Cadres', 'Intermédiaires', 'Employés', 'Ouvriers', 'Retraités', 'Etudiants', 'Inactifs', '15-24 ans', '25-39 ans', '40-54 ans', '55-64 ans', '65-79 ans', '80 ans et +', 'Mariés', 'Pacsés', 'Concubinage', 'Veufs', 'Divorcés', 'Célibataires']
    cols_household = ['Personne seule', 'Homme seul', 'Femme seule', 'Colocation', 'Famille', 'Famille monoparentale', 'Couple sans enfant', 'Couple avec enfants']
    
    df_train = convert_columns_to_percentages(df_train, cols_active, 'Population_active')
    df_train = convert_columns_to_percentages(df_train, cols_household, 'Population avec enfants')

    training_cols = ['Code_INSEE', 'Résultat', 'Population avec enfants', 'Population_active'] + cols_active + cols_household
    
    df_train[training_cols].to_sql('training', engine, if_exists='replace', index=False)
    print("✅ Table 'training' injectée.")

    # --- PARTIE 2 : COMMUNES_STATS (Optimisé JSONB) ---
    print("📦 Préparation table 'communes_stats'...")
    
    # 1. Ajoute 'Libellé de la commune' à tes colonnes JSON
    cols_json_with_city = [
        'Libellé de la commune', # <--- Crucial pour ton API
        'Inscrits', 'Abstentions', 'Votants', 'Blancs', 'Nuls', 'Exprimés', 'Résultat',
        'Population avec enfants', 'Population_active'
    ] + cols_active + cols_household
    
    # 2. Prépare le DataFrame final
    # On crée d'abord le dictionnaire pour pouvoir renommer la clé à l'intérieur du JSON
    stats_dict = df_raw[cols_json_with_city].fillna(0).copy()
    stats_dict = stats_dict.rename(columns={'Libellé de la commune': 'city'}) # Renommé pour l'API

    df_final = pd.DataFrame({
        'years': df_raw['Année'].astype(str),
        'city': df_raw['Libellé de la commune'].fillna("Inconnu"),
        'code_insee': df_raw['Code_INSEE'].astype(str),
        'pct_gauche': pd.to_numeric(df_raw['% gauche/Exp'], errors='coerce').fillna(0),
        'pct_centre': pd.to_numeric(df_raw['% centre/Exp'], errors='coerce').fillna(0),
        'pct_droite': pd.to_numeric(df_raw['% droite/Exp'], errors='coerce').fillna(0),
        'statistics': stats_dict.to_dict(orient='records') # Contient maintenant 'city'
    })

    # On transforme le dictionnaire Python en chaîne JSON pour que Postgres l'accepte
    df_final['statistics'] = df_final['statistics'].apply(json.dumps)

    # On utilise engine.begin() pour garantir une transaction
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS communes_stats;"))
        conn.execute(text("""
            CREATE TABLE communes_stats (
                id SERIAL PRIMARY KEY,
                years VARCHAR(4) NOT NULL,
                city VARCHAR(255) NOT NULL,
                code_insee VARCHAR(10) NOT NULL,
                pct_gauche FLOAT DEFAULT 0,
                pct_centre FLOAT DEFAULT 0,
                pct_droite FLOAT DEFAULT 0,
                statistics JSONB,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

    df_final.to_sql('communes_stats', engine, if_exists='append', index=False, method='multi', chunksize=1000)
    print("✅ Ingestion terminée avec succès !")

if __name__ == "__main__":
    run_ingestion()