"""
FINANZAS PRO - Centralized Database Logic Layer
Supabase + PostgreSQL Backend
MULTI-USER SAAS VERSION - All functions require user_id for data isolation
"""

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from supabase import create_client, Client
import streamlit as st
from typing import Dict, List, Tuple, Optional

# ============================================
# SUPABASE CONNECTION
# ============================================

@st.cache_resource
def get_supabase_client() -> Client:
    """Initialize and cache Supabase client"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# ============================================
# LOGIC A: CASH TRANSACTIONS (Immediate Impact)
# ============================================

def save_cash_transaction(
    user_id: str,
    trans_type: str,  # 'Income', 'Fixed', 'Debit'
    date: datetime,
    amount: float,
    category: str,
    description: str = ""
) -> bool:
    """
    Save Cash/Debit/Fixed/Income transaction with user isolation.
    Rule: payment_date = date (Immediate impact)
    """
    try:
        supabase = get_supabase_client()
        
        # Validate type
        if trans_type not in ['Income', 'Fixed', 'Debit']:
            raise ValueError(f"Invalid type for cash transaction: {trans_type}")
        
        # Prepare data with user_id
        data = {
            "user_id": user_id,
            "date": date.strftime("%Y-%m-%d"),
            "payment_date": date.strftime("%Y-%m-%d"),  # LOGIC A: Same as transaction date
            "amount": amount,
            "category": category,
            "description": description,
            "type": trans_type,
            "card_id": None,
            "installments_total": 1,
            "installment_number": 1
        }
        
        # Insert into database
        supabase.table("transactions").insert(data).execute()
        return True
        
    except Exception as e:
        st.error(f"Error saving transaction: {str(e)}")
        return False

# ============================================
# LOGIC B: CARD TRANSACTIONS (Calculated Payment Date)
# ============================================

def calculate_payment_date(
    purchase_date: datetime,
    closing_day: int
) -> datetime:
    """
    Calculate payment_date using Technical Closing + Grace Period logic.
    
    Algorithm:
    1. Determine Statement Month:
       - If purchase_day <= closing_day: This month's statement
       - If purchase_day > closing_day: Next month's statement
    
    2. Calculate Technical Close Date:
       - Technical Close = Statement Month + closing_day
    
    3. Add Grace Period:
       - Payment Date = Technical Close + 10 days
    
    Example:
    - Purchase Dec 10, Closing Day 5:
      → 10 > 5, so Next Month's statement (Jan 5)
      → Payment: Jan 5 + 10 days = Jan 15
    
    - Purchase Dec 29, Closing Day 28:
      → 29 > 28, so Next Month's statement (Jan 28)
      → Payment: Jan 28 + 10 days = Feb 7
    
    Returns: Exact payment date (not first of month)
    """
    purchase_day = purchase_date.day
    
    # Step 1: Determine which statement month this purchase belongs to
    if purchase_day <= closing_day:
        # This month's statement
        statement_month = purchase_date
    else:
        # Next month's statement
        statement_month = purchase_date + relativedelta(months=1)
    
    # Step 2: Calculate Technical Close Date
    # Handle edge case: if closing_day doesn't exist in statement month (e.g., Feb 30)
    # Use the last day of that month instead
    try:
        technical_close_date = statement_month.replace(day=closing_day)
    except ValueError:
        # Closing day doesn't exist in this month (e.g., Feb 30)
        # Use last day of the month
        next_month = statement_month + relativedelta(months=1)
        technical_close_date = next_month.replace(day=1) - timedelta(days=1)
    
    # Step 3: Add 10-day grace period
    payment_date = technical_close_date + timedelta(days=10)
    
    return payment_date



def save_card_transaction(
    user_id: str,
    card_id: int,
    date: datetime,
    amount: float,
    category: str,
    description: str = "",
    installments: int = 1
) -> Tuple[bool, List[str]]:
    """
    Save Credit Card transaction with installments and user isolation.
    
    Rule: payment_date is calculated at insertion time based on card's CURRENT closing_day.
    Returns: (success: bool, affected_months: List[str])
    """
    try:
        supabase = get_supabase_client()
        affected_months = []
        
        # Fetch card's current closing_day (must belong to user)
        card_response = supabase.table("credit_cards") \
            .select("closing_day") \
            .eq("id", card_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not card_response.data:
            st.error("Card not found or doesn't belong to you")
            return False, []
        
        closing_day = card_response.data[0]["closing_day"]
        
        # Calculate starting payment month
        base_payment_date = calculate_payment_date(date, closing_day)
        
        # Calculate amount per installment
        amount_per_installment = round(amount / installments, 2)
        
        # Generate installment rows
        for i in range(installments):
            # Calculate payment date for this installment
            installment_payment_date = base_payment_date + relativedelta(months=i)
            
            # Track affected month
            month_str = installment_payment_date.strftime("%B %Y")
            if month_str not in affected_months:
                affected_months.append(month_str)
            
            # Prepare installment data with user_id
            data = {
                "user_id": user_id,
                "date": date.strftime("%Y-%m-%d"),
                "payment_date": installment_payment_date.strftime("%Y-%m-%d"),
                "amount": amount_per_installment,
                "category": category,
                "description": description,
                "type": "Card",
                "card_id": card_id,
                "installments_total": installments,
                "installment_number": i + 1
            }
            
            # Insert into database
            supabase.table("transactions").insert(data).execute()
        
        return True, affected_months
        
    except Exception as e:
        st.error(f"Error saving card transaction: {str(e)}")
        return False, []

# ============================================
# DASHBOARD QUERIES
# ============================================

def get_available_months(user_id: str) -> List[Tuple[int, int, str]]:
    """
    Get list of months with transactions based on payment_date (user-specific).
    Returns: List of (year, month, display_string) tuples
    """
    try:
        supabase = get_supabase_client()
        
        # Get distinct payment_dates for this user
        response = supabase.table("transactions") \
            .select("payment_date") \
            .eq("user_id", user_id) \
            .execute()
        
        if not response.data:
            return []
        
        # Extract unique year-month combinations
        months_set = set()
        for record in response.data:
            payment_date = datetime.strptime(record["payment_date"], "%Y-%m-%d")
            months_set.add((payment_date.year, payment_date.month))
        
        # Sort by year, month (most recent first)
        sorted_months = sorted(months_set, reverse=True)
        
        # Convert to display format
        month_names = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        
        result = []
        for year, month in sorted_months:
            display = f"{month_names[month]} {year}"
            result.append((year, month, display))
        
        return result
        
    except Exception as e:
        st.error(f"Error fetching available months: {str(e)}")
        return []


def get_monthly_summary(user_id: str, year: int, month: int) -> Dict[str, float]:
    """
    Get financial summary for a specific month based on payment_date (user-specific).
    
    Returns: Dict with keys:
        - 'income': Total income
        - 'fixed': Total fixed expenses
        - 'debit': Total debit expenses
        - 'card': Total credit card payments
        - 'net_balance': Income - Total Expenses
    """
    try:
        supabase = get_supabase_client()
        
        # Build date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Query transactions for the month (user-specific)
        response = supabase.table("transactions") \
            .select("type, amount") \
            .eq("user_id", user_id) \
            .gte("payment_date", start_date.strftime("%Y-%m-%d")) \
            .lt("payment_date", end_date.strftime("%Y-%m-%d")) \
            .execute()
        
        # Initialize summary
        summary = {
            "income": 0.0,
            "fixed": 0.0,
            "debit": 0.0,
            "card": 0.0,
            "net_balance": 0.0
        }
        
        # Aggregate by type
        for record in response.data:
            trans_type = record["type"]
            amount = float(record["amount"])
            
            if trans_type == "Income":
                summary["income"] += amount
            elif trans_type == "Fixed":
                summary["fixed"] += amount
            elif trans_type == "Debit":
                summary["debit"] += amount
            elif trans_type == "Card":
                summary["card"] += amount
        
        # Calculate net balance
        total_expenses = summary["fixed"] + summary["debit"] + summary["card"]
        summary["net_balance"] = summary["income"] - total_expenses
        
        return summary
        
    except Exception as e:
        st.error(f"Error fetching monthly summary: {str(e)}")
        return {
            "income": 0.0,
            "fixed": 0.0,
            "debit": 0.0,
            "card": 0.0,
            "net_balance": 0.0
        }

# ============================================
# CARD MANAGEMENT
# ============================================

def get_all_cards(user_id: str) -> List[Dict]:
    """Get all credit cards for the authenticated user"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("credit_cards") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching cards: {str(e)}")
        return []


