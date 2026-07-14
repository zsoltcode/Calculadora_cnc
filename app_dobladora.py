import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# NUEVA VERSIÓN: AMADA CNC (Calculo Ideal de Matrices)
# ==========================================

# Funciones de conversión
def inches_to_mm(inches):
    return inches * 25.4

def mm_to_inches(mm):
    return mm / 25.4

# Funciones de cálculo mejoradas
def calcular_tonelaje(espesor, v_real, longitud_doblez, factor_fuerza):
    """Calcula el tonelaje correctamente"""
    if v_real == 0:
        return 0
    # Fórmula más precisa: (575 * t^2) / V * L * factor
    tonelaje = ((575 * (espesor ** 2)) / v_real) * longitud_doblez * factor_fuerza
    return tonelaje

def calcular_ala_minima(v_real, material):
    """Calcula ala mínima según material"""
    factores = {
        "Acero Estándar (Cold Rolled)": 0.7,
        "Acero Inoxidable": 0.8,
        "Aluminio": 0.6
    }
    factor = factores.get(material, 0.7)
    return v_real * factor

def calcular_radio_interior(v_real):
    """Calcula radio interior"""
    return v_real / 6

def calcular_deduccion(espesor, material):
    """Calcula deducción según material"""
    factores = {
        "Acero Estándar (Cold Rolled)": 1.5,
        "Acero Inoxidable": 1.8,
        "Aluminio": 1.2
    }
    factor = factores.get(material, 1.5)
    return espesor * factor

def calcular_angulo_programado(grados, material):
    """Calcula ángulo programado con retorno elástico"""
    retornos = {
        "Acero Estándar (Cold Rolled)": 1.5,
        "Acero Inoxidable": 3.0,
        "Aluminio": 1.0
    }
    retorno = retornos.get(material, 1.5)
    return grados - retorno

# Configuración inicial
st.set_page_config(page_title="Amada CNC Calculator", layout="wide")
st.title("🚀 Calculadora Amada CNC Pro")
st.write("Calculadora avanzada para doblado CNC con cálculo automático de matrices")

# Selector de unidad
unidad = st.radio("Selecciona la unidad:", ("Pulgadas", "Milímetros"), horizontal=True)

# Convertir valores a pulgadas para cálculos internos
def convert_to_inches(value, unit):
    if unit == "Milímetros":
        return mm_to_inches(value)
    return value

def convert_from_inches(value, unit):
    if unit == "Milímetros":
        return inches_to_mm(value)
    return value

def format_value(value, unit):
    if unit == "Milímetros":
        return f"{value:.2f} mm"
    return f"{value:.3f}\""

# Panel de configuración
st.header("🔧 Configuración de Parámetros")

# Panel de datos del material
st.header("1. Datos del Material")
material = st.selectbox("Tipo de Material:", ["Acero Estándar (Cold Rolled)", "Acero Inoxidable", "Aluminio"])

col_input1, col_input2 = st.columns(2)
with col_input1:
    espesor_input = st.number_input(
        "Espesor:",
        min_value=0.010 if unidad == "Pulgadas" else 0.1,
        value=0.060 if unidad == "Pulgadas" else 1.52,
        step=0.001 if unidad == "Pulgadas" else 0.1,
        format="%.3f" if unidad == "Pulgadas" else "%.2f"
    )
    espesor = convert_to_inches(espesor_input, unidad)
with col_input2:
    longitud_doblez_input = st.number_input(
        "Longitud a doblar:",
        min_value=0.1 if unidad == "Pulgadas" else 1.0,
        value=12.0 if unidad == "Pulgadas" else 304.8,
        step=0.1 if unidad == "Pulgadas" else 1.0,
        format="%.1f" if unidad == "Pulgadas" else "%.1f"
    )
    longitud_doblez = convert_to_inches(longitud_doblez_input, unidad)

# Panel de datos de la pieza
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

# Panel de cálculo de matrices
st.header("3. Cálculo de Matrices")
st.info("La matriz ideal se calcula automáticamente según el espesor ingresado")

# Cálculo de matrices basado en el espesor
# Regla clásica: V = 8 veces el espesor
apertura_v_ideal = espesor * 8

# Mostrar cálculo de matrices
col_matrix1, col_matrix2, col_matrix3 = st.columns(3)

with col_matrix1:
    st.metric("V Ideal", f"{apertura_v_ideal:.3f}\"")
    st.info("8 veces el espesor (regla clásica)")

