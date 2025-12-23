"""
Configuration View - Credit Card Management
Add and delete credit cards
"""

import streamlit as st
from database import get_all_cards, create_card, delete_card

def main():
    # Get authenticated user ID from session state
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("⚠️ Error: No user authenticated")
        return
    
    st.title("💳 Configuración de Tarjetas")
    st.markdown("---")
    
    # ============================================
    # SECTION 1: MY CARDS LIST
    # ============================================
    
    st.markdown("### 🗂️ Mis Tarjetas")
    
    # Load user's cards
    cards = get_all_cards(user_id)
    
    if not cards:
        st.info("👋 No tienes tarjetas registradas. Agrega tu primera tarjeta abajo.")
    else:
        st.caption(f"Tienes {len(cards)} tarjeta(s) registrada(s)")
        
        # Display cards in a table-like format
        for card in cards:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**💳 {card['name']}**")
                
                with col2:
                    st.markdown(f"**Cierre:** Día {card['closing_day']}")
                
                with col3:
                    st.caption(f"ID: {card['id']}")
                
                with col4:
                    # Delete button
                    if st.button("🗑️", key=f"delete_{card['id']}", help="Eliminar tarjeta"):
                        st.session_state[f"confirm_delete_card_{card['id']}"] = True
                        st.rerun()
                
                # Show confirmation if delete was clicked
                if st.session_state.get(f"confirm_delete_card_{card['id']}", False):
                    st.warning(f"⚠️ ¿Estás seguro de eliminar '{card['name']}'?")
                    
                    col_a, col_b, col_c = st.columns([1, 1, 2])
                    
                    with col_a:
                        if st.button("✅ Sí, eliminar", key=f"confirm_yes_{card['id']}", type="primary"):
                            success = delete_card(user_id, card['id'])
                            if success:
                                st.session_state[f"confirm_delete_card_{card['id']}"] = False
                                st.rerun()
                    
                    with col_b:
                        if st.button("❌ Cancelar", key=f"confirm_no_{card['id']}"):
                            st.session_state[f"confirm_delete_card_{card['id']}"] = False
                            st.rerun()
                
                st.markdown("---")
    
    # ============================================
    # SECTION 2: ADD NEW CARD FORM
    # ============================================
    
    st.markdown("### ➕ Agregar Nueva Tarjeta")
    
    with st.form("add_card_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Card name
            card_name = st.text_input(
                "💳 Nombre del Banco/Tarjeta",
                placeholder="ej: Visa Galicia, Mastercard BBVA",
                help="Nombre descriptivo para identificar tu tarjeta"
            )
            
            # Closing day
            closing_day = st.number_input(
                "📅 Día de Cierre del Resumen",
                min_value=1,
                max_value=31,
                value=28,
                step=1,
                help="Día del mes en que cierra el período de facturación"
            )
        
        with col2:
            st.markdown("#### 💡 Información")
            st.info("""
            **Día de Cierre**: Es el último día del período de facturación de tu tarjeta.
            
            Este dato lo encuentras en tu resumen de cuenta o consultando con tu banco.
            
            **Importante**: El sistema usa este valor para calcular automáticamente en qué mes deberás pagar cada compra.
            """)
        
        # Submit button
        submitted = st.form_submit_button(
            "💾 Guardar Tarjeta",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not card_name or not card_name.strip():
                st.error("⚠️ Por favor ingresa un nombre para la tarjeta")
            else:
                # Create the card
                success = create_card(user_id, card_name, closing_day)
                
                if success:
                    st.success(f"✅ Tarjeta '{card_name}' creada exitosamente!")
                    st.balloons()
                    st.rerun()
    
    st.markdown("---")
    
    # ============================================
    # INFO SECTION
    # ============================================
    
    with st.expander("❓ Preguntas Frecuentes"):
        st.markdown("""
        **¿Por qué necesito configurar el día de cierre?**
        
        El día de cierre es fundamental para que el sistema calcule correctamente en qué mes deberás pagar cada compra con tarjeta de crédito.
        
        **¿Puedo cambiar el día de cierre después?**
        
        Sí, puedes modificarlo en la sección "Configuración", pero solo afectará a las compras nuevas. Las compras ya registradas mantendrán su fecha de pago original.
        
        **¿Qué pasa si elimino una tarjeta?**
        
        Solo puedes eliminar tarjetas que no tengan transacciones asociadas. Si quieres eliminar una tarjeta con movimientos, primero debes eliminar esas transacciones desde "Gestión" → "Ver/Eliminar".
        
        **¿Cuántas tarjetas puedo tener?**
        
        No hay límite. Puedes agregar todas las tarjetas que necesites.
        
        **¿Puedo tener dos tarjetas con el mismo nombre?**
        
        No, cada tarjeta debe tener un nombre único para evitar confusiones. Puedes usar nombres como "Visa Galicia 1" y "Visa Galicia 2" si tienes dos tarjetas del mismo banco.
        """)
    
    st.markdown("---")
    st.caption("💡 Tip: Usa nombres descriptivos para identificar fácilmente tus tarjetas")

if __name__ == "__main__":
    main()
