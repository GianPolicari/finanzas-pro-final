"""
Credit Cards View - Card Transaction Entry
Implements Logic B with installments
"""

import streamlit as st
from datetime import datetime, date
from database import get_all_cards, save_card_transaction

def main():
    # Get authenticated user ID from session state
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("⚠️ Error: No user authenticated")
        return
    
    st.title("💳 Compras con Tarjeta")
    st.markdown("---")
    
    # ============================================
    # LOAD CARDS
    # ============================================
    
    cards = get_all_cards(user_id)
    
    if not cards:
        st.error("⚠️ No hay tarjetas configuradas. Ve a Configuración para agregar tarjetas.")
        return
    
    # ============================================
    # TRANSACTION FORM
    # ============================================
    
    st.markdown("### 📝 Registrar Compra")
    
    with st.form("card_transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Card selection
            card_options = {f"{card['name']} (Cierre: día {card['closing_day']})": card['id'] 
                          for card in cards}
            
            selected_card_display = st.selectbox(
                "💳 Tarjeta",
                options=list(card_options.keys())
            )
            selected_card_id = card_options[selected_card_display]
            
            # Purchase date
            purchase_date = st.date_input(
                "📅 Fecha de Compra",
                value=date.today()
            )
            
            # Amount
            amount = st.number_input(
                "💰 Monto Total",
                min_value=0.01,
                value=100.00,
                step=10.00,
                format="%.2f"
            )
        
        with col2:
            # Category
            category = st.text_input(
                "🏷️ Categoría",
                placeholder="ej: Supermercado, Ropa, Tecnología"
            )
            
            # Installments
            installments = st.number_input(
                "🔢 Cuotas",
                min_value=1,
                max_value=24,
                value=1,
                step=1,
                help="Número de pagos mensuales"
            )
            
            # Description
            description = st.text_area(
                "📋 Descripción (opcional)",
                placeholder="Detalles adicionales...",
                height=100
            )
        
        # Submit button
        submitted = st.form_submit_button("✅ Guardar Compra", use_container_width=True, type="primary")
        
        if submitted:
            # Validate
            if not category:
                st.error("⚠️ Por favor ingresa una categoría")
                return
            
            # Save transaction
            with st.spinner("Guardando..."):
                success, affected_months = save_card_transaction(
                    user_id=user_id,
                    card_id=selected_card_id,
                    date=datetime.combine(purchase_date, datetime.min.time()),
                    amount=amount,
                    category=category,
                    description=description,
                    installments=installments
                )
            
            if success:
                st.success("✅ Compra guardada exitosamente!")
                
                # Show affected months
                if affected_months:
                    months_str = ", ".join(affected_months)
                    st.info(f"💡 **Meses afectados:** {months_str}")
                
                # Show installment details
                if installments > 1:
                    amount_per_installment = amount / installments
                    st.info(f"🔢 **{installments} cuotas** de ${amount_per_installment:,.2f} cada una")
    
    st.markdown("---")
    
    # ============================================
    # INFO SECTION
    # ============================================
    
    st.markdown("### ℹ️ Cómo Funciona")
    
    with st.expander("📖 Leer más sobre el cálculo de fechas de pago"):
        st.markdown("""
        **Sistema de Cálculo Automático (Técnico):**
        
        El sistema utiliza un algoritmo de **Cierre Técnico + Período de Gracia** para calcular con precisión la fecha de pago:
        
        **Paso 1: Determinar el Resumen al que Pertenece**
        - **Si compras ANTES o EN el día de cierre:** La compra va al resumen del mes actual.
        - **Si compras DESPUÉS del día de cierre:** La compra va al resumen del mes siguiente.
        
        **Paso 2: Calcular la Fecha de Cierre Técnico**
        - Se toma el mes del resumen + el día de cierre configurado.
        
        **Paso 3: Agregar Período de Gracia (10 días)**
        - La fecha de pago es 10 días después del cierre técnico.
        
        **Ejemplos Reales:**
        
        **Tarjeta con cierre día 5:**
        - Compra del 3 de Diciembre → Resumen: Diciembre 5 → Pago: **Diciembre 15**
        - Compra del 10 de Diciembre → Resumen: Enero 5 → Pago: **Enero 15**
        
        **Tarjeta con cierre día 28:**
        - Compra del 15 de Diciembre → Resumen: Diciembre 28 → Pago: **Enero 7**
        - Compra del 29 de Diciembre → Resumen: Enero 28 → Pago: **Febrero 7**
        
        **Cuotas:**
        
        Si divides una compra en cuotas, el sistema creará automáticamente los pagos mensuales:
        - Cuota 1 → Fecha calculada según regla de cierre + gracia
        - Cuota 2 → Mes siguiente, mismo día
        - Cuota N → N-1 meses después, mismo día
        
        **IMPORTANTE:** La fecha de pago se calcula al momento de guardar la compra. 
        Cambios posteriores en el día de cierre NO afectan compras ya registradas.
        """)
    
    st.markdown("---")
    st.caption("💡 Tip: Puedes cambiar el día de cierre de tus tarjetas en Configuración")

if __name__ == "__main__":
    main()
