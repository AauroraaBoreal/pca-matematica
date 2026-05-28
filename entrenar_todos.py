from modules.modulo1_carga import cargar_csv
from modules.modulo2_clasificacion import entrenar_modelo
from modules.modulo3_anomalias import actualizar_modelo_incremental
import os
import glob
import pandas as pd

def validar_sistema():
    """Verifica que todos los módulos del sistema funcionan correctamente."""
    print("\n" + "=" * 60)
    print("VALIDACIÓN DEL SISTEMA — QA")
    print("=" * 60)
    errores = []

    # Verificar que existen los modelos entrenados
    if not os.path.exists('modelo_clasificador.pkl'):
        errores.append("❌ modelo_clasificador.pkl no encontrado")
    else:
        print("✅ Modelo clasificador encontrado")

    if not os.path.exists('modelo_anomalias.pkl'):
        errores.append("❌ modelo_anomalias.pkl no encontrado")
    else:
        print("✅ Modelo de anomalías encontrado")

    # Verificar conexión a base de datos
    try:
        from modules.modulo4_base_datos import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        print("✅ Conexión a Supabase correcta")
    except Exception as e:
        errores.append(f"❌ Error de conexión a base de datos: {e}")

    # Verificar que hay archivos CSV disponibles
    archivos = glob.glob('data/*.csv')
    if not archivos:
        errores.append("❌ No hay archivos CSV en la carpeta data/")
    else:
        print(f"✅ {len(archivos)} archivos CSV disponibles para entrenamiento")

    # Verificar módulos importables
    try:
        from modules.modulo1_carga import cargar_csv
        from modules.modulo2_clasificacion import clasificar_eventos
        from modules.modulo3_anomalias import detectar_anomalias
        from modules.modulo5_reportes import mostrar_reportes
        print("✅ Todos los módulos importan correctamente")
    except Exception as e:
        errores.append(f"❌ Error al importar módulos: {e}")

    print("\n" + "-" * 60)
    if errores:
        print("RESULTADO: ⚠️  Se encontraron problemas:")
        for e in errores:
            print(f"  {e}")
    else:
        print("RESULTADO: ✅ Sistema validado correctamente — sin problemas")
    print("=" * 60 + "\n")

    return len(errores) == 0

archivos = glob.glob('data/*.csv')
print(f"Archivos encontrados: {len(archivos)}")

df_total = None

for archivo in archivos:
    print(f"\nProcesando: {archivo}")
    try:
        df = cargar_csv(archivo)
        if df_total is None:
            df_total = df
        else:
            df_total = pd.concat([df_total, df], ignore_index=True)
    except Exception as e:
        print(f"Error en {archivo}: {e}")

print(f"\nTotal de registros combinados: {len(df_total)}")
print("Entrenando modelo con todos los datos...")
modelo_clf, df_total = entrenar_modelo(df_total)
actualizar_modelo_incremental(df_total)
print("\nEntrenamiento completo con todos los CSV.")

# Ejecutar validación QA al final
validar_sistema()