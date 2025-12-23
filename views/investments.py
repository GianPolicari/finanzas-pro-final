"""
Investments View - Investment Tracking
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
    
    st.title("📈 Inversiones")
    st.markdown("---")
    
    # ============================================
    # INVESTMENT FORM
    # ============================================
    
    st.markdown("### 📝 Registrar Inversión")
    
    # Type selector
    investment_type = st.radio(
        "Tipo de Operación",
        options=["💸 Gasto (Compra)", "💵 Ingreso (Venta/Rendimiento)"],
        horizontal=True
    )
    
    trans_type = "Debit" if investment_type.startswith("💸") else "Income"
    
    with st.form("investment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date
            investment_date = st.date_input(
                "📅 Fecha de la Operación",
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
            if trans_type == "Debit":
                category_options = [
                    "Acciones",
                    "Bonos",
                    "Fondos Comunes",
                    "Plazo Fijo",
                    "Criptomonedas",
                    "Dólar (Compra)",
                    "Otro"
                ]
            else:
                category_options = [
                    "Venta de Acciones",
                    "Venta de Bonos",
                    "Rescate de Fondos",
                    "Vencimiento Plazo Fijo",
                    "Venta de Cripto",
                    "Dólar (Venta)",
                    "Dividendos",
                    "Intereses",
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
                    placeholder="ej: Oro, Commodities"
                )
            
            # Description
            description = st.text_area(
                "📋 Descripción (opcional)",
                placeholder="Detalles de la inversión (ticker, cantidad, etc.)...",
                height=100
            )
        
        # Submit button
        submitted = st.form_submit_button(
            "✅ Guardar Operación", 
            use_container_width=True, 
            type="primary"
        )
        
        if submitted:
            # Validate
            if not category or category == "Otro":
                st.error("⚠️ Por favor selecciona o especifica una categoría")
                return
            
            # Save transaction
            with st.spinner("Guardando..."):
                success = save_cash_transaction(
                    user_id=user_id,
                    trans_type=trans_type,
                    date=datetime.combine(investment_date, datetime.min.time()),
                    amount=amount,
                    category=category,
                    description=description
                )
            
            if success:
                operation = "gasto" if trans_type == "Debit" else "ingreso"
                st.success(f"✅ Inversión registrada como {operation} de ${amount:,.2f}!")
    
    st.markdown("---")
    
    # ============================================
    # INFO SECTION
    # ============================================
    
    st.markdown("### 💡 Gestión de Inversiones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **💸 Compras (Gastos)**
        
        Registra aquí cuando inviertes dinero:
        - Compra de acciones
        - Compra de bonos
        - Suscripción a fondos
        - Compra de dólares
        - Apertura de plazo fijo
        
        Esto aparecerá como un GASTO en tu dashboard.
        """)
    
    with col2:
        st.success("""
        **💵 Ventas/Rendimientos (Ingresos)**
        
        Registra aquí cuando recuperas o ganas dinero:
        - Venta de activos
        - Vencimiento de inversiones
        - Dividendos
        - Intereses
        - Rendimientos
        
        Esto aparecerá como un INGRESO en tu dashboard.
        """)
    
    st.markdown("---")
    
    with st.expander("📊 Ejemplo: Flujo de una Inversión"):
        st.markdown("""
        **Caso: Compra y Venta de Acciones**
        
        1. **Enero:** Compras acciones por $10,000
           - Registrar: Tipo = Gasto, Categoría = Acciones, Monto = $10,000
           - Dashboard Enero: -$10,000 (gasto)
        
        2. **Marzo:** Vendes las acciones por $12,000
           - Registrar: Tipo = Ingreso, Categoría = Venta de Acciones, Monto = $12,000
           - Dashboard Marzo: +$12,000 (ingreso)
        
        **Resultado:** Ganancia neta de $2,000 distribuida entre los meses correspondientes.
        """)
    
    st.markdown("---")
    st.caption("📈 Tip: Usa la descripción para anotar tickers, cantidades o tasas de retorno")

if __name__ == "__main__":
    main()
