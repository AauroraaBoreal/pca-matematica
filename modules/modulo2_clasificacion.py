import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import pickle
import os

MODELO_PATH = 'modelo_clasificador.pkl'

def etiquetar_evento(row):
    # Retiro: balance cae sin ganancia
    if row['BalanceChange'] < 0 and row['TotalWin'] == 0 and row['TotalBet'] == 0:
        return 'retiro'
    # Recarga: balance sube sin apuesta ni ganancia
    if row['BalanceChange'] > 0 and row['TotalBet'] == 0 and row['TotalWin'] == 0:
        return 'recarga'
    # Jackpot
    if pd.notna(row['TotalJPWin']) and row['TotalJPWin'] > 0:
        return 'jackpot'
    # Ganancia alta
    if row['ratio_ganancia'] >= 26:
        return 'ganancia_alta'
    # Ganancia media
    if row['ratio_ganancia'] >= 11:
        return 'ganancia_media'
    # Ganancia normal
    if row['ratio_ganancia'] > 0:
        return 'ganancia_normal'
    # Jugada sin ganancia
    return 'sin_ganancia'

def preparar_features(df):
    features = [
        'TotalBet', 'TotalWin', 'TotalJPWin',
        'BalanceChange', 'BalanceStart', 'ratio_ganancia'
    ]
    X = df[features].copy()
    X['TotalJPWin'] = X['TotalJPWin'].fillna(0)
    return X

def entrenar_modelo(df):
    print("Etiquetando eventos...")
    df['etiqueta'] = df.apply(etiquetar_evento, axis=1)

    print("Distribución de eventos:")
    print(df['etiqueta'].value_counts())

    X = preparar_features(df)
    y = df['etiqueta']

    # Separar en entrenamiento y prueba 70/30
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Aplicar SMOTE solo en clases con menos de 6 muestras no se aplica
    conteo = y_train.value_counts()
    clases_validas = conteo[conteo >= 6].index
    mask = y_train.isin(clases_validas)
    X_train_sm = X_train[mask]
    y_train_sm = y_train[mask]

    print("Aplicando SMOTE...")
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_resampled, y_resampled = smote.fit_resample(X_train_sm, y_train_sm)

    print("Entrenando Random Forest...")
    modelo = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    modelo.fit(X_resampled, y_resampled)

    print("\nEvaluación del modelo:")
    y_pred = modelo.predict(X_test[X_test.index.isin(X_train_sm.index) == False] 
                            if False else X_test)
    print(classification_report(y_test, modelo.predict(X_test), zero_division=0))

    # Guardar modelo
    with open(MODELO_PATH, 'wb') as f:
        pickle.dump(modelo, f)
    print(f"Modelo guardado en {MODELO_PATH}")

    return modelo, df

def clasificar_eventos(df):
    X = preparar_features(df)

    if os.path.exists(MODELO_PATH):
        with open(MODELO_PATH, 'rb') as f:
            modelo = pickle.load(f)
        print("Modelo cargado desde archivo")
    else:
        print("No hay modelo entrenado, entrenando ahora...")
        modelo, df = entrenar_modelo(df)

    df['clasificacion'] = modelo.predict(X)
    return df