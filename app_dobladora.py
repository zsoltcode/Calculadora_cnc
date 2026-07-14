import streamlit as st

# ==========================================
# NUEVA VERSIÓN: AMADA CNC (Con cambio de unidades)
# ==========================================

# Funciones de conversión
def inches_to_mm(inches):
    return inches * 25.4

def mm_to_inches(mm):
    return mm / 25.4

st.set_page_config(page_title="Amada CNC Calculator", layout="centered")
st.title("🚀 Calculadora Amada CNC")
st.write("Optimizada para milésimas de pulgada (0.000\") y milímetros.")

# Selector de unidad
unidad = st.radio("Selecciona la unidad:", ("Pulgadas", "Milímetros"))

# Convertir valores a pulgadas para cálculos internos
def convert_to_inches(value, unit):
    if unit == "Milímetros":
        return mm_to_inches(value)
    return value

def convert_from_inches(value, unit):
    if unit == "Milímetros":
        return inches_to_mm(value)
    return value

# Formato de entrada según unidad
def format_value(value, unit):
    if unit == "Milímetros":
        return f"{value:.2f} mm"
    return f"{value:.3f}\""

st.header("1. Datos del Material")
material = st.selectbox("Tipo de Material:", ["Acero Estándar (Cold Rolled)", "Acero Inoxidable", "Aluminio"])

col_input1, col_input2 = st.columns(2)
with col_input1:
    # Ajustamos a 3 decimales (milésimas) o 2 decimales (mm) según unidad
    espesor_input = st.number_input(
        "Espesor:",
        min_value=0.010 if unidad == "Pulgadas" else 0.1,
        value=0.060 if unidad == "Pulgadas" else 1.52,
        step=0.001 if unidad == "Pulgadas" else 0.1,
        format="%.3f" if unidad == "Pulgadas" else "%.2f"
    )
    espesor = convert_to_inches(espesor_input, unidad)
with col_input2:
    # La longitud de doblez también en pulgadas
    longitud_doblez_input = st.number_input(
        "Longitud a doblar:",
        min_value=0.1 if unidad == "Pulgadas" else 1.0,
        value=12.0 if unidad == "Pulgadas" else 304.8,
        step=0.1 if unidad == "Pulgadas" else 1.0,
        format="%.1f" if unidad == "Pulgadas" else "%.1f"
    )
    longitud_doblez = convert_to_inches(longitud_doblez_input, unidad)

st.header("2. Datos de la Pieza")
col_input3, col_input4 = st.columns(2)
with col_input3:
    grados = st.number_input("Ángulo deseado (grados):", min_value=10.0, max_value=180.0, value=90.0, step=0.5)
with col_input4:
    ala_deseada_input = st.number_input(
        "Longitud del ala:",
        min_value=0.050 if unidad == "Pulgadas" else 0.1,
        value=1.000 if unidad == "Pulgadas" else 25.4,
        step=0.001 if unidad == "Pulgadas" else 0.1,
        format="%.3f" if unidad == "Pulgadas" else "%.2f"
    )
    ala_deseada = convert_to_inches(ala_deseada_input, unidad)

if st.button("Calcular Parámetros de Máquina", type="primary"):
    
    # --- 1. PROPIEDADES DEL MATERIAL ---
    if material == "Acero Estándar (Cold Rolled)":
        factor_fuerza = 1.0; retorno_elastico = 1.5  
    elif material == "Acero Inoxidable":
        factor_fuerza = 1.5; retorno_elastico = 3.0  
    else: 
        factor_fuerza = 0.5; retorno_elastico = 1.0  
        
    # --- 2. INVENTARIO DE MATRICES (En pulgadas) ---
    # Nota: Amada suele usar matrices en milímetros (4mm, 6mm, 8mm, etc.)
    # Aquí están sus equivalentes en milésimas de pulgada. ¡Cámbialas por las tuyas!
    matrices_disponibles = [0.157, 0.236, 0.315, 0.394, 0.472, 0.630]
    
    # Regla clásica: V = 8 veces el espesor
    apertura_v_ideal = espesor * 8
    
    # Buscamos la matriz real más cercana en tu inventario
    v_real = min(matrices_disponibles, key=lambda x: abs(x - apertura_v_ideal))
        
    # --- 3. MATEMÁTICAS (SISTEMA IMPERIAL) ---
    # Fórmula imperial empírica para US Tons: (575 * t^2) / V * L
    tonelaje_requerido = ((575 * (espesor ** 2)) / v_real) * longitud_doblez * factor_fuerza
    
    # Deducción y radio
    deduccion_simple = espesor * 1.5 
    eje_x = ala_deseada - (deduccion_simple / 2)
    angulo_maquina = grados - retorno_elastico
    ala_minima = v_real * 0.7
    radio_interior = v_real / 6

    # --- 4. MOSTRAR RESULTADOS ---
    st.markdown("---")
    st.subheader("📊 Resultados para Amada CNC")
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.success(f"🔽 **Matriz a usar (V):** {format_value(v_real, unidad)}")
        st.error(f"⚖️ **Tonelaje Estimado:** {tonelaje_requerido:.1f} US Tons")
        st.success(f"📏 **Tope Eje X:** {format_value(eje_x, unidad)}")
        
    with res_col2:
        st.warning(f"📐 **Ángulo a programar:** {angulo_maquina:.1f}°")
        st.success(f"🔄 **Radio Interior:** {format_value(radio_interior, unidad)}") 
        st.info(f"🛑 **Ala Mínima:** {format_value(ala_minima, unidad)}")

    # --- 5. ALERTAS ---
    if ala_deseada < ala_minima:
        st.error(f"⚠️ **¡CUIDADO!** El ala de {format_value(ala_deseada, unidad)} es muy corta para la matriz de {format_value(v_real, unidad)}.")
