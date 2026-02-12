# Three Statements Automation

**AI-Powered Financial Statement Generator with TB/GL Validation**

Generate professional 3-statement financial models (Income Statement, Balance Sheet, Cash Flow) from your accounting data with automated validation and reconciliation checks.

---

## 🎯 What This App Does

Transform your accounting data into comprehensive financial statements in minutes:
- **Upload** Trial Balance (TB) and General Ledger (GL) data
- **Validate** data quality with automated checks
- **Map** accounts to financial statement line items
- **Generate** Excel model with formulas + PDF report
- **Verify** with built-in reconciliation checks (Row 3 & Row 81)

---

## ✨ Key Features

### 📊 **Professional 3-Statement Output**
- **Income Statement**: Revenue → Net Income (GAAP-compliant)
- **Balance Sheet**: Assets, Liabilities, Equity (balanced)
- **Cash Flow Statement**: CFO, CFI, CFF (indirect method)
- **Template-driven preview**: Website matches Excel/PDF layout exactly

### 🔒 **Strict Validation Mode**
- **Year0 Requirement**: Enforces 4-year TB (Year0 + 3 statement years)
- **Transaction Balancing**: Validates GL per-transaction (if TransactionID present)
- **Period Balancing**: Ensures TB balances per TxnDate
- **Reconciliation Checks**: 
  - **Row 3** (Balance Sheet): Assets - (Liabilities + Equity) = 0
  - **Row 81** (Cash Tie-out): Ending Cash - (Beginning Cash + Net Change) = 0

### 🎨 **Template-Driven Design**
- Years as columns, line items as rows
- Blue text = inputs, Black text = formulas
- Label-based writing (no hardcoded row numbers)
- Preserves Excel formula integrity

