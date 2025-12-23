"""
Settings View - Configuration Management
Card closing day updates
"""

import streamlit as st
from database import get_all_cards, update_card_closing

def main():
    # Get authenticated user ID from session state
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("⚠️ Error: No user authenticated")
        return
    
    st.title("⚙️ Configuración")
    st.markdown("---")
    
    # ============================================
    # CARD SETTINGS
    # ============================================
    
    st.markdown("### 💳 Configuración de Tarjetas")
    
    # Important warning
    st.warning("""
    **⚠️ IMPORTANTE:** 
    
    Los cambios en el día de cierre solo afectan a las **nuevas transacciones**.
    
    Las compras ya registradas mantienen su fecha de pago original (Snapshot Date Logic).
    """)
    
    st.markdown("---")
    
    # Load cards
    cards = get_all_cards(user_id)
    
    if not cards:
        st.info("No hay tarjetas configuradas en el sistema.")
        return
    
    # Display each card with edit option
    for card in cards:
        with st.expander(f"💳 {card['name']}", expanded=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Tarjeta:** {card['name']}")
                st.caption(f"ID: {card['id']}")
            
            with col2:
                st.metric("Día de Cierre Actual", card['closing_day'])
            
            with col3:
                # Edit button
                if st.button(f"✏️ Editar", key=f"edit_{card['id']}"):
                    st.session_state[f"editing_{card['id']}"] = True
            
            # Edit form
            if st.session_state.get(f"editing_{card['id']}", False):
                st.markdown("---")
                
                with st.form(f"update_card_{card['id']}"):
                    new_closing_day = st.number_input(
                        "Nuevo Día de Cierre",
                        min_value=1,
                        max_value=31,
                        value=card['closing_day'],
                        step=1,
                        help="Día del mes en que cierra el resumen de la tarjeta"
                    )
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        save_btn = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
                    
                    with col_b:
                        cancel_btn = st.form_submit_button("❌ Cancelar", use_container_width=True)
                    
                    if save_btn:
                        if new_closing_day != card['closing_day']:
                            with st.spinner("Actualizando..."):
                                success = update_card_closing(user_id, card['id'], new_closing_day)
                            
                            if success:
                                st.success(f"✅ Día de cierre actualizado a {new_closing_day}")
                                st.session_state[f"editing_{card['id']}"] = False
                                st.rerun()
                        else:
                            st.info("No hay cambios para guardar")
                            st.session_state[f"editing_{card['id']}"] = False
                    
                    if cancel_btn:
                        st.session_state[f"editing_{card['id']}"] = False
                        st.rerun()
    
    st.markdown("---")
    
    # ============================================
    # INFO SECTION
    # ============================================
    
    st.markdown("### ℹ️ Acerca del Día de Cierre")
    
    with st.expander("📖 ¿Qué es el día de cierre?"):
        st.markdown("""
        **Definición:**
        
        El día de cierre es el último día del período de facturación de tu tarjeta de crédito.
        
        **¿Por qué es importante?**
        
        El sistema usa el día de cierre para calcular en qué mes deberás pagar cada compra:
        
        - **Compras ANTES o EN el día de cierre:** Se pagan el mes siguiente
        - **Compras DESPUÉS del día de cierre:** Se pagan el mes subsiguiente
        
        **Ejemplo con cierre día 28:**
        
        - Compra del 15 de Enero → Pago en Febrero
        - Compra del 30 de Enero → Pago en Marzo
        
        **¿Dónde encontrar esta información?**
        
        Generalmente viene en tu resumen de tarjeta o lo puedes consultar con tu banco.
        """)
    
    with st.expander("🔒 Snapshot Date Logic - ¿Por qué no se actualizan las compras viejas?"):
        st.markdown("""
        **Principio de Inmutabilidad:**
        
        Cuando registras una compra, el sistema toma una "foto" (snapshot) de la configuración actual
        de tu tarjeta (día de cierre) y calcula la fecha de pago basándose en esa información.
        
        **¿Por qué funciona así?**
        
        1. **Precisión Histórica:** Las fechas de pago ya calculadas reflejan la realidad al momento de la compra.
        2. **Evita Caos:** Si cambiáramos fechas retroactivamente, tus números mensuales cambiarían constantemente.
        3. **Alineación con Resúmenes:** Las fechas coinciden con los resúmenes reales de tu banco.
        
        **Flujo Correcto:**
        
        1. Configuras el día de cierre correcto ANTES de registrar compras
        2. Registras tus compras → El sistema calcula la fecha de pago
        3. Si cambias el día de cierre más adelante, solo afecta a compras NUEVAS
        
        **¿Qué hacer si me equivoqué?**
        
        Si necesitas corregir compras ya registradas, por ahora deberás:
        1. Eliminarlas manualmente desde la base de datos
        2. Configurar el día de cierre correcto
        3. Volver a registrarlas
        
        (Funcionalidad de edición vendrá en futuras versiones)
        """)
    
    st.markdown("---")
    
    # Database info
    with st.expander("🗄️ Información de Base de Datos"):
        st.markdown(f"""
        **Tarjetas en el Sistema:** {len(cards)}
        
        **Estructura:**
        - Cada tarjeta tiene un ID único
        - El día de cierre puede estar entre 1 y 31
        - Las transacciones están vinculadas a las tarjetas mediante `card_id`
        """)
    
    st.markdown("---")
    st.caption("💾 Todos los cambios se guardan automáticamente en Supabase")

if __name__ == "__main__":
    main()
