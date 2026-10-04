import streamlit as st
import cv2
import mediapipe as mp
import tempfile
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis de Salto", layout="wide")
st.title("🤸 Análisis Bioinstrumental: Conteo de Saltos")

video_file = st.file_uploader("Sube un video de perfil realizando saltos (.mp4, .mov)", type=['mp4', 'mov'])

if video_file:
    # Guardar temporalmente para que OpenCV lo lea
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    
    st.video(tfile.name)
    
    if st.button("Iniciar Análisis Cuantitativo"):
        with st.spinner("Procesando fotogramas con Inteligencia Artificial..."):
            mp_pose = mp.solutions.pose
            pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
            cap = cv2.VideoCapture(tfile.name)
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            alturas_cadera = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # MediaPipe requiere imágenes en formato RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
                
                if results.pose_landmarks:
                    # Rastrear la cadera izquierda (punto 23)
                    cadera_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y
                    alturas_cadera.append(cadera_y)
                    
            cap.release()
            
            if alturas_cadera:
                # Procesar datos numéricos
                df = pd.DataFrame(alturas_cadera, columns=['Altura_Cadera'])
                # En MediaPipe, Y=0 es arriba. Invertimos para que el gráfico sea lógico.
                df['Altura_Invertida'] = 1 - df['Altura_Cadera']
                df['Tiempo_Segundos'] = df.index / fps
                
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
                
                # Mostrar métricas
                st.success("Análisis finalizado")
                col1, col2 = st.columns(2)
                col1.metric("Cantidad de Saltos (Frecuencia)", f"{saltos_detectados} saltos")
                col2.metric("Duración analizada", f"{round(len(df)/fps, 2)} seg")
                
               # Gráfico
                fig = px.line(df, x='Tiempo_Segundos', y='Altura_Invertida', title="Desplazamiento Vertical de Cadera")
                fig.add_hline(y=umbral, line_dash="dash", line_color="red", annotation_text="Umbral de Detección")
                st.plotly_chart(fig, use_container_width=True)

else:
    st.error("No se detectó el cuerpo en el video. Usa una toma de cuerpo completo.")