### 🤖 **Intelligent Account Mapping**
1. **Primary**: Name-based alias matching ("Cash" / "Bank" → cash)
2. **Secondary**: Account number range fallback (1000-1099 → cash)
3. **Configurable**: Custom ranges and aliases supported

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/accounting-three-statements.git
cd accounting-three-statements

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run streamlit_app.py
```

### First Test (Using Demo Data)

1. **Launch app**: `streamlit run streamlit_app.py`
2. **Load demo**: Click "🎲 Load Random Backup Set"
3. **Generate**: Click "🚀 Generate 3-Statement Model"
4. **Verify**: Check that Row 3 = 0 and Row 81 = 0 for all years
5. **Download**: Get Excel model + PDF report

---

## 📋 Complete Workflow

### **STEP 1: Prepare Your Data**

You need **both** Trial Balance (TB) and General Ledger (GL):

#### Trial Balance Requirements:
- **Format**: CSV or Excel
- **Structure**: Period snapshots (at least monthly recommended)
- **Years**: 4 distinct years minimum (Year0 + 3 statement years)
  - Example: For statements covering 2021-2023, TB must include 2020 (Year0)
- **Year0 Definition**: Year0 = (First Statement Year) - 1
- **Year0 Date**: Preferably 12/31 of prior year (year-end snapshot)

#### General Ledger Requirements:
- **Format**: CSV or Excel
- **Structure**: Transaction-level detail
- **Coverage**: Same date range as TB
- **TransactionID**: Strongly recommended (enables per-transaction validation)

#### Required Columns (Both TB and GL):

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| **TxnDate** | Date | ✅ Yes | Transaction/snapshot date |
| **AccountNumber** | Number | ✅ Yes | Chart of accounts code |
| **AccountName** | Text | ✅ Yes | Account description |
| **Debit** | Number | ✅ Yes | Debit amount (≥ 0) |
| **Credit** | Number | ✅ Yes | Credit amount (≥ 0) |
| **TransactionID** | Text/Number | ⚠️ Optional | Journal Entry ID (GL only, strongly recommended) |

**Column Rules:**
- ✅ Names are case-insensitive
- ✅ Column order doesn't matter
- ✅ Extra columns are ignored
- ✅ Common variations accepted (e.g., "Transaction_Date", "TxnDate", "Date")

---

### **STEP 2: Upload and Validate**

1. **Upload Files**:
   - TB file in left column
   - GL file in right column
   - Both must be uploaded (generation blocked if either missing)

2. **Automatic Validation** runs:
   - ✅ Column detection and normalization
   - ✅ TB period balancing (per TxnDate)
   - ✅ GL transaction balancing (per TransactionID if present)
   - ✅ Year0 detection (strict mode)
   - ✅ Data quality checks (missing dates, account numbers, etc.)

3. **Review Issues**:
   - **Critical** (🔴): Must fix or generation blocked
   - **Warning** (🟡): Recommended fixes
   - **Info** (ℹ️): Informational only

4. **Apply Fixes** (Optional):
   - Select which auto-fixes to apply via checkboxes
   - Common fixes: remove missing dates, map unclassified accounts
   - Click "Apply Selected Fixes" to proceed

---

### **STEP 3: Generate Statements**

1. **Click "🚀 Generate 3-Statement Model"**

2. **Processing Steps**:
   - Account mapping (name-based → range-based → unclassified)
   - Financial calculations (IS → BS → CF)
   - Reconciliation checks (Row 3, Row 81)
   - Excel template population
   - PDF report generation

3. **Preview on Website**:
   - **Income Statement** tab: Revenue through Net Income
   - **Balance Sheet** tab: Assets, Liabilities, Equity
   - **Cash Flow** tab: CFO, CFI, CFF (Year 2+ only)
   - **Checks** tab: Row 3 and Row 81 validation

4. **Verify Checks**:
   - ✅ **Row 3 = 0**: Balance sheet balances
   - ✅ **Row 81 = 0**: Cash flow ties to ending cash
   - ⚠️ If either ≠ 0: Review data quality, check Year0 completeness

---

### **STEP 4: Download and Use**

1. **Download Excel Model**:
   - Click "📊 Download Excel Model"
   - Contains: 3 statements + formulas + inputs (blue) vs formulas (black)
   - Template layout preserved

2. **Download PDF Report**:
   - Click "📄 Download PDF Report"
   - Contains: All 3 statements + AI summary (if enabled)
   - Professional formatting for presentations

3. **Verify Output**:
   - Open Excel file
   - Check Row 3 (Balance Sheet Check) = 0
   - Check Row 81 (Cash Tie-out Check) = 0
   - Review statement values for reasonableness

---

## 🔧 Settings & Configuration

### **Strict Mode** (Default: ON)

Toggle in sidebar settings. Controls:
- **Year0 enforcement**: Requires 4 years in TB
- **Validation strictness**: Blocks generation on Critical issues
- **Demo data handling**: Enables Year0 synthesis for random sets

**Important**: Even with strict mode OFF, generation still requires Year0 (enforced by calculation engine).

### **Unit Scale** (Default: USD thousands)

Select data scale:
- **USD dollars**: Source data in dollars (divided by 1,000 for template)
- **USD thousands**: Source data already in thousands (used as-is)

Affects:
- Excel template values
- PDF report display
- Tolerance calculations

### **AI Summary** (Optional)

Enable AI-powered insights:
- Requires: Anthropic API key (set in Streamlit secrets or .env)
- Provides: Executive summary, trends, recommendations
- Fallback: Rule-based analysis if API unavailable

---

## 📊 Understanding the Output

### **Statement Years vs Year0**

The app outputs **3 statement years** (e.g., 2021, 2022, 2023):

- **Income Statement**: Shows all 3 years
- **Balance Sheet**: Shows all 3 years (year-end snapshots)
- **Cash Flow**: Shows **Year 2 and Year 3 only** (requires deltas)

**Year0** (e.g., 2020):
- Not displayed in final statements
- Required for calculations (beginning balances, deltas)
- Enables proper cash flow reconciliation

### **Reconciliation Checks**

#### **Row 3: Balance Sheet Check**
```
Assets - (Liabilities + Equity) = 0
```

**What it validates**:
- Accounting equation holds
- All balance sheet accounts properly classified
- No missing accounts or data

**If ≠ 0**: Review account mapping, check for missing balance sheet accounts

---

#### **Row 81: Cash Tie-out Check**
```
Ending Cash (from TB) - (Beginning Cash + Net Cash Change) = 0
```

**What it validates**:
- Cash flow statement reconciles to balance sheet
- All cash drivers captured (CFO + CFI + CFF)
- Year0 beginning cash is correct

**If ≠ 0**: Most commonly caused by:
- Incomplete Year0 data (especially cash, working capital accounts)
- Missing cash flow drivers (capex, debt, equity movements)
- TB snapshot timing issues (ensure year-end snapshots)

---

## 🗂️ Account Mapping Logic

### **Mapping Priority**

1. **Name-Based Matching** (Primary):
   - Checks AccountName against comprehensive alias list
   - Example: "Cash and Cash Equivalents" → `cash`
   - Example: "Accounts Receivable" / "A/R" / "Trade Receivables" → `accounts_receivable`
   - Uses word-boundary regex (avoids false matches like "ar" in "retained")

2. **Range-Based Matching** (Fallback):
   - If name matching fails, checks AccountNumber against ranges
   - Example: 1000-1099 → `cash`
   - Example: 4000-4999 → `revenue`

3. **Unclassified**:
   - Accounts that don't match any rule
   - Still included in calculations but may need manual review

### **Default Account Ranges**

| Category | Range | Line Item |
|----------|-------|-----------|
| Cash | 1000-1099 | cash |
| Accounts Receivable | 1100-1199 | accounts_receivable |
| Inventory | 1200-1299 | inventory |
| PP&E Gross | 1500-1589 | ppe_gross |
| Accumulated Depreciation | 1590-1599 | accumulated_depreciation |
| Accounts Payable | 2000-2099 | accounts_payable |
| Long-term Debt | 2500-2999 | long_term_debt |
| Common Stock | 3000-3099 | common_stock |
| Retained Earnings | 3100-3199 | retained_earnings |
| Revenue | 4000-4999 | revenue |
| COGS | 5000-5099 | cogs |
| Operating Expenses | 5100-5999 | Various OpEx categories |
| Interest Expense | 6000-6099 | interest_expense |
| Tax Expense | 6100-6999 | tax_expense |

**Customization**: Edit `DEFAULT_ACCOUNT_RANGES` in `mapping.py` to match your chart of accounts.

---

## 🎲 Demo Data (Backup Sets)

The app includes realistic backup TB+GL packs for testing:

### **What's Included**

- Multiple year ranges (e.g., 2020-2023, 2021-2024, 2022-2025)
- Each pack contains:
  - `backup_tb_YYYY_YYYY.csv` (4-year TB with Year0)
  - `backup_gl_YYYY_YYYY_with_txnid.csv` (TransactionID-balanced GL)
  - `backup_gl_YYYY_YYYY_no_txnid.csv` (Optional variant without TransactionID)

### **Characteristics**

- **Scale**: Big company ($1B-$20B revenue)
- **Quality**: "Healthy but not perfect"
  - Revenue: $1B - $20B per year
  - Gross margin: 25% - 55%
  - EBITDA margin: 8% - 25%
  - Net margin: 5% - 18%
  - Leverage: 0.5x - 3.5x EBITDA
- **Validation**: All packs pass strict mode
- **Checks**: Row 3 = 0, Row 81 = 0 for all years

### **How to Use**

1. Click "🎲 Load Random Backup Set"
2. App randomly selects a year range
3. Loads matching TB + GL pair
4. Auto-validates and displays preview
5. Generate model immediately (no manual upload needed)

---

## 🚨 Troubleshooting

### **Common Issues**

#### **"Year0 not found" Error**
- **Cause**: TB doesn't contain 4 distinct years
- **Fix**: Add Year0 snapshot (prior year-end) to your TB
- **Example**: For 2021-2023 statements, add 2020-12-31 snapshot

#### **"TB and GL must be loaded as a set"**
- **Cause**: Only one file uploaded
- **Fix**: Upload both TB and GL files
- **Note**: Generation requires both (no TB-only or GL-only mode)

#### **Row 3 (Balance Sheet) ≠ 0**
- **Possible causes**:
  - Missing balance sheet accounts
  - Incorrect account mapping
  - Data entry errors in TB
- **Debug steps**:
  1. Check mapping stats for "unclassified" accounts
  2. Verify all major BS accounts are mapped
  3. Review TB for obvious errors (negative balances where unexpected)

#### **Row 81 (Cash Tie-out) ≠ 0**
- **Most common cause**: Incomplete Year0
- **Critical Year0 accounts**:
  - Cash (obvious)
  - All working capital (AR, Inventory, AP, Accrued, etc.)
  - PP&E Gross + Accumulated Depreciation
  - Retained Earnings
  - Long-term Debt
- **Debug steps**:
  1. Verify Year0 snapshot exists (check earliest TxnDate in TB)
  2. Confirm Year0-12-31 snapshot is present
  3. Review Year0 account coverage (should include all major BS accounts)
  4. Check that Year0 values are realistic (not all zeros)

#### **GL Transaction Imbalances**
- **Cause**: TransactionID exists but transactions don't balance
- **Common errors**:
  - One-sided tax entries (expense without payable offset)
  - Missing journal entry lines
  - Data export truncated
- **Fix**: Review GL export, ensure all JE lines included

#### **TB Period Imbalances**
- **Cause**: Per-period debits ≠ credits
- **Fix**: Check TB export at source (ensure export is balanced)
- **Note**: TB represents snapshots, so each period must independently balance

### **Tolerance Settings**

The app uses hybrid tolerance to avoid false failures:

```python
tolerance = max(0.01, max_amount * 0.0001)
```

**For $5B transaction total**:
- Absolute tolerance: $0.01 (USD thousands = $10 actual)
- Relative tolerance: $5B * 0.0001 = $500,000
- **Effective tolerance**: $500,000 (larger of the two)

This means:
- ✅ Small datasets: Strict (±$10 in thousands)
- ✅ Large datasets: Scaled (±0.01% of transaction size)

---

## 📁 Project Structure

```
accounting-three-statements/
├── streamlit_app.py              # Main Streamlit UI
├── validation.py                 # TB/GL validation logic
├── mapping.py                    # Account mapping (name + range)
├── excel_writer.py               # Excel template population
├── pdf_export.py                 # PDF report generation
├── ai_summary.py                 # AI/rule-based summaries
├── sample_data.py                # Demo data loader
├── requirements.txt              # Python dependencies
├── assets/
│   ├── templates/
│   │   ├── Financial_Model_TEMPLATE_ZERO_USD_thousands_GAAP.xlsx
│   │   └── Financial_Model_SAMPLE_DEMO_USD_thousands_GAAP.xlsx
│   └── sample_data/
│       ├── backup_tb_2020_2023.csv
│       ├── backup_gl_2020_2023_with_txnid.csv
│       ├── backup_tb_2021_2024.csv
│       ├── backup_gl_2021_2024_with_txnid.csv
│       └── ... (additional backup sets)
├── docs/
│   ├── SAMPLE_DATASET_REQUIREMENTS.md   # Dataset creation guide
│   └── CHANGELOG.md                      # Version history
└── tests/
    └── test_validation.py                # Unit tests
