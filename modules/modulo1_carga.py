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

    if not ruta_archivo.endswith('.csv'):
        raise ValueError("El archivo debe ser de formato CSV (.csv)")

    df = pd.read_csv(ruta_archivo, on_bad_lines='skip', quotechar='"', engine='python')
    print(f"Archivo cargado: {len(df)} registros")

    # Capturar fila original del CSV antes de cualquier filtrado
    df['_fila_csv'] = df.index + 2

    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        raise ValueError(f"El archivo no tiene el formato esperado. Columnas faltantes: {faltantes}")

    if df['PlayerId'].isna().all():
        raise ValueError("El archivo no contiene registros válidos de jugador")

    df['EventTime'] = pd.to_datetime(df['EventTime'], errors='coerce')

    filas_sin_fecha = df['EventTime'].isna().sum()
    if filas_sin_fecha > 0:
        print(f"Se eliminaron {filas_sin_fecha} filas sin fecha válida")
    df = df.dropna(subset=['EventTime'])

    if len(df) == 0:
        raise ValueError("El archivo no contiene registros con fecha válida")

    df = df.sort_values('EventTime').reset_index(drop=True)

    for col in COLUMNAS_MONTO:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) / 100

    df['ratio_ganancia'] = df.apply(
        lambda row: row['TotalWin'] / row['TotalBet'] if row['TotalBet'] > 0 else 0,
        axis=1
    )

    player_id = str(df['PlayerId'].iloc[0])
    fecha_inicio = df['EventTime'].min()
    fecha_fin = df['EventTime'].max()

    print(f"Registros válidos tras limpieza: {len(df)}")
    print(f"Periodo: {fecha_inicio} → {fecha_fin}")
    print(f"Jugador: {player_id}")

    return df