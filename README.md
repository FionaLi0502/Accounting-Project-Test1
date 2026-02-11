# Three Statements Automation - V5 Complete

**AI-Powered Financial Statement Generator with TB/GL Validation**

---

## 🎯 What This App Does

Generate professional 3-statement financial models (Income Statement, Balance Sheet, Cash Flow) from your accounting data in seconds.

---

## ✨ V5 Key Features

### 🔒 Strict USD Mode
- Blocks multi-currency data automatically
- Clear error messages

### ✅ Enhanced Validation
- Debit/Credit must be ≥ 0, cannot both be > 0
- TransactionID optional (50% threshold for per-JE validation)
- Full-row duplicates only (TransactionID repetition is NORMAL)
- User-selected fixes (nothing auto-applied)

### 📊 Professional Outputs
- Tables with years as columns, line items as rows
- Complete PDF with full IS, BS, CF tables
- TB as source of truth when both TB+GL uploaded

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Click "Download Sample Data" → Upload → Generate!

---

## 📥 Data Format

### Required Columns

| Column | TB | GL | Notes |
|--------|----|----|-------|
| TxnDate | ✅ | ✅ | Transaction date |
| AccountNumber | ✅ | ✅ | Account code |
| AccountName | ✅ | ✅ | Account description |
| Debit | ✅ | ✅ | ≥ 0, single-sided |
| Credit | ✅ | ✅ | ≥ 0, single-sided |
| TransactionID | ❌ | ⚠️ | Optional for GL |
| Currency | ⚠️ | ⚠️ | Must be USD |

### Rules
1. **Column names** case-insensitive, order-independent
2. **Debit/Credit** cannot both be > 0 in same row
3. **TransactionID** treated as Journal Entry ID (optional)
4. **Currency** strict USD mode enforced

---

## 🔧 Key Features

### Dual Upload System
- **TB** → Complete 3 statements
- **GL** → Transaction validation + IS
- **Both** → Best results (TB = source of truth)

### Sample Data
- **Download Sample Data** - TB and GL CSV files
- **Load Random Test Dataset** - Auto-loads TB+GL pair

### Validation
- Strict USD (blocks non-USD)
- Debit/Credit validation
- TB balances per period
- GL per-JE balancing (if TransactionID ≥ 50%)
- Full-row duplicate detection

### Account Mapping
1. **Name-based** (primary): "Cash" / "Bank" → cash
2. **Range-based** (fallback): 1000-1099 → cash

### Outputs
- **Excel**: Label-based writing, 3 year columns
- **PDF**: Full tables, all 3 statements
- **AI Summary**: Optional (works without API key)

---

## 📊 Output Tables

Years as columns, line items as rows:

```
Line Item          | 2023    | 2024    | 2025
-------------------|---------|---------|--------
Revenue            | 1,000   | 1,200   | 1,400
```

**Income Statement**: Revenue → Net Income (8 line items)  
**Balance Sheet**: Assets, Liabilities, Equity (14 line items)  
**Cash Flow**: CFO, CFI, CFF (13 line items, Year 2+)

---

## 🔧 TB vs GL Logic

### TB Only
✅ IS ⚠️ BS ⚠️ CF

### GL Only
✅ IS ⚠️ BS (incomplete) ⚠️ CF (incomplete)

### TB + GL
**TB is source of truth** for totals  
**GL for validation only**  
GL NOT added to TB (avoids double-counting)

---

## 📝 Quick Tests

### Random Loader
1. Click "Load Random Test Dataset"
2. Verify TB + GL both loaded
3. Generate → Download Excel + PDF

### TransactionID Optional
1. Upload GL without TransactionID
2. Verify: Info message, overall validation
3. Generate successfully

### Strict USD
1. Upload EUR data → Critical error, blocked
2. Upload USD data → Proceeds normally

---

## 🚨 Troubleshooting

**Multi-currency error**: Convert to USD before uploading  
**No clean data**: Decline fixes and proceed with original  
**TB unbalanced**: Fix your TB export, must balance per period  
**TransactionID not validating**: <50% populated, falls back to overall

---

## 📁 Files

```
streamlit_app.py      # Main UI
validation.py         # Validations
mapping.py           # Account mapping
excel_writer.py      # Excel generator
pdf_export.py        # PDF generator
ai_summary.py        # AI summaries
sample_data.py       # V5 data loader
```

---

## 🎯 Architecture

Upload → Validate (strict USD, debit/credit) → Fix (user-selected) → Map accounts → Calculate statements (TB = source) → Generate Excel/PDF → Download

---

**Built with Streamlit, Python, and Claude AI**