```

---

## 🎯 Architecture Overview

### **Data Flow**

```
Upload TB + GL
    ↓
Normalize Columns (case-insensitive, handle variations)
    ↓
Validate Data Quality
  ├── TB: Period balancing, Year0 detection
  ├── GL: Transaction balancing (if TransactionID)
  └── Common: Missing data, duplicates, outliers
    ↓
Apply User-Selected Fixes (optional)
    ↓
Map Accounts to FSLI Categories
  ├── Primary: Name-based alias matching
  └── Secondary: Account number ranges
    ↓
Calculate Financial Statements
  ├── Income Statement (all years)
  ├── Balance Sheet (all years, using Year0 for deltas)
  └── Cash Flow (Year 2+, indirect method)
    ↓
Compute Reconciliation Checks
  ├── Row 3: Assets - (L + E) = 0
  └── Row 81: Cash tie-out = 0
    ↓
Generate Outputs
  ├── Excel: Label-based template population
  ├── PDF: Professional 3-statement report
  └── Website Preview: Template-driven layout
```

### **Key Design Principles**

1. **Template is Source of Truth**: Layout, labels, formulas from template
2. **Label-Based Writing**: No hardcoded row numbers (searches for labels)
3. **Formula Preservation**: Never overwrites formula cells
4. **Year0 Requirement**: Enforced for proper cash flow reconciliation
5. **Modular Validation**: Separate validators for TB, GL, common issues
6. **Two-Pass Mapping**: Name first, then range fallback

---

## 🔬 Advanced Topics

### **Year0 Synthesis (Demo Data Only)**

For random backup sets, the app can synthesize Year0 if missing:

```python
def add_year0_snapshot(tb_df):
    """
    Copies earliest snapshot, sets TxnDate to Year0-12-31
    Used only for demo/random sets, NOT for user uploads
    """
