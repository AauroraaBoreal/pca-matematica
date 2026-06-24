# GDP Validator — Sistema de Validación Inteligente

**GDP Validator** es un sistema automatizado diseñado para la validación de jugadas y detección de anomalías en el historial de los jugadores. Permite la ingesta de datos en formato CSV, identifica comportamientos anómalos o retiros inusuales mediante modelos de Machine Learning y genera reportes detallados.

Cuenta con un pipeline de ejecución por consola y una interfaz visual interactiva (Dashboard) desarrollada en Streamlit.

---

## Distribución de Carpetas

La estructura del proyecto está organizada de la siguiente manera:

- **`data/`**: Contiene los archivos CSV de prueba y datos de origen con los historiales de juego de los usuarios.
- **`modules/`**: Contiene el código fuente dividido de manera modular, agrupando las diferentes fases del proceso de validación.
- **`venv/`**, **`__pycache__/`**: Directorios del entorno virtual y archivos compilados de Python.

---

## Conexión de Archivos y Módulos

El proyecto sigue una arquitectura modular donde el flujo de la información pasa por distintas etapas:

### Puntos de entrada principales
- **`main.py`**: Es el punto de entrada para ejecutar el sistema desde la línea de comandos (CLI). Coordina el flujo de trabajo importando los módulos: toma un CSV, limpia los datos, detecta las anomalías, genera reportes y guarda en la base de datos.
- **`app.py`**: Es el archivo principal de la interfaz web (Dashboard). Utiliza Streamlit para ofrecer una forma gráfica e interactiva de cargar los archivos, ver análisis detallados y validar retiros.

### Scripts secundarios
- **`entrenar_todos.py`**: Se encarga de entrenar y generar los modelos predictivos de Machine Learning, guardándolos en formato `.pkl` (por ejemplo, `modelo_random_forest.pkl`, `modelo_anomalias.pkl`).

### Pipeline Modular (`modules/`)
Los archivos dentro de `modules/` se conectan secuencialmente para procesar la información:
1. **`modulo1_carga.py`**: Limpia, formatea y prepara los datos extraídos del CSV.
2. **`modulo3_random_forest.py`**, **`modulo3_anomalias.py`**, **`modulo3_autoencoder.py`**: Aplican los modelos predictivos preentrenados (`.pkl`) para clasificar jugadas e identificar eventos inusuales o retiros anómalos.
3. **`modulo5_reportes.py`**: Recibe los resultados de las anomalías detectadas y genera textos estructurados para revisión (como formatos para WhatsApp y reportes de QA).
4. **`modulo4_base_datos.py`**: Finalmente, se conecta a la base de datos (Supabase) para persistir la información procesada: perfil actualizado del jugador, historial de la validación y detalle de cada anomalía detectada.
5. **`modulo6_evaluacion_no_supervisada.py`**: Para validaciones sin etiquetado previo.

---

## Cómo Levantar el Proyecto

Sigue estos pasos para instalar y ejecutar el proyecto en tu entorno local:

### 1. Requisitos Previos
Asegúrate de tener instalado **Python**. Además, es posible que requieras configurar credenciales de Supabase en un archivo de variables de entorno `.env` si las funciones de base de datos están activas en tu uso.

### 2. Instalación
Crea un entorno virtual, actívalo e instala las dependencias necesarias que se encuentran en `requirements.txt`:

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual (en macOS/Linux)
source venv/bin/activate
# En Windows usa: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Ejecución

Se puede ejecutar el proyecto de dos maneras diferentes, dependiendo de tus necesidades:

**Opción A: Interfaz Web (Dashboard Visual)**
Levanta el Dashboard interactivo usando Streamlit:
```bash
streamlit run app.py
```
Esto abrirá automáticamente una pestaña en tu navegador web donde podrás interactuar con el sistema de manera gráfica.

**Opción B: Consola / Línea de Comandos (CLI)**
Si prefieres procesar un archivo directamente por consola de manera rápida, puedes utilizar `main.py` pasándole la ruta del archivo CSV a validar:
```bash
python3 main.py data/10069.csv
```

---

## Plan de Implementación del Sistema en GDP Studios

A continuación se presenta la planificación estructurada para el despliegue e integración de la solución en GDP Studios, ajustado para el uso exclusivo del modelo de clasificación **Random Forest**:

### Cuadro 18: Plan de implementación del sistema en GDP Studios

| Fase | Actividad | Responsable | Duración estimada |
| :--- | :--- | :--- | :--- |
| **Fase 1 - Preparación** | Configurar el acceso de los analistas en Supabase Auth con sus correos institucionales. | Área de TI de GDP Studios | 1 semana |
| **Fase 1 - Preparación** | Verificar que los archivos CSV exportados desde el sistema interno cumplen el formato requerido. | Analista responsable | 1 semana |
| **Fase 1 - Preparación** | Recolectar archivos CSV históricos de al menos 15 jugadores adicionales para ampliar el dataset de entrenamiento. | Área de validación | 2 semanas |
| **Fase 2 - Entrenamiento inicial** | Ejecutar `entrenar_todos.py` con el dataset ampliado para entrenar y ajustar el modelo **Random Forest** (configurando estimadores y profundidad óptimos). | Analista responsable | 1 semana |
| **Fase 2 - Entrenamiento inicial** | Verificar que las métricas (Accuracy, Balanced Accuracy, Precision, Recall y F1-Score) del modelo **Random Forest** entrenado mantienen los umbrales de negocio definidos. | Analista responsable | 1 semana |
| **Fase 3 - Piloto** | Operar el sistema en paralelo con el proceso manual durante 4 semanas comparando resultados y alertas del modelo **Random Forest**. | Todos los analistas | 4 semanas |
| **Fase 3 - Piloto** | Registrar casos donde el sistema (vía **Random Forest**) y el proceso manual difieran para ajustar hiperparámetros o refinar las reglas de negocio asociadas. | Analista responsable | 4 semanas |
| **Fase 4 - Adopción** | Reemplazar el proceso manual por el sistema respaldado por **Random Forest** como método principal de validación de jugadas. | Área de validación | Permanente |
| **Fase 4 - Adopción** | Reentrenar el modelo **Random Forest** mensualmente con los nuevos CSV procesados para evitar la degradación del rendimiento por cambios de comportamiento (*concept drift*). | Analista responsable | Mensual |