with col_matrix2:
    # Encontrar la matriz más cercana disponible (usando rangos comunes)
    matrices_disponibles = [0.157, 0.236, 0.315, 0.394, 0.472, 0.630]  # pulgadas
    v_mas_cercana = min(matrices_disponibles, key=lambda x: abs(x - apertura_v_ideal))
    st.metric("V Más Cercana", f"{v_mas_cercana:.3f}\"")
    st.info("Matriz disponible más cercana")

with col_matrix3:
    # Mostrar recomendación basada en el espesor
    if apertura_v_ideal < 0.157:
        recomendacion = "Usar V = 0.157\" (mínima disponible)"
    elif apertura_v_ideal > 0.630:
        recomendacion = "Usar V = 0.630\" (máxima disponible)"
    else:
        recomendacion = f"Usar V = {v_mas_cercana:.3f}\""
    
    st.metric("Recomendación", recomendacion)
    st.info("Matriz recomendada para tu espesor")

# Panel de tonelaje
st.header("4. Cálculo de Tonelaje")
col_ton1, col_ton2 = st.columns(2)

with col_ton1:
    st.subheader("📊 Tonelaje Estimado")
    
    # Factores de material
    factores_material = {
        "Acero Estándar (Cold Rolled)": 1.0,
        "Acero Inoxidable": 1.5,
        "Aluminio": 0.5
    }
    
    factor_fuerza = factores_material[material]
    
    # Cálculo de tonelaje con la matriz recomendada
    tonelaje_recomendado = calcular_tonelaje(espesor, v_mas_cercana, longitud_doblez, factor_fuerza)
    st.metric("Tonelaje Recomendado", f"{tonelaje_recomendado:.1f} US Tons")
    
    # Alertas de tonelaje
    if tonelaje_recomendado > 150:
        st.error("⚠️ ¡ATENCIÓN! Tonelaje muy alto, puede sobrecargar la máquina")
    elif tonelaje_recomendado > 100:
        st.warning("⚠️ Tonelaje alto, revisar condiciones de trabajo")

with col_ton2:
    st.subheader("📋 Información Técnica")
    
    # Mostrar información sobre matrices
    st.write("**Matrices Disponibles (pulgadas):**")
    st.write("- 0.157\" (4mm)")
    st.write("- 0.236\" (6mm)") 
    st.write("- 0.315\" (8mm)")
    st.write("- 0.394\" (10mm)")
    st.write("- 0.472\" (12mm)")
    st.write("- 0.630\" (16mm)")
    
    st.write(f"**Escala recomendada:** V = 8 × Espesor = {apertura_v_ideal:.3f}\"")

# Panel de parámetros adicionales
st.header("5. Parámetros Adicionales")
col_params1, col_params2 = st.columns(2)

with col_params1:
    st.subheader("📏 Dimensiones")
    
    deduccion = calcular_deduccion(espesor, material)
    ala_minima = calcular_ala_minima(v_mas_cercana, material)
    radio_interior = calcular_radio_interior(v_mas_cercana)
    angulo_programado = calcular_angulo_programado(grados, material)
    
    st.metric("Deducción", f"{deduccion:.3f}\"")
    st.metric("Ala Mínima", f"{ala_minima:.3f}\"")
    st.metric("Radio Interior", f"{radio_interior:.3f}\"")
    st.metric("Ángulo Programado", f"{angulo_programado:.1f}°")

with col_params2:
    st.subheader("🔍 Análisis")
    
    # Análisis de la recomendación
    diferencia = abs(apertura_v_ideal - v_mas_cercana)
    if diferencia < 0.01:
        st.success("✅ Matriz recomendada muy cercana al ideal")
    elif diferencia < 0.05:
        st.warning("⚠️ Matriz recomendada con ligera diferencia")
    else:
        st.error("❌ Matriz recomendada con diferencia considerable")
    
    # Información sobre el espesor
    st.info(f"Espesor: {espesor_input} {unidad}")
    st.info(f"Longitud doblada: {longitud_doblez_input} {unidad}")

# Panel de cálculo de material con costillas
st.header("6. Cálculo de Material con Costillas")
col_mat1, col_mat2 = st.columns(2)

