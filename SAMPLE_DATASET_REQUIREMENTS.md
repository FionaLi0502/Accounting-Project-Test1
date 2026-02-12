# Sample Dataset Requirements

**Technical Specification for Creating Compliant TB+GL Dataset Packs**

This document defines the requirements for creating backup dataset packs that work correctly with the Three Statements Automation app, particularly focusing on achieving **Row 3 = 0** and **Row 81 = 0** reconciliation checks.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Year0 Construction (Critical)](#year0-construction-critical)
4. [Column Requirements](#column-requirements)
5. [Trial Balance Requirements](#trial-balance-requirements)
6. [General Ledger Requirements](#general-ledger-requirements)
7. [Data Quality Guidelines](#data-quality-guidelines)
8. [Validation Checklist](#validation-checklist)
9. [Common Mistakes](#common-mistakes)
10. [Example Pack Walkthrough](#example-pack-walkthrough)

---

## Overview

### What is a "Dataset Pack"?

A compliant dataset pack consists of:
- **One Trial Balance (TB) CSV file**
- **One General Ledger (GL) CSV file**

Both files must be uploaded together; generation is blocked if only one is present.

### Acceptance Criteria

A dataset pack is considered "clean" and production-ready when:

✅ **Row 3 (Balance Sheet Check) = 0** for all statement years  
✅ **Row 81 (Cash Tie-out Check) = 0** for all statement years  
✅ All validation checks pass (TB balancing, GL balancing, Year0 detection)  
✅ Minimal "unclassified" accounts after mapping  
✅ Realistic financial ratios (for demo/sample packs)

### Year0 Requirement

**Critical**: The TB file MUST contain **4 distinct years**:
- **Year0** (opening snapshot, prior year-end)
- **Year 1** (first statement year)
- **Year 2** (second statement year)
- **Year 3** (third statement year)

**Example**: For statements covering 2021-2023:
- Year0 = 2020 (required for beginning balances and deltas)
- Years 1-3 = 2021, 2022, 2023 (statement years)

---

## File Structure

### Recommended Filename Format

For backup dataset packs stored in `assets/sample_data/`:

```
backup_tb_YYYY_YYYY.csv          # Trial Balance
backup_gl_YYYY_YYYY_with_txnid.csv   # GL with TransactionID
backup_gl_YYYY_YYYY_no_txnid.csv     # GL without TransactionID (optional)
```

**Where**:
- First `YYYY` = First statement year (Year 1, NOT Year0)
- Second `YYYY` = Last statement year (Year 3)

**Example**:
```
backup_tb_2021_2023.csv
backup_gl_2021_2023_with_txnid.csv
```

This pack provides:
- Year0 = 2020
- Statements = 2021, 2022, 2023

### Directory Structure

```
assets/
└── sample_data/
    ├── backup_tb_2020_2023.csv
    ├── backup_gl_2020_2023_with_txnid.csv
    ├── backup_gl_2020_2023_no_txnid.csv
    ├── backup_tb_2021_2024.csv
    ├── backup_gl_2021_2024_with_txnid.csv
    └── ... (additional packs)
```

---

## Year0 Construction (Critical)

### What is Year0?

**Year0** is the opening balance snapshot used to compute:
- Beginning cash for first statement year
- Working capital deltas (AR, Inventory, AP, etc.)
- Accumulated depreciation beginning balance
- Retained earnings roll-forward
- Debt beginning balance

**Without correct Year0, Row 81 (cash tie-out) will fail.**

### Year0 Definition

```
Year0 = (First Statement Year) - 1
```

**Examples**:
- Statements = 2021-2023 → Year0 = 2020
- Statements = 2022-2024 → Year0 = 2021
- Statements = 2024-2026 → Year0 = 2023

### Year0 Date Convention

**Best practice**: Year0 snapshot should be dated **12/31 of Year0** (year-end).

**Example**: For 2021-2023 statements:
- Year0 date = 2020-12-31
- Year 1 dates = Any dates in 2021 (app uses latest per year)
- Year 2 dates = Any dates in 2022
- Year 3 dates = Any dates in 2023

### Which Accounts MUST Have Year0 Values?

To ensure Row 81 = 0, Year0 must include **all balance sheet accounts**:

#### **Critical Accounts (Must Have Year0)**:

**Assets**:
- ✅ Cash and Cash Equivalents
- ✅ Accounts Receivable
- ✅ Inventory
- ✅ Prepaid Expenses
- ✅ Other Current Assets
- ✅ PP&E Gross
- ✅ Accumulated Depreciation (contra-asset)

**Liabilities**:
- ✅ Accounts Payable
- ✅ Accrued Payroll
- ✅ Deferred Revenue
- ✅ Interest Payable
- ✅ Other Current Liabilities
- ✅ Income Taxes Payable
- ✅ Long-term Debt

**Equity**:
- ✅ Common Stock / Paid-in Capital
- ✅ Retained Earnings

#### **Income Statement Accounts (Year0 NOT Required)**:
- Revenue, COGS, Operating Expenses, Interest, Taxes
- These are flow accounts, not needed for Year0 snapshot

### Year0 Construction Logic

#### **Step-by-Step Process**:

1. **Determine Year0**:
   ```
   First Statement Year = 2021
   Year0 = 2021 - 1 = 2020
   ```

2. **Create Year0 Snapshot (2020-12-31)**:
   - Copy or create balance sheet account values as of 12/31/2020
   - Set all `TxnDate` values to `2020-12-31`

3. **Ensure Consistency with Year 1**:
   
   Year0 values must be internally consistent with Year 1 so that:
   
   ```
   Ending Cash (Year 1) = Beginning Cash (Year0) + Net Cash Change (Year 1)
   ```
   
   This requires:
   
   - **Cash**: Year0 cash + Year 1 net cash change = Year 1 ending cash
   - **Working Capital**: Year0 AR/Inventory/AP/etc. create realistic deltas
   - **Accumulated Depreciation**: Year0 + Year 1 depreciation = Year 1 ending
   - **Retained Earnings**: Year0 + Year 1 net income - Year 1 dividends = Year 1 ending

#### **Common Approach (Simplified)**:

For **demo/sample packs**, you can back-calculate Year0 from Year 1:

```python
# Simplified Year0 Construction
Year0_Cash = Year1_Cash - Year1_NetCashChange
Year0_AR = Year1_AR - Year1_Revenue_Change * 0.1  # Assume 10% of revenue change
Year0_Inventory = Year1_Inventory - Year1_COGS_Change * 0.15  # Assume 15% of COGS change
Year0_AccDep = Year1_AccDep - Year1_Depreciation
Year0_RetainedEarnings = Year1_RetainedEarnings - Year1_NetIncome + Year1_Dividends
# ... etc for all BS accounts
```

**Goal**: Make Year0 → Year1 deltas realistic and reconcilable.

---

## Column Requirements

### Required Columns (Both TB and GL)

| Column Name | Data Type | Valid Values | Required | Notes |
|-------------|-----------|--------------|----------|-------|
| **TxnDate** | Date/String | Any valid date | ✅ Yes | Parsed by pandas.to_datetime() |
| **AccountNumber** | Number | Integer or float | ✅ Yes | Chart of accounts code |
| **AccountName** | Text | Any string | ✅ Yes | Account description |
| **Debit** | Number | ≥ 0 | ✅ Yes | Debit amount (non-negative) |
| **Credit** | Number | ≥ 0 | ✅ Yes | Credit amount (non-negative) |
| **TransactionID** | Text/Number | Any | ⚠️ Optional | Journal Entry ID (GL only) |

### Column Naming Flexibility

The app accepts common variations (case-insensitive):

| Standard | Accepted Variations |
|----------|---------------------|
| TxnDate | Transaction_Date, Date, TransDate |
| AccountNumber | Account_Number, Acct_Num, Account, Acct |
| AccountName | Account_Name, Acct_Name, Description |
| Debit | DR |
| Credit | CR |
| TransactionID | Transaction_ID, Txn_ID, TxnID, GLID |

**Column order does NOT matter** - app matches by name.

### Additional Columns

✅ **Extra columns are ignored** - no need to remove them.

---

## Trial Balance Requirements

### Structure

TB represents **snapshots** at points in time (typically month-end or quarter-end).

**Format**:
```csv
TxnDate,AccountNumber,AccountName,Debit,Credit
2020-12-31,1000,Cash and Cash Equivalents,5000000,0
2020-12-31,1100,Accounts Receivable,2000000,0
2020-12-31,2000,Accounts Payable,0,1500000
...
2021-12-31,1000,Cash and Cash Equivalents,5500000,0
2021-12-31,1100,Accounts Receivable,2200000,0
...
```

### Period Balancing Requirement

**Rule**: For each unique `TxnDate`, the following must hold:

```
sum(Debit) ≈ sum(Credit)  within tolerance
```

**Tolerance**:
```python
tolerance = max(0.01, max_amount * 0.0001)
```

**Example**:
- For $5B in debits/credits (USD thousands): tolerance = $500,000
- For $10M in debits/credits: tolerance = $1,000

**Why**: TB represents a snapshot - total debits must equal total credits at each point in time.

### Year Requirements

TB must contain **at least 4 distinct years**:
1. Year0 (at least one snapshot in Year0)
2. Year 1 (at least one snapshot, preferably year-end)
3. Year 2 (at least one snapshot, preferably year-end)
4. Year 3 (at least one snapshot, preferably year-end)

**Best practice**: Include year-end snapshots (12/31) for each year.

### Snapshot Selection Logic

The app uses **latest `TxnDate` within each year** as the year-end snapshot:

```python
# For each year, app finds:
year_end_snapshot = tb_df[tb_df['Year'] == year].sort_values('TxnDate').tail(1)
```

**Implication**: You can include monthly/quarterly snapshots, but only the latest date per year is used for balance sheet.

---

## General Ledger Requirements

### Structure

GL represents **transaction-level detail** (journal entries).

**Format**:
```csv
TxnDate,AccountNumber,AccountName,Debit,Credit,TransactionID
2021-01-15,1000,Cash,10000,0,JE001
2021-01-15,4000,Revenue,0,10000,JE001
2021-01-20,5000,COGS,6000,0,JE002
2021-01-20,1200,Inventory,0,6000,JE002
2021-01-25,6100,Tax Expense,2000,0,JE003
2021-01-25,2450,Taxes Payable,0,2000,JE003
...
```

### Transaction Balancing (With TransactionID)

**Strongly Recommended**: Include `TransactionID` column.

**Rule**: For each unique `TransactionID`:

```
sum(Debit) ≈ sum(Credit)  within tolerance
```

**Why**: Each journal entry must balance - this is standard accounting.

**Validation**:
- If TransactionID exists: Per-transaction balancing checked
- If TransactionID missing: Only overall file balancing checked (weaker validation)

### Overall Balancing (Always Required)

Even without TransactionID:

```
sum(All Debits) ≈ sum(All Credits)  within tolerance
```

### Common GL Mistakes

❌ **One-sided tax entries**:
```csv
# WRONG - Unbalanced
2021-01-25,6100,Tax Expense,2000,0,JE003
# Missing offset: Taxes Payable or Cash
```

✅ **Correct - Balanced**:
```csv
2021-01-25,6100,Tax Expense,2000,0,JE003
2021-01-25,2450,Taxes Payable,0,2000,JE003
```

❌ **Missing journal entry lines**:
- Ensure GL export includes ALL lines for each transaction
- Partial exports break transaction balancing

❌ **Incorrect deduplication**:
- **NEVER** dedupe by `TransactionID` alone (removes valid lines)
- **ONLY** dedupe by full row (all columns identical)

---

## Data Quality Guidelines

### Scale Recommendations (For Demo/Sample Packs)

To create realistic "big company" demo data:

| Metric | Range | Notes |
|--------|-------|-------|
| **Revenue** (per year) | $1B - $20B | In USD thousands: 1,000,000 - 20,000,000 |
| **Gross Margin** | 25% - 55% | (Revenue - COGS) / Revenue |
| **EBITDA Margin** | 8% - 25% | EBITDA / Revenue |
| **Net Margin** | 5% - 18% | Net Income / Revenue |
| **Leverage** | 0.5x - 3.5x EBITDA | LT Debt / EBITDA |
| **Capex** | 1% - 8% of revenue | Capital expenditures |
| **Working Capital** | Varies | AR, Inventory, AP should have realistic turnover |

### "Healthy but Not Perfect"

Good demo packs should show:
- ✅ Year-over-year growth (but not constant)
- ✅ Reasonable margins (not too high or too low)
- ✅ One "challenge area" per pack:
  - Working capital pressure (AR increasing faster than revenue)
  - Margin squeeze (COGS growing faster than revenue)
  - High leverage (Debt/EBITDA > 3x)
  - CapEx heavy (expansion phase)

### Account Coverage

Ensure mappable accounts for all template line items:

**Minimum chart of accounts**:
- Cash (1 account minimum)
- AR, Inventory, Prepaid, Other CA (1 each minimum)
- PP&E Gross, Accumulated Depreciation (1 each minimum)
- AP, Accrued Payroll, Deferred Rev, Other CL, Taxes Payable (1 each)
- LT Debt, Common Stock, Retained Earnings (1 each)
- Revenue, COGS (1 each minimum)
- Operating Expense categories (3-5 accounts)
- Interest Expense, Tax Expense (1 each)

**Realistic charts**: 50-150 accounts for big company.

---

## Validation Checklist

Use this checklist to verify your dataset pack before committing:

### ✅ File Structure
- [ ] TB file exists: `backup_tb_YYYY_YYYY.csv`
- [ ] GL file exists: `backup_gl_YYYY_YYYY_with_txnid.csv`
- [ ] Filenames match year range (statement years, not Year0)
- [ ] Files are CSV format (or Excel .xlsx)

### ✅ Column Requirements
- [ ] TB has: TxnDate, AccountNumber, AccountName, Debit, Credit
- [ ] GL has: TxnDate, AccountNumber, AccountName, Debit, Credit, TransactionID
- [ ] No missing required columns
- [ ] Column names normalized (case-insensitive match)

### ✅ Year0 Requirements
- [ ] TB contains 4 distinct years (Year0 + Years 1-3)
- [ ] Year0 snapshot exists (at least one row dated in Year0)
- [ ] Year0 date is year-end (YYYY-12-31 recommended)
- [ ] Year0 includes all balance sheet accounts
- [ ] Year0 values are realistic (not all zeros)

### ✅ TB Validation
- [ ] TB balances per TxnDate (sum(Debit) ≈ sum(Credit))
- [ ] Each year has at least one snapshot (preferably year-end)
- [ ] Latest snapshot per year represents year-end balances
- [ ] All Debit/Credit values ≥ 0 (no negatives)
- [ ] No rows with both Debit > 0 AND Credit > 0

### ✅ GL Validation
- [ ] GL balances overall (sum(All Debits) ≈ sum(All Credits))
- [ ] If TransactionID present: Each transaction balances
- [ ] All Debit/Credit values ≥ 0 (no negatives)
- [ ] No rows with both Debit > 0 AND Credit > 0
- [ ] TransactionID populated (not blank/null)

### ✅ Account Mapping
- [ ] All major balance sheet accounts present and mappable
- [ ] Revenue and expense categories present
- [ ] Unclassified accounts < 10% (after mapping)
- [ ] Account numbers follow logical ranges (or names are clear)

### ✅ Financial Realism (For Demo Packs)
- [ ] Revenue in realistic range ($1B-$20B for big company)
- [ ] Gross margin reasonable (25%-55%)
- [ ] Net margin positive (5%-18%)
- [ ] Working capital turnover realistic (not zero deltas)
- [ ] Capex present (not zero)
- [ ] Depreciation matches Capex scale roughly

### ✅ Reconciliation Checks
- [ ] **Row 3 = 0** for all statement years (Assets - L - E = 0)
- [ ] **Row 81 = 0** for all statement years (Cash tie-out = 0)
- [ ] Generate model → Download Excel → Verify checks

---

## Common Mistakes

### ❌ Mistake 1: Year0 Missing or Incomplete

**Symptom**: Row 81 ≠ 0 for first statement year only

**Cause**: Year0 snapshot missing or incomplete

**Fix**:
1. Add Year0-12-31 snapshot to TB
2. Include ALL balance sheet accounts in Year0
3. Ensure Year0 values are consistent with Year 1 deltas

---

### ❌ Mistake 2: Year0 = First Statement Year

**Symptom**: "Year0 not found" error or unexpected behavior

**Example**:
```
# WRONG - No Year0
backup_tb_2021_2023.csv contains:
- 2021 data  ← This is Year 1, not Year0!
- 2022 data
- 2023 data
```

**Fix**:
```
# CORRECT - Has Year0
backup_tb_2021_2023.csv contains:
- 2020 data  ← Year0 (opening snapshot)
- 2021 data  ← Year 1 (first statement year)
- 2022 data  ← Year 2
- 2023 data  ← Year 3
```

---

### ❌ Mistake 3: One-Sided Tax/Payroll Entries

**Symptom**: GL transaction imbalance errors

**Wrong GL**:
```csv
2021-12-31,6100,Tax Expense,500000,0,YE001
# Missing offset!
```

**Correct GL**:
```csv
2021-12-31,6100,Tax Expense,500000,0,YE001
2021-12-31,2450,Taxes Payable,0,500000,YE001
```

---

### ❌ Mistake 4: TB Period Imbalance

**Symptom**: "TB does not balance for period YYYY-MM-DD"

**Cause**: Export error, missing accounts, or data entry error

**Check**:
```python
# For each TxnDate in TB:
period_sum = tb[tb['TxnDate'] == date].agg({'Debit': 'sum', 'Credit': 'sum'})
print(period_sum['Debit'] - period_sum['Credit'])  # Should be ≈ 0
```

**Fix**: Review TB export at source system, ensure complete export

---

### ❌ Mistake 5: Deduplicating by TransactionID

**Symptom**: GL transaction imbalances or missing data

**Wrong**:
```python
# WRONG - Removes valid JE lines!
gl_deduped = gl.drop_duplicates(subset=['TransactionID'])
```

**Correct**:
```python
# CORRECT - Only removes true duplicates
gl_deduped = gl.drop_duplicates()  # All columns
```

---

### ❌ Mistake 6: Missing Working Capital Accounts in Year0

**Symptom**: Row 81 ≠ 0, especially for Year 1

**Missing Year0 accounts**:
- Accounts Receivable
- Inventory
- Accounts Payable
- Accrued Payroll

**Impact**: Deltas can't be calculated → cash flow breaks

**Fix**: Ensure Year0 snapshot includes ALL working capital accounts

---

## Example Pack Walkthrough

### Scenario: Create 2022-2024 Statement Pack

**Goal**: Statements for 2022, 2023, 2024 (3 years)

**Step 1: Determine Year0**
```
First Statement Year = 2022
Year0 = 2022 - 1 = 2021
```

**Step 2: Create TB File**

Filename: `backup_tb_2022_2024.csv`

**Required snapshots**:
```
2021-12-31  ← Year0 snapshot (critical!)
2022-12-31  ← Year 1 year-end
2023-12-31  ← Year 2 year-end
2024-12-31  ← Year 3 year-end
```

**Sample TB content**:
```csv
TxnDate,AccountNumber,AccountName,Debit,Credit
2021-12-31,1000,Cash,5000,0
2021-12-31,1100,Accounts Receivable,2000,0
2021-12-31,2000,Accounts Payable,0,1500
2021-12-31,3100,Retained Earnings,0,5500
2022-12-31,1000,Cash,5500,0
2022-12-31,1100,Accounts Receivable,2200,0
2022-12-31,2000,Accounts Payable,0,1600
2022-12-31,3100,Retained Earnings,0,6100
... (continue for 2023, 2024)
```

**Step 3: Create GL File**

Filename: `backup_gl_2022_2024_with_txnid.csv`

**Date range**: 2022-01-01 through 2024-12-31 (statement years only, NOT Year0)

**Sample GL content**:
```csv
TxnDate,AccountNumber,AccountName,Debit,Credit,TransactionID
2022-01-15,1000,Cash,10000,0,JE2022001
2022-01-15,4000,Revenue,0,10000,JE2022001
2022-01-20,5000,COGS,6000,0,JE2022002
2022-01-20,1200,Inventory,0,6000,JE2022002
2022-12-31,6100,Tax Expense,500,0,JE2022999
2022-12-31,2450,Taxes Payable,0,500,JE2022999
... (continue for all 2022 transactions, then 2023, 2024)
```

**Step 4: Validate**

Run through checklist:
- [x] TB has 4 years (2021, 2022, 2023, 2024)
- [x] Year0 (2021) snapshot exists at 2021-12-31
- [x] TB balances per period
- [x] GL transactions balance per TransactionID
- [x] GL overall balances

**Step 5: Test in App**

1. Load pack: `backup_tb_2022_2024.csv` + `backup_gl_2022_2024_with_txnid.csv`
2. Generate model
3. **Verify**:
   - Row 3 = 0 for 2022, 2023, 2024
   - Row 81 = 0 for 2022, 2023, 2024

**If checks fail**: Debug Year0 consistency, review working capital deltas.

---

## Testing Your Pack

### Quick Test Script

```python
import pandas as pd

# Load files
tb = pd.read_csv('backup_tb_2022_2024.csv')
gl = pd.read_csv('backup_gl_2022_2024_with_txnid.csv')

# Check 1: TB has 4 years
tb['TxnDate'] = pd.to_datetime(tb['TxnDate'])
years = sorted(tb['TxnDate'].dt.year.unique())
print(f"TB Years: {years}")
assert len(years) >= 4, "TB must have at least 4 years!"

# Check 2: TB balances per period
for date in tb['TxnDate'].unique():
    period = tb[tb['TxnDate'] == date]
    diff = period['Debit'].sum() - period['Credit'].sum()
    assert abs(diff) < 1.0, f"TB imbalance on {date}: {diff}"
print("✓ TB balances per period")

# Check 3: GL balances per transaction
for txn in gl['TransactionID'].unique():
    txn_data = gl[gl['TransactionID'] == txn]
    diff = txn_data['Debit'].sum() - txn_data['Credit'].sum()
    assert abs(diff) < 0.01, f"Transaction {txn} imbalance: {diff}"
print("✓ GL balances per transaction")

# Check 4: GL overall balance
diff = gl['Debit'].sum() - gl['Credit'].sum()
assert abs(diff) < 1.0, f"GL overall imbalance: {diff}"
print("✓ GL overall balance")

print("\n✅ All checks passed! Pack ready for use.")
```

---

## Summary

Creating compliant dataset packs requires:

1. ✅ **Year0 snapshot** (critical for Row 81 reconciliation)
2. ✅ **4-year TB** (Year0 + 3 statement years)
3. ✅ **Balanced TB** (per period)
4. ✅ **Balanced GL** (per transaction if TransactionID present)
5. ✅ **Complete account coverage** (all balance sheet accounts in Year0)
6. ✅ **Realistic financial data** (for demo packs)

**Most common failure**: Incomplete or missing Year0 → Row 81 ≠ 0

**Quick validation**: Generate model → Check Row 3 and Row 81 = 0

---

**Questions? Issues?**  
See main [README.md](../README.md) or open a GitHub issue.
