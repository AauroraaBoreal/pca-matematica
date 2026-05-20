from modules.modulo1_carga import cargar_csv
from modules.modulo2_clasificacion import entrenar_modelo, clasificar_eventos

# Cargar CSV
df = cargar_csv('data/10069.csv')

# Entrenar modelo
modelo, df = entrenar_modelo(df)

# Clasificar eventos
df = clasificar_eventos(df)

# Ver resultados
print("\nEjemplo de clasificaciones:")
print(df[['EventTime', 'TotalBet', 'TotalWin', 'TotalJPWin', 'ratio_ganancia', 'clasificacion']].head(15))