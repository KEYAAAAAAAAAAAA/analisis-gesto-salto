Aquí tienes la propuesta de **`README.md`** estructurada y profesional para tu repositorio de GitHub (`analisis-gero-sako`), ajustada al flujo original de tu código (detección de pose, inversión de ejes, conteo de saltos y gráfica interactiva con Plotly):

---

```markdown
# 🏋️‍♂️ Análisis Bioinstrumental: Conteo de Saltos y Cadencia Pliométrica

Aplicación web interactiva desarrollada en **Python** y **Streamlit** para la evaluación biomecánica y cuantificación automática de saltos en tiempo real mediante visión por computador y estimación postural (*Pose Estimation*).

---

## 📌 Descripción del Proyecto

El análisis cinemático del salto es una prueba fundamental en Kinesiología y Ciencias del Deporte para evaluar la fuerza reactiva, la potencia muscular y la cadencia pliométrica. Tradicionalmente, esta evaluación requiere plataformas de contacto o sistemas de captura de movimiento costosos.

Esta plataforma ofrece una alternativa **portátil, accesible y objetiva** que permite a profesionales de la salud y entrenadores procesar archivos de video y obtener métricas cuantitativas instantáneas mediante algoritmos de inteligencia artificial.

---

## ✨ Características Principales

- **Carga de Video Flexible:** Admite archivos de video de cuerpo completo en formatos `.mp4`, `.mov` y `.avi`.
- **Rastreo Anatomofisiológico:** Detección automática del punto de la cadera (*LEFT_HIP*) mediante **MediaPipe Pose**.
- **Procesamiento Cinemático:**
  - Inversión matemática del eje $Y$ para reflejar el comportamiento vertical real del salto.
  - Conversión del índice de fotogramas a tiempo continuo en segundos ($\text{FPS}$).
  - Algoritmo cinemático para la identificación y conteo automático de cada salto.
- **Métricas Instantáneas:**
  - N° Total de Saltos Detectados.
  - Duración total de la prueba (segundos).
- **Gráfica Interactiva:** Visualización cinemática con **Plotly**, que incluye estampa de tiempo, altura relativa y delimitación del umbral de conteo.

---

## 📐 Fundamento Algorítmico y Matemático

1. **Estimación Postural (MediaPipe Pose):**
   Se utiliza el modelo de visión por computador para rastrear el **Landmark 23** (*cadera izquierda / LEFT_HIP*), garantizando estabilidad cinemática durante el ciclo del salto.

2. **Inversión de Coordenadas:**
   En visión por computador, el origen $(0,0)$ se ubica en la esquina superior izquierda. Para alinear el gráfico con la elevación real del cuerpo, se aplica la transformación:
   $$Y_{\text{inverso}} = 1 - Y_{\text{normado}}$$

3. **Eje Temporal Real:**
   El tiempo en segundos para cada fotograma se calcula a partir de la tasa de refresco ($FPS$) extraída del video:
   $$\text{Tiempo } (s) = \frac{\text{Fotograma}}{\text{FPS}}$$

4. **Conteo de Saltos:**
   El algoritmo evalúa la trayectoria vertical de la cadera identificando las fases de despegue y elevación máxima cuando la curva cruza el umbral de activación definido en la prueba.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.9+
- **Interfaz Web:** [Streamlit](https://streamlit.io/)
- **Visión por Computador:** [OpenCV](https://opencv.org/) & [MediaPipe Pose](https://developers.google.com/mediapipe)
- **Visualización de Datos:** [Plotly Express / Graph Objects](https://plotly.com/python/)
- **Procesamiento Numérico:** NumPy / Pandas

---

## 📁 Estructura del Repositorio

```text
analisis-gero-sako/
├── app.py              # Código fuente principal de la aplicación Streamlit
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Documentación técnica del proyecto

```

---

## 🚀 Instalación y Ejecución Local

1. **Clonar el repositorio:**
```bash
git clone [https://github.com/tu-usuario/analisis-gero-sako.git](https://github.com/tu-usuario/analisis-gero-sako.git)
cd analisis-gero-sako

```


2. **Crear y activar un entorno virtual (recomendado):**
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

```


3. **Instalar dependencias:**
```bash
pip install -r requirements.txt

```


4. **Ejecutar la aplicación:**
```bash
streamlit run app.py

```



---

## 🎥 Recomendaciones para la Grabación del Video

Para garantizar la mayor precisión en la detección:

* **Encuadre:** Plano general que mantenga al sujeto en vista de **cuerpo completo** durante toda la prueba.
* **Cámara:** Dispositivo fijo (preferiblemente en trípode) para evitar desplazamientos del fondo.
* **Plano:** Vista sagital (lateral) o frontal.
* **Iluminación:** Buena iluminación y contraste entre el sujeto y el fondo.

---

## 👥 Autores y Créditos

Proyecto desarrollado para la asignatura de **Bioinstrumentación / Biomecánica**.

```

```
