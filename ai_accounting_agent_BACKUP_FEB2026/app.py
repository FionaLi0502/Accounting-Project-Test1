"""
AI Accounting Agent - Executive Insights Generator
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Import our custom modules
from data_processor import DataProcessor
from financial_statements import FinancialStatementGenerator
from ai_analyzer import AIAnalyzer
from excel_report_generator import ExcelReportGenerator
from pdf_report_generator import PDFReportGenerator

# Page configuration
st.set_page_config(
    page_title="AI Accounting Agent",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<div class="main-header">📊 AI Accounting Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Executive Insights Generator - From Raw Data to Board-Ready Presentation</div>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info("Upload your General Ledger data to begin analysis")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload GL Data (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            help="Upload your General Ledger export file"
        )
        
        st.divider()
        
        # Analysis options
        st.subheader("Analysis Options")
        include_market_analysis = st.checkbox("Include Market Context", value=True)
        variance_threshold = st.slider("Variance Alert Threshold (%)", 5, 25, 10)
        
        st.divider()
        st.caption("Built with Streamlit & Claude AI")
    
    # Main content area
    if uploaded_file is None:
        # Welcome screen
        st.info("👈 Please upload a General Ledger file to begin")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🔍 Step 1: Data Validation")
            st.write("Automatically checks for:")
            st.write("- Missing data")
            st.write("- Duplicate entries")
            st.write("- Balance verification")
            st.write("- Data quality issues")
        
        with col2:
            st.markdown("### 📈 Step 2: Financial Analysis")
            st.write("Generates:")
            st.write("- P&L Statement")
            st.write("- Variance analysis")
            st.write("- Trend identification")
            st.write("- KPI calculations")
        
        with col3:
            st.markdown("### 🎯 Step 3: AI Insights")
            st.write("Delivers:")
            st.write("- Executive summary")
            st.write("- Root cause analysis")
            st.write("- Market context")
            st.write("- Actionable recommendations")
        
        st.divider()
        
        # Sample data format
        with st.expander("📋 Expected Data Format"):
            st.write("Your GL data should contain these columns:")
            sample_df = pd.DataFrame({
                'TxnDate': ['2024-01-15', '2024-01-16'],
                'AccountNumber': [4000, 5000],
                'AccountName': ['Revenue - Product A', 'COGS - Materials'],
                'Debit': [0, 5000],
                'Credit': [10000, 0],
                'Dept': ['Sales', 'Operations'],
                'Description': ['Invoice #1234', 'Vendor ABC']
            })
            st.dataframe(sample_df, use_container_width=True)
        
        return
    
    # Process uploaded file
    try:
        # Initialize session state for data persistence
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        
        # Load and process data
        with st.spinner("Loading and validating data..."):
            processor = DataProcessor(uploaded_file)
            df = processor.load_data()
            
            st.session_state.df = df
            st.session_state.processor = processor
            st.session_state.data_loaded = True
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Data Overview",
            "✅ Validation Results", 
            "📊 Financial Statements",
            "🤖 AI Analysis",
            "📑 Executive Report"
        ])
        
        # Tab 1: Data Overview
        with tab1:
            st.header("Data Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Transactions", f"{len(df):,}")
            with col2:
                st.metric("Date Range", f"{df['TxnDate'].min().strftime('%Y-%m-%d')} to {df['TxnDate'].max().strftime('%Y-%m-%d')}")
            with col3:
                total_debit = df['Debit'].sum()
                st.metric("Total Debits", f"${total_debit:,.0f}")
            with col4:
                total_credit = df['Credit'].sum()
                st.metric("Total Credits", f"${total_credit:,.0f}")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Data Sample")
                st.dataframe(df.head(10), use_container_width=True)
            
            with col2:
                st.subheader("Data Summary")
                st.write(f"**Unique Accounts:** {df['AccountNumber'].nunique()}")
                st.write(f"**Departments:** {df['Dept'].nunique()}")
                st.write(f"**Cost Centers:** {df['CostCenter'].nunique()}")
                st.write(f"**Currencies:** {', '.join(df['Currency'].unique())}")
                
                st.divider()
                
                st.subheader("Account Distribution")
                account_counts = df['AccountName'].value_counts().head(10)
                st.bar_chart(account_counts)
        
        # Tab 2: Validation Results
        with tab2:
            st.header("Data Validation Results")
            
            with st.spinner("Running validation checks..."):
                validation_results = processor.validate_data(df)
            
            # Display validation summary
            total_issues = sum(len(issues) for issues in validation_results.values())
            
            if total_issues == 0:
                st.markdown('<div class="success-box">✅ <strong>All validation checks passed!</strong> No issues detected.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="warning-box">⚠️ <strong>{total_issues} issues detected</strong> - Review below for details</div>', unsafe_allow_html=True)
            
            # Display each validation category
            for check_name, issues in validation_results.items():
                with st.expander(f"**{check_name}** - {len(issues)} issue(s)", expanded=(len(issues) > 0)):
                    if len(issues) == 0:
                        st.success("✅ No issues found")
                    else:
                        for i, issue in enumerate(issues, 1):
                            st.warning(f"{i}. {issue}")
        
        # Tab 3: Financial Statements
        with tab3:
            st.header("Financial Statements")
            
            with st.spinner("Generating financial statements..."):
                fs_generator = FinancialStatementGenerator(df)
                pl_statement = fs_generator.generate_pl_statement()
            
            if pl_statement is not None and not pl_statement.empty:
                st.subheader("Profit & Loss Statement")
                
                # Display P&L
                st.dataframe(
                    pl_statement.style.format({
                        'Amount': '${:,.2f}',
                        '% of Revenue': '{:.1f}%'
                    }),
                    use_container_width=True
                )
                
                # Visualizations
                st.divider()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Revenue vs Expenses")
                    chart_data = fs_generator.get_revenue_expense_chart()
                    if chart_data is not None:
                        st.plotly_chart(chart_data, use_container_width=True)
                
                with col2:
                    st.subheader("Expense Breakdown")
                    expense_chart = fs_generator.get_expense_breakdown()
                    if expense_chart is not None:
                        st.plotly_chart(expense_chart, use_container_width=True)
            else:
                st.warning("Unable to generate P&L statement. Please check your data structure.")
        
        # Tab 4: AI Analysis
        with tab4:
            st.header("AI-Powered Analysis")
            
            if st.button("🤖 Generate AI Insights", type="primary", use_container_width=True):
                with st.spinner("Claude is analyzing your financial data..."):
                    analyzer = AIAnalyzer()
                    
                    # Prepare context for AI
                    context = {
                        'pl_statement': pl_statement if 'pl_statement' in locals() else None,
                        'validation_results': validation_results,
                        'data_summary': {
                            'total_transactions': len(df),
                            'date_range': f"{df['TxnDate'].min()} to {df['TxnDate'].max()}",
                            'total_debit': df['Debit'].sum(),
                            'total_credit': df['Credit'].sum()
                        }
                    }
                    
                    analysis = analyzer.generate_analysis(context, include_market_analysis)
                    
                    st.session_state.ai_analysis = analysis
                
                st.success("✅ Analysis complete!")
            
            # Display analysis if available
            if 'ai_analysis' in st.session_state:
                st.markdown(st.session_state.ai_analysis)
        
        # Tab 5: Executive Report
        with tab5:
            st.header("Executive Report Generation")
            
            st.info("Generate professional Excel and PDF reports for executive review and Power BI integration")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                report_title = st.text_input("Report Title", "Monthly Financial Review")
                report_period = st.text_input("Period", f"{df['TxnDate'].min().strftime('%B %Y')}")
            
            with col2:
                report_format = st.radio("Report Format", ["Excel", "PDF", "Both"])
            
            if st.button("📑 Generate Report", type="primary", use_container_width=True):
                with st.spinner("Creating reports..."):
                    # Prepare data for report
                    report_data = {
                        'title': report_title,
                        'period': report_period,
                        'validation_summary': validation_results,
                        'pl_statement': pl_statement if 'pl_statement' in locals() else None,
                        'ai_insights': st.session_state.get('ai_analysis', 'No analysis available'),
                        'data_summary': {
                            'total_transactions': len(df),
                            'date_range': f"{df['TxnDate'].min().strftime('%Y-%m-%d')} to {df['TxnDate'].max().strftime('%Y-%m-%d')}",
                            'accounts': df['AccountNumber'].nunique(),
                            'departments': df['Dept'].nunique()
                        }
                    }
                    
                    generated_files = []
                    
                    # Generate Excel report
                    if report_format in ["Excel", "Both"]:
                        excel_gen = ExcelReportGenerator()
                        excel_path = excel_gen.generate_report(report_data)
                        generated_files.append(("Excel", excel_path, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                    
                    # Generate PDF report
                    if report_format in ["PDF", "Both"]:
                        pdf_gen = PDFReportGenerator()
                        pdf_path = pdf_gen.generate_report(report_data)
                        generated_files.append(("PDF", pdf_path, "application/pdf"))
                    
                    st.success(f"✅ {report_format} report(s) generated successfully!")
                    
                    # Provide download buttons
                    for file_type, file_path, mime_type in generated_files:
                        with open(file_path, 'rb') as file:
                            file_ext = "xlsx" if file_type == "Excel" else "pdf"
                            st.download_button(
                                label=f"📥 Download {file_type} Report",
                                data=file,
                                file_name=f"Financial_Report_{report_period.replace(' ', '_')}.{file_ext}",
                                mime=mime_type,
                                use_container_width=True,
                                key=f"download_{file_type}"
                            )
                    
                    # Power BI integration note
                    if report_format in ["Excel", "Both"]:
                        st.info("💡 **Power BI Integration**: The Excel report can be directly imported into Power BI. Use 'Get Data' → 'Excel' and select the P&L Statement sheet.")
    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
