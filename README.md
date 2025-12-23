# 💰 Finanzas Pro

Personal Finance Manager built with Streamlit + Supabase

## 🎯 Core Features

- **Dual Payment Logic**: Separate tracking for immediate (cash/debit) and future (credit card) expenses
- **Smart Date Calculation**: Automatic payment date calculation based on card closing days
- **Installment Support**: Split card purchases into multiple monthly payments
- **Dynamic Dashboard**: Real-time financial overview with visual expense separation
- **Snapshot Date Logic**: Historical accuracy - past transactions remain unchanged

## 🏗️ Tech Stack

- **Frontend**: Streamlit (Native Navigation)
- **Database**: Supabase (PostgreSQL)
- **Python**: 3.9+

## 📋 Prerequisites

1. Python 3.9 or higher
2. Supabase account and project
3. Git (optional)

## 🚀 Installation

### 1. Clone or Download

```bash
cd "c:\Users\USUARIO\Documents\app- gerstion financiera"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Supabase

1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy your **Project URL** and **anon/public key**
4. Open `.streamlit\secrets.toml` and replace with your credentials:

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key-here"
```

### 4. Initialize Database

The SQL schema has already been created. Your database should have:
- ✅ `credit_cards` table
- ✅ `transactions` table
- ✅ `usd_rates` table

## ▶️ Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
app- gerstion financiera/
├── app.py                 # Main entry point
├── database.py            # Centralized logic layer
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml      # Supabase credentials
└── views/
    ├── dashboard.py      # Financial overview
    ├── cards.py          # Credit card transactions
    ├── incomes.py        # Income entry
    ├── fixed.py          # Fixed expenses
    ├── investments.py    # Investment tracking
    └── settings.py       # Card configuration
```

## 💡 How It Works

### Logic A: Cash/Debit/Fixed/Income
- `payment_date = date`
- Immediate impact on the selected month

### Logic B: Credit Cards
- `payment_date` calculated based on card's closing day
- **Rule 1**: Purchase day ≤ closing day → Payment next month
- **Rule 2**: Purchase day > closing day → Payment month after next
- Supports installments (cuotas)

### Example (Card with closing day 28):
- Purchase on Jan 15 → Payment in Feb
- Purchase on Jan 30 → Payment in Mar

## 🎨 Features Walkthrough

### Dashboard
- View monthly financial summary
- Separate visualization: Credit Cards vs Daily Expenses
- Net balance calculation
- Dynamic month filtering

### Credit Cards
- Register purchases with automatic payment date calculation
- Split into installments
- See affected months

### Income/Fixed/Investments
- Simple forms for quick entry
- Immediate payment impact
- Category management

### Settings
- Update card closing days
- Changes only affect new transactions (Snapshot Logic)

## 🔐 Security

- Never commit `.streamlit/secrets.toml` to version control
- Keep your Supabase keys private
- Use environment variables in production

## 🐛 Troubleshooting

**Error: "Supabase credentials not found"**
- Check that `.streamlit\secrets.toml` exists and has valid credentials

**Error: "Table does not exist"**
- Verify SQL script was executed successfully in Supabase

**Dashboard shows no months**
- Add some transactions first to see available months

## 📝 Future Enhancements

- [ ] Transaction editing/deletion UI
- [ ] Budget tracking and alerts
- [ ] Expense analytics and charts
- [ ] Multi-currency support with USD rates
- [ ] Export to CSV/Excel
- [ ] Mobile responsive optimization

## 👨‍💻 Developer Notes

### Business Rules (Non-Negotiable)

1. **Unified Storage**: All transactions in one table
2. **Visual Separation**: Dashboard separates cash from cards
3. **Snapshot Date Logic**: payment_date calculated at insertion, never retroactively changed
4. **Installments**: Only for cards, generates N database rows

### Database Schema

```sql
transactions(
  id, created_at, date, payment_date,
  amount, category, description, type,
  card_id, installments_total, installment_number
)
```

## 📄 License

Personal use only.

---

**Built with ❤️ using Streamlit + Supabase**
