"""
Three Statements Automation - Refactored Main Application
Supports Trial Balance and GL Activity uploads with intelligent downgrade behavior
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import os
from typing import Dict, List, Tuple, Optional

# Import custom modules
from validation import (normalize_column_headers, check_required_columns,
                       validate_trial_balance, validate_gl_activity,
                       validate_common_issues, apply_auto_fixes,
                       validate_strict_usd, validate_debit_credit)
from mapping import map_accounts, get_mapping_stats
from excel_writer import (write_financial_data_to_template, 
                          calculate_financial_statements,
                          validate_template_structure)
from pdf_export import create_pdf_report
from ai_summary import generate_ai_summary, summarize_validation_issues
from sample_data import (load_sample_tb, load_sample_gl, load_random_backup_pair,
                         get_template_path, list_available_datasets,
                         get_sample_tb_file, get_sample_gl_files)

# Page config
st.set_page_config(
    page_title="Three Statements Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.validation-critical{background-color:#f8d7da;border-left:4px solid #dc3545;padding:1rem;margin:0.5rem 0;border-radius:4px}
.validation-warning{background-color:#fff3cd;border-left:4px solid #ffc107;padding:1rem;margin:0.5rem 0;border-radius:4px}
.validation-info{background-color:#d1ecf1;border-left:4px solid #17a2b8;padding:1rem;margin:0.5rem 0;border-radius:4px}
.success-box{background-color:#d4edda;border-left:4px solid #28a745;padding:1rem;margin:0.5rem 0;border-radius:4px}
.info-box{background-color:#e7f3ff;border-left:4px solid #2196F3;padding:1rem;margin:0.5rem 0;border-radius:4px}
.warning-banner{background-color:#fff3cd;border:2px solid #ffc107;padding:1rem;margin:1rem 0;border-radius:8px;text-align:center;font-weight:bold}
</style>
""", unsafe_allow_html=True)

# Initialize session state
for key in ['tb_data', 'gl_data', 'tb_cleaned', 'gl_cleaned', 'tb_issues', 'gl_issues',
            'issue_selections', 'financial_data', 'changes_log', 'excel_output', 'pdf_output',
            'validation_complete', 'model_generated', 'unit_selection', 'has_tb', 'has_gl']:
    if key not in st.session_state:
        if key in ['tb_issues', 'gl_issues', 'changes_log']:
            st.session_state[key] = []
        elif key == 'issue_selections':
            st.session_state[key] = {}
        elif key == 'unit_selection':
            st.session_state[key] = 'USD dollars'
        elif key in ['has_tb', 'has_gl']:
            st.session_state[key] = False
        else:
            st.session_state[key] = None

for key in ['validation_complete', 'model_generated']:
    if key not in st.session_state:
        st.session_state[key] = False

# Currency conversion
EXCHANGE_RATES = {
    'USD': 1.0, 'EUR': 1.08, 'GBP': 1.27, 'JPY': 0.0067, 'CNY': 0.14,
    'CAD': 0.71, 'AUD': 0.64, 'CHF': 1.13, 'INR': 0.012, 'MXN': 0.058
}

def detect_currency(df):
    """Detect currency from DataFrame"""
    if 'Currency' in df.columns and not df['Currency'].isna().all():
        return df['Currency'].mode()[0]
    return 'USD'

def convert_to_usd(df):
    """Convert amounts to USD"""
    df = df.copy()
    src_currency = detect_currency(df)
    
    if src_currency != 'USD':
        rate = EXCHANGE_RATES.get(src_currency, 1.0)
        for col in ['Amount', 'Debit', 'Credit']:
            if col in df.columns:
                df[col] = df[col] * rate
        st.info(f"💱 Converted from {src_currency} to USD (rate: {rate})")
    
    return df