def update_card_closing(user_id: str, card_id: int, new_closing_day: int) -> bool:
    """
    Update card's closing day (user must own the card).
    Note: This only affects NEW transactions.
    """
    try:
        supabase = get_supabase_client()
        
        # Validate closing day
        if not (1 <= new_closing_day <= 31):
            st.error("Closing day must be between 1 and 31")
            return False
        
        # Update card (only if user owns it)
        supabase.table("credit_cards") \
            .update({"closing_day": new_closing_day}) \
            .eq("id", card_id) \
            .eq("user_id", user_id) \
            .execute()
        
        return True
        
    except Exception as e:
        st.error(f"Error updating card: {str(e)}")
        return False


def create_default_cards(user_id: str) -> bool:
    """
    Create default starter cards for a new user
    """
    try:
        supabase = get_supabase_client()
        
        # Check if user already has cards
        existing = supabase.table("credit_cards") \
            .select("id") \
            .eq("user_id", user_id) \
            .execute()
        
        if existing.data:
            return False  # User already has cards
        
        # Create default cards
        default_cards = [
            {"name": "Mi Tarjeta 1", "closing_day": 28, "user_id": user_id},
            {"name": "Mi Tarjeta 2", "closing_day": 28, "user_id": user_id}
        ]
        
        supabase.table("credit_cards").insert(default_cards).execute()
        return True
        
    except Exception as e:
        st.error(f"Error creating default cards: {str(e)}")
        return False


