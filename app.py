import streamlit as st
import pandas as pd
import plotly.express as px
from datos import CANDIDATOS, PROPUESTAS

st.set_page_config(page_title="Match Electoral UC", page_icon="🗳️", layout="centered")

st.title("🗳️ Arma tu Consejería Ideal")
st.markdown("Selecciona **todas las propuestas** que consideres importantes o urgentes para la Escuela. El sistema calculará qué candidato incluye la mayor cantidad de las propuestas que elegiste dentro de su propio programa.")

# Agrupar propuestas por eje para mostrarlas ordenadas
ejes = []
for p in PROPUESTAS:
    if p['eje'] not in ejes:
        ejes.append(p['eje'])

# Diccionario para guardar el estado de los checkboxes
if 'selecciones' not in st.session_state:
    st.session_state.selecciones = {i: False for i in range(len(PROPUESTAS))}

# Renderizar checkboxes agrupados por eje
for eje in ejes:
    st.header(f"📌 {eje}")
    for i, p in enumerate(PROPUESTAS):
        if p['eje'] == eje:
            # Checkbox para cada propuesta
            st.session_state.selecciones[i] = st.checkbox(
                p['texto'], 
                value=st.session_state.selecciones[i],
                key=f"prop_{i}"
            )
    st.divider()

if st.button("Calcular mi Candidato Afín 📊", type="primary"):
    # 1. Contar cuántas propuestas tiene cada candidato en total (para sacar el porcentaje)
    total_propuestas_candidato = {c: 0 for c in CANDIDATOS}
    for p in PROPUESTAS:
        for c in p['candidatos']:
            total_propuestas_candidato[c] += 1

    # 2. Contar cuántas propuestas SELECCIONADAS pertenecen a cada candidato
    puntos_candidato = {c: 0 for c in CANDIDATOS}
    propuestas_marcadas = 0

    for i, p in enumerate(PROPUESTAS):
        if st.session_state.selecciones[i]:
            propuestas_marcadas += 1
            for c in p['candidatos']:
                puntos_candidato[c] += 1

    if propuestas_marcadas == 0:
        st.warning("Debes seleccionar al menos una propuesta para ver tus resultados.")
    else:
        # 3. Calcular Porcentaje de Afinidad: (Propuestas marcadas del candidato / Total de propuestas del candidato) * 100
        afinidad_porcentaje = {}
        for c in CANDIDATOS:
            if total_propuestas_candidato[c] > 0:
                afinidad_porcentaje[c] = (puntos_candidato[c] / total_propuestas_candidato[c]) * 100
            else:
                afinidad_porcentaje[c] = 0

        # Ordenar ranking
        ranking = sorted(afinidad_porcentaje.items(), key=lambda x: x[1], reverse=True)
        ganador = ranking[0][0]
        porcentaje_ganador = ranking[0][1]

        # --- MOSTRAR RESULTADOS ---
        st.header("🏆 Resultados de Afinidad")
        
        if porcentaje_ganador > 0:
            st.success(f"### Tu mayor afinidad es con: **{ganador}**")
            st.write(f"De todo el programa de este candidato, seleccionaste el **{porcentaje_ganador:.1f}%** de sus propuestas.")
        else:
            st.info("No seleccionaste propuestas asociadas a ningún candidato de la lista.")

        # Gráfico Visual
        st.subheader("📊 Porcentaje de compatibilidad con tu programa ideal")
        df_ranking = pd.DataFrame(ranking, columns=["Candidato", "Afinidad (%)"])
        
        fig = px.bar(
            df_ranking, 
            x="Afinidad (%)", 
            y="Candidato", 
            orientation='h', 
            color="Candidato",
            range_x=[0, 100] # Fija el eje X hasta 100%
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
