"""
PDF Export Module
Generates a professional PDF report with full 3-statement tables.

Key goals:
- Render full statement tables (not just a short summary)
- Allow multi-page tables when statements are long (repeat header row)
- Keep function name `create_pdf_report` for backward compatibility
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, LongTable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from typing import Dict, List, Optional, Callable, Tuple, Any


def create_pdf_report(
    financial_data: Dict[int, Dict],
    ai_summary: Optional[str] = None,
    company_name: str = "Sample Company",
    unit_label: str = "USD thousands",
) -> io.BytesIO:
    """
    Create comprehensive PDF report with all three statements.

    Args:
        financial_data: Dict of {year: {line_item: value}}
        ai_summary: Optional AI-generated summary text
        company_name: Name to display in report
        unit_label: Unit label (e.g., "USD dollars" / "USD thousands")

    Returns:
        BytesIO containing PDF file
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        title=f"{company_name} Financial Statements",
        author="Three Statements Automation",
        allowSplitting=1,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        spaceAfter=14,
        alignment=TA_CENTER,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=10,
        spaceBefore=14,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#222222"),
    )

    elements = []
    years = sorted([y for y in financial_data.keys() if isinstance(y, int)])

    # Title page header
    elements.append(Paragraph(company_name, title_style))
    elements.append(Paragraph(f"Financial Statements ({unit_label})", subtitle_style))
    elements.append(Spacer(1, 0.15 * inch))

    # Income Statement
    elements.append(Paragraph("Income Statement", section_style))
    elements.append(_create_statement_table(
        financial_data,
        years,
        _income_statement_lines(),
        number_format="{:,.1f}",
    ))
    elements.append(PageBreak())

    # Balance Sheet
    elements.append(Paragraph("Balance Sheet", section_style))
    elements.append(_create_statement_table(
        financial_data,
        years,
        _balance_sheet_lines(),
        number_format="{:,.1f}",
    ))
    elements.append(PageBreak())

    # Cash Flow (if multi-year)
    if len(years) >= 2:
        elements.append(Paragraph("Cash Flow Statement", section_style))
        # Cash flow is typically shown for years 2..N (needs prior year for deltas)
        cf_years = years[1:]
        elements.append(_create_statement_table(
            financial_data,
            cf_years,
            _cash_flow_lines(),
            number_format="{:,.1f}",
        ))
        elements.append(PageBreak())

    # AI Summary
    if ai_summary and ai_summary.strip():
        elements.append(Paragraph("AI-Generated Summary & Insights", section_style))
        elements.append(Spacer(1, 0.08 * inch))
        for para in ai_summary.split("\n\n"):
            para = para.strip()
            if para:
                elements.append(Paragraph(para, body_style))
                elements.append(Spacer(1, 0.08 * inch))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def _create_statement_table(
    financial_data: Dict[int, Dict],
    years: List[int],
    line_items: List[Tuple[str, Optional[Any]]],
    number_format: str = "{:,.1f}",
):
    """
    Build a multipage-safe table (LongTable) with repeated header row.
    line_items: List of (label, key) where key can be:
      - None (section header / blank line)
      - str (dictionary key)
      - callable(dict)-> number
    """
    # Header
    header = [""] + [str(y) for y in years]
    data = [header]

    for label, key in line_items:
        row = [label]
        for year in years:
            if key is None:
                row.append("")
                continue

            year_dict = financial_data.get(year, {}) if financial_data else {}
            if callable(key):
                try:
                    val = key(year_dict)
                except Exception:
                    val = None
            else:
                val = year_dict.get(key, None)

            if val is None:
                row.append("—")
            else:
                try:
                    row.append(number_format.format(float(val)))
                except Exception:
                    row.append(str(val))
        data.append(row)

    # Use LongTable so statements can span multiple pages
    table = LongTable(data, repeatRows=1)
    table.setStyle(_default_table_style())
    return table


def _default_table_style() -> TableStyle:
    return TableStyle([
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f4f7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111111")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9.5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#d0d7de")),
        # Body
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfcfe")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])


