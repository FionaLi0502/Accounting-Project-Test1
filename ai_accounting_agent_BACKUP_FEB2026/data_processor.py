"""
Data Processor Module
Handles data loading, cleaning, and validation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

class DataProcessor:
    """Process and validate General Ledger data"""
    
    def __init__(self, file):
        """Initialize with uploaded file"""
        self.file = file
        self.df = None
    
    def load_data(self) -> pd.DataFrame:
        """Load data from Excel or CSV file"""
        try:
            if self.file.name.endswith('.csv'):
                df = pd.read_csv(self.file)
            else:
                df = pd.read_excel(self.file)
            
            # Clean and standardize data
            df = self._clean_data(df)
            
            self.df = df
            return df
        
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the data"""
        
        # Convert date column to datetime
        if 'TxnDate' in df.columns:
            df['TxnDate'] = pd.to_datetime(df['TxnDate'], errors='coerce')
        
        # Ensure numeric columns are properly typed
        numeric_columns = ['Debit', 'Credit', 'AccountNumber']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill NaN values in Debit/Credit with 0
        if 'Debit' in df.columns:
            df['Debit'] = df['Debit'].fillna(0)
        if 'Credit' in df.columns:
            df['Credit'] = df['Credit'].fillna(0)
        
        # Strip whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Add calculated fields
        df['NetAmount'] = df['Debit'] - df['Credit']
        df['Year'] = df['TxnDate'].dt.year
        df['Month'] = df['TxnDate'].dt.month
        df['Quarter'] = df['TxnDate'].dt.quarter
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Run comprehensive data validation checks"""
        
        validation_results = {
            'Missing Data': [],
            'Duplicate Entries': [],
            'Balance Verification': [],
            'Data Quality': [],
            'Date Issues': [],
            'Account Structure': []
        }
        
        # Check for missing critical data
        critical_columns = ['TxnDate', 'AccountNumber', 'AccountName']
        for col in critical_columns:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    validation_results['Missing Data'].append(
                        f"{missing_count} rows missing {col}"
                    )
        
        # Check for duplicate transaction IDs
        if 'GLID' in df.columns:
            duplicates = df[df.duplicated(subset=['GLID'], keep=False)]
            if len(duplicates) > 0:
                validation_results['Duplicate Entries'].append(
                    f"Found {len(duplicates)} duplicate GLID entries"
                )
        
        # Verify debit/credit balance
        total_debit = df['Debit'].sum()
        total_credit = df['Credit'].sum()
        difference = abs(total_debit - total_credit)
        
        if difference > 0.01:  # Allow for small rounding errors
            validation_results['Balance Verification'].append(
                f"Debits (${total_debit:,.2f}) and Credits (${total_credit:,.2f}) "
                f"do not balance. Difference: ${difference:,.2f}"
            )
        
        # Check for transactions with both debit and credit
        both_entries = df[(df['Debit'] > 0) & (df['Credit'] > 0)]
        if len(both_entries) > 0:
            validation_results['Data Quality'].append(
                f"Found {len(both_entries)} transactions with both Debit and Credit amounts"
            )
        
        # Check for zero-amount transactions
        zero_transactions = df[(df['Debit'] == 0) & (df['Credit'] == 0)]
        if len(zero_transactions) > 0:
            validation_results['Data Quality'].append(
                f"Found {len(zero_transactions)} zero-amount transactions"
            )
        
        # Check for future dates
        today = pd.Timestamp.now()
        future_dates = df[df['TxnDate'] > today]
        if len(future_dates) > 0:
            validation_results['Date Issues'].append(
                f"Found {len(future_dates)} transactions with future dates"
            )
        
        # Check for very old dates (potential data errors)
        old_threshold = pd.Timestamp.now() - pd.Timedelta(days=365*5)  # 5 years ago
        old_dates = df[df['TxnDate'] < old_threshold]
        if len(old_dates) > 0:
            validation_results['Date Issues'].append(
                f"Found {len(old_dates)} transactions older than 5 years"
            )
        
        # Check for unusual account numbers
        if 'AccountNumber' in df.columns:
            # Check for negative account numbers
            negative_accounts = df[df['AccountNumber'] < 0]
            if len(negative_accounts) > 0:
                validation_results['Account Structure'].append(
                    f"Found {len(negative_accounts)} entries with negative account numbers"
                )
            
            # Check for very high account numbers (potential data entry errors)
            high_accounts = df[df['AccountNumber'] > 99999]
            if len(high_accounts) > 0:
                validation_results['Account Structure'].append(
                    f"Found {len(high_accounts)} entries with account numbers > 99999"
                )
        
        # Check for missing department or cost center
        if 'Dept' in df.columns:
            missing_dept = df[df['Dept'].isna() | (df['Dept'] == 'nan')]
            if len(missing_dept) > 0:
                validation_results['Missing Data'].append(
                    f"{len(missing_dept)} transactions missing Department"
                )
        
        if 'CostCenter' in df.columns:
            missing_cc = df[df['CostCenter'].isna() | (df['CostCenter'] == 'nan')]
            if len(missing_cc) > 0:
                validation_results['Missing Data'].append(
                    f"{len(missing_cc)} transactions missing Cost Center"
                )
        
        # Check for unusual amounts (potential outliers)
        if 'NetAmount' in df.columns:
            # Calculate statistics
            mean_amount = df['NetAmount'].abs().mean()
            std_amount = df['NetAmount'].abs().std()
            
            # Flag transactions > 3 standard deviations
            outliers = df[df['NetAmount'].abs() > (mean_amount + 3 * std_amount)]
            if len(outliers) > 0:
                validation_results['Data Quality'].append(
                    f"Found {len(outliers)} transactions with unusual amounts (>3σ from mean)"
                )
        
        return validation_results
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics for the dataset"""
        
        summary = {
            'total_rows': len(df),
            'date_range': {
                'start': df['TxnDate'].min(),
                'end': df['TxnDate'].max()
            },
            'total_debit': df['Debit'].sum(),
            'total_credit': df['Credit'].sum(),
            'unique_accounts': df['AccountNumber'].nunique(),
            'unique_departments': df['Dept'].nunique() if 'Dept' in df.columns else 0,
            'currencies': df['Currency'].unique().tolist() if 'Currency' in df.columns else []
        }
        
        return summary
