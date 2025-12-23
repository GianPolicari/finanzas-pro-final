"""
FINANZAS PRO - Main Application Entry Point
Streamlit Navigation Structure
"""

import streamlit as st

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
# NAVIGATION PAGES
# ============================================

from views import dashboard, cards, incomes, fixed, investments, settings, transactions

# Define navigation structure
pages = {
    "📊 Dashboard": dashboard,
    "💳 Tarjetas": cards,
    "💵 Ingresos": incomes,
    "📌 Gastos Fijos": fixed,
    "📈 Inversiones": investments,
    "🗂️ Transacciones": transactions,
    "⚙️ Configuración": settings
}

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
