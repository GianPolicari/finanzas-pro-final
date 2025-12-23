"""
Dashboard View - Financial Overview
Shows visual separation of Cash vs Card expenses
"""

import streamlit as st
from datetime import datetime
from database import get_available_months, get_monthly_summary, get_monthly_transactions

def main():
    st.title("📊 Dashboard Financiero")
    st.markdown("---")
    
    # ============================================
    # MONTH FILTER
    # ============================================
    
    available_months = get_available_months()
    
    if not available_months:
        st.info("👋 No hay transacciones registradas aún. ¡Comienza agregando ingresos o gastos!")
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
    # MONTHLY SUMMARY
    # ============================================
    
    summary = get_monthly_summary(selected_year, selected_month)
    
    # Row 1: Net Balance (Hero Metric)
    st.markdown("### 💰 Balance Neto")
    
    balance_color = "normal" if summary["net_balance"] >= 0 else "inverse"
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.metric(
            label="Balance del Mes",
            value=f"${summary['net_balance']:,.2f}",
            delta=None,
            delta_color=balance_color
        )
    
    with col2:
        st.metric(
            label="💵 Ingresos",
            value=f"${summary['income']:,.2f}"
        )
    
    with col3:
        total_expenses = summary['fixed'] + summary['debit'] + summary['card']
        st.metric(
            label="💸 Gastos Totales",
            value=f"${total_expenses:,.2f}"
        )
    
    st.markdown("---")
    
    # Row 2: Expense Breakdown
    st.markdown("### 📊 Desglose de Gastos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💳 Tarjetas de Crédito")
        st.markdown(f"**Pagos del mes:** `${summary['card']:,.2f}`")
        st.caption("Compras realizadas en períodos anteriores")
        
        # Show card transactions
        card_trans = get_monthly_transactions(selected_year, selected_month, "Card")
        if card_trans:
            with st.expander(f"📋 Ver {len(card_trans)} movimientos"):
                for trans in card_trans:
                    card_name = trans.get("credit_cards", {}).get("name", "N/A") if trans.get("credit_cards") else "N/A"
                    installment_info = ""
                    if trans["installments_total"] > 1:
                        installment_info = f" (Cuota {trans['installment_number']}/{trans['installments_total']})"
                    
                    st.markdown(f"- **{card_name}**: {trans['category']} - ${trans['amount']:,.2f}{installment_info}")
                    if trans['description']:
                        st.caption(f"  ↳ {trans['description']}")
    
    with col2:
        st.markdown("#### 💸 Gastos Diarios (Efectivo/Débito)")
        daily_total = summary['fixed'] + summary['debit']
        st.markdown(f"**Total del mes:** `${daily_total:,.2f}`")
        st.caption("Gastos con impacto inmediato")
        
        # Breakdown
        st.markdown(f"- 📌 Fijos: `${summary['fixed']:,.2f}`")
        st.markdown(f"- 💵 Débito: `${summary['debit']:,.2f}`")
        
        # Show recent transactions
        cash_trans = get_monthly_transactions(selected_year, selected_month)
        cash_trans = [t for t in cash_trans if t["type"] in ["Fixed", "Debit"]]
        
        if cash_trans:
            with st.expander(f"📋 Ver {len(cash_trans)} movimientos"):
                for trans in cash_trans:
                    icon = "📌" if trans["type"] == "Fixed" else "💵"
                    st.markdown(f"- **{icon} {trans['category']}**: ${trans['amount']:,.2f}")
                    if trans['description']:
                        st.caption(f"  ↳ {trans['description']}")
    
    st.markdown("---")
    
    # ============================================
    # VISUAL CHART (Optional Enhancement)
    # ============================================
    
    st.markdown("### 📈 Distribución de Gastos")
    
    chart_data = {
        "Categoría": ["Tarjetas", "Fijos", "Débito"],
        "Monto": [summary['card'], summary['fixed'], summary['debit']]
    }
    
    st.bar_chart(chart_data, x="Categoría", y="Monto", color="#4F46E5")
    
    # ============================================
    # FOOTER STATS
    # ============================================
    
    st.markdown("---")
    st.caption(f"📅 Período: {selected_display} | 🔄 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if __name__ == "__main__":
    main()