def _income_statement_lines() -> List[Tuple[str, Optional[Any]]]:
    return [
        ("Revenues", "revenue"),
        ("Cost of Goods Sold", "cogs"),
        ("Gross Profit", lambda d: (d.get("revenue", 0) - d.get("cogs", 0))),
        ("", None),
        ("Operating Expenses:", None),
        ("  Distribution Expenses", "distribution_expenses"),
        ("  Marketing and Administration", "marketing_admin"),
        ("  Research and Development", "research_dev"),
        ("  Depreciation", "depreciation_expense"),
        ("Total Operating Expenses", lambda d: (
            d.get("distribution_expenses", 0)
            + d.get("marketing_admin", 0)
            + d.get("research_dev", 0)
            + d.get("depreciation_expense", 0)
        )),
        ("", None),
        ("EBIT (Operating Profit)", lambda d: (
            (d.get("revenue", 0) - d.get("cogs", 0))
            - (d.get("distribution_expenses", 0)
               + d.get("marketing_admin", 0)
               + d.get("research_dev", 0)
               + d.get("depreciation_expense", 0))
        )),
        ("Interest Expense", "interest_expense"),
        ("Income Before Taxes", lambda d: (
            (d.get("revenue", 0) - d.get("cogs", 0))
            - (d.get("distribution_expenses", 0)
               + d.get("marketing_admin", 0)
               + d.get("research_dev", 0)
               + d.get("depreciation_expense", 0))
            - d.get("interest_expense", 0)
        )),
        ("Income Tax Expense", "tax_expense"),
        ("Net Income", lambda d: (
            (d.get("revenue", 0) - d.get("cogs", 0))
            - (d.get("distribution_expenses", 0)
               + d.get("marketing_admin", 0)
               + d.get("research_dev", 0)
               + d.get("depreciation_expense", 0))
            - d.get("interest_expense", 0)
            - d.get("tax_expense", 0)
        )),
    ]


def _balance_sheet_lines() -> List[Tuple[str, Optional[Any]]]:
    # Note: values should already be positive for liabilities/equity if upstream normalizes.
    return [
        ("Assets", None),
        ("Current Assets:", None),
        ("  Cash", "cash"),
        ("  Accounts Receivable", "accounts_receivable"),
        ("  Inventory", "inventory"),
        ("  Prepaid Expenses", "prepaid_expenses"),
        ("  Other Current Assets", "other_current_assets"),
        ("Total Current Assets", lambda d: (
            d.get("cash", 0) + d.get("accounts_receivable", 0) + d.get("inventory", 0)
            + d.get("prepaid_expenses", 0) + d.get("other_current_assets", 0)
        )),
        ("", None),
        ("Non-Current Assets:", None),
        ("  Property, Plant & Equipment (Gross)", "ppe_gross"),
        ("  Accumulated Depreciation", "accumulated_depreciation"),
        ("  Property, Plant & Equipment (Net)", lambda d: (
            d.get("ppe_gross", 0) - d.get("accumulated_depreciation", 0)
        )),
        ("Total Assets", lambda d: (
            (d.get("cash", 0) + d.get("accounts_receivable", 0) + d.get("inventory", 0)
             + d.get("prepaid_expenses", 0) + d.get("other_current_assets", 0))
            + (d.get("ppe_gross", 0) - d.get("accumulated_depreciation", 0))
        )),
        ("", None),
        ("Liabilities and Equity", None),
        ("Current Liabilities:", None),
        ("  Accounts Payable", "accounts_payable"),
        ("  Accrued Payroll", "accrued_payroll"),
        ("  Deferred Revenue", "deferred_revenue"),
        ("  Interest Payable", "interest_payable"),
        ("  Income Taxes Payable", "income_taxes_payable"),
        ("  Other Current Liabilities", "other_current_liabilities"),
        ("Total Current Liabilities", lambda d: (
            d.get("accounts_payable", 0) + d.get("accrued_payroll", 0) + d.get("deferred_revenue", 0)
            + d.get("interest_payable", 0) + d.get("income_taxes_payable", 0) + d.get("other_current_liabilities", 0)
        )),
        ("Long-Term Liabilities:", None),
        ("  Long-Term Debt", "long_term_debt"),
        ("Total Liabilities", lambda d: (
            (d.get("accounts_payable", 0) + d.get("accrued_payroll", 0) + d.get("deferred_revenue", 0)
             + d.get("interest_payable", 0) + d.get("income_taxes_payable", 0) + d.get("other_current_liabilities", 0))
            + d.get("long_term_debt", 0)
        )),
        ("", None),
        ("Equity:", None),
        ("  Common Stock and APIC", "common_stock"),
        ("  Retained Earnings", "retained_earnings"),
        ("Total Equity", lambda d: (d.get("common_stock", 0) + d.get("retained_earnings", 0))),
        ("Total Liabilities & Equity", lambda d: (
            (d.get("accounts_payable", 0) + d.get("accrued_payroll", 0) + d.get("deferred_revenue", 0)
             + d.get("interest_payable", 0) + d.get("income_taxes_payable", 0) + d.get("other_current_liabilities", 0)
             + d.get("long_term_debt", 0))
            + (d.get("common_stock", 0) + d.get("retained_earnings", 0))
        )),
    ]


