# DOCUMENTO TÉCNICO Y EXPLICACIÓN DEL CÓDIGO FUENTE (`app.py`)

**Proyecto:** Aplicación para el Análisis Bioinstrumental de Cadencia Pliométrica

**Área:** Kinesiología / Biomecánica del Movimiento Humano

**Plataforma de Despliegue:** Streamlit Cloud

---

## 1. Módulos y Librerías Utilizadas

El sistema utiliza seis librerías especializadas en Python para procesar el video en la nube, extraer los datos cinemáticos y presentar los resultados interactivos:

* **`streamlit (st)`:** Construye la interfaz gráfica de usuario (web), gestiona la carga de archivos, despliega métricas numéricas y renderiza los gráficos dinámicos.
* **`cv2` (OpenCV Headless):** Procesa la secuencia de video fotograma a fotograma, extrayendo la tasa de refresco nativa ($\text{FPS}$) y las dimensiones de la imagen.
* **`mediapipe (mp)`:** Sublibrería de inteligencia artificial desarrollada por Google para la estimación de postura corporal (*Pose Estimation*). Permite rastrear 33 puntos anatómicos clave en 2D a partir del fotograma RGB.
* **`pandas (pd)`:** Estructura las coordenadas temporales extraídas en matrices de datos organizadas (*DataFrames*), facilitando las operaciones matemáticas vectoriales.
* **`plotly.express (px)`:** Crea el gráfico cinemático vectorial e interactivo donde el evaluador puede explorar la curva de movimiento y consultar marcas temporales con precisión decimal.
* **`tempfile`:** Genera un puente de memoria guardando el video subido por el usuario en una ubicación temporal en disco dentro del servidor en la nube, permitiendo la lectura directa por parte de OpenCV.

---

## 2. Explicación Detallada del Código por Bloques

### Bloque 1: Configuración de la Interfaz de Usuario

```python
import streamlit as st
import cv2
import mediapipe as mp
import pandas as pd
import plotly.express as px
import tempfile

st.title("Análisis Bioinstrumental de Cadencia Pliométrica")
st.write("Carga un video de saltos para cuantificar la frecuencia y duración del movimiento.")

video_file = st.file_uploader("Cargar Video (.mp4, .mov)", type=["mp4", "mov"])

```

* **Lógica:** Despliega el encabezado institucional de la plataforma y habilita el componente de carga de archivos (`st.file_uploader`).
* **Comportamiento:** La ejecución de la aplicación se pausa en este punto hasta que el usuario sube un archivo con extensión `.mp4` o `.mov`.

---

### Bloque 2: Recepción del Video y Puente de Memoria

```python
if video_file is not None:
    # Guardar el archivo temporalmente
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())
    
    cap = cv2.VideoCapture(tfile.name)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or pd.isna(fps):
        fps = 30.0  # Valor de respaldo por seguridad

```

* **Gestión de Memoria:** Streamlit almacena los archivos subidos en la memoria RAM del servidor. Sin embargo, OpenCV requiere una ruta de almacenamiento físico para procesar el video. `tempfile` crea este archivo físico temporal.
* **Frecuencia de Muestreo ($\text{FPS}$):** Se obtiene la velocidad del video registrada en fotogramas por segundo. Esta variable determina la resolución temporal del análisis: si la grabación fue hecha a 30 $\text{FPS}$, la distancia entre cada punto de la curva es de $\frac{1}{30} \approx 0,033$ segundos.

---

### Bloque 3: Inicialización del Rastreador Corporal (MediaPipe Pose)

```python
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    alturas_cadera = []

```

* **Configuración del Detector:** Se instancia la red neuronal de estimación postural con un umbral de confianza mínimo del $50\%$ tanto para la detección inicial como para el seguimiento fotograma a fotograma.
* **Contenedor Cinemático:** Se define la lista `alturas_cadera` vacía para acumular la posición vertical normalizada de la pelvis a lo largo del tiempo.

---

### Bloque 4: Lectura Fotograma a Fotograma y Extracción Cinemática

```python
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convertir el formato de color de BGR a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            # Punto 23: LEFT_HIP (Cadera izquierda)
            cadera_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y
            alturas_cadera.append(cadera_y)

    cap.release()

```

* **Bucle de Procesamiento:** Transforma la secuencia de video en una serie de imágenes estáticas. Cuando el video finaliza, `ret` conmuta a `False` y finaliza la lectura.
* **Conversión de Espacio de Color:** OpenCV procesa por defecto en codificación BGR, mientras que MediaPipe requiere una matriz en RGB, realizándose la conversión mediante `cv2.cvtColor`.
* **Aislamiento Anatómico:** Se extrae la coordenada vertical normalizada $Y$ de la cadera izquierda (`LEFT_HIP`, hito anatómico número 23 en la topología de MediaPipe Pose) y se añade a la matriz cinemática.

---

### Bloque 5: Transformación de Datos y Construcción del Eje Temporal

