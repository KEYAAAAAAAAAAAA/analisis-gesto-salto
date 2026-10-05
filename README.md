# 🤸 Análisis Bioinstrumental: Conteo Automatizado de Saltos

¡Hola! Bienvenid@ al repositorio y documentación de nuestro proyecto. Esta aplicación nace de la necesidad kinesiológica de contar con una herramienta **portable, gratuita y objetiva** para evaluar la capacidad pliométrica y la cadencia de salto en atletas o pacientes.

En la evaluación de campo tradicional, la cantidad de saltos se registra mediante observación directa y cronometraje manual (lo que genera un alto margen de error humano) o con plataformas de contacto de laboratorio (que resultan sumamente costosas y difíciles de transportar). A través de este código escrito en Python y desplegado en la web con Streamlit, logramos automatizar el conteo a partir de un simple video grabado con un teléfono celular.

---

## 🛠️ ¿Cómo funciona el código? (Explicación paso a paso)

Aunque no tengo una formación especializada en programación, he estructurado la lógica de este script para que replique el flujo cinemático de una evaluación biomecánica. A continuación, explico el funcionamiento de cada sección del código:

### 1. Interfaz y Almacenamiento Temporal (`Streamlit` y `tempfile`)

* La librería **Streamlit** se encarga de estructurar la pantalla web, agregando títulos, el cargador de archivos (`st.file_uploader`) y las ventanas de resultados.
* Cuando el usuario sube un video (`.mp4` o `.mov`), el código utiliza `tempfile.NamedTemporaryFile` para guardarlo momentáneamente en el servidor. Esto es indispensable porque la librería de procesamiento de video (**OpenCV**) necesita una ruta física en disco para leer el archivo fotograma a fotograma.

### 2. Detección de Puntos Anatómicos (`OpenCV` y `MediaPipe Pose`)

* El código procesa el video dentro de un bucle `while cap.isOpened()`.
* **Transformación de Color:** OpenCV lee las imágenes en formato **BGR** (Blue, Green, Red), pero el modelo de inteligencia artificial **MediaPipe** requiere el formato estándar **RGB** (Red, Green, Blue). Por ello, aplicamos `cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)`.
* **Rastreo de la Cadera:** MediaPipe detecta 33 puntos clave del cuerpo (*landmarks*). Extraemos la coordenada vertical ($Y$) de la **cadera izquierda** (`LEFT_HIP`, punto 23), la cual representa adecuadamente el desplazamiento vertical del centro de masa.

### 3. Inversión Cinemática y Eje de Tiempo (`Pandas`)

* **Inversión de Coordenadas:** En visión por computador, la esquina superior izquierda de la imagen es el origen $(0,0)$. Esto implica que cuando la persona salta hacia arriba, el valor numérico de la coordenada $Y$ disminuye. Para que el gráfico sea biomecánicamente intuitivo (donde la cima del salto corresponda al punto más alto de la curva), aplicamos la transformación:

$$\text{Altura\_Invertida} = 1 - \text{Altura\_Cadera}$$


* **Cálculo de Tiempo:** Dividimos el índice de cada fotograma entre la tasa de fotogramas por segundo del video ($\text{FPS}$):

$$\text{Tiempo\_Segundos} = \frac{\text{Índice}}{\text{FPS}}$$



### 4. Algoritmo de Detección por Umbral y Fase de Vuelo

* **Cálculo del Umbral Dinámico:** Para evitar que pequeños temblores o movimientos posturales mínimos cuenten como saltos, calculamos la mediana de la altura de la cadera en todo el video y le sumamos un margen del $5\%$ ($0.05$):

$$\text{Umbral} = \text{Mediana}(\text{Altura\_Invertida}) + 0.05$$


* **Máquina de Estados (`en_fase_vuelo`):**
* El código recorre la serie de tiempo evaluando la posición de la cadera.
* Si la altura invertida supera la línea del umbral (`y > umbral`) y el sujeto no estaba registrado en el aire (`not en_fase_vuelo`), el sistema suma **+1 al contador de saltos** y cambia la variable a `en_fase_vuelo = True`.
* Cuando la cadera vuelve a descender por debajo del umbral (`y < umbral`), la variable regresa a `en_fase_vuelo = False`, quedando lista para la siguiente repetición.



### 5. Presentación de Resultados y Gráfico Interactivo (`Plotly`)

* **Métricas Principales:** Mediante `st.metric`, la pantalla muestra de forma clara dos tarjetas con el número total de saltos contabilizados y la duración total del análisis en segundos (`len(df) / fps`).
* **Gráfica de Desplazamiento:** Utilizando **Plotly Express**, se genera una curva interactiva que grafica la posición de la cadera en función del tiempo y dibuja una línea roja segmentada (`fig.add_hline`) que marca visualmente el umbral de corte.

---

## 📚 Librerías Utilizadas y su Función

| Librería | Función en el Proyecto |
| --- | --- |
| `streamlit` | Genera la plataforma web interactiva (botones, cargador de archivos, tarjetas de métricas). |
| `cv2` (OpenCV) | Lee el archivo de video fotograma por fotograma y convierte los espacios de color (BGR a RGB). |
| `mediapipe` | Modelo de Inteligencia Artificial que detecta la postura del cuerpo y entrega las coordenadas de la cadera. |
| `tempfile` | Permite crear un archivo temporal en el servidor para que OpenCV pueda procesar el video cargado. |
| `pandas` | Organiza los datos extraídos en una tabla (DataFrame) para realizar cálculos matemáticos de forma limpia. |
| `plotly.express` | Dibuja la gráfica cinemática interactiva con la línea del umbral de detección. |

---

## 📋 Instrucciones de Uso

1. Accede a la aplicación a través del enlace público en **Streamlit Cloud**.
2. Haz clic en **"Browse files"** y sube un video grabado de perfil en formato `.mp4` o `.mov`.
3. Comprueba en el reproductor de video integrado que el atleta esté enfocado correctamente.
4. Presiona el botón **"Iniciar Análisis Cuantitativo"**.
5. Revisa la cantidad de saltos contabilizados y analiza la regularidad del movimiento en el gráfico de desplazamiento vertical.

---

## 🎥 Criterios para un Registro de Video Adecuado

Para asegurar que el algoritmo procese los datos sin margen de error:

* **Encuadre Completo:** Graba al atleta de cuerpo entero (cabeza a pies). Si los pies o la pelvis salen del encuadre, la IA perderá el rastreo.
* **Cámara Fija:** Es fundamental utilizar un trípode o apoyar la cámara sobre una superficie estable; el movimiento de la cámara altera la línea base del umbral.
* **Plano:** Mantén una toma perpendicular (de perfil o de frente) a una velocidad estándar de 30 a 60 FPS.
