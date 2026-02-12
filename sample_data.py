"""
Sample Data Handler Module (Option B2)

- ONLY supports backup TB+GL packs (no sample_tb/sample_gl files).
- Backup packs must exist on disk (A1 policy). If none exist, raise a clear error.

Expected filenames under assets/sample_data:
  backup_tb_YYYY_YYYY.csv
  backup_gl_YYYY_YYYY_with_txnid.csv
  backup_gl_YYYY_YYYY_no_txnid.csv (optional)

This module is used by Streamlit demo controls and dataset download bundling.
"""

from __future__ import annotations

import os
import random
from typing import List, Tuple, Optional, Dict

import pandas as pd


def get_sample_data_path(filename: str) -> str:
    """
    Resolve a sample/backup data file path by checking common locations.
    """
    base_dir = os.path.dirname(__file__)

    possible_paths = [
        os.path.join(base_dir, filename),
        os.path.join(base_dir, "assets", "sample_data", filename),
        os.path.join("assets", "sample_data", filename),
        os.path.join("accounting_app", "assets", "sample_data", filename),
        os.path.join("/home/claude/accounting_app", "assets", "sample_data", filename),
        filename,  # current directory
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(f"Sample/backup data file not found: {filename}")


def _list_dir_candidates() -> List[str]:
    """
    List filenames in the most likely sample_data directory (best effort).
    """
    base_dir = os.path.dirname(__file__)
    candidates = [
        os.path.join(base_dir, "assets", "sample_data"),
        os.path.join("assets", "sample_data"),
        os.path.join("accounting_app", "assets", "sample_data"),
        os.path.join("/home/claude/accounting_app", "assets", "sample_data"),
        os.path.dirname(__file__),  # fallback
    ]
    for d in candidates:
        if os.path.isdir(d):
            try:
                return os.listdir(d)
            except Exception:
                continue
    return []


def list_backup_sets(require_with_txnid: bool = True) -> List[Tuple[int, int]]:
    """
    Discover available backup packs by scanning filenames.

    A set is considered available if:
      - backup_tb_YYYY_YYYY.csv exists
      - AND backup_gl_YYYY_YYYY_with_txnid.csv exists (default)
        (or no_txnid if require_with_txnid=False)

    Returns:
      List of (start_year, end_year) tuples.
    """
    files = _list_dir_candidates()
    sets = set()

    for fn in files:
        if not fn.startswith("backup_tb_") or not fn.endswith(".csv"):
            continue
        # backup_tb_2020_2022.csv
        try:
            core = fn.replace("backup_tb_", "").replace(".csv", "")
            y0, y1 = core.split("_")
            y0, y1 = int(y0), int(y1)
        except Exception:
            continue

        tb_name = f"backup_tb_{y0}_{y1}.csv"
        gl_name = f"backup_gl_{y0}_{y1}_{'with_txnid' if require_with_txnid else 'no_txnid'}.csv"

        try:
            get_sample_data_path(tb_name)
            get_sample_data_path(gl_name)
            sets.add((y0, y1))
        except Exception:
            continue

    return sorted(list(sets))


def load_backup_set(start_year: int, end_year: int, with_txnid: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    Load a specific backup TB+GL set.
    """
    tb_file = f"backup_tb_{start_year}_{end_year}.csv"
    gl_file = f"backup_gl_{start_year}_{end_year}_{'with_txnid' if with_txnid else 'no_txnid'}.csv"

    tb_df = pd.read_csv(get_sample_data_path(tb_file))
    gl_df = pd.read_csv(get_sample_data_path(gl_file))
    return tb_df, gl_df, f"{start_year}_{end_year}"


def load_random_backup_set(with_txnid: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """
    Load a random backup TB+GL set.

    A1 policy: backup packs must exist; if none exist, raise.
    """
    available = list_backup_sets(require_with_txnid=with_txnid)
    if not available:
        raise FileNotFoundError(
            "No backup sample packs found. Expected files like "
            "assets/sample_data/backup_tb_2020_2022.csv and "
            "assets/sample_data/backup_gl_2020_2022_with_txnid.csv."
        )
    start_year, end_year = random.choice(available)
    return load_backup_set(start_year, end_year, with_txnid=with_txnid)


def get_template_path(template_type: str = "zero") -> str:
    """
    Resolve template path.

    template_type:
      - 'zero' -> processing template (TEMPLATE_ZERO)
      - 'demo' -> sample demo template (SAMPLE_DEMO)
    """
    base_dir = os.path.dirname(__file__)

    if template_type == "zero":
        filename = "Financial_Model_TEMPLATE_ZERO_USD_thousands_GAAP.xlsx"
    else:
        filename = "Financial_Model_SAMPLE_DEMO_USD_thousands_GAAP.xlsx"

    possible_paths = [
        os.path.join(base_dir, filename),
        os.path.join(base_dir, "assets", "templates", filename),
        os.path.join("assets", "templates", filename),
        os.path.join("accounting_app", "assets", "templates", filename),
        os.path.join("/home/claude/accounting_app", "assets", "templates", filename),
        filename,
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(f"Template file not found: {filename}")
