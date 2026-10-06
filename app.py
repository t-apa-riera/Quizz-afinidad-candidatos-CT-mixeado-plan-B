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
                f"**{p['titulo']}**: {p['descripcion']}", 
                value=st.session_state.selecciones[i],
                key=f"prop_{i}"
            )
    st.divider()

# 4. Cálculo de resultados
if st.button("Calcular mi Candidato Afín 📊", type="primary"):
    
    errores = False
    for eje in ejes:
        seleccionadas_en_eje = sum(1 for i, p in enumerate(PROPUESTAS) if p['eje'] == eje and st.session_state.selecciones[i])
        if seleccionadas_en_eje > 5:
            st.error(f"⚠️ Te pasaste en **{eje}**. Elegiste {seleccionadas_en_eje} propuestas, pero el máximo es 5. Desmarca algunas para continuar.")
            errores = True
            
    if not errores:
        total_seleccionadas = sum(1 for i in st.session_state.selecciones if st.session_state.selecciones[i])
        
        if total_seleccionadas == 0:
            st.warning("Debes seleccionar al menos una propuesta para ver tus resultados.")
        else:
            coincidencias_candidato = {c: 0 for c in CANDIDATOS}
            
            for i, p in enumerate(PROPUESTAS):
                if st.session_state.selecciones[i]:
                    for c in p['candidatos']:
                        coincidencias_candidato[c] += 1
            
            afinidad_porcentaje = {}
            for c in CANDIDATOS:
                afinidad_porcentaje[c] = (coincidencias_candidato[c] / total_seleccionadas) * 100

            ranking = sorted(afinidad_porcentaje.items(), key=lambda x: x[1], reverse=True)
            ganador = ranking[0][0]
            porcentaje_ganador = ranking[0][1]

            st.header("🏆 Resultados de Afinidad")
            
            if porcentaje_ganador > 0:
                st.success(f"### Tu mayor afinidad es con: **{ganador}**")
                st.write(f"De tu programa ideal de {total_seleccionadas} propuestas, este candidato abarca el **{porcentaje_ganador:.1f}%** de lo que exiges.")
            else:
                st.info("Tus selecciones no coinciden con las propuestas de ningún candidato.")

            st.subheader("📊 Grado de coincidencia con tu selección")
            df_ranking = pd.DataFrame(ranking, columns=["Candidato", "Afinidad (%)"])
            df_ranking = df_ranking[df_ranking["Afinidad (%)"] > 0]
            
            # Mapeo exacto de colores actualizados
            colores_movimientos = {
                "Gabriel Vilugrón (NAU)": "#1ED680",
                "Victoria Trejo (NAU)": "#1ED680",
                "Cristóbal Mingo (Solidaridad)": "#FF0000",
                "Tomás Vásquez (Solidaridad)": "#FF0000",
                "Max Weldt (Avanzar)": "#128EFF",
                "Carlos Abogabir (1A)": "#FFAD29",
                "Antonia Ríos (1A)": "#FFAD29"
            }
            
            if not df_ranking.empty:
                fig = px.bar(
                    df_ranking, 
                    x="Afinidad (%)", 
                    y="Candidato", 
                    orientation='h', 
                    color="Candidato",
                    color_discrete_map=colores_movimientos,
                    range_x=[0, 100]
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
