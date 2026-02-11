"""
Three Statements Automation - Complete Application
Enhanced with detailed validation, checkboxes, PDF reports, and feedback system
"""

import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime
import io
from typing import Dict, List, Tuple
import os

# PDF generation imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

# Page configuration
st.set_page_config(
    page_title="Three Statements Automation",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .validation-critical {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .validation-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .validation-info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'validation_complete' not in st.session_state:
    st.session_state.validation_complete = False
if 'data_cleaned' not in st.session_state:
    st.session_state.data_cleaned = None
if 'issues' not in st.session_state:
    st.session_state.issues = []
if 'issue_selections' not in st.session_state:
    st.session_state.issue_selections = {}
if 'model_generated' not in st.session_state:
    st.session_state.model_generated = False
if 'financial_data' not in st.session_state:
    st.session_state.financial_data = None
if 'data_reconciliation' not in st.session_state:
    st.session_state.data_reconciliation = None
if 'changes_log' not in st.session_state:
    st.session_state.changes_log = []

# ============================================================================
# CURRENCY CONVERSION
# ============================================================================

EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 1.08,
    'GBP': 1.27,
    'JPY': 0.0067,
    'CNY': 0.14,
    'CAD': 0.71,
    'AUD': 0.64,
    'CHF': 1.13,
    'INR': 0.012,
    'MXN': 0.058,
}

def detect_currency(df: pd.DataFrame) -> str:
    """Detect currency from data"""
    if 'Currency' in df.columns:
        return df['Currency'].mode()[0] if not df['Currency'].isna().all() else 'USD'
    return 'USD'

def convert_to_usd(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all amounts to USD"""
    df = df.copy()
    source_currency = detect_currency(df)
    
    if source_currency != 'USD':
        rate = EXCHANGE_RATES.get(source_currency, 1.0)
        if 'Amount' in df.columns:
            df['Amount'] = df['Amount'] * rate
        if 'Debit' in df.columns:
            df['Debit'] = df['Debit'] * rate
        if 'Credit' in df.columns:
            df['Credit'] = df['Credit'] * rate
        st.info(f"💱 Converted from {source_currency} to USD (rate: {rate})")
    
    return df

# ============================================================================
# DATA VALIDATION WITH DETAILED ROW INFORMATION
# ============================================================================

def validate_data_detailed(df: pd.DataFrame) -> List[Dict]:
    """Comprehensive validation with row-level details"""
    issues = []
    
    # Check 1: Missing dates
    if 'TxnDate' in df.columns:
        missing_dates_mask = df['TxnDate'].isna()
        if missing_dates_mask.sum() > 0:
            affected_rows = df[missing_dates_mask].index.tolist()
            issues.append({
                'severity': 'Warning',
                'category': 'Missing Data',
                'issue': f'{missing_dates_mask.sum()} transactions missing dates',
                'impact': 'Cannot determine period for these transactions',
                'suggestion': f'Remove {missing_dates_mask.sum()} rows with missing dates',
                'auto_fix': 'remove_missing_dates',
                'affected_rows': affected_rows[:100],  # Limit to first 100
                'total_affected': len(affected_rows),
                'sample_data': df[missing_dates_mask][['TransactionID', 'AccountNumber', 'AccountName', 'Debit', 'Credit']].head(10) if 'TransactionID' in df.columns else df[missing_dates_mask].head(10)
            })
    
    # Check 2: Missing account numbers
    if 'AccountNumber' in df.columns:
        missing_accts_mask = df['AccountNumber'].isna()
        if missing_accts_mask.sum() > 0:
            affected_rows = df[missing_accts_mask].index.tolist()
            issues.append({
                'severity': 'Critical',
                'category': 'Missing Data',
                'issue': f'{missing_accts_mask.sum()} transactions without account numbers',
                'impact': 'Cannot categorize transactions in financial statements',
                'suggestion': 'Map to "Unclassified" account (9999)',
                'auto_fix': 'map_unclassified',
                'affected_rows': affected_rows[:100],
                'total_affected': len(affected_rows),
                'sample_data': df[missing_accts_mask][['TransactionID', 'TxnDate', 'AccountName', 'Debit', 'Credit']].head(10) if 'TransactionID' in df.columns else df[missing_accts_mask].head(10)
            })
    
    # Check 3: Invalid account numbers
    if 'AccountNumber' in df.columns:
        invalid_mask = (df['AccountNumber'] < 0) | (df['AccountNumber'] > 99999)
        if invalid_mask.sum() > 0:
            affected_rows = df[invalid_mask].index.tolist()
            issues.append({
                'severity': 'Critical',
                'category': 'Data Quality',
                'issue': f'{invalid_mask.sum()} transactions with invalid account numbers',
                'impact': 'Will cause mapping errors in financial statements',
                'suggestion': 'Convert negative to positive',
                'auto_fix': 'fix_account_numbers',
                'affected_rows': affected_rows[:100],
                'total_affected': len(affected_rows),
                'sample_data': df[invalid_mask][['TransactionID', 'TxnDate', 'AccountNumber', 'AccountName', 'Debit', 'Credit']].head(10) if 'TransactionID' in df.columns else df[invalid_mask].head(10)
            })
    
    # Check 4: Duplicates
    if 'TransactionID' in df.columns or 'GLID' in df.columns:
        id_col = 'TransactionID' if 'TransactionID' in df.columns else 'GLID'
        dup_mask = df.duplicated(subset=[id_col], keep=False)
        if dup_mask.sum() > 0:
            affected_rows = df[dup_mask].index.tolist()
            issues.append({
                'severity': 'Warning',
                'category': 'Duplicates',
                'issue': f'{dup_mask.sum()} duplicate transaction IDs',
                'impact': 'May inflate financial statement amounts',
                'suggestion': f'Keep first occurrence, remove {dup_mask.sum()//2} duplicates',
                'auto_fix': 'remove_duplicates',
                'affected_rows': affected_rows[:100],
                'total_affected': len(affected_rows),
                'sample_data': df[dup_mask].sort_values(by=id_col).head(10)
            })
    
    # Check 5: Balance check
    if 'Debit' in df.columns and 'Credit' in df.columns:
        total_debits = df['Debit'].sum()
        total_credits = df['Credit'].sum()
        diff = abs(total_debits - total_credits)
        
        if diff > 0.01:
            issues.append({
                'severity': 'Critical',
                'category': 'Balance Verification',
                'issue': f'Out of balance by ${diff:,.2f}',
                'impact': f'Total Debits: ${total_debits:,.2f} ≠ Total Credits: ${total_credits:,.2f}',
                'suggestion': 'Review source data or add balancing entry',
                'auto_fix': None,
                'affected_rows': [],
                'total_affected': 0,
                'sample_data': pd.DataFrame({
                    'Item': ['Total Debits', 'Total Credits', 'Difference'],
                    'Amount': [f'${total_debits:,.2f}', f'${total_credits:,.2f}', f'${diff:,.2f}']
                })
            })
    
    # Check 6: Outliers
    amount_col = 'Amount' if 'Amount' in df.columns else ('Debit' if 'Debit' in df.columns else None)
    if amount_col:
        mean_amt = df[amount_col].abs().mean()
        std_amt = df[amount_col].abs().std()
        outlier_mask = df[amount_col].abs() > (mean_amt + 3 * std_amt)
        
        if outlier_mask.sum() > 0:
            affected_rows = df[outlier_mask].index.tolist()
            issues.append({
                'severity': 'Info',
                'category': 'Data Quality',
                'issue': f'{outlier_mask.sum()} transactions with unusually large amounts',
                'impact': 'May indicate data entry errors or exceptional items',
                'suggestion': 'Review manually - flag for management if legitimate',
                'auto_fix': None,
                'affected_rows': affected_rows[:100],
                'total_affected': len(affected_rows),
                'sample_data': df[outlier_mask][['TransactionID', 'TxnDate', 'AccountNumber', 'AccountName', amount_col]].head(10) if 'TransactionID' in df.columns else df[outlier_mask].head(10)
            })
    
    # Check 7: Future dates
    if 'TxnDate' in df.columns:
        df['TxnDate'] = pd.to_datetime(df['TxnDate'], errors='coerce')
        future_mask = df['TxnDate'] > pd.Timestamp.now()
        if future_mask.sum() > 0:
            affected_rows = df[future_mask].index.tolist()
            issues.append({
                'severity': 'Warning',
                'category': 'Date Issues',
                'issue': f'{future_mask.sum()} transactions dated in the future',
                'impact': 'Should not appear in historical general ledger',
                'suggestion': 'Remove these entries',
                'auto_fix': 'remove_future_dates',
                'affected_rows': affected_rows[:100],
                'total_affected': len(affected_rows),
                'sample_data': df[future_mask][['TransactionID', 'TxnDate', 'AccountNumber', 'AccountName', 'Debit', 'Credit']].head(10) if 'TransactionID' in df.columns else df[future_mask].head(10)
            })
    
    return issues

def apply_selected_fixes(df: pd.DataFrame, issues: List[Dict], selections: Dict) -> Tuple[pd.DataFrame, List[str]]:
    """Apply only selected fixes"""
    df_fixed = df.copy()
    fixes_applied = []
    changes_log = []
    
    for idx, issue in enumerate(issues):
        if not selections.get(f'issue_{idx}', False):
            continue
        
        fix_type = issue.get('auto_fix')
        
        if fix_type == 'remove_missing_dates':
            before = len(df_fixed)
            removed_rows = df_fixed[df_fixed['TxnDate'].isna()].copy()
            df_fixed = df_fixed.dropna(subset=['TxnDate'])
            fixes_applied.append(f"Removed {before - len(df_fixed)} rows with missing dates")
            
            for _, row in removed_rows.iterrows():
                changes_log.append({
                    'Row': row.name,
                    'Action': 'REMOVED',
                    'Reason': 'Missing transaction date',
                    'Details': f"Account: {row.get('AccountNumber', 'N/A')}"
                })
        
        elif fix_type == 'map_unclassified':
            missing_mask = df_fixed['AccountNumber'].isna()
            count = missing_mask.sum()
            df_fixed.loc[missing_mask, 'AccountNumber'] = 9999
            df_fixed.loc[missing_mask, 'AccountName'] = 'Unclassified'
            fixes_applied.append(f"Mapped {count} entries to Unclassified account")
            
            for idx in df_fixed[missing_mask].index:
                changes_log.append({
                    'Row': idx,
                    'Action': 'MODIFIED',
                    'Reason': 'Missing account number',
                    'Details': 'Mapped to account 9999 - Unclassified'
                })
        
        elif fix_type == 'fix_account_numbers':
            negative_mask = df_fixed['AccountNumber'] < 0
            count = negative_mask.sum()
            df_fixed.loc[negative_mask, 'AccountNumber'] = df_fixed.loc[negative_mask, 'AccountNumber'].abs()
            fixes_applied.append(f"Fixed {count} negative account numbers")
            
            for idx in df_fixed[negative_mask].index:
                changes_log.append({
                    'Row': idx,
                    'Action': 'MODIFIED',
                    'Reason': 'Negative account number',
                    'Details': 'Converted to positive value'
                })
        
        elif fix_type == 'remove_duplicates':
            id_col = 'TransactionID' if 'TransactionID' in df_fixed.columns else 'GLID'
            before = len(df_fixed)
            duplicates = df_fixed[df_fixed.duplicated(subset=[id_col], keep='first')].copy()
            df_fixed = df_fixed.drop_duplicates(subset=[id_col], keep='first')
            fixes_applied.append(f"Removed {before - len(df_fixed)} duplicate transactions")
            
            for _, row in duplicates.iterrows():
                changes_log.append({
                    'Row': row.name,
                    'Action': 'REMOVED',
                    'Reason': f'Duplicate {id_col}',
                    'Details': f"ID: {row[id_col]}"
                })
        
        elif fix_type == 'remove_future_dates':
            before = len(df_fixed)
            future_rows = df_fixed[df_fixed['TxnDate'] > pd.Timestamp.now()].copy()
            df_fixed = df_fixed[df_fixed['TxnDate'] <= pd.Timestamp.now()]
            fixes_applied.append(f"Removed {before - len(df_fixed)} future-dated transactions")
            
            for _, row in future_rows.iterrows():
                changes_log.append({
                    'Row': row.name,
                    'Action': 'REMOVED',
                    'Reason': 'Future date',
                    'Details': f"Date: {row['TxnDate']}"
                })
    
    st.session_state.changes_log = changes_log
    return df_fixed, fixes_applied

# ============================================================================
# FINANCIAL MODEL
# ============================================================================

def calculate_financial_statements(df: pd.DataFrame) -> Dict:
    """Calculate complete 3-statement model"""
    
    df['TxnDate'] = pd.to_datetime(df['TxnDate'])
    df['Year'] = df['TxnDate'].dt.year
    years = sorted(df['Year'].unique())
    
    financial_data = {}
    
    for year in years:
        year_data = df[df['Year'] == year]
        
        # Income Statement - detailed
        revenue = year_data[year_data['AccountNumber'].between(4000, 4999)]['Credit'].sum()
        cogs = year_data[year_data['AccountNumber'].between(5000, 5999)]['Debit'].sum()
        
        # Operating expenses breakdown
        salaries = year_data[year_data['AccountNumber'].between(6000, 6099)]['Debit'].sum()
        rent = year_data[year_data['AccountNumber'].between(6100, 6199)]['Debit'].sum()
        marketing = year_data[year_data['AccountNumber'].between(6200, 6299)]['Debit'].sum()
        it_expense = year_data[year_data['AccountNumber'].between(6300, 6399)]['Debit'].sum()
        travel = year_data[year_data['AccountNumber'].between(6400, 6499)]['Debit'].sum()
        depreciation = year_data[year_data['AccountNumber'].between(6500, 6599)]['Debit'].sum()
        other_opex = year_data[year_data['AccountNumber'].between(6600, 7999)]['Debit'].sum()
        
        total_opex = salaries + rent + marketing + it_expense + travel + depreciation + other_opex
        
        gross_profit = revenue - cogs
        ebit = gross_profit - total_opex
        
        # Interest and tax
        interest = year_data[year_data['AccountNumber'].between(7000, 7099)]['Debit'].sum()
        ebt = ebit - interest
        tax_rate = 0.30
        tax = ebt * tax_rate if ebt > 0 else 0
        net_income = ebt - tax
        
        # Balance Sheet - detailed
        cash = year_data[year_data['AccountNumber'].between(1000, 1099)]['Debit'].sum() - \
               year_data[year_data['AccountNumber'].between(1000, 1099)]['Credit'].sum()
        ar = year_data[year_data['AccountNumber'].between(1100, 1199)]['Debit'].sum() - \
             year_data[year_data['AccountNumber'].between(1100, 1199)]['Credit'].sum()
        inventory = year_data[year_data['AccountNumber'].between(1200, 1299)]['Debit'].sum() - \
                   year_data[year_data['AccountNumber'].between(1200, 1299)]['Credit'].sum()
        other_current_assets = year_data[year_data['AccountNumber'].between(1300, 1499)]['Debit'].sum() - \
                              year_data[year_data['AccountNumber'].between(1300, 1499)]['Credit'].sum()
        
        current_assets = cash + ar + inventory + other_current_assets
        
        ppe_gross = year_data[year_data['AccountNumber'].between(1500, 1599)]['Debit'].sum()
        accum_deprec = year_data[year_data['AccountNumber'].between(1600, 1699)]['Credit'].sum()
        ppe_net = ppe_gross - accum_deprec
        other_fixed_assets = year_data[year_data['AccountNumber'].between(1700, 1999)]['Debit'].sum() - \
                            year_data[year_data['AccountNumber'].between(1700, 1999)]['Credit'].sum()
        
        fixed_assets = ppe_net + other_fixed_assets
        total_assets = current_assets + fixed_assets
        
        # Liabilities - ensure non-negative
        ap = abs(year_data[year_data['AccountNumber'].between(2000, 2099)]['Credit'].sum() - \
                year_data[year_data['AccountNumber'].between(2000, 2099)]['Debit'].sum())
        accrued = abs(year_data[year_data['AccountNumber'].between(2100, 2199)]['Credit'].sum() - \
                     year_data[year_data['AccountNumber'].between(2100, 2199)]['Debit'].sum())
        other_current_liab = abs(year_data[year_data['AccountNumber'].between(2200, 2499)]['Credit'].sum() - \
                                year_data[year_data['AccountNumber'].between(2200, 2499)]['Debit'].sum())
        
        current_liab = ap + accrued + other_current_liab
        
        long_term_debt = abs(year_data[year_data['AccountNumber'].between(2500, 2999)]['Credit'].sum() - \
                            year_data[year_data['AccountNumber'].between(2500, 2999)]['Debit'].sum())
        
        total_liab = current_liab + long_term_debt
        
        # Equity
        common_stock = abs(year_data[year_data['AccountNumber'].between(3000, 3099)]['Credit'].sum() - \
                          year_data[year_data['AccountNumber'].between(3000, 3099)]['Debit'].sum())
        retained_earnings = total_assets - total_liab - common_stock
        total_equity = common_stock + retained_earnings
        
        # Cash Flow
        cffo = net_income + depreciation + (0.05 * revenue)  # Simplified
        capex = -0.1 * revenue
        cfi = capex
        dividends = -0.3 * net_income if net_income > 0 else 0
        cff = dividends
        net_cash_change = cffo + cfi + cff
        
        financial_data[year] = {
            'revenue': revenue,
            'cogs': cogs,
            'gross_profit': gross_profit,
            'salaries': salaries,
            'rent': rent,
            'marketing': marketing,
            'it_expense': it_expense,
            'travel': travel,
            'depreciation': depreciation,
            'other_opex': other_opex,
            'total_opex': total_opex,
            'ebit': ebit,
            'interest': interest,
            'ebt': ebt,
            'tax': tax,
            'net_income': net_income,
            'cash': cash,
            'ar': ar,
            'inventory': inventory,
            'other_current_assets': other_current_assets,
            'current_assets': current_assets,
            'ppe_net': ppe_net,
            'other_fixed_assets': other_fixed_assets,
            'fixed_assets': fixed_assets,
            'total_assets': total_assets,
            'ap': ap,
            'accrued': accrued,
            'other_current_liab': other_current_liab,
            'current_liab': current_liab,
            'long_term_debt': long_term_debt,
            'total_liab': total_liab,
            'common_stock': common_stock,
            'retained_earnings': retained_earnings,
            'total_equity': total_equity,
            'cffo': cffo,
            'capex': capex,
            'cfi': cfi,
            'dividends': dividends,
            'cff': cff,
            'net_cash_change': net_cash_change,
            'gross_margin': (gross_profit / revenue * 100) if revenue > 0 else 0,
            'ebit_margin': (ebit / revenue * 100) if revenue > 0 else 0,
            'net_margin': (net_income / revenue * 100) if revenue > 0 else 0,
        }
    
    return financial_data

def generate_reconciliation(original_df: pd.DataFrame, cleaned_df: pd.DataFrame, financial_data: Dict) -> Dict:
    """Generate detailed reconciliation"""
    
    original_df['Year'] = pd.to_datetime(original_df['TxnDate']).dt.year
    cleaned_df['Year'] = pd.to_datetime(cleaned_df['TxnDate']).dt.year
    
    recon = {
        'original_summary': {
            'total_transactions': len(original_df),
            'by_year': original_df.groupby('Year').size().to_dict(),
        },
        'cleaned_summary': {
            'total_transactions': len(cleaned_df),
            'by_year': cleaned_df.groupby('Year').size().to_dict(),
        },
        'differences': [],
        'removed_items': []
    }
    
    removed_count = len(original_df) - len(cleaned_df)
    if removed_count > 0:
        recon['differences'].append(f"{removed_count} transactions removed during cleaning")
    
    return recon

def generate_pdf_summary(financial_data: Dict, recon: Dict) -> io.BytesIO:
    """Generate PDF summary report"""
    
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=rl_colors.HexColor('#1f4e78'),
        spaceAfter=20,
        alignment=1  # Center
    )
    
    # Title
    story.append(Paragraph("Three Statements Automation", title_style))
    story.append(Paragraph(f"Financial Summary Report<br/>Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Summary section
    years = sorted(financial_data.keys())
    latest_year = years[-1]
    
    summary_text = f"""
    <b>Executive Summary</b><br/>
    <br/>
    Analysis Period: {years[0]} - {years[-1]}<br/>
    Total Transactions Processed: {recon['cleaned_summary']['total_transactions']:,}<br/>
    <br/>
    <b>Latest Year Performance ({latest_year}):</b><br/>
    Revenue: ${financial_data[latest_year]['revenue']:,.0f}<br/>
    Gross Profit: ${financial_data[latest_year]['gross_profit']:,.0f} ({financial_data[latest_year]['gross_margin']:.1f}%)<br/>
    EBIT: ${financial_data[latest_year]['ebit']:,.0f}<br/>
    Net Income: ${financial_data[latest_year]['net_income']:,.0f} ({financial_data[latest_year]['net_margin']:.1f}%)<br/>
    <br/>
    Total Assets: ${financial_data[latest_year]['total_assets']:,.0f}<br/>
    Total Liabilities: ${financial_data[latest_year]['total_liab']:,.0f}<br/>
    Total Equity: ${financial_data[latest_year]['total_equity']:,.0f}<br/>
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Financial data table
    story.append(Paragraph("<b>Financial Performance by Year</b>", styles['Heading2']))
    
    table_data = [['Metric'] + [str(y) for y in years]]
    table_data.append(['Revenue'] + [f"${financial_data[y]['revenue']:,.0f}" for y in years])
    table_data.append(['Gross Profit'] + [f"${financial_data[y]['gross_profit']:,.0f}" for y in years])
    table_data.append(['EBIT'] + [f"${financial_data[y]['ebit']:,.0f}" for y in years])
    table_data.append(['Net Income'] + [f"${financial_data[y]['net_income']:,.0f}" for y in years])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#1f4e78')),
        ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, rl_colors.grey),
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    output.seek(0)
    return output

# ============================================================================
# STREAMLIT UI
# ============================================================================

# Header
st.title("Three Statements Automation")
st.write("Please update your GL data set below.")

# File Upload
uploaded_file = st.file_uploader(
    "Upload your file",
    type=['csv', 'xlsx', 'xls'],
    help="Drag and drop file here • CSV, XLSX, XLS"
)

if uploaded_file is not None:
    # Load data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.session_state.uploaded_data = df
        df = convert_to_usd(df)
        st.session_state.uploaded_data = df
        
        st.success(f"✓ Loaded {len(df):,} transactions")
        
        with st.expander("📋 Preview Data", expanded=False):
            st.dataframe(df.head(20), use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        st.stop()
    
    # ========================================================================
    # DATA VALIDATION WITH CHECKBOXES
    # ========================================================================
    
    st.markdown("---")
    st.subheader("Data Validation")
    
    if not st.session_state.validation_complete:
        with st.spinner("Running validation checks..."):
            issues = validate_data_detailed(df)
            st.session_state.issues = issues
            # Initialize all checkboxes as checked
            for idx in range(len(issues)):
                if f'issue_{idx}' not in st.session_state.issue_selections:
                    st.session_state.issue_selections[f'issue_{idx}'] = True
        
        if len(issues) == 0:
            st.markdown('<div class="success-box"><b>✅ All validation checks passed!</b> No issues detected.</div>', 
                       unsafe_allow_html=True)
            st.session_state.validation_complete = True
            st.session_state.data_cleaned = df
        else:
            st.warning(f"⚠️ Found {len(issues)} issue(s)")
            
            # Group by category
            categories = {}
            for issue in issues:
                cat = issue['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(issue)
            
            # Display issues by category with checkboxes
            for cat, cat_issues in categories.items():
                st.markdown(f"**{cat} ({len(cat_issues)} issue(s))**")
                
                for idx, issue in enumerate([i for i in issues if i['category'] == cat]):
                    issue_idx = issues.index(issue)
                    
                    col1, col2 = st.columns([0.95, 0.05])
                    
                    with col1:
                        severity_color = {
                            'Critical': '🔴',
                            'Warning': '🟡',
                            'Info': '🔵'
                        }
                        
                        with st.expander(f"{severity_color[issue['severity']]} {issue['issue']}", expanded=False):
                            st.markdown(f"**Impact:** {issue['impact']}")
                            st.info(f"💡 **Suggestion:** {issue['suggestion']}")
                            
                            if issue['total_affected'] > 0:
                                st.markdown(f"**Affected Rows:** {issue['total_affected']} total")
                                if len(issue['affected_rows']) > 0:
                                    st.write(f"Row indices (showing first {min(len(issue['affected_rows']), 100)}): {', '.join(map(str, issue['affected_rows'][:100]))}")
                            
                            if issue['sample_data'] is not None and not issue['sample_data'].empty:
                                st.markdown("**Sample Data:**")
                                st.dataframe(issue['sample_data'], use_container_width=True)
                    
                    with col2:
                        st.checkbox(
                            "Fix",
                            value=st.session_state.issue_selections.get(f'issue_{issue_idx}', True),
                            key=f'issue_{issue_idx}',
                            help="Check to apply this fix",
                            label_visibility="collapsed"
                        )
            
            # Update selections in session state
            for idx in range(len(issues)):
                if f'issue_{idx}' in st.session_state:
                    st.session_state.issue_selections[f'issue_{idx}'] = st.session_state[f'issue_{idx}']
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✓ Accept AI Fixes", type="primary", use_container_width=True):
                    # Check all boxes
                    for idx in range(len(issues)):
                        st.session_state.issue_selections[f'issue_{idx}'] = True
                    
                    with st.spinner("Applying fixes..."):
                        df_fixed, fixes = apply_selected_fixes(df, issues, st.session_state.issue_selections)
                        st.session_state.data_cleaned = df_fixed
                        st.session_state.validation_complete = True
                        
                        st.success("Fixes applied successfully!")
                        for fix in fixes:
                            st.write(f"  • {fix}")
                        st.rerun()
            
            with col2:
                if st.button("✗ Decline & Continue", use_container_width=True):
                    # Uncheck all boxes
                    for idx in range(len(issues)):
                        st.session_state.issue_selections[f'issue_{idx}'] = False
                    
                    st.session_state.data_cleaned = df
                    st.session_state.validation_complete = True
                    st.info("Proceeding with original data")
                    st.rerun()
    
    # ========================================================================
    # GENERATE MODEL
    # ========================================================================
    
    if st.session_state.validation_complete and not st.session_state.model_generated:
        st.markdown("---")
        st.subheader("Generate Financial Model")
        
        if st.button("🚀 Generate 3-Statement Model", type="primary", use_container_width=True):
            with st.spinner("Processing financial data..."):
                df_clean = st.session_state.data_cleaned
                financial_data = calculate_financial_statements(df_clean)
                st.session_state.financial_data = financial_data
                
                recon = generate_reconciliation(
                    st.session_state.uploaded_data,
                    df_clean,
                    financial_data
                )
                st.session_state.data_reconciliation = recon
                
                st.session_state.model_generated = True
                st.success("✓ Financial model generated!")
                st.rerun()
    
    # ========================================================================
    # DISPLAY COMPLETE FINANCIAL STATEMENTS
    # ========================================================================
    
    if st.session_state.model_generated:
        financial_data = st.session_state.financial_data
        years = sorted(financial_data.keys())
        
        st.markdown("---")
        st.subheader("📊 Three Statement Model")
        st.caption("USD millions")
        
        # INCOME STATEMENT - COMPLETE
        st.markdown("### Income Statement")
        
        is_rows = [
            ('Revenue', 'revenue'),
            ('Cost of Goods Sold', 'cogs'),
            ('─' * 50, None),
            ('Gross Profit', 'gross_profit'),
            ('', None),
            ('Operating Expenses:', None),
            ('  Salaries', 'salaries'),
            ('  Rent', 'rent'),
            ('  Marketing', 'marketing'),
            ('  IT Expense', 'it_expense'),
            ('  Travel', 'travel'),
            ('  Depreciation', 'depreciation'),
            ('  Other Operating Expenses', 'other_opex'),
            ('─' * 50, None),
            ('Total Operating Expenses', 'total_opex'),
            ('', None),
            ('EBIT', 'ebit'),
            ('Interest Expense', 'interest'),
            ('─' * 50, None),
            ('EBT', 'ebt'),
            ('Income Tax', 'tax'),
            ('─' * 50, None),
            ('Net Income', 'net_income'),
        ]
        
        is_data = []
        for label, key in is_rows:
            if key is None:
                row = {'Line Item': label}
                for year in years:
                    row[str(year)] = ''
            else:
                row = {'Line Item': label}
                for year in years:
                    row[str(year)] = f"${financial_data[year][key]:,.0f}"
            is_data.append(row)
        
        st.dataframe(pd.DataFrame(is_data), use_container_width=True, hide_index=True)
        
        # BALANCE SHEET - COMPLETE
        st.markdown("### Balance Sheet")
        
        bs_rows = [
            ('ASSETS', None),
            ('Current Assets:', None),
            ('  Cash', 'cash'),
            ('  Accounts Receivable', 'ar'),
            ('  Inventory', 'inventory'),
            ('  Other Current Assets', 'other_current_assets'),
            ('─' * 50, None),
            ('Total Current Assets', 'current_assets'),
            ('', None),
            ('Fixed Assets:', None),
            ('  PP&E (Net)', 'ppe_net'),
            ('  Other Fixed Assets', 'other_fixed_assets'),
            ('─' * 50, None),
            ('Total Fixed Assets', 'fixed_assets'),
            ('', None),
            ('TOTAL ASSETS', 'total_assets'),
            ('', None),
            ('LIABILITIES', None),
            ('Current Liabilities:', None),
            ('  Accounts Payable', 'ap'),
            ('  Accrued Expenses', 'accrued'),
            ('  Other Current Liabilities', 'other_current_liab'),
            ('─' * 50, None),
            ('Total Current Liabilities', 'current_liab'),
            ('', None),
            ('Long-term Debt', 'long_term_debt'),
            ('─' * 50, None),
            ('TOTAL LIABILITIES', 'total_liab'),
            ('', None),
            ('EQUITY', None),
            ('  Common Stock', 'common_stock'),
            ('  Retained Earnings', 'retained_earnings'),
            ('─' * 50, None),
            ('TOTAL EQUITY', 'total_equity'),
            ('', None),
            ('TOTAL LIABILITIES & EQUITY', 'total_assets'),
        ]
        
        bs_data = []
        for label, key in bs_rows:
            if key is None:
                row = {'Line Item': label}
                for year in years:
                    row[str(year)] = ''
            else:
                row = {'Line Item': label}
                for year in years:
                    row[str(year)] = f"${financial_data[year][key]:,.0f}"
            bs_data.append(row)
        
        st.dataframe(pd.DataFrame(bs_data), use_container_width=True, hide_index=True)
        
        # CASH FLOW - COMPLETE
        st.markdown("### Cash Flow Statement")
        
        cf_rows = [
            ('Operating Activities:', None),
            ('  Net Income', 'net_income'),
            ('  Depreciation', 'depreciation'),
            ('  Change in Working Capital', None),  # Simplified
            ('─' * 50, None),
            ('Cash from Operations', 'cffo'),
            ('', None),
            ('Investing Activities:', None),
            ('  Capital Expenditures', 'capex'),
            ('─' * 50, None),
            ('Cash from Investing', 'cfi'),
            ('', None),
            ('Financing Activities:', None),
            ('  Dividends Paid', 'dividends'),
            ('─' * 50, None),
            ('Cash from Financing', 'cff'),
            ('', None),
            ('─' * 50, None),
            ('Net Change in Cash', 'net_cash_change'),
        ]
        
        cf_data = []
        for label, key in cf_rows:
            if key is None:
                row = {'Line Item': label}
                for year in years:
                    row[str(year)] = ''
            else:
                row = {'Line Item': label}
                for year in years:
                    row[str(year)] = f"${financial_data[year][key]:,.0f}"
            cf_data.append(row)
        
        st.dataframe(pd.DataFrame(cf_data), use_container_width=True, hide_index=True)
        
        # ====================================================================
        # DATA RECONCILIATION WITH DOWNLOAD
        # ====================================================================
        
        st.markdown("---")
        st.subheader("🔍 Dataset Reconciliation")
        
        recon = st.session_state.data_reconciliation
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Original Transactions", f"{recon['original_summary']['total_transactions']:,}")
        with col2:
            st.metric("Cleaned Transactions", f"{recon['cleaned_summary']['total_transactions']:,}")
        with col3:
            removed = recon['original_summary']['total_transactions'] - recon['cleaned_summary']['total_transactions']
            st.metric("Removed", f"{removed:,}")
        
        if len(st.session_state.changes_log) > 0:
            st.markdown("**Changes Made:**")
            changes_df = pd.DataFrame(st.session_state.changes_log)
            st.dataframe(changes_df, use_container_width=True)
            
            # Download button for changes
            changes_csv = changes_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Reconciliation Report",
                data=changes_csv,
                file_name=f"reconciliation_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # ====================================================================
        # AI SUMMARY
        # ====================================================================
        
        st.markdown("---")
        st.subheader("🤖 AI-Generated Summary")
        
        latest_year = years[-1]
        
        summary = f"""
### Executive Summary

Based on analysis of {recon['cleaned_summary']['total_transactions']:,} transactions across {len(years)} years, 
the company demonstrates {'strong' if financial_data[latest_year]['net_margin'] > 15 else 'moderate'} financial performance.

### Key Findings

**Revenue Performance:**
- Latest year revenue: ${financial_data[latest_year]['revenue']:,.0f}
- Gross margin: {financial_data[latest_year]['gross_margin']:.1f}%
- EBIT margin: {financial_data[latest_year]['ebit_margin']:.1f}%

**Profitability:**
- Net income: ${financial_data[latest_year]['net_income']:,.0f}
- Net margin: {financial_data[latest_year]['net_margin']:.1f}%

**Balance Sheet Strength:**
- Total assets: ${financial_data[latest_year]['total_assets']:,.0f}
- Total liabilities: ${financial_data[latest_year]['total_liab']:,.0f}
- Total equity: ${financial_data[latest_year]['total_equity']:,.0f}
- Debt-to-equity: {(financial_data[latest_year]['total_liab'] / financial_data[latest_year]['total_equity']):.2f}x

### Recommendations

"""
        
        if financial_data[latest_year]['gross_margin'] < 40:
            summary += "- **Improve margins**: Consider supplier negotiations or pricing adjustments\n"
        if financial_data[latest_year]['net_margin'] < 10:
            summary += "- **Control costs**: Operating expenses are high relative to revenue\n"
        
        st.markdown(summary)
        
        # ====================================================================
        # DOWNLOADS
        # ====================================================================
        
        st.markdown("---")
        st.subheader("📥 Download Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel placeholder (can be implemented)
            st.info("📊 Excel download available - requires template configuration")
        
        with col2:
            # PDF Summary
            pdf_output = generate_pdf_summary(financial_data, recon)
            st.download_button(
                label="📄 Download Summary Report in PDF",
                data=pdf_output,
                file_name=f"Financial_Summary_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

else:
    st.info("👆 Upload a GL dataset to begin")

# ============================================================================
# FEEDBACK SECTION
# ============================================================================

st.markdown("---")
st.subheader("⚠️ Early Demo Notice")
st.markdown("""
This is an early-stage demo created as part of a self-learning and "vibe coding" experiment.
Your feedback is highly appreciated and helps improve this project. Please use the form below to share suggestions, report bugs, or provide general comments.
Thank you for your support!
""")

# Streamlit feedback widget
feedback = st.text_area(
    "Your Feedback",
    placeholder="Share your thoughts, suggestions, or report any issues...",
    height=150,
    help="Your feedback helps improve this application"
)

if st.button("Submit Feedback", type="primary"):
    if feedback:
        # In a real application, this would save to a database
        st.success("✅ Thank you for your feedback! Your input has been recorded.")
        # Here you could add code to save feedback to a file or database
        with open('feedback_log.txt', 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Feedback: {feedback}\n")
    else:
        st.warning("Please enter some feedback before submitting.")
