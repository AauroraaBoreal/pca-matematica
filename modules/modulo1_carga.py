import pandas as pd
import os

COLUMNAS_REQUERIDAS = [
    'PlayerId', 'BalanceStart', 'BalanceChange', 'TotalBet',
    'TotalWin', 'TotalJPWin', 'EventTime', 'GameInstanceId'
]

COLUMNAS_MONTO = [
    'TotalBet', 'BalanceStart', 'TotalWin',
    'TotalJPWin', 'BalanceChange', 'Balance'
]

def cargar_csv(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    df = pd.read_csv(ruta_archivo, on_bad_lines='skip')
    print(f"Archivo cargado: {len(df)} registros")

    # Verificar columnas requeridas
    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes en el archivo: {faltantes}")

    # Convertir EventTime a datetime
    df['EventTime'] = pd.to_datetime(df['EventTime'])

    # Ordenar cronológicamente
    df = df.sort_values('EventTime').reset_index(drop=True)

    # Convertir montos a escala real (dividir entre 100)
    for col in COLUMNAS_MONTO:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce') / 100

    # Eliminar filas donde TotalBet sea nulo
    df = df.dropna(subset=['TotalBet'])

    # Calcular ratio ganancia/apuesta
    df['ratio_ganancia'] = df.apply(
        lambda row: row['TotalWin'] / row['TotalBet'] if row['TotalBet'] > 0 else 0,
        axis=1
    )

    print(f"Registros válidos tras limpieza: {len(df)}")
    print(f"Periodo: {df['EventTime'].min()} → {df['EventTime'].max()}")
    print(f"Jugador: {df['PlayerId'].iloc[0]}")

    return df