```python
    if alturas_cadera:
        # Procesar datos numéricos
        df = pd.DataFrame(alturas_cadera, columns=['Altura_Cadera'])
        df['Altura_Invertida'] = 1 - df['Altura_Cadera']
        df['Tiempo_Segundos'] = df.index / fps

```

* **Inversión del Eje Vertical:** En visión por computador, el origen $(0,0)$ está fijado en el vértice superior izquierdo de la imagen. Por lo tanto, el desplazamiento hacia arriba disminuye el valor de $Y$. Se aplica la transformación matemática para hacer el gráfico intuitivo para la interpretación clínica:

$$Y_{inverso} = 1 - Y_{cadera}$$


* **Escala de Tiempo Continua:** Transforma el número de fotograma en tiempo real en segundos dividiendo la posición en la matriz por la velocidad de grabación:

$$\text{Tiempo (s)} = \frac{\text{Índice del Fotograma}}{\text{FPS}}$$



---

### Bloque 6: Algoritmo Dinámico de Conteo de Saltos

```python
        # Algoritmo de conteo (detectar cuando sube y baja del promedio)
        umbral = df['Altura_Invertida'].median() + 0.05
        saltos_detectados = 0
        en_fase_vuelo = False

        for y in df['Altura_Invertida']:
            if y > umbral and not en_fase_vuelo:
                saltos_detectados += 1
                en_fase_vuelo = True
            elif y < umbral:
                en_fase_vuelo = False

```

* **Umbral Dinámico Basado en Mediana:** Para prevenir que los movimientos preparatorios iniciales o finales (como agacharse para encender o apagar la cámara) desplacen la referencia, se reemplaza la media aritmética por la **mediana estadística** de la señal, sumando un margen estandarizado de $0,05$ unidades relativas:

$$\text{Umbral} = \text{Mediana}(Y_{inverso}) + 0,05$$


* **Máquina de Estados Finitos (`en_fase_vuelo`):** Evita la duplicación de conteos dentro de una misma fase aérea. Solo incrementa el contador ($+1$) en el cruce ascendente inicial ($Y_{inverso} > \text{Umbral}$). La variable `en_fase_vuelo` permanece activa hasta que la cadera desciende por debajo de la línea límite en la fase de contacto.

---

### Bloque 7: Despliegue de Resultados y Métricas en Pantalla

```python
        # Mostrar métricas
        st.success("Análisis finalizado")
        col1, col2 = st.columns(2)
        col1.metric("Cantidad de Saltos (Frecuencia)", f"{saltos_detectados} saltos")
        col2.metric("Duración analizada", f"{round(len(df)/fps, 2)} seg")

```

* Genera una notificación de procesamiento exitoso y presenta de manera destacada las dos métricas fundamentales del análisis: **Cantidad Total de Saltos** (frecuencia absoluta) y **Tiempo Total Analizado** en segundos (redondeado a dos decimales).

---

### Bloque 8: Construcción del Gráfico Cinemático Interactivo

```python
        # 1. Convertir estrictamente la columna a números decimales
        df['Tiempo_Segundos'] = df['Tiempo_Segundos'].astype(float)

        # 2. Crear el gráfico base
        fig = px.line(df, x='Tiempo_Segundos', y='Altura_Invertida', title="Desplazamiento Vertical de Cadera")
        fig.add_hline(y=umbral, line_dash="dash", line_color="red", annotation_text="Umbral de Detección")

        # 3. Forzar el eje X a ser numérico (lineal) y aplicar formato de 2 decimales
        fig.update_xaxes(
            type='linear',
            tickformat=".2f",
            title_text="Tiempo (Segundos)"
        )

        # 4. Formatear la etiqueta flotante al pasar el mouse
        fig.update_traces(hovertemplate="Tiempo: %{x:.2f} seg<br>Altura: %{y:.3f}")

        st.plotly_chart(fig, use_container_width=True)

```

* **Conversión Explícita de Tipo (`astype(float)`):** Asegura que la serie de tiempo sea interpretada como una variable numérica continua y no como etiquetas discretas.
* **Formateo del Eje X (`type='linear'`, `tickformat=".2f"`):** Fuerza a Plotly a proyectar una escala numérica lineal continua con ticks configurados estrictamente a dos decimales de precisión.
* **Etiquetas Flotantes (`hovertemplate`):** Define la información emergente al interactuar con el gráfico, mostrando la estampa de tiempo exacta (en centésimas de segundo) y la altura relativa de la cadera en cada fotograma.
* **Línea de Umbral (`add_hline`):** Traza la recta discontinua de color rojo correspondiente al límite de corte, permitiendo la auditoría visual por parte del evaluador.

---

### Bloque 9: Manejo de Excepciones

```python
    else:
        st.error("No se detectó el cuerpo en el video. Usa una toma de cuerpo completo.")

```

* Si la red de MediaPipe no detecta un cuerpo humano en la secuencia (debido a problemas de encuadre, iluminación o planos demasiado cerrados), la aplicación interrumpe el análisis y muestra un mensaje de error instructivo.

---
