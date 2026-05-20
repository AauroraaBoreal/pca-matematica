from modules.modulo1_carga import cargar_csv
from modules.modulo2_clasificacion import entrenar_modelo, clasificar_eventos
from modules.modulo3_anomalias import entrenar_detector, detectar_anomalias

# Cargar CSV
df = cargar_csv('data/10069.csv')

# Clasificación de eventos
modelo_clf, df = entrenar_modelo(df)
df = clasificar_eventos(df)

# Detección de anomalías
entrenar_detector(df)
df, modelo_anomalias = detectar_anomalias(df)

# Ver anomalías detectadas
anomalias = df[df['es_anomalia'] == True]
print(f"\nRegistros anómalos detectados: {len(anomalias)}")
print(anomalias[['EventTime', 'TotalBet', 'TotalWin', 'TotalJPWin', 
                  'ratio_ganancia', 'clasificacion', 'tipo_anomalia']].to_string())