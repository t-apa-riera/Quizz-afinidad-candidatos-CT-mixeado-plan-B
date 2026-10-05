import streamlit as st
import pandas as pd
import plotly.express as px
from datos import CANDIDATOS, PROPUESTAS

st.set_page_config(page_title="Match Electoral UC", page_icon="🗳️", layout="centered")

st.title("🗳️ Arma tu Consejería Ideal")
st.markdown("Lee las iniciativas y selecciona **hasta 5 propuestas que más te representen por área temática**. Al final, el sistema evaluará qué candidato es el más compatible con el programa que acabas de armar.")

# 1. Agrupar propuestas por eje
ejes = []
for p in PROPUESTAS:
    if p['eje'] not in ejes:
        ejes.append(p['eje'])

# 2. Inicializar estado de selecciones
if 'selecciones' not in st.session_state:
    st.session_state.selecciones = {i: False for i in range(len(PROPUESTAS))}

st.divider()

# 3. Renderizar checkboxes por área
for eje in ejes:
    st.header(f"📌 {eje}")
    st.caption("Selecciona máximo 5 propuestas de esta lista:")
    
    for i, p in enumerate(PROPUESTAS):
        if p['eje'] == eje:
            st.session_state.selecciones[i] = st.checkbox(
                p['texto'], 
                value=st.session_state.selecciones[i],
                key=f"prop_{i}"
            )
    st.divider()

# 4. Cálculo de resultados
if st.button("Calcular mi Candidato Afín 📊", type="primary"):
    
    # Validar que no se pasen de 5 por eje
    errores = False
    for eje in ejes:
        seleccionadas_en_eje = sum(1 for i, p in enumerate(PROPUESTAS) if p['eje'] == eje and st.session_state.selecciones[i])
        if seleccionadas_en_eje > 5:
            st.error(f"⚠️ Te pasaste en **{eje}**. Elegiste {seleccionadas_en_eje} propuestas, pero el máximo es 5. Desmarca algunas para continuar.")
            errores = True
            
    if not errores:
        # Contar total de propuestas seleccionadas por el usuario (El "Programa Ideal")
        total_seleccionadas = sum(1 for i in st.session_state.selecciones if st.session_state.selecciones[i])
        
        if total_seleccionadas == 0:
            st.warning("Debes seleccionar al menos una propuesta para ver tus resultados.")
        else:
            # Contar cuántas propuestas seleccionadas le pertenecen a cada candidato
            coincidencias_candidato = {c: 0 for c in CANDIDATOS}
            
            for i, p in enumerate(PROPUESTAS):
                if st.session_state.selecciones[i]:
                    for c in p['candidatos']:
                        coincidencias_candidato[c] += 1
            
            # Calcular porcentaje de afinidad: (Coincidencias del candidato / Total de propuestas elegidas) * 100
            afinidad_porcentaje = {}
            for c in CANDIDATOS:
                afinidad_porcentaje[c] = (coincidencias_candidato[c] / total_seleccionadas) * 100

            # Ordenar el ranking de mayor a menor
            ranking = sorted(afinidad_porcentaje.items(), key=lambda x: x[1], reverse=True)
            ganador = ranking[0][0]
            porcentaje_ganador = ranking[0][1]

            # --- MOSTRAR RESULTADOS ---
            st.header("🏆 Resultados de Afinidad")
            
            if porcentaje_ganador > 0:
                st.success(f"### Tu mayor afinidad es con: **{ganador}**")
                st.write(f"De tu programa ideal de {total_seleccionadas} propuestas, este candidato abarca el **{porcentaje_ganador:.1f}%** de lo que exiges.")
            else:
                st.info("Tus selecciones no coinciden con las propuestas de ningún candidato.")

            # Gráfico de barras
            st.subheader("📊 Grado de coincidencia con tu selección")
            df_ranking = pd.DataFrame(ranking, columns=["Candidato", "Afinidad (%)"])
            # Mostrar solo los que tienen más de 0% para limpiar el gráfico
            df_ranking = df_ranking[df_ranking["Afinidad (%)"] > 0]
            
            if not df_ranking.empty:
                fig = px.bar(
                    df_ranking, 
                    x="Afinidad (%)", 
                    y="Candidato", 
                    orientation='h', 
                    color="Candidato",
                    range_x=[0, 100]
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