with col_mat1:
    st.subheader("📋 Costillas")
    # Opciones para costillas
    tiene_costillas = st.checkbox("¿La pieza tiene costillas?")
    
    if tiene_costillas:
        num_costillas = st.number_input("Número de costillas", min_value=0, value=0)
        costillas = []
        
        for i in range(num_costillas):
            st.write(f"Costilla {i+1}")
            tipo = st.selectbox(f"Tipo de costilla {i+1}", ["V", "Media Luna"], key=f"tipo_{i}")
            longitud = st.number_input(f"Longitud de costilla {i+1}", 
                                    min_value=0.1, value=1.0, step=0.1, key=f"long_{i}")
            posicion = st.number_input(f"Posición de costilla {i+1}", 
                                    min_value=0.0, value=0.0, step=0.1, key=f"pos_{i}")
            
            costillas.append({
                'tipo': tipo.lower(),
                'longitud': longitud,
                'posicion': posicion
            })

with col_mat2:
    st.subheader("📊 Cálculo de Material")
    
    # Entradas para cálculo de material
    longitud_original = st.number_input("Longitud original (pulgadas)", min_value=0.1, value=12.0, step=0.1)
    ancho_original = st.number_input("Ancho original (pulgadas)", min_value=0.1, value=8.0, step=0.1)
    
    # Cálculo de material
    if tiene_costillas and costillas:
        # Simulación simple de cálculo con costillas
        material_con_costillas = longitud_original * ancho_original * espesor
        # Añadir material adicional por costillas (aproximación simple)
        material_adicional = sum(c['longitud'] * 0.1 * espesor for c in costillas)
        material_total = material_con_costillas + material_adicional
        st.metric("Material con Costillas", f"{material_total:.2f} pulg³")
    else:
        material_base = longitud_original * ancho_original * espesor
        st.metric("Material Base", f"{material_base:.2f} pulg³")
    
    # Desperdicio
    desperdicio = st.slider("Porcentaje de desperdicio (%)", 0, 20, 10)
    material_con_desperdicio = material_base * (1 + desperdicio/100)
    st.metric("Material con Desperdicio", f"{material_con_desperdicio:.2f} pulg³")

# Botón de cálculo
if st.button("Calcular Parámetros de Máquina", type="primary"):
    
    # --- 1. PROPIEDADES DEL MATERIAL ---
    if material == "Acero Estándar (Cold Rolled)":
        factor_fuerza = 1.0; retorno_elastico = 1.5  
    elif material == "Acero Inoxidable":
        factor_fuerza = 1.5; retorno_elastico = 3.0  
    else: 
        factor_fuerza = 0.5; retorno_elastico = 1.0  
        
    # --- 2. CÁLCULO DE MATRICES ---
    # Regla clásica: V = 8 veces el espesor
    apertura_v_ideal = espesor * 8
    
    # Matriz recomendada (más cercana a la ideal)
    matrices_comunes = [0.157, 0.236, 0.315, 0.394, 0.472, 0.630]
    v_recomendada = min(matrices_comunes, key=lambda x: abs(x - apertura_v_ideal))
        
    # --- 3. MATEMÁTICAS (SISTEMA IMPERIAL) ---
    # Fórmula imperial empírica para US Tons: (575 * t^2) / V * L
    tonelaje_requerido = ((575 * (espesor ** 2)) / v_recomendada) * longitud_doblez * factor_fuerza
    
    # Deducción y radio
    deduccion_simple = espesor * 1.5 
    eje_x = ala_deseada - (deduccion_simple / 2)
    angulo_maquina = grados - retorno_elastico
    ala_minima = v_recomendada * 0.7
    radio_interior = v_recomendada / 6

    # --- 4. MOSTRAR RESULTADOS ---
    st.markdown("---")
    st.subheader("📊 Resultados para Amada CNC")
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.success(f"🔽 **Matriz a usar (V):** {format_value(v_recomendada, unidad)}")
        st.error(f"⚖️ **Tonelaje Estimado:** {tonelaje_requerido:.1f} US Tons")
        st.success(f"📏 **Tope Eje X:** {format_value(eje_x, unidad)}")
        
    with res_col2:
        st.warning(f"📐 **Ángulo a programar:** {angulo_maquina:.1f}°")
        st.success(f"🔄 **Radio Interior:** {format_value(radio_interior, unidad)}") 
        st.info(f"🛑 **Ala Mínima:** {format_value(ala_minima, unidad)}")

    # --- 5. ALERTAS ---
    if ala_deseada < ala_minima:
        st.error(f"⚠️ **¡CUIDADO!** El ala de {format_value(ala_deseada, unidad)} es muy corta para la matriz de {format_value(v_recomendada, unidad)}.")
