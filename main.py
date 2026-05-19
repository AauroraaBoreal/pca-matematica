from modules.modulo1_carga import cargar_csv

df = cargar_csv('data/10069.csv')
print(df[['EventTime', 'TotalBet', 'TotalWin', 'TotalJPWin', 'ratio_ganancia']].head(10))