
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Proyecto Tasas Forward", layout="wide")
st.title("Cálculo de Curvas Forward")

datos_mercado = {
    "Mexico (Cetes)": {28: 6.15, 91: 6.45, 182: 6.76, 364: 7.06, 728: 7.89},
    "USA (T-Bills)": {28: 3.64, 91: 3.79, 182: 3.90, 364: 3.98, 728: 4.05},
    "Francia (Euribor/BTF)": {28: 2.32, 77: 2.39, 98: 2.48, 175: 2.60, 357: 2.78, 728: 3.04}
}

lista_resultados = []
for pais, curva in datos_mercado.items():
    nodos = list(curva.keys())
    nodos.sort()
    
    for i in range(len(nodos)):
        for j in range(i+1, len(nodos)):
            t1 = nodos[i]
            t2 = nodos[j]
            r1 = curva[t1]
            r2 = curva[t2]
            
            factor1 = 1.0 + (r1 / 100) * (t1 / 360)
            factor2 = 1.0 + (r2 / 100) * (t2 / 360)
            tasa_forward = ((factor2 / factor1) - 1.0) * (360 / (t2 - t1)) * 100
            
            lista_resultados.append({
                "País": pais,
                "Nodo Inicial (t1)": t1,
                "Nodo Final (t2)": t2,
                "Plazo Forward": t2 - t1,
                "Tasa Forward (%)": round(tasa_forward, 2)
            })

df_completo = pd.DataFrame(lista_resultados)

mejor_opcion_global = df_completo.loc[df_completo['Tasa Forward (%)'].idxmax()]

st.success(f"**Recomendación Global del Mercado:** La mayor oportunidad de tasa forward considerando todos los instrumentos está en **{mejor_opcion_global['País']}**, en el tramo de **{mejor_opcion_global['Nodo Inicial (t1)']} a {mejor_opcion_global['Nodo Final (t2)']} días**, con un rendimiento de **{mejor_opcion_global['Tasa Forward (%)']}%**.")
st.markdown("---")

st.markdown("### Selecciona el mercado a visualizar en la matriz y gráfica:")
pais_elegido = st.selectbox("", list(datos_mercado.keys()), label_visibility="collapsed")

df_pais = df_completo[df_completo["País"] == pais_elegido]

columna_izquierda, columna_derecha = st.columns([1, 2.5])

with columna_izquierda:
    st.subheader("Matriz de Combinaciones")
    df_mostrar = df_pais[["Nodo Inicial (t1)", "Nodo Final (t2)", "Plazo Forward", "Tasa Forward (%)"]]
    st.dataframe(df_mostrar, height=500, use_container_width=True)

with columna_derecha:
    st.subheader("Análisis Gráfico: Spot vs Forward")
    
    plazos_spot = list(datos_mercado[pais_elegido].keys())
    tasas_spot = list(datos_mercado[pais_elegido].values())
    
    plazos_fwd = []
    tasas_fwd = []
    
    for i in range(len(plazos_spot)-1):
        t_inicial = plazos_spot[i]
        t_final = plazos_spot[i+1]
        fila = df_pais[(df_pais["Nodo Inicial (t1)"] == t_inicial) & (df_pais["Nodo Final (t2)"] == t_final)]
        if not fila.empty:
            plazos_fwd.append(t_inicial) 
            tasas_fwd.append(fila["Tasa Forward (%)"].values[0])

    fig, ax = plt.subplots(figsize=(12, 5.5))
    
    ax.plot(plazos_spot, tasas_spot, marker='o', color='#2874A6', linewidth=2.5, label='Curva Spot')
    for x, y in zip(plazos_spot, tasas_spot):
        ax.annotate(f"{y:.2f}%", (x, y), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=9, color='#2874A6', fontweight='bold')
        
    if plazos_fwd:
        ax.plot(plazos_fwd, tasas_fwd, marker='s', color='#E74C3C', linewidth=2.5, linestyle='--', label='Curva Forward')
        
        for x, y in zip(plazos_fwd, tasas_fwd):
            idx_spot = plazos_spot.index(x)
            y_spot = tasas_spot[idx_spot]
            
            if y < y_spot:
                offset_y = -30
            else:
                offset_y = 12
                
            ax.annotate(f"{y:.2f}%", (x, y), textcoords="offset points", xytext=(0, offset_y), ha='center', fontsize=9, color='#E74C3C', fontweight='bold')
            
    ax.set_xlabel("Plazo al Vencimiento (Días)", fontsize=10)
    ax.set_ylabel("Tasa de Rendimiento (%)", fontsize=10)
    ax.legend(loc="upper left")
    
    plt.tight_layout()
    ax.grid(True, linestyle='--', alpha=0.4)
    
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    st.pyplot(fig)
