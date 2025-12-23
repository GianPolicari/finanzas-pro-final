"""
Fixed Expenses View - Recurring Fixed Costs
Implements Logic A (Immediate payment_date)
"""

import streamlit as st
from datetime import datetime, date
from database import save_cash_transaction

def main():
    # Get authenticated user ID from session state
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("⚠️ Error: No user authenticated")
        return
    
    st.title("📌 Gastos Fijos")
    st.markdown("---")
    
    # ============================================
    # FIXED EXPENSE FORM
    # ============================================
    
    st.markdown("### 📝 Registrar Gasto Fijo")
    
    with st.form("fixed_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date
            expense_date = st.date_input(
                "📅 Fecha del Pago",
                value=date.today()
            )
            
            # Amount
            amount = st.number_input(
                "💰 Monto",
                min_value=0.01,
                value=100.00,
                step=10.00,
                format="%.2f"
            )
        
        with col2:
            # Category
            category_options = [
                "Alquiler",
                "Expensas",
                "Servicios (Luz/Gas/Agua)",
                "Internet/Cable",
                "Teléfono",
                "Suscripciones",
                "Seguro",
                "Transporte",
                "Otro"
            ]
            
            category = st.selectbox(
                "🏷️ Categoría",
                options=category_options
            )
            
            # Custom category
            if category == "Otro":
                category = st.text_input(
                    "Especificar categoría",
                    placeholder="ej: Gimnasio, Colegio"
                )
            
            # Description
            description = st.text_area(
                "📋 Descripción (opcional)",
                placeholder="Detalles del gasto...",
                height=100
            )
        
        # Submit button
        submitted = st.form_submit_button("✅ Guardar Gasto Fijo", use_container_width=True, type="primary")
        
        if submitted:
            # Validate
            if not category or category == "Otro":
                st.error("⚠️ Por favor selecciona o especifica una categoría")
                return
            
            # Save transaction
            with st.spinner("Guardando..."):
                success = save_cash_transaction(
                    user_id=user_id,
                    trans_type="Fixed",
                    date=datetime.combine(expense_date, datetime.min.time()),
                    amount=amount,
                    category=category,
                    description=description
                )
            
            if success:
                st.success(f"✅ Gasto fijo de ${amount:,.2f} guardado exitosamente!")
    
    st.markdown("---")
    
    # ============================================
    # INFO SECTION
    # ============================================
    
    st.markdown("### 📋 Categorías Comunes de Gastos Fijos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🏠 Vivienda**
        - Alquiler
        - Expensas
        - Servicios básicos
        """)
    
    with col2:
        st.markdown("""
        **📡 Conectividad**
        - Internet
        - Cable/Streaming
        - Teléfono
        """)
    
    with col3:
        st.markdown("""
        **🛡️ Otros**
        - Seguros
        - Suscripciones
        - Transporte
        """)
    
    st.markdown("---")
    
    with st.expander("ℹ️ ¿Qué es un Gasto Fijo?"):
        st.markdown("""
        **Definición:**
        
        Los gastos fijos son aquellos que se repiten mensualmente y tienen un monto predecible.
        
        **Características:**
        - Recurrencia mensual
        - Monto similar cada mes
        - Generalmente no discrecionales (necesarios)
        
        **Ejemplos:**
        - Alquiler/hipoteca
        - Servicios (luz, gas, agua)
        - Internet y teléfono
        - Seguros
        - Suscripciones (Netflix, Spotify, etc.)
        
        **Tip:** Registra estos gastos cuando realizas el pago, no cuando vence la factura.
        """)
    
    st.markdown("---")
    st.caption("💡 Los gastos fijos impactan inmediatamente en el mes registrado")

if __name__ == "__main__":
    main()
