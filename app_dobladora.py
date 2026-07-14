import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# NUEVA VERSIÓN: AMADA CNC (Corregida)
# ==========================================

# Funciones de conversión
def inches_to_mm(inches):
    return inches * 25.4

def mm_to_inches(mm):
    return mm / 25.4

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
        # Ahora sí aplicamos la conversión inversa antes de mostrar el dato
        val_mm = convert_from_inches(value, unit)
        return f"{val_mm:.2f} mm"
    return f"{value:.3f}\""

# Funciones de cálculo mejoradas
def calcular_tonelaje(espesor, v_real, longitud_doblez, factor_fuerza):
    """Calcula el tonelaje correctamente"""
    if v_real == 0:
        return 0
    # Corrección matemática: Se debe dividir entre 12 para calcular toneladas por pulgada
    tonelaje = ((575 * (espesor ** 2)) / v_real / 12) * longitud_doblez * factor_fuerza
    return tonelaje

def calcular_ala_minima(v_real, material):
    factores = {
        "Acero Estándar (Cold Rolled)": 0.7,
        "Acero Inoxidable": 0.8,
        "Aluminio": 0.6
    }
    return v_real * factores.get(material, 0.7)

def calcular_radio_interior(v_real):
    return v_real / 6

def calcular_deduccion(espesor, material):
    factores = {
        "Acero Estándar (Cold Rolled)": 1.5,
        "Acero Inoxidable": 1.8,
        "Aluminio": 1.2
    }
    return espesor * factores.get(material, 1.5)

def calcular_angulo_programado(grados, material):
    retornos = {
        "Acero Estándar (Cold Rolled)": 1.5,
        "Acero Inoxidable": 3.0,
        "Aluminio": 1.0
    }
    return grados - retornos.get(material, 1.5)

def calcular_matriz_ideal(espesor):
    return espesor * 8

# Configuración inicial
st.set_page_config(page_title="Amada CNC Calculator", layout="wide")
st.title("🚀 Calculadora Amada CNC Pro")
st.write("Calculadora avanzada para doblado CNC con cálculo automático de matrices")

# Crear pestañas
tab1, tab2 = st.tabs(["📊 Cálculo Principal", "🧮 Desarrollo"])

# PESTAÑA 1: Cálculo Principal
with tab1:
    unidad = st.radio("Selecciona la unidad:", ("Pulgadas", "Milímetros"), horizontal=True)
    
    st.header("🔧 Configuración de Parámetros")
    
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
    
    st.header("3. Cálculo de Matrices")
    st.info("La matriz se calcula automáticamente según el espesor ingresado")
    
    apertura_v_ideal = calcular_matriz_ideal(espesor)
    
    col_matrix1, col_matrix2 = st.columns(2)
    
    with col_matrix1:
        st.metric("V Ideal", format_value(apertura_v_ideal, unidad))
        st.info("8 veces el espesor (regla clásica)")
    
    with col_matrix2:
        if apertura_v_ideal < 0.157:
            recomendacion = f"Usar V = {format_value(0.157, unidad)} (mínima disponible)"
            v_recomendada = 0.157
        elif apertura_v_ideal > 0.630:
            recomendacion = f"Usar V = {format_value(0.630, unidad)} (máxima disponible)"
            v_recomendada = 0.630
        else:
            recomendacion = f"Usar V ≈ {format_value(apertura_v_ideal, unidad)}"
            v_recomendada = apertura_v_ideal
        
        st.metric("Recomendación", recomendacion)
        st.info("Matriz recomendada para tu espesor")
    
    st.header("4. Cálculo de Tonelaje")
    col_ton1, col_ton2 = st.columns(2)
    
    with col_ton1:
        st.subheader("📊 Tonelaje Estimado")
        
        factores_material = {
            "Acero Estándar (Cold Rolled)": 1.0,
            "Acero Inoxidable": 1.5,
            "Aluminio": 0.5
        }
        factor_fuerza = factores_material[material]
        
        tonelaje_recomendado = calcular_tonelaje(espesor, v_recomendada, longitud_doblez, factor_fuerza)
        st.metric("Tonelaje Recomendado", f"{tonelaje_recomendado:.1f} US Tons")
        
        if tonelaje_recomendado > 150:
            st.error("⚠️ ¡ATENCIÓN! Tonelaje muy alto, puede sobrecargar la máquina")
        elif tonelaje_recomendado > 100:
            st.warning("⚠️ Tonelaje alto, revisar condiciones de trabajo")
    
    with col_ton2:
        st.subheader("📋 Información Técnica")
        st.write("**Matrices Disponibles (pulgadas/mm):**")
        st.write("- 0.157\" (4mm)")
        st.write("- 0.236\" (6mm)") 
        st.write("- 0.315\" (8mm)")
        st.write("- 0.394\" (10mm)")
        st.write("- 0.472\" (12mm)")
        st.write("- 0.630\" (16mm)")
        
        st.write(f"**Escala recomendada:** V = 8 × Espesor = {format_value(apertura_v_ideal, unidad)}")
    
    st.header("5. Parámetros Adicionales")
    col_params1, col_params2 = st.columns(2)
    
    with col_params1:
        st.subheader("📏 Dimensiones")
        
        deduccion = calcular_deduccion(espesor, material)
        ala_minima = calcular_ala_minima(v_recomendada, material)
        radio_interior = calcular_radio_interior(v_recomendada)
        angulo_programado = calcular_angulo_programado(grados, material)
        
        st.metric("Deducción", format_value(deduccion, unidad))
        st.metric("Ala Mínima", format_value(ala_minima, unidad))
        st.metric("Radio Interior", format_value(radio_interior, unidad))
        st.metric("Ángulo Programado", f"{angulo_programado:.1f}°")
    
    with col_params2:
        st.subheader("🔍 Análisis")
        if 0.157 <= apertura_v_ideal <= 0.630:
            diferencia = abs(apertura_v_ideal - v_recomendada)
            if diferencia < 0.01:
                st.success("✅ Matriz recomendada muy cercana al ideal")
            elif diferencia < 0.05:
                st.warning("⚠️ Matriz recomendada con ligera diferencia")
            else:
                st.error("❌ Matriz recomendada con diferencia considerable")
        else:
            st.info("⚠️ Extremo de rango de matrices")
        
        st.info(f"Espesor: {espesor_input} {unidad}")
        st.info(f"Longitud doblada: {longitud_doblez_input} {unidad}")
    
    if st.button("Calcular Parámetros de Máquina", type="primary"):
        
        # Aprovechamos las funciones estructuradas para el cálculo final
        tonelaje_requerido = calcular_tonelaje(espesor, v_recomendada, longitud_doblez, factor_fuerza)
        
        deduccion_real = calcular_deduccion(espesor, material)
        eje_x = ala_deseada - (deduccion_real / 2)
        
        angulo_maquina = calcular_angulo_programado(grados, material)
        ala_minima_req = calcular_ala_minima(v_recomendada, material)
        radio_interior_req = calcular_radio_interior(v_recomendada)
    
        st.markdown("---")
        st.subheader("📊 Resultados para Amada CNC")
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.success(f"🔽 **Matriz a usar (V):** {format_value(v_recomendada, unidad)}")
            st.error(f"⚖️ **Tonelaje Estimado:** {tonelaje_requerido:.1f} US Tons")
            st.success(f"📏 **Tope Eje X:** {format_value(eje_x, unidad)}")
            
        with res_col2:
            st.warning(f"📐 **Ángulo a programar:** {angulo_maquina:.1f}°")
            st.success(f"🔄 **Radio Interior:** {format_value(radio_interior_req, unidad)}") 
            st.info(f"🛑 **Ala Mínima:** {format_value(ala_minima_req, unidad)}")
    
        if ala_deseada < ala_minima_req:
            st.error(f"⚠️ **¡CUIDADO!** El ala de {format_value(ala_deseada, unidad)} es muy corta para la matriz de {format_value(v_recomendada, unidad)}.")