def create_card(user_id: str, name: str, closing_day: int) -> bool:
    """
    Create a new credit card for the user
    
    Args:
        user_id: User's ID
        name: Card name (e.g., "Visa Galicia")
        closing_day: Day of month when statement closes (1-31)
        
    Returns:
        bool: True if creation was successful
    """
    try:
        supabase = get_supabase_client()
        
        # Validate closing day
        if not (1 <= closing_day <= 31):
            st.error("El día de cierre debe estar entre 1 y 31")
            return False
        
        # Validate name
        if not name or not name.strip():
            st.error("El nombre de la tarjeta no puede estar vacío")
            return False
        
        # Check for duplicate name for this user
        existing = supabase.table("credit_cards") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("name", name.strip()) \
            .execute()
        
        if existing.data:
            st.error(f"Ya tienes una tarjeta con el nombre '{name}'")
            return False
        
        # Create the card
        data = {
            "user_id": user_id,
            "name": name.strip(),
            "closing_day": closing_day
        }
        
        supabase.table("credit_cards").insert(data).execute()
        return True
        
    except Exception as e:
        st.error(f"Error creating card: {str(e)}")
        return False


def delete_card(user_id: str, card_id: int) -> bool:
    """
    Delete a credit card (user must own it)
    
    Args:
        user_id: User's ID
        card_id: Card ID to delete
        
    Returns:
        bool: True if deletion was successful
    """
    try:
        supabase = get_supabase_client()
        
        # Check if card has associated transactions
        transactions = supabase.table("transactions") \
            .select("id") \
            .eq("card_id", card_id) \
            .eq("user_id", user_id) \
            .limit(1) \
            .execute()
        
        if transactions.data:
            st.warning("⚠️ No se puede eliminar la tarjeta porque tiene transacciones asociadas. Elimina las transacciones primero.")
            return False
        
        # Delete the card (only if user owns it)
        response = supabase.table("credit_cards") \
            .delete() \
            .eq("id", card_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if response.data:
            st.success(f"✅ Tarjeta eliminada correctamente")
            return True
        else:
            st.warning("⚠️ No se encontró la tarjeta o no te pertenece")
            return False
            
    except Exception as e:
        st.error(f"Error deleting card: {str(e)}")
        return False

# ============================================
# TRANSACTION QUERIES
# ============================================

def get_monthly_transactions(
    user_id: str,
    year: int,
    month: int,
    trans_type: Optional[str] = None
) -> List[Dict]:
    """
    Get all transactions for a specific month (user-specific).
    Optionally filter by type.
    """
    try:
        supabase = get_supabase_client()
        
        # Build date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Build query (user-specific)
        query = supabase.table("transactions") \
            .select("*, credit_cards(name)") \
            .eq("user_id", user_id) \
            .gte("payment_date", start_date.strftime("%Y-%m-%d")) \
            .lt("payment_date", end_date.strftime("%Y-%m-%d"))
        
        # Add type filter if specified
        if trans_type:
            query = query.eq("type", trans_type)
        
        # Execute and order by date
        response = query.order("date", desc=True).execute()
        
        return response.data
        
    except Exception as e:
        st.error(f"Error fetching transactions: {str(e)}")
        return []


def delete_transaction(user_id: str, transaction_id: int) -> bool:
    """
    Delete a transaction by ID (user must own it).
    
    Args:
        user_id: The authenticated user's ID
        transaction_id: The database ID of the transaction to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        # Attempt to delete the transaction (only if user owns it)
        response = supabase.table("transactions") \
            .delete() \
            .eq("id", transaction_id) \
            .eq("user_id", user_id) \
            .execute()
        
        # Check if deletion was successful
        if response.data:
            # Row was deleted successfully
            st.success(f"✅ Transacción eliminada correctamente (ID: {transaction_id})")
            return True
        else:
            # No rows were deleted (transaction doesn't exist or doesn't belong to user)
            st.warning(f"⚠️ No se encontró la transacción o no te pertenece (ID: {transaction_id})")
            return False
            
    except Exception as e:
        # Catch and display any errors
        st.error(f"❌ Error borrando transacción (ID: {transaction_id}): {str(e)}")
        st.error(f"Detalles técnicos: {type(e).__name__}")
        return False

# ============================================
# USER MANAGEMENT
# ============================================

def claim_orphaned_data(user_id: str) -> Tuple[int, int]:
    """
    Claim orphaned data (transactions & cards with NULL user_id)
    This is used for migration from single-user to multi-user
    
    Returns: (transactions_claimed, cards_claimed)
    """
    try:
        supabase = get_supabase_client()
        
        # Call the SQL function
        response = supabase.rpc('claim_orphaned_data', {
            'claiming_user_id': user_id
        }).execute()
        
        if response.data and len(response.data) > 0:
            result = response.data[0]
            return result.get('transactions_claimed', 0), result.get('cards_claimed', 0)
        
        return 0, 0
        
    except Exception as e:
        st.error(f"Error claiming orphaned data: {str(e)}")
        return 0, 0

# ============================================
# USD RATES (Future Enhancement)
# ============================================

def save_usd_rate(date: datetime, official: float, blue: float) -> bool:
    """Save USD exchange rate (shared data, no user_id)"""
    try:
        supabase = get_supabase_client()
        
        data = {
            "date": date.strftime("%Y-%m-%d"),
            "official": official,
            "blue": blue
        }
        
        # Upsert (insert or update)
        supabase.table("usd_rates").upsert(data).execute()
        return True
        
    except Exception as e:
        st.error(f"Error saving USD rate: {str(e)}")
        return False


def get_usd_rate(date: datetime) -> Optional[Dict[str, float]]:
    """Get USD rate for a specific date (shared data)"""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("usd_rates") \
            .select("official, blue") \
            .eq("date", date.strftime("%Y-%m-%d")) \
            .execute()
        
        if response.data:
            return response.data[0]
        return None
        
    except Exception as e:
        st.error(f"Error fetching USD rate: {str(e)}")
        return None
