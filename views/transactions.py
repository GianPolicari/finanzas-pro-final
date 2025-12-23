"""
Transaction Management View - View and Delete Transactions
"""

import streamlit as st
from datetime import datetime
from database import get_available_months, get_monthly_transactions, delete_transaction

def main():
    # Get authenticated user ID from session state
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("⚠️ Error: No user authenticated")
        return
    
    st.title("🗂️ Gestión de Transacciones")
    st.markdown("---")
    
    # ============================================
    # MONTH FILTER
    # ============================================
    
    available_months = get_available_months(user_id)
    
    if not available_months:
        st.info("👋 No hay transacciones registradas aún.")
        return
    
    # Create selectbox with month options
    month_options = {display: (year, month) for year, month, display in available_months}
    
    selected_display = st.selectbox(
        "📅 Seleccionar Período",
        options=list(month_options.keys()),
        index=0
    )
    
    selected_year, selected_month = month_options[selected_display]
    
    st.markdown("---")
    
    # ============================================
    # FILTER BY TYPE
    # ============================================
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📋 Transacciones del Mes")
    
    with col2:
        filter_type = st.selectbox(
            "Filtrar por tipo",
            options=["Todas", "Income", "Fixed", "Debit", "Card"],
            index=0
        )
    
    # ============================================
    # FETCH TRANSACTIONS
    # ============================================
    
    # Get transactions
    if filter_type == "Todas":
        transactions = get_monthly_transactions(user_id, selected_year, selected_month)
    else:
        transactions = get_monthly_transactions(user_id, selected_year, selected_month, filter_type)
    
    if not transactions:
        st.info("No hay transacciones para este período con los filtros seleccionados.")
        return
    
    # ============================================
    # DISPLAY TRANSACTIONS WITH DELETE BUTTONS
    # ============================================
    
    st.caption(f"Mostrando {len(transactions)} transacciones")
    
    # Type icons and colors
    type_config = {
        "Income": {"icon": "💵", "color": "green", "label": "Ingreso"},
        "Fixed": {"icon": "📌", "color": "orange", "label": "Gasto Fijo"},
        "Debit": {"icon": "💸", "color": "red", "label": "Débito"},
        "Card": {"icon": "💳", "color": "blue", "label": "Tarjeta"}
    }
    
    for trans in transactions:
        trans_type = trans["type"]
        config = type_config.get(trans_type, {"icon": "❓", "color": "gray", "label": trans_type})
        
        # Create expander for each transaction
        with st.expander(
            f"{config['icon']} {trans['category']} - ${trans['amount']:,.2f} ({trans['date']})",
            expanded=False
        ):
            # Transaction details
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**Tipo:** {config['label']}")
                st.markdown(f"**Categoría:** {trans['category']}")
                st.markdown(f"**Monto:** ${trans['amount']:,.2f}")
            
            with col2:
                st.markdown(f"**Fecha Transacción:** {trans['date']}")
                st.markdown(f"**Fecha Pago:** {trans['payment_date']}")
                
                # Show card info if it's a card transaction
                if trans_type == "Card" and trans.get("credit_cards"):
                    card_name = trans["credit_cards"]["name"]
                    st.markdown(f"**Tarjeta:** {card_name}")
                
                # Show installment info
                if trans.get("installments_total", 1) > 1:
                    st.markdown(
                        f"**Cuota:** {trans['installment_number']}/{trans['installments_total']}"
                    )
            
            with col3:
                st.markdown(f"**ID:** {trans['id']}")
                st.caption(f"Creado: {trans['created_at'][:10]}")
            
            # Description
            if trans.get("description"):
                st.markdown(f"**📝 Descripción:** {trans['description']}")
            
            st.markdown("---")
            
            # Delete button
            col_a, col_b, col_c = st.columns([1, 1, 2])
            
            with col_a:
                if st.button(
                    "🗑️ Eliminar",
                    key=f"delete_{trans['id']}",
                    type="primary",
                    use_container_width=True
                ):
                    # Store the ID to delete in session state
                    st.session_state[f"confirm_delete_{trans['id']}"] = True
                    st.rerun()
            
            # Confirmation step
            if st.session_state.get(f"confirm_delete_{trans['id']}", False):
                with col_b:
                    if st.button(
                        "✅ Confirmar",
                        key=f"confirm_{trans['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        # Perform the deletion
                        success = delete_transaction(user_id, trans['id'])
                        
                        if success:
                            # Clear confirmation state
                            st.session_state[f"confirm_delete_{trans['id']}"] = False
                            # Rerun to refresh the list
                            st.rerun()
                
                with col_c:
                    if st.button(
                        "❌ Cancelar",
                        key=f"cancel_{trans['id']}",
                        use_container_width=True
                    ):
                        # Clear confirmation state
                        st.session_state[f"confirm_delete_{trans['id']}"] = False
                        st.rerun()
                
                st.warning("⚠️ ¿Estás seguro? Esta acción no se puede deshacer.")
    
    st.markdown("---")
    
    # ============================================
    # SUMMARY
    # ============================================
    
    st.markdown("### 📊 Resumen del Período")
    
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
    total_expenses = sum(t['amount'] for t in transactions if t['type'] in ['Fixed', 'Debit', 'Card'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💵 Ingresos", f"${total_income:,.2f}")
    
    with col2:
        st.metric("💸 Gastos", f"${total_expenses:,.2f}")
    
    with col3:
        balance = total_income - total_expenses
        st.metric("💰 Balance", f"${balance:,.2f}", delta=None)
    
    st.caption(f"📅 Período: {selected_display} | Total de registros: {len(transactions)}")

if __name__ == "__main__":
    main()
