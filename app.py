"""
FINANZAS PRO - Main Application Entry Point
Streamlit Navigation Structure
MULTI-USER SAAS VERSION with Supabase Authentication
"""

import streamlit as st
from database import get_supabase_client, create_default_cards, claim_orphaned_data

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Finanzas Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# AUTHENTICATION CHECK
# ============================================

# Initialize session state
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# Check if user is logged in
if st.session_state['user'] is None:
    # Show login page
    from views import login
    login.render_login()
    
else:
    # User is authenticated - show main app
    user_id = st.session_state['user_id']
    user_email = st.session_state['user'].email
    
    # ============================================
    # SIDEBAR: USER PROFILE & LOGOUT
    # ============================================
    
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 👤 {user_email}")
        st.caption(f"ID: {user_id[:8]}...")
        
        # Logout button
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            try:
                supabase = get_supabase_client()
                supabase.auth.sign_out()
            except:
                pass  # Ignore errors on logout
            
            # Clear session
            st.session_state.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Check if this is a new user (first login)
        # Try to create default cards or claim orphaned data
        if 'setup_complete' not in st.session_state:
            # Try to create default cards
            created = create_default_cards(user_id)
            
            if created:
                st.success("🎉 Tarjetas iniciales creadas!")
            
            # Try to claim orphaned data (for migration from single-user)
            trans_claimed, cards_claimed = claim_orphaned_data(user_id)
            
            if trans_claimed > 0 or cards_claimed > 0:
                st.success(f"📦 Datos migrados: {trans_claimed} transacciones, {cards_claimed} tarjetas")
            
            st.session_state['setup_complete'] = True
    
    # ============================================
    # NAVIGATION PAGES
    # ============================================
    
    from views import dashboard, cards, incomes, fixed, investments, settings, transactions
    
    # Create navigation
    pg = st.navigation(
        {
            "Principal": [
                st.Page(dashboard.main, title="📊 Dashboard", url_path="dashboard", default=True)
            ],
            "Transacciones": [
                st.Page(cards.main, title="💳 Tarjetas", url_path="cards"),
                st.Page(incomes.main, title="💵 Ingresos", url_path="incomes"),
                st.Page(fixed.main, title="📌 Gastos Fijos", url_path="fixed"),
                st.Page(investments.main, title="📈 Inversiones", url_path="investments")
            ],
            "Gestión": [
                st.Page(transactions.main, title="🗂️ Ver/Eliminar", url_path="transactions"),
                st.Page(settings.main, title="⚙️ Configuración", url_path="settings")
            ]
        }
    )
    
    # Run navigation
    pg.run()