# PESTAÑA 2: Desarrollo
with tab2:
    st.header("🧮 Desarrollo de Cálculo de Material")
    st.write("Esta sección permite calcular el material necesario para piezas con características especiales (Unidades operan base Pulgadas).")
    
    st.subheader("📋 Cálculo de Material con Costillas")
    col_mat1, col_mat2 = st.columns(2)
    
    with col_mat1:
        st.write("### Parámetros de la Pieza Base")
        longitud_original = st.number_input("Longitud original (pulgadas)", min_value=0.1, value=12.0, step=0.1)
        ancho_original = st.number_input("Ancho original (pulgadas)", min_value=0.1, value=8.0, step=0.1)
        espesor_material = st.number_input("Espesor del material (pulgadas)", min_value=0.01, value=0.060, step=0.001)
        
        tiene_costillas = st.checkbox("¿La pieza tiene costillas?")
        
        if tiene_costillas:
            num_costillas = st.number_input("Número de costillas", min_value=0, value=0)
            costillas = []
            
            for i in range(int(num_costillas)):
                st.write(f"#### Costilla {i+1}")
                tipo = st.selectbox(f"Tipo de costilla {i+1}", ["V", "Media Luna"], key=f"tipo_{i}")
                longitud = st.number_input(f"Longitud de costilla {i+1}", min_value=0.1, value=1.0, step=0.1, key=f"long_{i}")
                posicion = st.number_input(f"Posición de costilla {i+1}", min_value=0.0, value=0.0, step=0.1, key=f"pos_{i}")
                
                costillas.append({'tipo': tipo.lower(), 'longitud': longitud, 'posicion': posicion})
    
    with col_mat2:
        st.write("### Resultados de Cálculo")
        
        material_base = longitud_original * ancho_original * espesor_material
        st.metric("Material Base", f"{material_base:.2f} pulg³")
        
        if tiene_costillas and 'costillas' in locals():
            material_adicional = 0
            for costilla in costillas:
                if costilla['tipo'] == 'v':
                    material_adicional += costilla['longitud'] * 0.1 * espesor_material
                elif costilla['tipo'] == 'media_luna':
                    material_adicional += (costilla['longitud'] * 0.5 * espesor_material) * 0.5
            
            material_total = material_base + material_adicional
            st.metric("Material con Costillas", f"{material_total:.2f} pulg³")
            st.metric("Material Adicional", f"{material_adicional:.2f} pulg³")
        else:
            st.metric("Material Total", f"{material_base:.2f} pulg³")
        
        desperdicio = st.slider("Porcentaje de desperdicio (%)", 0, 20, 10)
        material_con_desperdicio = material_base * (1 + desperdicio/100)
        st.metric("Material con Desperdicio", f"{material_con_desperdicio:.2f} pulg³")
        
        peso_base = material_base * 0.283
        st.metric("Peso Estimado (Acero)", f"{peso_base:.2f} lbs")
        
        area_base = longitud_original * ancho_original
        st.metric("Área Base", f"{area_base:.2f} pulg²")
