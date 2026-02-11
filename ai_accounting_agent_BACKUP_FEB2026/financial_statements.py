"""
Financial Statements Generator Module
Generates P&L, Balance Sheet, and other financial reports
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional

class FinancialStatementGenerator:
    """Generate financial statements from GL data"""
    
    # Account mapping - simplified chart of accounts
    ACCOUNT_MAPPING = {
        'Revenue': range(4000, 5000),
        'Cost of Goods Sold': range(5000, 6000),
        'Operating Expenses': range(6000, 8000),
        'Other Income/Expense': range(8000, 9000),
        'Assets': range(1000, 2000),
        'Liabilities': range(2000, 3000),
        'Equity': range(3000, 4000)
    }
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with GL data"""
        self.df = df
        self.pl_statement = None
    
    def _categorize_account(self, account_number: int) -> str:
        """Categorize account based on account number"""
        for category, account_range in self.ACCOUNT_MAPPING.items():
            if account_number in account_range:
                return category
        return 'Other'
    
    def generate_pl_statement(self) -> pd.DataFrame:
        """Generate Profit & Loss Statement"""
        
        try:
            # Add account category
            self.df['Category'] = self.df['AccountNumber'].apply(self._categorize_account)
            
            # Calculate net amount for each transaction
            # Revenue and income are credits (positive), expenses are debits (negative)
            self.df['PLAmount'] = np.where(
                self.df['Category'].isin(['Revenue', 'Other Income/Expense']),
                self.df['Credit'] - self.df['Debit'],  # Revenue: credits are positive
                self.df['Debit'] - self.df['Credit']   # Expenses: debits are positive
            )
            
            # Group by category and account
            pl_summary = self.df.groupby(['Category', 'AccountName']).agg({
                'PLAmount': 'sum'
            }).reset_index()
            
            # Rename for clarity
            pl_summary.columns = ['Category', 'Account', 'Amount']
            
            # Calculate totals by category
            category_totals = pl_summary.groupby('Category')['Amount'].sum().reset_index()
            category_totals['Account'] = category_totals['Category'] + ' - Total'
            
            # Build P&L structure
            pl_items = []
            
            # Revenue section
            revenue_items = pl_summary[pl_summary['Category'] == 'Revenue'].copy()
            if not revenue_items.empty:
                pl_items.append({'Section': 'Revenue', 'Line Item': 'Revenue', 'Amount': revenue_items['Amount'].sum(), 'Level': 1})
                for _, row in revenue_items.iterrows():
                    pl_items.append({'Section': 'Revenue', 'Line Item': f"  {row['Account']}", 'Amount': row['Amount'], 'Level': 2})
            
            total_revenue = revenue_items['Amount'].sum() if not revenue_items.empty else 0
            pl_items.append({'Section': 'Revenue', 'Line Item': 'Total Revenue', 'Amount': total_revenue, 'Level': 0})
            
            # COGS section
            cogs_items = pl_summary[pl_summary['Category'] == 'Cost of Goods Sold'].copy()
            if not cogs_items.empty:
                pl_items.append({'Section': 'COGS', 'Line Item': '', 'Amount': None, 'Level': -1})
                pl_items.append({'Section': 'COGS', 'Line Item': 'Cost of Goods Sold', 'Amount': cogs_items['Amount'].sum(), 'Level': 1})
                for _, row in cogs_items.iterrows():
                    pl_items.append({'Section': 'COGS', 'Line Item': f"  {row['Account']}", 'Amount': row['Amount'], 'Level': 2})
            
            total_cogs = cogs_items['Amount'].sum() if not cogs_items.empty else 0
            pl_items.append({'Section': 'COGS', 'Line Item': 'Total COGS', 'Amount': total_cogs, 'Level': 0})
            
            # Gross Profit
            gross_profit = total_revenue - total_cogs
            pl_items.append({'Section': 'Gross Profit', 'Line Item': '', 'Amount': None, 'Level': -1})
            pl_items.append({'Section': 'Gross Profit', 'Line Item': 'Gross Profit', 'Amount': gross_profit, 'Level': 0})
            
            # Operating Expenses
            opex_items = pl_summary[pl_summary['Category'] == 'Operating Expenses'].copy()
            if not opex_items.empty:
                pl_items.append({'Section': 'OpEx', 'Line Item': '', 'Amount': None, 'Level': -1})
                pl_items.append({'Section': 'OpEx', 'Line Item': 'Operating Expenses', 'Amount': opex_items['Amount'].sum(), 'Level': 1})
                for _, row in opex_items.iterrows():
                    pl_items.append({'Section': 'OpEx', 'Line Item': f"  {row['Account']}", 'Amount': row['Amount'], 'Level': 2})
            
            total_opex = opex_items['Amount'].sum() if not opex_items.empty else 0
            pl_items.append({'Section': 'OpEx', 'Line Item': 'Total Operating Expenses', 'Amount': total_opex, 'Level': 0})
            
            # Operating Income
            operating_income = gross_profit - total_opex
            pl_items.append({'Section': 'Operating Income', 'Line Item': '', 'Amount': None, 'Level': -1})
            pl_items.append({'Section': 'Operating Income', 'Line Item': 'Operating Income', 'Amount': operating_income, 'Level': 0})
            
            # Other Income/Expense
            other_items = pl_summary[pl_summary['Category'] == 'Other Income/Expense'].copy()
            total_other = 0
            if not other_items.empty:
                total_other = other_items['Amount'].sum()
                pl_items.append({'Section': 'Other', 'Line Item': '', 'Amount': None, 'Level': -1})
                pl_items.append({'Section': 'Other', 'Line Item': 'Other Income/(Expense)', 'Amount': total_other, 'Level': 1})
            
            # Net Income
            net_income = operating_income + total_other
            pl_items.append({'Section': 'Net Income', 'Line Item': '', 'Amount': None, 'Level': -1})
            pl_items.append({'Section': 'Net Income', 'Line Item': 'Net Income', 'Amount': net_income, 'Level': 0})
            
            # Convert to DataFrame
            pl_df = pd.DataFrame(pl_items)
            
            # Add percentage of revenue
            pl_df['% of Revenue'] = np.where(
                total_revenue != 0,
                (pl_df['Amount'] / total_revenue * 100),
                0
            )
            
            # Clean up display
            pl_df = pl_df[['Line Item', 'Amount', '% of Revenue']]
            
            self.pl_statement = pl_df
            return pl_df
        
        except Exception as e:
            print(f"Error generating P&L: {str(e)}")
            return None
    
    def get_revenue_expense_chart(self) -> Optional[go.Figure]:
        """Create a bar chart comparing revenue vs expenses"""
        
        try:
            if self.pl_statement is None:
                return None
            
            # Extract key metrics
            total_revenue = self.pl_statement[self.pl_statement['Line Item'] == 'Total Revenue']['Amount'].values[0]
            total_cogs = self.pl_statement[self.pl_statement['Line Item'] == 'Total COGS']['Amount'].values[0]
            total_opex = self.pl_statement[self.pl_statement['Line Item'] == 'Total Operating Expenses']['Amount'].values[0]
            net_income = self.pl_statement[self.pl_statement['Line Item'] == 'Net Income']['Amount'].values[-1]
            
            # Create chart
            fig = go.Figure(data=[
                go.Bar(
                    name='Revenue',
                    x=['Revenue'],
                    y=[total_revenue],
                    marker_color='#2ecc71'
                ),
                go.Bar(
                    name='COGS',
                    x=['COGS'],
                    y=[total_cogs],
                    marker_color='#e74c3c'
                ),
                go.Bar(
                    name='OpEx',
                    x=['Operating Expenses'],
                    y=[total_opex],
                    marker_color='#e67e22'
                ),
                go.Bar(
                    name='Net Income',
                    x=['Net Income'],
                    y=[net_income],
                    marker_color='#3498db'
                )
            ])
            
            fig.update_layout(
                title='Revenue vs Expenses',
                yaxis_title='Amount ($)',
                barmode='group',
                showlegend=False,
                height=400
            )
            
            return fig
        
        except Exception as e:
            print(f"Error creating chart: {str(e)}")
            return None
    
    def get_expense_breakdown(self) -> Optional[go.Figure]:
        """Create a pie chart of expense breakdown"""
        
        try:
            # Get expense details
            expense_data = self.df[self.df['Category'].isin(['Cost of Goods Sold', 'Operating Expenses'])].copy()
            
            if expense_data.empty:
                return None
            
            expense_summary = expense_data.groupby('AccountName')['Debit'].sum().reset_index()
            expense_summary = expense_summary.sort_values('Debit', ascending=False).head(10)
            
            fig = px.pie(
                expense_summary,
                values='Debit',
                names='AccountName',
                title='Top 10 Expense Accounts'
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            
            return fig
        
        except Exception as e:
            print(f"Error creating expense breakdown: {str(e)}")
            return None
    
    def get_monthly_trend(self) -> Optional[go.Figure]:
        """Create a line chart showing monthly trends"""
        
        try:
            # Group by month
            monthly_data = self.df.groupby(['Year', 'Month', 'Category']).agg({
                'PLAmount': 'sum'
            }).reset_index()
            
            monthly_data['Period'] = pd.to_datetime(
                monthly_data['Year'].astype(str) + '-' + monthly_data['Month'].astype(str) + '-01'
            )
            
            # Pivot for plotting
            pivot_data = monthly_data.pivot(index='Period', columns='Category', values='PLAmount').fillna(0)
            
            fig = go.Figure()
            
            for category in pivot_data.columns:
                fig.add_trace(go.Scatter(
                    x=pivot_data.index,
                    y=pivot_data[category],
                    mode='lines+markers',
                    name=category
                ))
            
            fig.update_layout(
                title='Monthly Financial Trends',
                xaxis_title='Month',
                yaxis_title='Amount ($)',
                height=400
            )
            
            return fig
        
        except Exception as e:
            print(f"Error creating trend chart: {str(e)}")
            return None
