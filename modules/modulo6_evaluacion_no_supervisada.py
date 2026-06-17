import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, balanced_accuracy_score


from modules.modulo3_anomalias import preparar_features_anomalias


def marcar_anomalia_por_reglas(row):
    """
    Esta función NO representa una etiqueta real.
    Solo representa una regla de negocio para comparar contra el modelo.
    """
    if pd.notna(row.get("TotalJPWin")) and row["TotalJPWin"] > 0:
        return True

    if row.get("ratio_ganancia", 0) >= 26:
        return True

    if row.get("TotalBet", 0) == 0 and row.get("TotalWin", 0) > 50000:
        return True

    return False


def nivel_riesgo_por_score(score, q10, q25):
    """
    En IsolationForest, mientras menor es el score, más anómalo es el registro.
    """
    if score <= q10:
        return "alto"
    elif score <= q25:
        return "medio"
    else:
        return "bajo"


def evaluar_detector_no_supervisado(df, modelo, salida_csv="resultados_evaluacion_no_supervisada.csv"):
    print("\n" + "=" * 70)
    print("EVALUACIÓN NO SUPERVISADA - ISOLATION FOREST")
    print("=" * 70)

    df_eval = df.copy()

    X = preparar_features_anomalias(df_eval)

    df_eval["anomalia_score"] = modelo.decision_function(X)
    df_eval["prediccion_modelo"] = modelo.predict(X)
    df_eval["es_anomalia_modelo"] = df_eval["prediccion_modelo"] == -1


    df_eval["es_anomalia_regla"] = df_eval.apply(marcar_anomalia_por_reglas, axis=1)

    q10 = df_eval["anomalia_score"].quantile(0.10)
    q25 = df_eval["anomalia_score"].quantile(0.25)

    df_eval["nivel_riesgo_modelo"] = df_eval["anomalia_score"].apply(
        lambda score: nivel_riesgo_por_score(score, q10, q25)
    )

    total = len(df_eval)
    anom_modelo = int(df_eval["es_anomalia_modelo"].sum())
    anom_regla = int(df_eval["es_anomalia_regla"].sum())

    coincidencias = int(
        ((df_eval["es_anomalia_modelo"] == True) &
         (df_eval["es_anomalia_regla"] == True)).sum()
    )

    solo_modelo = int(
        ((df_eval["es_anomalia_modelo"] == True) &
         (df_eval["es_anomalia_regla"] == False)).sum()
    )

    solo_reglas = int(
        ((df_eval["es_anomalia_modelo"] == False) &
         (df_eval["es_anomalia_regla"] == True)).sum()
    )

    print(f"Total de registros evaluados: {total}")
    print(f"Anomalías detectadas por el modelo: {anom_modelo} ({anom_modelo / total * 100:.2f}%)")
    print(f"Anomalías marcadas por reglas: {anom_regla} ({anom_regla / total * 100:.2f}%)")
    print(f"Coincidencias modelo + reglas: {coincidencias}")
    print(f"Casos detectados solo por el modelo: {solo_modelo}")
    print(f"Casos detectados solo por reglas: {solo_reglas}")

    # ==========================================================
    # CUADRO DE MÉTRICAS DEL MODELO NO SUPERVISADO
    # ==========================================================
    # Importante:
    # Aquí NO estamos comparando contra una etiqueta humana real.
    # Estamos comparando la predicción del modelo contra reglas de negocio
    # usadas como referencia técnica.

    y_regla = df_eval["es_anomalia_regla"].astype(int)
    y_modelo = df_eval["es_anomalia_modelo"].astype(int)

    print("\n" + "=" * 70)
    print("CUADRO DE MÉTRICAS — MODELO NO SUPERVISADO VS REGLAS")
    print("=" * 70)

    print("\nReporte de clasificación:")
    print(
        classification_report(
            y_regla,
            y_modelo,
            labels=[0, 1],
            target_names=["normal", "anomalia"],
            digits=4,
            zero_division=0
        )
    )

    acc = accuracy_score(y_regla, y_modelo)
    bal_acc = balanced_accuracy_score(y_regla, y_modelo)

    print(f"Accuracy general: {acc:.4f} ({acc * 100:.2f}%)")
    print(f"Balanced accuracy: {bal_acc:.4f} ({bal_acc * 100:.2f}%)")

    matriz = confusion_matrix(y_regla, y_modelo, labels=[0, 1])

    matriz_df = pd.DataFrame(
        matriz,
        index=["Regla: normal", "Regla: anomalía"],
        columns=["Modelo: normal", "Modelo: anomalía"]
    )

    print("\nMatriz de confusión:")
    print(matriz_df)

    print("\nDistribución de riesgo según modelo:")
    print(df_eval["nivel_riesgo_modelo"].value_counts())

    print("\nTop 10 registros más anómalos según el modelo:")
    columnas_mostrar = [
        "PlayerId",
        "EventTime",
        "TotalBet",
        "TotalWin",
        "TotalJPWin",
        "BalanceChange",
        "ratio_ganancia",
        "anomalia_score",
        "nivel_riesgo_modelo",

        "es_anomalia_modelo",
        "es_anomalia_regla"
    ]

    columnas_existentes = [c for c in columnas_mostrar if c in df_eval.columns]

    print(
        df_eval[columnas_existentes]
        .sort_values("anomalia_score", ascending=True)
        .head(10)
    )

    df_eval.to_csv(salida_csv, index=False)
    print(f"\nArchivo generado: {salida_csv}")
    print("=" * 70)

    return df_eval