import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import itertools

# ====================================================================
# PASO 1: CONFIGURACIÓN 
# ====================================================================
st.set_page_config(page_title="Proyecto Tasas Forward", layout="wide")
st.title("Cálculo de Curvas Forward")

# ====================================================================
# PASO 2: DATOS FIJOS DEL DÍA (20 DE AGOSTO DE 2026)
# ====================================================================
datos_mercado = {
    "Mexico (Cetes)": {28: 6.15, 91: 6.45, 182: 6.76, 364: 7.06, 728: 7.89},
    "USA (T-Bills)": {28: 3.64, 91: 3.79, 182: 3.90, 364: 3.98, 728: 4.05},
    "Francia (Euribor/BTF)": {28: 2.32, 77: 2.39, 98: 2.48, 175: 2.60, 357: 2.78, 728: 3.04}
}

# ====================================================================
# PASO 3: MOTOR MATEMÁTICO
# ====================================================================
lista_resultados = []
for pais, tasas in datos_mercado.items():
    plazos = sorted(tasas.keys())
    combinaciones = list(itertools.combinations(plazos, 2))
    
    for t1, t2 in combinaciones:
        tasa1, tasa2 = tasas[t1], tasas[t2]
        
        # Fórmula Forward (Actual/360)
        factor1 = 1.0 + (tasa1 / 100) * (t1 / 360)
        factor2 = 1.0 + (tasa2 / 100) * (t2 / 360)
        tasa_forward = ((factor2 / factor1) - 1.0) * (360 / (t2 - t1)) * 100
        
        dias_forward = t2 - t1
        
        lista_resultados.append({
            "País": pais,
            "Nodo Inicial (t1)": t1,
            "Nodo Final (t2)": t2,
            "Plazo Forward (Días)": dias_forward,
            "Tasa Forward (%)": round(tasa_forward, 2)
        })

tabla_completa = pd.DataFrame(lista_resultados)
tabla_matriz = tabla_completa.sort_values(by=["País", "Nodo Inicial (t1)", "Nodo Final (t2)"]).reset_index(drop=True)

mejor_opcion = tabla_completa.loc[tabla_completa['Tasa Forward (%)'].idxmax()]

# ====================================================================
# PASO 4: INTERFAZ VISUAL Y GRÁFICAS DOBLES
# ====================================================================
st.subheader("Mayor Tasa Forward")
st.success(f"**Recomendación del Modelo:** La tasa forward pura más alta de la matriz se encuentra en **{mejor_opcion['País']}**, en el tramo de **{mejor_opcion['Nodo Inicial (t1)']} a {mejor_opcion['Nodo Final (t2)']} días**.")

col1, col2 = st.columns(2)
col1.metric("Instrumento", mejor_opcion['País'])
col2.metric("Tasa Forward Máxima", f"{mejor_opcion['Tasa Forward (%)']}%")

st.markdown("---")

columna_izquierda, columna_derecha = st.columns([1.2, 1])

with columna_izquierda:
    st.subheader("Matriz Completa de Combinaciones")
    st.dataframe(tabla_matriz, height=400, use_container_width=True)

with columna_derecha:
    st.subheader("Análisis Gráfico: Spot vs Forward")
    pais_elegido = st.selectbox("Selecciona un país para graficar:", list(datos_mercado.keys()))
    
    # 1. Preparar datos Spot
    datos_pais = datos_mercado[pais_elegido]
    plazos_spot = list(datos_pais.keys())
    tasas_spot = list(datos_pais.values())
    
    # 2. Preparar datos Forward (Tramos consecutivos)
    df_pais = tabla_matriz[tabla_matriz["País"] == pais_elegido]
    plazos_fwd = []
    tasas_fwd = []
    
    for i in range(len(plazos_spot)-1):
        t1, t2 = plazos_spot[i], plazos_spot[i+1]
        fila = df_pais[(df_pais["Nodo Inicial (t1)"] == t1) & (df_pais["Nodo Final (t2)"] == t2)]
        if not fila.empty:
            plazos_fwd.append(t2)
            tasas_fwd.append(fila["Tasa Forward (%)"].values[0])

    # 3. Construir la gráfica doble
    fig, ax = plt.subplots(figsize=(7, 4))
    
    # Línea Azul: Spot
    ax.plot(plazos_spot, tasas_spot, marker='o', color='#2874A6', linewidth=2, label='Curva Spot')
    for x, y in zip(plazos_spot, tasas_spot):
        ax.annotate(f"{y:.2f}%", (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='#2874A6')
        
    # Línea Roja: Forward
    if plazos_fwd:
        ax.plot(plazos_fwd, tasas_fwd, marker='s', color='#E74C3C', linewidth=2, linestyle='--', label='Curva Forward')
        for x, y in zip(plazos_fwd, tasas_fwd):
            ax.annotate(f"{y:.2f}%", (x, y), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=8, color='#E74C3C')
            
    ax.set_title(f"Estructura Temporal y Tasas Forward - {pais_elegido}")
    ax.set_xlabel("Plazo al Vencimiento (Días)")
    ax.set_ylabel("Tasa de Rendimiento (%)")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    
    st.pyplot(fig)