```

**Why not for uploads?**
- Year0 synthesis requires assumptions (beginning balances)
- Wrong assumptions break Row 81 reconciliation
- Better to require users provide real Year0

### **Cash Flow Calculation (GAAP Indirect Method)**

```python
CFO = Net Income
    + Depreciation & Amortization
    - Δ Accounts Receivable
    - Δ Inventory
    - Δ Prepaid Expenses
    - Δ Other Current Assets
    + Δ Accounts Payable
    + Δ Accrued Payroll
    + Δ Deferred Revenue
    + Δ Interest Payable
    + Δ Other Current Liabilities
    + Δ Income Taxes Payable

CFI = - Capital Expenditures (ΔPP&E Gross)

CFF = + Δ Long-term Debt
      + Stock Issuance
      - Dividends Paid

Net Cash Change = CFO + CFI + CFF
```

**Delta Calculation**: Year(N) - Year(N-1)
- Requires Year0 for Year 1 deltas
- Year 1 CF uses: Year1 values - Year0 values

---

## 📚 Additional Resources

- **[SAMPLE_DATASET_REQUIREMENTS.md](docs/SAMPLE_DATASET_REQUIREMENTS.md)**: Technical guide for creating compliant datasets
- **[CHANGELOG.md](docs/CHANGELOG.md)**: Complete version history and bug fixes
- **[Template Documentation](assets/templates/README.md)**: Excel template structure and formulas

---

## 🤝 Contributing

This project is open for contributions:

1. **Report Issues**: GitHub Issues for bugs or feature requests
2. **Submit PRs**: Follow existing code style
3. **Improve Docs**: Documentation PRs always welcome
4. **Add Mappings**: Contribute account name aliases or range definitions

---

## 📄 License

MIT License - See LICENSE file for details

---

## ⚠️ Disclaimer

This is a demonstration/educational tool:
- ✅ Great for: Learning, prototyping, internal analysis
- ❌ Not for: Audited financials, regulatory filings, production accounting

**Always verify outputs against source data. No warranty provided.**

---

## 🙏 Acknowledgments

Built with:
- **Streamlit**: Web UI framework
- **Pandas**: Data processing
- **OpenPyXL**: Excel manipulation
- **ReportLab**: PDF generation
- **Anthropic Claude**: AI summaries

---

**Questions? Issues? See [Troubleshooting](#-troubleshooting) or open a GitHub issue.**