def main():
    """Main application"""
    
    # Header
    st.title("📊 Three Statements Automation")
    st.markdown("**AI-Powered Financial Statement Generator**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Unit selection (REQUIRED)
        st.subheader("Data Unit")
        unit_selection = st.radio(
            "My GL amounts are in:",
            options=['USD dollars', 'USD thousands'],
            index=0 if st.session_state.unit_selection == 'USD dollars' else 1,
            help="Select the unit of your source data. The template uses USD thousands."
        )
        st.session_state.unit_selection = unit_selection
        
        # Calculate scale factor
        if unit_selection == 'USD dollars':
            unit_scale = 1000.0  # Divide by 1000 to convert to thousands
        else:
            unit_scale = 1.0  # Already in thousands
        
        st.markdown("---")
        
        # Sample data buttons
        st.subheader("📥 Sample Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Download Sample Model", use_container_width=True):
                try:
                    demo_path = get_template_path('demo')
                    with open(demo_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Demo Model",
                            data=f,
                            file_name="Financial_Model_SAMPLE_DEMO.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            # Download Sample Data dropdown
            with st.expander("📊 Download Sample Data", expanded=False):
                st.markdown("**Choose data to download:**")
                
                # Download Sample TB
                try:
                    tb_bytes, tb_filename = get_sample_tb_file()
                    st.download_button(
                        label="📥 Download Sample Trial Balance (TB) Data",
                        data=tb_bytes,
                        file_name=tb_filename,
                        mime="text/csv",
                        use_container_width=True,
                        help="Sample Trial Balance with month-end balances"
                    )
                except Exception as e:
                    st.error(f"TB download error: {str(e)}")
                
                st.markdown("---")
                
                # Download Sample GL
                try:
                    gl_files = get_sample_gl_files()
                    
                    st.markdown("**General Ledger (GL) Activity samples:**")
                    st.caption("TransactionID is optional; these samples include it for demonstration.")
                    
                    for gl_bytes, gl_filename in gl_files:
                        label = "📥 GL with TransactionID" if "with_txnid" in gl_filename else "📥 GL without TransactionID"
                        st.download_button(
                            label=label,
                            data=gl_bytes,
                            file_name=gl_filename,
                            mime="text/csv",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"GL download error: {str(e)}")
        
        if st.button("🎲 Load Random Test Dataset", use_container_width=True):
            try:
                tb_df, gl_df, name = load_random_backup_pair()
                st.session_state.tb_data = tb_df
                st.session_state.gl_data = gl_df
                st.session_state.has_tb = True
                st.session_state.has_gl = True
                st.info(f"📦 Loaded TB + GL pair: {name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading random dataset: {str(e)}")
        
        st.markdown("---")
        
        # Info box
        st.info("""
        **Upload Tips:**
        
        ✅ **Best results:** Upload Trial Balance (ending balances) including both BS and P&L accounts.
        
        ⚠️ **GL Activity only:** Works well for Income Statement. Balance Sheet and Cash Flow may be incomplete.
        
        💡 **Required columns:** TxnDate, AccountNumber, AccountName, Debit, Credit
        
        🔧 **TransactionID:** Optional but recommended for better validation
        """)
    
    # Main content area
    
    # Upload section
    st.header("1️⃣ Upload Data")
    
    # Info box about workflow
    st.markdown("""
    <div class="info-box">
    <strong>📘 How to use:</strong><br>
    • Upload Trial Balance for complete 3-statement model (recommended)<br>
    • Upload GL Activity for transaction-level validation and Income Statement<br>
    • Upload both for best results
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trial Balance (TB)")
        tb_file = st.file_uploader(
            "Upload Trial Balance CSV/Excel",
            type=['csv', 'xlsx'],
            key='tb_upload',
            help="Ending balances by account. Required for complete Balance Sheet and Cash Flow."
        )
        
        if tb_file:
            try:
                if tb_file.name.endswith('.csv'):
                    df = pd.read_csv(tb_file)
                else:
                    df = pd.read_excel(tb_file)
                
                df = normalize_column_headers(df)
                df = convert_to_usd(df)
                st.session_state.tb_data = df
                st.session_state.has_tb = True
                st.success(f"✅ Loaded {len(df)} Trial Balance entries")
                
                # Preview
                with st.expander("Preview TB Data"):
                    st.dataframe(df.head(10))
                
            except Exception as e:
                st.error(f"Error loading TB: {str(e)}")
    
    with col2:
        st.subheader("General Ledger (GL) Activity")
        gl_file = st.file_uploader(
            "Upload General Ledger CSV/Excel",
            type=['csv', 'xlsx'],
            key='gl_upload',
            help="Transaction-level detail. Optional but recommended for validation."
        )
        
        if gl_file:
            try:
                if gl_file.name.endswith('.csv'):
                    df = pd.read_csv(gl_file)
                else:
                    df = pd.read_excel(gl_file)
                
                df = normalize_column_headers(df)
                df = convert_to_usd(df)
                st.session_state.gl_data = df
                st.session_state.has_gl = True
                st.success(f"✅ Loaded {len(df)} GL transactions")
                
                # Preview
                with st.expander("Preview GL Data"):
                    st.dataframe(df.head(10))
                
            except Exception as e:
                st.error(f"Error loading GL: {str(e)}")
    
    # Sample data format example
    st.markdown("---")
    with st.expander("📋 Sample Data Format Example", expanded=False):
        st.markdown("**Required columns (TB and GL have similar format):**")
        
        sample_data = {
            'TxnDate': ['2024-01-31', '2024-01-31', '2024-02-15', '2024-02-15'],
            'AccountNumber': [1000, 4000, 1100, 5000],
            'AccountName': ['Cash', 'Revenue', 'Accounts Receivable', 'COGS'],
            'Debit': [5000.00, 0.00, 1200.00, 800.00],
            'Credit': [0.00, 5000.00, 0.00, 0.00],
            'TransactionID': [1001, 1001, 1002, 1003],
        }
        
        st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
        
        st.markdown("""
        **Column notes:**
        - **TxnDate:** Date of transaction (required)
        - **AccountNumber:** Account code (required)
        - **AccountName:** Account description (required)
        - **Debit/Credit:** Transaction amounts (required, both must be ≥ 0)
        - **TransactionID:** Journal Entry ID (**not required for TB, optional for GL**)
        - **Currency:** USD assumed if not specified (strict USD mode enforced)
        
        **Key rules:**
        - Column names are **case-insensitive** and order-independent
        - Extra columns are ignored
        - Each row should be single-sided (either Debit OR Credit > 0, not both)
        """)
    
    # Check what we have
    has_tb = st.session_state.has_tb and st.session_state.tb_data is not None
    has_gl = st.session_state.has_gl and st.session_state.gl_data is not None
    
    if not has_tb and not has_gl:
        st.info("👆 Please upload Trial Balance and/or GL Activity data to continue")
        return
    
    # Downgrade warning
    if has_gl and not has_tb:
        st.markdown("""
        <div class="warning-banner">
        ⚠️ DOWNGRADED MODE: Only GL Activity uploaded<br>
        Income Statement: ✅ Available<br>
        Balance Sheet: ⚠️ Incomplete (opening balances missing)<br>
        Cash Flow: ⚠️ Incomplete (Trial Balance required)
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Validation section
    st.header("2️⃣ Data Validation")
    
    all_issues = []
    
    # Validate TB if present
    if has_tb:
        st.subheader("Trial Balance Validation")
        
        # Strict USD validation
        usd_issues = validate_strict_usd(st.session_state.tb_data)
        
        # Debit/Credit validation
        debit_credit_issues = validate_debit_credit(st.session_state.tb_data)
        
        # TB balance validation
        tb_issues = validate_trial_balance(st.session_state.tb_data)
        
        # Common issues
        tb_common_issues = validate_common_issues(st.session_state.tb_data)
        
        # Combine all TB issues
        all_tb_issues = usd_issues + debit_credit_issues + tb_issues + tb_common_issues
        st.session_state.tb_issues = all_tb_issues
        all_issues.extend(all_tb_issues)
        
        # Check for critical USD issues (blocks generation)
        has_critical_usd_error = any(issue.get('severity') == 'Critical' and issue.get('category') == 'Currency' 
                                      for issue in all_tb_issues)
        
        if all_tb_issues:
            st.warning(f"⚠️ Found {len(all_tb_issues)} issue(s) in Trial Balance")
            
            for i, issue in enumerate(all_tb_issues):
                severity_class = f"validation-{issue['severity'].lower()}"
                with st.expander(f"{issue['severity']}: {issue['issue']}", expanded=False):
                    st.markdown(f"**Impact:** {issue['impact']}")
                    st.markdown(f"**Suggestion:** {issue['suggestion']}")
                    
                    if 'detail' in issue:
                        st.markdown(f"**Details:** {issue['detail']}")
                    
                    if 'sample_data' in issue and issue['sample_data'] is not None:
                        st.dataframe(issue['sample_data'])
                    
                    # Checkbox for auto-fix (NOT auto-checked, user must select)
                    # Info-only issues (like "Unusual amounts") should NOT have checkboxes
                    if issue['auto_fix'] and issue['severity'] != 'Info':
                        key = f"tb_fix_{i}"
                        if key not in st.session_state.issue_selections:
                            st.session_state.issue_selections[key] = False  # Default unchecked
                        
                        st.session_state.issue_selections[key] = st.checkbox(
                            "Apply this fix",
                            value=st.session_state.issue_selections[key],
                            key=f"checkbox_{key}"
                        )
        else:
            st.success("✅ No issues found in Trial Balance")
    
    # Validate GL if present
    if has_gl:
        st.subheader("General Ledger (GL) Activity Validation")
        
        # Strict USD validation
        gl_usd_issues = validate_strict_usd(st.session_state.gl_data)
        
        # Debit/Credit validation
        gl_debit_credit_issues = validate_debit_credit(st.session_state.gl_data)
        
        # GL activity validation
        gl_issues = validate_gl_activity(st.session_state.gl_data)
        
        # Common issues
        gl_common_issues = validate_common_issues(st.session_state.gl_data)
        
        # Combine all GL issues
        all_gl_issues = gl_usd_issues + gl_debit_credit_issues + gl_issues + gl_common_issues
        st.session_state.gl_issues = all_gl_issues
        all_issues.extend(all_gl_issues)
        
        # Check for critical USD issues
        has_critical_usd_error_gl = any(issue.get('severity') == 'Critical' and issue.get('category') == 'Currency' 
                                         for issue in all_gl_issues)
        
        if all_gl_issues:
            st.warning(f"⚠️ Found {len(all_gl_issues)} issue(s) in GL Activity")
            
            for i, issue in enumerate(all_gl_issues):
                with st.expander(f"{issue['severity']}: {issue['issue']}", expanded=False):
                    st.markdown(f"**Impact:** {issue['impact']}")
                    st.markdown(f"**Suggestion:** {issue['suggestion']}")
                    
                    if 'detail' in issue:
                        st.markdown(f"**Details:** {issue['detail']}")
                    
                    if 'sample_data' in issue and issue['sample_data'] is not None:
                        st.dataframe(issue['sample_data'])
                    
                    # Checkbox for auto-fix (NOT auto-checked, no checkbox for Info-only)
                    if issue['auto_fix'] and issue['severity'] != 'Info':
                        key = f"gl_fix_{i}"
                        if key not in st.session_state.issue_selections:
                            st.session_state.issue_selections[key] = False  # Default unchecked
                        
                        st.session_state.issue_selections[key] = st.checkbox(
                            "Apply this fix",
                            value=st.session_state.issue_selections[key],
                            key=f"checkbox_{key}"
                        )
        else:
            st.success("✅ No issues found in GL Activity")
    
    # Fix buttons
    if all_issues:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Accept All Fixes", use_container_width=True):
                for key in st.session_state.issue_selections:
                    st.session_state.issue_selections[key] = True
                st.rerun()
        
        with col2:
            if st.button("❌ Decline All Fixes", use_container_width=True):
                for key in st.session_state.issue_selections:
                    st.session_state.issue_selections[key] = False
                st.rerun()
        
        with col3:
            if st.button("🔧 Apply Selected Fixes", type="primary", use_container_width=True):
                # Check for blocking Critical issues (e.g., multi-currency in strict mode)
                critical_currency_issues = [
                    issue for issue in all_issues 
                    if issue.get('severity') == 'Critical' and issue.get('category') == 'Currency'
                ]
                
                if critical_currency_issues:
                    st.error("❌ Cannot proceed: Multi-currency or non-USD data detected. STRICT USD MODE enforced.")
                    return
                
                # Apply fixes to TB
                if has_tb:
                    selected_tb_fixes = []
                    for i, issue in enumerate(st.session_state.tb_issues):
                        if issue['auto_fix'] and issue['severity'] != 'Info':
                            key = f"tb_fix_{i}"
                            if st.session_state.issue_selections.get(key, False):
                                selected_tb_fixes.append(issue['auto_fix'])
                    
                    if selected_tb_fixes:
                        tb_cleaned, tb_changes = apply_auto_fixes(
                            st.session_state.tb_data,
                            selected_tb_fixes
                        )
                        st.session_state.tb_cleaned = tb_cleaned
                        st.session_state.changes_log.extend(
                            [f"TB: {change}" for change in tb_changes]
                        )
                    else:
                        # No fixes selected, use original data
                        st.session_state.tb_cleaned = st.session_state.tb_data
                
                # Apply fixes to GL
                if has_gl:
                    selected_gl_fixes = []
                    for i, issue in enumerate(st.session_state.gl_issues):
                        if issue['auto_fix'] and issue['severity'] != 'Info':
                            key = f"gl_fix_{i}"
                            if st.session_state.issue_selections.get(key, False):
                                selected_gl_fixes.append(issue['auto_fix'])
                    
                    if selected_gl_fixes:
                        gl_cleaned, gl_changes = apply_auto_fixes(
                            st.session_state.gl_data,
                            selected_gl_fixes
                        )
                        st.session_state.gl_cleaned = gl_cleaned
                        st.session_state.changes_log.extend(
                            [f"GL: {change}" for change in gl_changes]
                        )
                    else:
                        # No fixes selected, use original data
                        st.session_state.gl_cleaned = st.session_state.gl_data
                
                st.session_state.validation_complete = True
                
                if st.session_state.changes_log:
                    st.success("✅ Fixes applied successfully!")
                    with st.expander("View Changes"):
                        for change in st.session_state.changes_log:
                            st.write(f"• {change}")
                else:
                    st.info("ℹ️ No fixes selected. Proceeding with original data.")
                
                st.rerun()
    else:
        # No issues, can proceed directly
        st.session_state.validation_complete = True
        st.session_state.tb_cleaned = st.session_state.tb_data
        st.session_state.gl_cleaned = st.session_state.gl_data
    
    st.markdown("---")
    
    # Generate financial model
    st.header("3️⃣ Generate Financial Model")
    
    if not st.session_state.validation_complete:
        st.info("Complete validation and apply fixes first")
        return
    
    if st.button("🚀 Generate 3-Statement Model", type="primary", use_container_width=True):
        with st.spinner("Generating financial statements..."):
            try:
                # CRITICAL: Use TB as source of truth when both TB and GL are present
                # GL is used for validation only, NOT added to TB totals
                if has_tb:
                    data_to_use = st.session_state.tb_cleaned if st.session_state.tb_cleaned is not None else st.session_state.tb_data
                    data_source = "Trial Balance"
                elif has_gl:
                    data_to_use = st.session_state.gl_cleaned if st.session_state.gl_cleaned is not None else st.session_state.gl_data
                    data_source = "General Ledger"
                else:
                    st.error("❌ No data available. Please upload Trial Balance and/or General Ledger data.")
                    return
                
                if data_to_use is None or len(data_to_use) == 0:
                    st.error("❌ No clean data available. This may be due to:")
                    st.markdown("""
                    - All rows filtered out by applied fixes
                    - Required columns missing
                    - All dates invalid
                    
                    **Next steps:** Try declining all fixes and re-validate, or re-upload your data.
                    """)
                    return
                
                st.info(f"📊 Using **{data_source}** as source of truth for financial statements")
                
                # Map accounts
                mapped_data = map_accounts(data_to_use)
                
                # Get mapping stats
                mapping_stats = get_mapping_stats(mapped_data)
                
                # Calculate financial statements
                financial_data = calculate_financial_statements(
                    mapped_data,
                    is_trial_balance=has_tb
                )
                
                st.session_state.financial_data = financial_data
                st.session_state.model_generated = True
                
                # Generate Excel
                template_path = get_template_path('zero')
                excel_output = write_financial_data_to_template(
                    template_path,
                    financial_data,
                    unit_scale
                )
                st.session_state.excel_output = excel_output
                
                # Generate AI summary
                has_cash_flow = len(financial_data) >= 2 and has_tb
                ai_summary, used_ai = generate_ai_summary(
                    financial_data,
                    has_balance_sheet=has_tb,
                    has_cash_flow=has_cash_flow
                )
                
                # Generate PDF
                pdf_output = create_pdf_report(
                    financial_data,
                    ai_summary=ai_summary,
                    unit_label=st.session_state.unit_selection
                )
                st.session_state.pdf_output = pdf_output
                
                st.success("✅ Financial model generated successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating model: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display results if generated
    if st.session_state.model_generated and st.session_state.financial_data:
        st.markdown("---")
        st.header("4️⃣ Results")
        
        financial_data = st.session_state.financial_data
        years = sorted(financial_data.keys())
        
        # Income Statement
        st.subheader("📈 Income Statement")
        
        # Build table with years as columns, line items as rows
        line_items = ['Revenue', 'COGS', 'Gross Profit', 'Operating Expenses', 'EBIT', 'Interest Expense', 'Tax Expense', 'Net Income']
        is_table = {'Line Item': line_items}
        
        for year in years:
            data = financial_data[year]
            revenue = data.get('revenue', 0)
            cogs = data.get('cogs', 0)
            gross_profit = revenue - cogs
            opex = sum([data.get(k, 0) for k in ['distribution_expenses', 'marketing_admin', 'research_dev', 'depreciation_expense']])
            ebit = gross_profit - opex
            interest = data.get('interest_expense', 0)
            tax = data.get('tax_expense', 0)
            net_income = ebit - interest - tax
            
            is_table[str(year)] = [revenue, cogs, gross_profit, opex, ebit, interest, tax, net_income]
        
        is_df = pd.DataFrame(is_table)
        st.dataframe(is_df, use_container_width=True, hide_index=True)
        
        # Balance Sheet (if TB available)
        if has_tb:
            st.subheader("💰 Balance Sheet")
            
            # Build table with years as columns, line items as rows
            bs_line_items = ['Cash', 'Accounts Receivable', 'Inventory', 'Total Current Assets', 
                           'PP&E (net)', 'Total Assets',
                           'Accounts Payable', 'Accrued Liabilities', 'Total Current Liabilities',
                           'Long-term Debt', 'Total Liabilities',
                           'Common Stock', 'Retained Earnings', 'Total Equity']
            
            bs_table = {'Line Item': bs_line_items}
            
            for year in years:
                data = financial_data[year]
                cash = data.get('cash', 0)
                ar = data.get('accounts_receivable', 0)
                inv = data.get('inventory', 0)
                current_assets = cash + ar + inv + data.get('prepaid_expenses', 0) + data.get('other_current_assets', 0)
                ppe_net = data.get('ppe_gross', 0) - data.get('accumulated_depreciation', 0)
                total_assets = current_assets + ppe_net
                
                ap = data.get('accounts_payable', 0)
                accrued = data.get('accrued_payroll', 0) + data.get('other_current_liabilities', 0)
                current_liab = ap + accrued + data.get('deferred_revenue', 0) + data.get('interest_payable', 0) + data.get('income_taxes_payable', 0)
                ltd = data.get('long_term_debt', 0)
                total_liab = current_liab + ltd
                
                stock = data.get('common_stock', 0)
                re = data.get('retained_earnings', 0)
                total_equity = stock + re
                
                bs_table[str(year)] = [cash, ar, inv, current_assets, ppe_net, total_assets,
                                      ap, accrued, current_liab, ltd, total_liab,
                                      stock, re, total_equity]
            
            bs_df = pd.DataFrame(bs_table)
            st.dataframe(bs_df, use_container_width=True, hide_index=True)
        else:
            st.info("⚠️ Balance Sheet incomplete (Trial Balance not provided)")
        
        # Cash Flow (if multi-year TB)
        if has_tb and len(years) >= 2:
            st.subheader("💵 Cash Flow Statement (GAAP Indirect Method)")
            
            # Build table with years as columns (skip first year, show Year 2+)
            cf_years = years[1:]  # Cash flow requires deltas, so start from year 2
            cf_line_items = ['Net Income', 'Depreciation & Amortization',
                           'Change in AR', 'Change in Inventory', 'Change in AP', 'Change in Accrued Liabilities',
                           'Cash from Operations',
                           'CapEx', 'Cash from Investing',
                           'Debt Issuance', 'Dividends Paid', 'Cash from Financing',
                           'Net Change in Cash']
            
            cf_table = {'Line Item': cf_line_items}
            
            for i, year in enumerate(cf_years):
                prev_year = years[i]
                curr_data = financial_data[year]
                prev_data = financial_data[prev_year]
                
                # Operating activities
                net_income = curr_data.get('revenue', 0) - curr_data.get('cogs', 0) - sum([curr_data.get(k, 0) for k in ['distribution_expenses', 'marketing_admin', 'research_dev', 'depreciation_expense', 'interest_expense', 'tax_expense']])
                depreciation = curr_data.get('depreciation_expense', 0)
                
                # Working capital changes
                delta_ar = -(curr_data.get('accounts_receivable', 0) - prev_data.get('accounts_receivable', 0))
                delta_inv = -(curr_data.get('inventory', 0) - prev_data.get('inventory', 0))
                delta_ap = curr_data.get('accounts_payable', 0) - prev_data.get('accounts_payable', 0)
                delta_accrued = (curr_data.get('accrued_payroll', 0) - prev_data.get('accrued_payroll', 0))
                
                cfo = net_income + depreciation + delta_ar + delta_inv + delta_ap + delta_accrued
                
                # Investing activities
                capex = -(curr_data.get('ppe_gross', 0) - prev_data.get('ppe_gross', 0))
                cfi = capex
                
                # Financing activities
                debt_change = curr_data.get('long_term_debt', 0) - prev_data.get('long_term_debt', 0)
                dividends = -(curr_data.get('dividends_paid', 0))
                cff = debt_change + dividends
                
                net_change_cash = cfo + cfi + cff
                
                cf_table[str(year)] = [net_income, depreciation, delta_ar, delta_inv, delta_ap, delta_accrued,
                                      cfo, capex, cfi, debt_change, dividends, cff, net_change_cash]
            
            cf_df = pd.DataFrame(cf_table)
            st.dataframe(cf_df, use_container_width=True, hide_index=True)
        else:
            st.info("⚠️ Cash Flow Statement requires multi-year Trial Balance data")
        
        # Downloads
        st.markdown("---")
        st.subheader("📥 Download Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.excel_output:
                st.download_button(
                    label="📊 Download Excel Model",
                    data=st.session_state.excel_output,
                    file_name=f"Financial_Model_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        with col2:
            if st.session_state.pdf_output:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=st.session_state.pdf_output,
                    file_name=f"Financial_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p><strong>⚠️ Early Demo Notice</strong></p>
    <p>This is an early-stage demo built as part of a self-learning experiment.</p>
    <p>For educational purposes only - not intended for production use.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
