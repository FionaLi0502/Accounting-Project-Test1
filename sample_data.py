"""
Sample Data Handler Module - V5 Integration
Manages sample data loading for demo buttons with TB+GL pairing
"""

import pandas as pd
import os
import random
import re
from typing import Tuple, Optional, List


def get_v5_data_path(filename: str) -> str:
    """
    Get full path to v5 package data file
    
    Args:
        filename: Name of data file
    
    Returns:
        Full path to file
    """
    # Try multiple possible locations for v5 package
    possible_paths = [
        os.path.join('assets', 'v5', filename),
        os.path.join('accounting_app', 'assets', 'v5', filename),
        os.path.join('/home/claude/accounting_app', 'assets', 'v5', filename),
        os.path.join('assets', filename),  # Fallback
        filename,  # Current directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError(f"V5 data file not found: {filename}")


def load_sample_tb() -> pd.DataFrame:
    """
    Load sample Trial Balance data (v5)
    
    Returns:
        DataFrame with sample TB data
    """
    try:
        path = get_v5_data_path('sample_tb.csv')
        df = pd.read_csv(path)
        return df
    except Exception as e:
        raise Exception(f"Error loading sample TB: {str(e)}")


def load_sample_gl(with_txnid: bool = True) -> pd.DataFrame:
    """
    Load sample GL Activity data (v5)
    
    Args:
        with_txnid: Whether to load version with TransactionID
    
    Returns:
        DataFrame with sample GL data
    """
    try:
        filename = 'sample_gl_with_txnid.csv' if with_txnid else 'sample_gl_no_txnid.csv'
        path = get_v5_data_path(filename)
        df = pd.read_csv(path)
        return df
    except Exception as e:
        raise Exception(f"Error loading sample GL: {str(e)}")


def get_sample_tb_file() -> Tuple[bytes, str]:
    """
    Get sample TB file for download
    
    Returns:
        (file_bytes, filename)
    """
    try:
        path = get_v5_data_path('sample_tb.csv')
        with open(path, 'rb') as f:
            return f.read(), 'sample_tb.csv'
    except Exception as e:
        raise Exception(f"Error reading sample TB file: {str(e)}")


def get_sample_gl_files() -> List[Tuple[bytes, str]]:
    """
    Get sample GL files for download (both variants)
    
    Returns:
        List of (file_bytes, filename) tuples
    """
    files = []
    try:
        # With TransactionID
        path_with = get_v5_data_path('sample_gl_with_txnid.csv')
        with open(path_with, 'rb') as f:
            files.append((f.read(), 'sample_gl_with_txnid.csv'))
        
        # Without TransactionID
        path_no = get_v5_data_path('sample_gl_no_txnid.csv')
        with open(path_no, 'rb') as f:
            files.append((f.read(), 'sample_gl_no_txnid.csv'))
        
        return files
    except Exception as e:
        raise Exception(f"Error reading sample GL files: {str(e)}")


def parse_year_range_from_filename(filename: str) -> Optional[str]:
    """
    Extract year range from backup filename
    
    Args:
        filename: Backup file name (e.g., 'backup_tb_2021_2022.csv')
    
    Returns:
        Year range string (e.g., '2021_2022') or None
    """
    match = re.search(r'(\d{4}_\d{4})', filename)
    return match.group(1) if match else None


def get_available_backup_ranges() -> dict:
    """
    Get available TB and GL backup year ranges from v5 package
    
    Returns:
        Dict with 'tb_ranges', 'gl_ranges', and 'valid_pairs'
    """
    import glob
    
    # Find all backup files in v5 directory
    v5_dir = None
    possible_dirs = [
        'assets/v5',
        'accounting_app/assets/v5',
        '/home/claude/accounting_app/assets/v5',
        'assets',
    ]
    
    for dir_path in possible_dirs:
        if os.path.exists(dir_path):
            v5_dir = dir_path
            break
    
    if not v5_dir:
        return {'tb_ranges': [], 'gl_ranges': [], 'valid_pairs': []}
    
    # Parse TB ranges
    tb_files = []
    gl_files = []
    
    for file in os.listdir(v5_dir):
        if file.startswith('backup_tb_') and file.endswith('.csv'):
            year_range = parse_year_range_from_filename(file)
            if year_range:
                tb_files.append((year_range, file))
        elif file.startswith('backup_gl_') and file.endswith('.csv'):
            year_range = parse_year_range_from_filename(file)
            if year_range:
                gl_files.append((year_range, file))
    
    # Get unique ranges
    tb_ranges = set([r for r, _ in tb_files])
    gl_ranges = set([r for r, _ in gl_files])
    
    # Compute intersection (valid pairs)
    valid_pairs = list(tb_ranges & gl_ranges)
    
    return {
        'tb_ranges': sorted(list(tb_ranges)),
        'gl_ranges': sorted(list(gl_ranges)),
        'valid_pairs': sorted(valid_pairs)
    }


def load_random_backup_pair() -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    Load a random matching TB + GL backup pair (v5)
    
    Returns:
        (tb_dataframe, gl_dataframe, year_range)
    """
    # Get available ranges
    ranges_info = get_available_backup_ranges()
    valid_pairs = ranges_info['valid_pairs']
    
    if not valid_pairs:
        raise Exception("No matching TB/GL backup pairs found in v5 package")
    
    # Randomly select a range
    selected_range = random.choice(valid_pairs)
    
    # Load TB for this range
    tb_filename = f'backup_tb_{selected_range}.csv'
    try:
        tb_path = get_v5_data_path(tb_filename)
        tb_df = pd.read_csv(tb_path)
    except Exception as e:
        raise Exception(f"Error loading TB backup {tb_filename}: {str(e)}")
    
    # Load GL for this range (prefer with_txnid)
    gl_with_txnid = f'backup_gl_{selected_range}_with_txnid.csv'
    gl_no_txnid = f'backup_gl_{selected_range}_no_txnid.csv'
    
    try:
        # Try with_txnid first
        gl_path = get_v5_data_path(gl_with_txnid)
        gl_df = pd.read_csv(gl_path)
        gl_variant = 'with_txnid'
    except:
        try:
            # Fall back to no_txnid
            gl_path = get_v5_data_path(gl_no_txnid)
            gl_df = pd.read_csv(gl_path)
            gl_variant = 'no_txnid'
        except Exception as e:
            raise Exception(f"Error loading GL backup for range {selected_range}: {str(e)}")
    
    dataset_name = f"{selected_range} ({gl_variant})"
    
    return tb_df, gl_df, dataset_name


def get_template_path(template_type: str = 'zero') -> str:
    """
    Get path to Excel template (v5)
    
    Args:
        template_type: 'zero' for processing template, 'demo' for sample
    
    Returns:
        Full path to template file
    """
    if template_type == 'zero':
        filename = 'Financial_Model_TEMPLATE_ZERO_USD_thousands_GAAP.xlsx'
    else:
        filename = 'Financial_Model_SAMPLE_DEMO_USD_thousands_GAAP.xlsx'
    
    # Try v5 locations first
    possible_paths = [
        os.path.join('assets', 'v5', filename),
        os.path.join('accounting_app', 'assets', 'v5', filename),
        os.path.join('/home/claude/accounting_app', 'assets', 'v5', filename),
        os.path.join('assets', 'templates', filename),  # Fallback
        filename,
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError(f"Template file not found: {filename}")


def list_available_datasets() -> dict:
    """
    List all available sample datasets (v5)
    
    Returns:
        Dict with dataset information
    """
    datasets = {
        'trial_balance': {
            'file': 'sample_tb.csv',
            'description': 'Sample Trial Balance (v5)',
            'has_txnid': False,
            'available': False
        },
        'gl_with_txnid': {
            'file': 'sample_gl_with_txnid.csv',
            'description': 'Sample GL Activity with TransactionID (v5)',
            'has_txnid': True,
            'available': False
        },
        'gl_no_txnid': {
            'file': 'sample_gl_no_txnid.csv',
            'description': 'Sample GL Activity without TransactionID (v5)',
            'has_txnid': False,
            'available': False
        },
        'backups': {
            'description': 'TB+GL backup pairs for random testing (v5)',
            'available': False,
            'pairs': []
        }
    }
    
    # Check sample files
    try:
        get_v5_data_path('sample_tb.csv')
        datasets['trial_balance']['available'] = True
    except:
        pass
    
    try:
        get_v5_data_path('sample_gl_with_txnid.csv')
        datasets['gl_with_txnid']['available'] = True
    except:
        pass
    
    try:
        get_v5_data_path('sample_gl_no_txnid.csv')
        datasets['gl_no_txnid']['available'] = True
    except:
        pass
    
    # Check backup pairs
    try:
        ranges_info = get_available_backup_ranges()
        if ranges_info['valid_pairs']:
            datasets['backups']['available'] = True
            datasets['backups']['pairs'] = ranges_info['valid_pairs']
            datasets['backups']['count'] = len(ranges_info['valid_pairs'])
    except:
        pass
    
    return datasets