def _cash_flow_lines() -> List[Tuple[str, Optional[Any]]]:
    return [
        ("Operating Activities:", None),
        ("  Net Income", lambda d: (
            (d.get("revenue", 0) - d.get("cogs", 0))
            - (d.get("distribution_expenses", 0)
               + d.get("marketing_admin", 0)
               + d.get("research_dev", 0)
               + d.get("depreciation_expense", 0))
            - d.get("interest_expense", 0)
            - d.get("tax_expense", 0)
        )),
        ("  Depreciation", "depreciation_expense"),
        ("  Change in Accounts Receivable", "delta_ar"),
        ("  Change in Inventory", "delta_inventory"),
        ("  Change in Prepaid Expenses", "delta_prepaid"),
        ("  Change in Other Current Assets", "delta_other_current_assets"),
        ("  Change in Accounts Payable", "delta_ap"),
        ("  Change in Accrued Payroll", "delta_accrued_payroll"),
        ("  Change in Deferred Revenue", "delta_deferred_revenue"),
        ("  Change in Interest Payable", "delta_interest_payable"),
        ("  Change in Other Current Liabilities", "delta_other_current_liabilities"),
        ("  Change in Income Taxes Payable", "delta_income_taxes_payable"),
        ("Cash from Operating Activities", lambda d: sum([
            # net income
            (d.get("revenue", 0) - d.get("cogs", 0))
            - (d.get("distribution_expenses", 0)
               + d.get("marketing_admin", 0)
               + d.get("research_dev", 0)
               + d.get("depreciation_expense", 0))
            - d.get("interest_expense", 0)
            - d.get("tax_expense", 0),
            # add-backs + wc
            d.get("depreciation_expense", 0),
            d.get("delta_ar", 0),
            d.get("delta_inventory", 0),
            d.get("delta_prepaid", 0),
            d.get("delta_other_current_assets", 0),
            d.get("delta_ap", 0),
            d.get("delta_accrued_payroll", 0),
            d.get("delta_deferred_revenue", 0),
            d.get("delta_interest_payable", 0),
            d.get("delta_other_current_liabilities", 0),
            d.get("delta_income_taxes_payable", 0),
        ])),
        ("", None),
        ("Investing Activities:", None),
        ("  Acquisitions of PP&E", "capex"),
        ("Cash from Investing Activities", "capex"),
        ("", None),
        ("Financing Activities:", None),
        ("  Issuance of Common Stock", "stock_issuance"),
        ("  Dividends", lambda d: -d.get("dividends", 0)),
        ("  Change in Long-Term Debt", "delta_debt"),
        ("Cash from Financing Activities", lambda d: (
            d.get("stock_issuance", 0) - d.get("dividends", 0) + d.get("delta_debt", 0)
        )),
        ("", None),
        ("Net Change in Cash", lambda d: (
            # CFO + CFI + CFF
            sum([
                (d.get("revenue", 0) - d.get("cogs", 0))
                - (d.get("distribution_expenses", 0)
                   + d.get("marketing_admin", 0)
                   + d.get("research_dev", 0)
                   + d.get("depreciation_expense", 0))
                - d.get("interest_expense", 0)
                - d.get("tax_expense", 0),
                d.get("depreciation_expense", 0),
                d.get("delta_ar", 0),
                d.get("delta_inventory", 0),
                d.get("delta_prepaid", 0),
                d.get("delta_other_current_assets", 0),
                d.get("delta_ap", 0),
                d.get("delta_accrued_payroll", 0),
                d.get("delta_deferred_revenue", 0),
                d.get("delta_interest_payable", 0),
                d.get("delta_other_current_liabilities", 0),
                d.get("delta_income_taxes_payable", 0),
            ]) + d.get("capex", 0) + (d.get("stock_issuance", 0) - d.get("dividends", 0) + d.get("delta_debt", 0))
        )),
    ]
