"""
Incomes View - Income Entry
Implements Logic A (Immediate payment_date)
"""

import streamlit as st
from datetime import datetime, date
from database import save_cash_transaction

def main():
    st.title("💵 Ingresos")
    st.markdown("---")
    
    # ============================================
    # INCOME FORM
    # ============================================
    
    st.markdown("### 📝 Registrar Ingreso")
    
    with st.form("income_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date
            income_date = st.date_input(
                "📅 Fecha del Ingreso",
                value=date.today()
            )
            
            # Amount
            amount = st.number_input(
                "💰 Monto",
                min_value=0.01,
                value=1000.00,
                step=100.00,
                format="%.2f"
            )
        
        with col2:
            # Category
            category_options = [
                "Salario",
                "Freelance",
                "Inversiones",
                "Venta",
                "Bono",
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
                    placeholder="ej: Reembolso, Regalo"
                )
            
            # Description
            description = st.text_area(
                "📋 Descripción (opcional)",
                placeholder="Detalles del ingreso...",
                height=100
            )
        
        # Submit button
        submitted = st.form_submit_button("✅ Guardar Ingreso", use_container_width=True, type="primary")
        
        if submitted:
            # Validate
            if not category or category == "Otro":
                st.error("⚠️ Por favor selecciona o especifica una categoría")
                return
            
            # Save transaction
            with st.spinner("Guardando..."):
                success = save_cash_transaction(
                    trans_type="Income",
                    date=datetime.combine(income_date, datetime.min.time()),
                    amount=amount,
                    category=category,
                    description=description
                )
            
            if success:
                st.success(f"✅ Ingreso de ${amount:,.2f} guardado exitosamente!")
                st.balloons()
    
    st.markdown("---")
    
    # ============================================
    # INFO SECTION
    # ============================================
    
    st.markdown("### 💡 Gestión de Ingresos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Impacto Inmediato**
        
        Los ingresos se registran con impacto inmediato en el mes seleccionado.
        
        Esto significa que el ingreso aparecerá en tu dashboard del mes correspondiente a la fecha ingresada.
        """)
    
    with col2:
        st.success("""
        **Categorías Sugeridas**
        
        - **Salario**: Ingreso mensual fijo
        - **Freelance**: Trabajos independientes
        - **Inversiones**: Dividendos, intereses
        - **Venta**: Venta de productos/servicios
        - **Bono**: Bonificaciones extraordinarias
        """)
    
    st.markdown("---")
    st.caption("📊 Los ingresos se reflejarán automáticamente en el Dashboard")

if __name__ == "__main__":
    main()
