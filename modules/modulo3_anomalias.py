import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import os

MODELO_ANOMALIAS_PATH = 'modelo_anomalias.pkl'

FEATURES_ANOMALIAS = [
    'TotalBet', 'TotalWin', 'TotalJPWin',
    'BalanceChange', 'ratio_ganancia'
]

def preparar_features_anomalias(df):
    X = df[FEATURES_ANOMALIAS].copy()
    X['TotalJPWin'] = X['TotalJPWin'].fillna(0)
    return X

def entrenar_detector(df):
    print("Entrenando Isolation Forest...")
    X = preparar_features_anomalias(df)

    modelo = IsolationForest(
        n_estimators=100,
        contamination=0.02,  # estimamos ~2% de registros anómalos
        random_state=42
    )
    modelo.fit(X)

    with open(MODELO_ANOMALIAS_PATH, 'wb') as f:
        pickle.dump(modelo, f)
    print(f"Modelo de anomalías guardado en {MODELO_ANOMALIAS_PATH}")

    return modelo

def detectar_anomalias(df):
    X = preparar_features_anomalias(df)

    if os.path.exists(MODELO_ANOMALIAS_PATH):
        with open(MODELO_ANOMALIAS_PATH, 'rb') as f:
            modelo = pickle.load(f)
        print("Modelo de anomalías cargado desde archivo")
    else:
        modelo = entrenar_detector(df)

    # Isolation Forest: -1 = anómalo, 1 = normal
    df['anomalia_score'] = modelo.decision_function(X)
    df['es_anomalia'] = modelo.predict(X) == -1

    # Clasificar tipo de anomalía
    df['tipo_anomalia'] = df.apply(clasificar_tipo_anomalia, axis=1)

    total_anomalias = df['es_anomalia'].sum()
    print(f"Anomalías detectadas: {total_anomalias} de {len(df)} registros ({total_anomalias/len(df)*100:.2f}%)")

    return df, modelo

def clasificar_tipo_anomalia(row):
    if not row['es_anomalia']:
        return None

    # Jackpot con sesión corta o monto muy alto
    if pd.notna(row['TotalJPWin']) and row['TotalJPWin'] > 0:
        return 'jackpot_sospechoso'

    # Ganancia desproporcionada respecto a la apuesta
    if row['ratio_ganancia'] >= 26:
        return 'ganancia_desproporcionada'

    # Retiro solapado: balance cae bruscamente sin apuesta
    if row['BalanceChange'] < 0 and row['TotalBet'] == 0 and row['TotalWin'] == 0:
        return 'retiro_solapado'

    # Comportamiento general anómalo
    return 'comportamiento_atipico'

def actualizar_modelo_incremental(df_nuevo):
    """
    Aprendizaje incremental: actualiza el modelo con nuevos datos.
    Se llama automáticamente cada vez que se carga un CSV nuevo.
    """
    X_nuevo = preparar_features_anomalias(df_nuevo)

    if os.path.exists(MODELO_ANOMALIAS_PATH):
        with open(MODELO_ANOMALIAS_PATH, 'rb') as f:
            modelo_anterior = pickle.load(f)
        print("Actualizando modelo con nuevos datos...")

        # Combinar estimadores del modelo anterior con nuevo entrenamiento
        modelo_nuevo = IsolationForest(
            n_estimators=100,
            contamination=0.02,
            random_state=42
        )
        modelo_nuevo.fit(X_nuevo)

        # Promediar los scores de ambos modelos para aprendizaje incremental
        modelo_nuevo.estimators_ = modelo_anterior.estimators_ + modelo_nuevo.estimators_
        modelo_nuevo.estimators_features_ = (
            modelo_anterior.estimators_features_ + modelo_nuevo.estimators_features_
        )
        modelo_nuevo.n_estimators = len(modelo_nuevo.estimators_)

        with open(MODELO_ANOMALIAS_PATH, 'wb') as f:
            pickle.dump(modelo_nuevo, f)
        print(f"Modelo actualizado con {len(df_nuevo)} registros nuevos. Total estimadores: {modelo_nuevo.n_estimators}")

        return modelo_nuevo
    else:
        return entrenar_detector(df_nuevo)