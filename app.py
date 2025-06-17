import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
load_dotenv()

from database import initialize_database, get_asado_service

# Configuración de la página
st.set_page_config(
    page_title="AsadoApp",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar base de datos
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = initialize_database()
    if not st.session_state.db_initialized:
        st.error("Error al conectar con la base de datos")
        st.stop()

# Inicializar session state
if 'current_asado' not in st.session_state:
    st.session_state.current_asado = None

# Categorías predefinidas para asados argentinos
DEFAULT_CATEGORIES = [
    "Carne", "Achuras", "Chorizo", "Morcilla", "Pollo",
    "Bebidas", "Vino", "Cerveza", "Gaseosas", "Agua",
    "Carbón", "Leña", "Encendedor",
    "Verduras", "Ensalada", "Tomate", "Lechuga", "Cebolla",
    "Condimentos", "Sal", "Chimichurri", "Salsa criolla",
    "Pan", "Postre", "Helado", "Fruta",
    "Varios", "Hielo", "Servilletas", "Platos", "Vasos"
]

def get_all_categories():
    """Obtener todas las categorías disponibles"""
    service = get_asado_service()
    if service:
        custom_categories = service.get_custom_categories()
        all_categories = list(DEFAULT_CATEGORIES) + list(custom_categories)
        return sorted(all_categories)
    return sorted(list(DEFAULT_CATEGORIES))

def create_asado(name):
    """Crear un nuevo asado"""
    service = get_asado_service()
    if service:
        asado = service.create_asado(name)
        return asado is not None
    return False

def get_current_asado_data():
    """Obtener datos del asado actual"""
    if not st.session_state.current_asado:
        return None
    
    service = get_asado_service()
    if service:
        participants = service.get_participants(st.session_state.current_asado)
        expenses = service.get_expenses(st.session_state.current_asado)
        return {
            'participants': participants,
            'expenses': expenses
        }
    return None

def add_participant(name):
    """Agregar un nuevo participante al asado actual"""
    if not st.session_state.current_asado:
        return False
    
    service = get_asado_service()
    if service:
        participant = service.add_participant(st.session_state.current_asado, name)
        return participant is not None
    return False

def add_expense(participant, category, amount, description=""):
    """Agregar un nuevo gasto al asado actual"""
    if not st.session_state.current_asado:
        return False
    
    service = get_asado_service()
    if service:
        expense = service.add_expense(st.session_state.current_asado, participant, category, amount, description)
        return expense is not None
    return False

def calculate_totals():
    """Calcular totales y división de gastos del asado actual"""
    asado_data = get_current_asado_data()
    if not asado_data or not asado_data['expenses'] or not asado_data['participants']:
        return None
    
    df = pd.DataFrame(asado_data['expenses'])
    
    # Total general
    total_general = df['amount'].sum()
    
    # Total por participante
    total_by_participant = df.groupby('participant')['amount'].sum()
    
    # Total por categoría
    total_by_category = df.groupby('category')['amount'].sum()
    
    # Cantidad a pagar por persona
    num_participants = len(asado_data['participants'])
    amount_per_person = total_general / num_participants if num_participants > 0 else 0
    
    # Calcular balance (cuánto pagó cada uno vs cuánto debe pagar)
    balance = {}
    for participant in asado_data['participants']:
        paid = float(total_by_participant.get(participant, 0))
        should_pay = float(amount_per_person)
        balance[participant] = paid - should_pay
    
    return {
        'total_general': total_general,
        'total_by_participant': total_by_participant,
        'total_by_category': total_by_category,
        'amount_per_person': amount_per_person,
        'balance': balance,
        'df': df
    }

def format_currency(amount):
    """Formatear cantidad como moneda argentina"""
    return f"${amount:,.2f}"

def main():
    st.title("🥩 AsadoApp")
    st.markdown("### Organizador de gastos para asados")
    
    # Selector de asado actual
    st.sidebar.title("Gestión de Asados")
    
    # Crear nuevo asado
    with st.sidebar.expander("Crear Nuevo Asado"):
        # Usar un contador para crear claves únicas y reiniciar el formulario
        if 'asado_counter' not in st.session_state:
            st.session_state.asado_counter = 0
            
        new_asado_name = st.text_input("Nombre del asado:", key=f"new_asado_{st.session_state.asado_counter}")
        if st.button("Crear Asado"):
            if new_asado_name:
                if create_asado(new_asado_name):
                    st.session_state.current_asado = new_asado_name
                    st.success(f"Asado '{new_asado_name}' creado!")
                    # Incrementar contador para reiniciar el campo
                    st.session_state.asado_counter += 1
                    st.rerun()
                else:
                    st.error("Ya existe un asado con ese nombre")
            else:
                st.error("Ingresa un nombre para el asado")
    
    # Seleccionar asado actual
    service = get_asado_service()
    if service:
        try:
            asados = service.get_all_asados()
            if asados:
                asado_options = [asado.name for asado in asados]
                current_index = 0
                if st.session_state.current_asado and st.session_state.current_asado in asado_options:
                    current_index = asado_options.index(st.session_state.current_asado)
                
                selected_asado = st.sidebar.selectbox(
                    "Asado actual:",
                    asado_options,
                    index=current_index,
                    key="asado_selector"
                )
                
                if selected_asado != st.session_state.current_asado:
                    st.session_state.current_asado = selected_asado
                    st.rerun()
            else:
                st.sidebar.info("No hay asados creados")
                st.warning("Primero debes crear un asado para comenzar")
                return
        except Exception as e:
            st.sidebar.error("Error conectando con la base de datos")
            st.error("No se puede conectar con la base de datos. Por favor, recarga la página.")
            return
    
    # Mostrar información del asado actual
    if st.session_state.current_asado:
        asado_data = get_current_asado_data()
        if asado_data:
            st.sidebar.markdown(f"**Asado:** {st.session_state.current_asado}")
            st.sidebar.markdown(f"**Participantes:** {len(asado_data['participants'])}")
            st.sidebar.markdown(f"**Gastos:** {len(asado_data['expenses'])}")
    
    # Sidebar para navegación
    st.sidebar.title("Navegación")
    page = st.sidebar.selectbox(
        "Seleccionar página:",
        ["Participantes", "Gastos", "Resumen", "Configuración"]
    )
    
    if page == "Participantes":
        show_participants_page()
    elif page == "Gastos":
        show_expenses_page()
    elif page == "Resumen":
        show_summary_page()
    elif page == "Configuración":
        show_settings_page()

def show_participants_page():
    st.header("👥 Gestión de Participantes")
    
    if not st.session_state.current_asado:
        st.warning("Selecciona un asado para gestionar participantes")
        return
    
    asado_data = get_current_asado_data()
    if not asado_data:
        st.error("Error al obtener datos del asado")
        return
    
    # Agregar nuevo participante
    st.subheader("Agregar Participante")
    
    # Usar un contador para crear claves únicas y reiniciar el formulario
    if 'participant_counter' not in st.session_state:
        st.session_state.participant_counter = 0
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_participant = st.text_input("Nombre del participante:", key=f"new_participant_{st.session_state.participant_counter}")
    
    with col2:
        if st.button("Agregar", type="primary"):
            if new_participant:
                if add_participant(new_participant):
                    st.success(f"Participante '{new_participant}' agregado!")
                    # Incrementar contador para reiniciar el campo
                    st.session_state.participant_counter += 1
                    st.rerun()
                else:
                    st.error("El participante ya existe o el nombre está vacío")
            else:
                st.error("Por favor ingresa un nombre")
    
    # Mostrar participantes actuales
    st.subheader("Participantes Actuales")
    if asado_data['participants']:
        for i, participant in enumerate(asado_data['participants']):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {participant}")
            with col2:
                if st.button("Eliminar", key=f"del_participant_{i}"):
                    service = get_asado_service()
                    if service:
                        service.remove_participant(st.session_state.current_asado, participant)
                        st.rerun()
    else:
        st.info("No hay participantes registrados")
    
    # Estadísticas
    if asado_data['participants']:
        st.subheader("Estadísticas")
        st.metric("Total de participantes", len(asado_data['participants']))

def show_expenses_page():
    st.header("💰 Gestión de Gastos")
    
    if not st.session_state.current_asado:
        st.warning("Selecciona un asado para gestionar gastos")
        return
    
    asado_data = get_current_asado_data()
    if not asado_data:
        st.error("Error al obtener datos del asado")
        return
        
    if not asado_data['participants']:
        st.warning("Primero debes agregar participantes en la página de Participantes")
        return
    
    # Agregar nuevo gasto
    st.subheader("Agregar Gasto")
    
    # Usar un contador para crear claves únicas y reiniciar el formulario
    if 'expense_counter' not in st.session_state:
        st.session_state.expense_counter = 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        participant = st.selectbox(
            "Participante que pagó:",
            asado_data['participants'],
            key=f"expense_participant_{st.session_state.expense_counter}"
        )
        
        category = st.selectbox(
            "Categoría:",
            get_all_categories(),
            key=f"expense_category_{st.session_state.expense_counter}"
        )
    
    with col2:
        amount = st.number_input(
            "Monto ($):",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key=f"expense_amount_{st.session_state.expense_counter}"
        )
        
        description = st.text_input(
            "Descripción (opcional):",
            key=f"expense_description_{st.session_state.expense_counter}"
        )
    
    if st.button("Agregar Gasto", type="primary"):
        if amount > 0:
            add_expense(participant, category, amount, description)
            st.success(f"Gasto agregado: {format_currency(amount)} - {category}")
            # Incrementar contador para reiniciar el formulario
            st.session_state.expense_counter += 1
            st.rerun()
        else:
            st.error("El monto debe ser mayor a 0")
    
    # Mostrar gastos actuales
    st.subheader("Gastos Registrados")
    if asado_data['expenses']:
        df = pd.DataFrame(asado_data['expenses'])
        df['amount_formatted'] = df['amount'].apply(format_currency)
        df['timestamp_formatted'] = df['timestamp'].dt.strftime("%d/%m/%Y %H:%M")
        
        # Tabla de gastos
        display_df = df[['participant', 'category', 'amount_formatted', 'description', 'timestamp_formatted']]
        display_df.columns = ['Participante', 'Categoría', 'Monto', 'Descripción', 'Fecha/Hora']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Opción para eliminar gastos
        with st.expander("Eliminar Gastos"):
            for i, expense in enumerate(asado_data['expenses']):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{expense['participant']} - {expense['category']} - {format_currency(expense['amount'])}")
                with col2:
                    if st.button("Eliminar", key=f"del_expense_{i}"):
                        service = get_asado_service()
                        if service:
                            service.remove_expense(expense['id'])
                            st.rerun()
    else:
        st.info("No hay gastos registrados")

def show_summary_page():
    st.header("📊 Resumen de Gastos")
    
    if not st.session_state.current_asado:
        st.warning("Selecciona un asado para ver el resumen")
        return
    
    asado_data = get_current_asado_data()
    if not asado_data:
        st.error("Error al obtener datos del asado")
        return
    
    if not asado_data['expenses']:
        st.warning("No hay gastos registrados para mostrar")
        return
    
    # Calcular totales
    totals = calculate_totals()
    if not totals:
        st.error("Error al calcular totales")
        return
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total General", format_currency(totals['total_general']))
    
    with col2:
        st.metric("Por Persona", format_currency(totals['amount_per_person']))
    
    with col3:
        st.metric("Participantes", len(asado_data['participants']))
    
    # Gráfico de gastos por categoría
    st.subheader("Gastos por Categoría")
    if len(totals['total_by_category']) > 0:
        fig_category = px.pie(
            values=totals['total_by_category'].values,
            names=totals['total_by_category'].index,
            title="Distribución de Gastos por Categoría"
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    # Gráfico de gastos por participante
    st.subheader("Gastos por Participante")
    if len(totals['total_by_participant']) > 0:
        fig_participant = px.bar(
            x=totals['total_by_participant'].index,
            y=totals['total_by_participant'].values,
            title="Gastos Pagados por Participante",
            labels={'x': 'Participante', 'y': 'Monto ($)'}
        )
        st.plotly_chart(fig_participant, use_container_width=True)
    
    # Balance de pagos
    st.subheader("Balance de Pagos")
    st.write("Resumen de pagos y transferencias necesarias:")
    
    # Mostrar balance general
    balance_data = []
    deudores = []
    acreedores = []
    
    for participant, balance in totals['balance'].items():
        if balance > 0.01:  # Debe recibir (acreedor)
            status = "Debe recibir"
            acreedores.append((participant, balance))
        elif balance < -0.01:  # Debe pagar (deudor)
            status = "Debe pagar"
            deudores.append((participant, abs(balance)))
        else:  # Está al día
            status = "Está al día"
        
        balance_data.append({
            'Participante': participant,
            'Balance': format_currency(abs(balance)),
            'Estado': status
        })
    
    balance_df = pd.DataFrame(balance_data)
    st.dataframe(balance_df, use_container_width=True)
    
    # Calcular transferencias específicas
    if deudores and acreedores:
        st.subheader("💰 Transferencias Necesarias")
        st.write("Quién le debe pagar a quién:")
        
        # Ordenar por montos (mayor a menor)
        deudores.sort(key=lambda x: x[1], reverse=True)
        acreedores.sort(key=lambda x: x[1], reverse=True)
        
        transferencias = []
        deudores_copy = deudores.copy()
        acreedores_copy = acreedores.copy()
        
        while deudores_copy and acreedores_copy:
            deudor_name, deuda = deudores_copy[0]
            acreedor_name, credito = acreedores_copy[0]
            
            # El monto a transferir es el menor entre la deuda y el crédito
            monto_transferencia = min(deuda, credito)
            
            transferencias.append({
                'De': deudor_name,
                'Para': acreedor_name,
                'Monto': format_currency(monto_transferencia)
            })
            
            # Actualizar los montos
            deudores_copy[0] = (deudor_name, deuda - monto_transferencia)
            acreedores_copy[0] = (acreedor_name, credito - monto_transferencia)
            
            # Remover si ya no deben nada
            if deudores_copy[0][1] <= 0.01:
                deudores_copy.pop(0)
            if acreedores_copy[0][1] <= 0.01:
                acreedores_copy.pop(0)
        
        if transferencias:
            transferencias_df = pd.DataFrame(transferencias)
            st.dataframe(transferencias_df, use_container_width=True)
            
            # Mostrar resumen en formato más legible
            st.write("**Instrucciones de pago:**")
            for i, transfer in enumerate(transferencias, 1):
                st.write(f"{i}. **{transfer['De']}** debe pagar **{transfer['Monto']}** a **{transfer['Para']}**")
        else:
            st.info("No hay transferencias necesarias, todos están al día")
    else:
        st.info("No hay transferencias necesarias, todos están al día")
    
    # Resumen detallado por categoría
    st.subheader("Detalle por Categoría")
    category_summary = totals['df'].groupby('category').agg({
        'amount': ['sum', 'count', 'mean']
    }).round(2)
    category_summary.columns = ['Total', 'Cantidad', 'Promedio']
    category_summary['Total'] = category_summary['Total'].apply(format_currency)
    category_summary['Promedio'] = category_summary['Promedio'].apply(format_currency)
    
    st.dataframe(category_summary, use_container_width=True)

def show_settings_page():
    st.header("⚙️ Configuración")
    
    # Gestión de asados
    st.subheader("Gestión de Asados")
    
    service = get_asado_service()
    if service:
        try:
            asados = service.get_all_asados()
            if asados:
                st.write("Asados creados:")
                for asado in asados:
                    try:
                        asado_data = {
                            'participants': service.get_participants(str(asado.name)),
                            'expenses': service.get_expenses(str(asado.name))
                        }
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(f"• **{str(asado.name)}**")
                        with col2:
                            st.write(f"Participantes: {len(asado_data['participants'])}, Gastos: {len(asado_data['expenses'])}")
                        with col3:
                            if st.button("Eliminar", key=f"del_asado_{str(asado.name)}"):
                                service.delete_asado(str(asado.name))
                                if st.session_state.current_asado == str(asado.name):
                                    st.session_state.current_asado = None
                                st.rerun()
                    except Exception as e:
                        st.write(f"• **{str(asado.name)}** (Error cargando datos)")
            else:
                st.info("No hay asados creados")
        except Exception as e:
            st.error("Error conectando con la base de datos. Intenta recargar la página.")
    
    # Agregar categorías personalizadas
    st.subheader("Categorías Personalizadas")
    
    # Usar un contador para crear claves únicas y reiniciar el formulario
    if 'category_counter' not in st.session_state:
        st.session_state.category_counter = 0
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_category = st.text_input("Nueva categoría:", key=f"new_category_{st.session_state.category_counter}")
    
    with col2:
        if st.button("Agregar Categoría"):
            if new_category and new_category not in get_all_categories():
                service = get_asado_service()
                if service:
                    service.add_custom_category(new_category)
                    st.success(f"Categoría '{new_category}' agregada!")
                    # Incrementar contador para reiniciar el campo
                    st.session_state.category_counter += 1
                    st.rerun()
            else:
                st.error("La categoría ya existe o está vacía")
    
    # Mostrar categorías personalizadas
    service = get_asado_service()
    if service:
        custom_categories = service.get_custom_categories()
        if custom_categories:
            st.write("Categorías personalizadas:")
            for i, category in enumerate(custom_categories):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {category}")
                with col2:
                    if st.button("Eliminar", key=f"del_category_{i}"):
                        service.remove_custom_category(str(category))
                        st.rerun()
    
    # Exportar/Importar datos
    st.subheader("Gestión de Datos")
    
    # Exportar datos del asado actual
    if st.session_state.current_asado:
        asado_data = get_current_asado_data()
        if st.button("Exportar Datos del Asado Actual"):
            if asado_data and asado_data['expenses']:
                df = pd.DataFrame(asado_data['expenses'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name=f"asado_{st.session_state.current_asado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No hay datos para exportar en este asado")
    
    # Limpiar datos
    st.subheader("Reiniciar Aplicación")
    st.warning("Esta acción eliminará todos los asados y datos registrados")
    
    if st.button("Limpiar Todo", type="secondary"):
        if st.button("Confirmar Limpieza", type="primary"):
            service = get_asado_service()
            if service:
                # Eliminar todos los asados (esto eliminará en cascada participantes y gastos)
                asados = service.get_all_asados()
                for asado in asados:
                    service.delete_asado(str(asado.name))
                
                # Eliminar categorías personalizadas
                custom_categories = service.get_custom_categories()
                for category in custom_categories:
                    service.remove_custom_category(str(category))
                
                st.session_state.current_asado = None
                st.success("Todos los datos han sido eliminados")
                st.rerun()

if __name__ == "__main__":
    main()
