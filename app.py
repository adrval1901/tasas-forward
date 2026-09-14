import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Proyecto Tasas Forward", layout="wide")
st.title("Cálculo de Curvas Forward")

# 1. Base de Datos Oficial (Corte: 20 de agosto de 2026)
datos_mercado = {
    "Mexico (Cetes)": {28: 6.15, 91: 6.45, 182: 6.76, 364: 7.06, 728: 7.89},
    "USA (T-Bills)": {28: 3.71, 91: 3.73, 182: 3.85, 364: 3.91, 728: 4.19},
    "Francia (Euribor/BTF)": {28: 2.50, 91: 2.69, 182: 2.81, 364: 2.88, 728: 3.10}
}

# 2. Cálculo de Tasas Forward
lista_resultados = []
for pais, curva in datos_mercado.items():
    nodos = list(curva.keys())
    nodos.sort()
    
    for i in range(len(nodos)):
        for j in range(i+1, len(nodos)):
            t1 = nodos[i]
            t2 = nodos[j]
            r1 = curva[t1] / 100
            r2 = curva[t2] / 100
            
            # Condicional para separar la convención matemática por país
            if pais == "Mexico (Cetes)":
                # Fórmula Interés Simple (Base 360) para México
                factor1 = 1.0 + r1 * (t1 / 360)
                factor2 = 1.0 + r2 * (t2 / 360)
                fwd_decimal = ((factor2 / factor1) - 1.0) * (360 / (t2 - t1))
            else:
                # Fórmula Actuarial Compuesta ACTEX (Base 365) para EE. UU. y Francia
                t1_anos = t1 / 365
                t2_anos = t2 / 365
                fwd_decimal = (((1 + r2)**t2_anos / (1 + r1)**t1_anos)**(1 / (t2_anos - t1_anos))) - 1
            
            tasa_forward = fwd_decimal * 100
            
            lista_resultados.append({
                "País": pais,
                "Nodo Inicial (t1)": t1,
                "Nodo Final (t2)": t2,
                "Plazo Forward": t2 - t1,
                "Tasa Forward (%)": round(tasa_forward, 4) 
            })

df_completo = pd.DataFrame(lista_resultados)

# 3. Recomendación Global
mejor_opcion_global = df_completo.loc[df_completo['Tasa Forward (%)'].idxmax()]

st.success(f"**Recomendación Global del Mercado:** La mayor oportunidad de tasa forward considerando todos los instrumentos está en **{mejor_opcion_global['País']}**, en el tramo de **{mejor_opcion_global['Nodo Inicial (t1)']} a {mejor_opcion_global['Nodo Final (t2)']} días**, con un rendimiento de **{mejor_opcion_global['Tasa Forward (%)']}%**.")
st.markdown("---")

# 4. Interfaz Gráfica de Selección
st.markdown("### Selecciona el mercado a visualizar en la matriz y gráfica:")
pais_elegido = st.selectbox("", list(datos_mercado.keys()), label_visibility="collapsed")

# Filtrar y ordenar la tabla para el país elegido
df_pais = df_completo[df_completo["País"] == pais_elegido].sort_values(by="Tasa Forward (%)", ascending=False)

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
    
    # Extraer las tasas forward consecutivas para graficar
    for i in range(len(plazos_spot)-1):
        t_inicial = plazos_spot[i]
        t_final = plazos_spot[i+1]
        fila = df_pais[(df_pais["Nodo Inicial (t1)"] == t_inicial) & (df_pais["Nodo Final (t2)"] == t_final)]
        if not fila.empty:
            plazos_fwd.append(t_inicial) 
            tasas_fwd.append(fila["Tasa Forward (%)"].values[0])

    # Construcción de la figura
    fig, ax = plt.subplots(figsize=(12, 5.5))
    
    # Curva Spot (Azul)
    ax.plot(plazos_spot, tasas_spot, marker='o', color='#2874A6', linewidth=2.5, label='Curva Spot')
    for x, y in zip(plazos_spot, tasas_spot):
        ax.annotate(f"{y:.2f}%", (x, y), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=9, color='#2874A6', fontweight='bold')
        
    # Curva Forward Implícita (Roja)
    if plazos_fwd:
        ax.plot(plazos_fwd, tasas_fwd, marker='s', color='#E74C3C', linewidth=2.5, linestyle='--', label='Curva Forward Implícita')
        
        for x, y in zip(plazos_fwd, tasas_fwd):
            idx_spot = plazos_spot.index(x)
            y_spot = tasas_spot[idx_spot]
            
            # Ajuste de las etiquetas para que no se sobrepongan
            if y < y_spot:
                offset_y = -30
            else:
                offset_y = 12
                
            ax.annotate(f"{y:.4f}%", (x, y), textcoords="offset points", xytext=(0, offset_y), ha='center', fontsize=9, color='#E74C3C', fontweight='bold')
            
    # Formato del gráfico
    ax.set_xlabel("Plazo al Vencimiento (Días)", fontsize=10)
    ax.set_ylabel("Tasa de Rendimiento (%)", fontsize=10)
    ax.legend(loc="upper left")
    
    # Límites del eje X para mejor visualización
    ax.set_xlim(0, 800)
    
    # Ajustar márgenes para evitar cortes
    plt.tight_layout()
    ax.grid(True, linestyle='--', alpha=0.4)
    
    # Fondos transparentes
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    st.pyplot(fig)
