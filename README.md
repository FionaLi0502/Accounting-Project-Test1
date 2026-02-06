# 🤖 AI Accounting Agent

An intelligent financial data processing system that automates GL validation, generates 3-statement models, and provides AI-powered insights.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **🔍 Smart Data Validation**: Automatically detects and fixes common GL data issues
- **💱 Currency Conversion**: Converts all currencies to USD automatically
- **📊 3-Statement Model**: Generates Income Statement, Balance Sheet, and Cash Flow
- **🔄 Data Reconciliation**: Tracks all changes and explains differences
- **🤖 AI Summary**: Generates insights and recommendations
- **📥 Export Options**: Download Excel models and summary reports

## 🚀 Quick Start

### Installation

```bash
# Clone or download this repository
cd ai-accounting-agent

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

### Demo

```bash
# Use the provided demo dataset
# Upload: messy_gl_data.csv
# This dataset has intentional issues for validation to catch
```

## 📊 How It Works

1. **Upload** your GL data (CSV or Excel)
2. **Validate** - AI detects issues and suggests fixes
3. **Clean** - One-click fixes or proceed with original data
4. **Generate** - Creates complete 3-statement model
5. **Analyze** - View reconciliation and AI insights
6. **Download** - Export Excel and reports

## 🎯 Use Cases

- Monthly financial close automation
- GL data quality checks
- Board report preparation
- Financial modeling
- Audit preparation
- M&A due diligence

## 📁 Project Structure

```
ai-accounting-agent/
├── streamlit_app.py          # Main application
├── requirements.txt           # Dependencies
├── messy_gl_data.csv         # Demo dataset
├── 3_statement_excel_completed_model.xlsx  # Excel template
└── README.md                 # This file
```

## 🔧 Configuration

### Account Number Ranges

The system expects standard GL account numbering:

- **1000-1999**: Assets
- **2000-2999**: Liabilities
- **3000-3999**: Equity
- **4000-4999**: Revenue
- **5000-5999**: Cost of Goods Sold
- **6000-7999**: Operating Expenses

### Required Columns

Your data should include:
- `TxnDate`: Transaction date
- `AccountNumber`: GL account number
- `AccountName`: Account description
- `Debit` / `Credit`: Transaction amounts
- `TransactionID`: Unique identifier (optional)

## 🎓 Customization

### Add New Validation Rules

```python
# In validate_data() function:
issues.append({
    'severity': 'Warning',
    'category': 'Your Category',
    'issue': 'Description',
    'impact': 'Why it matters',
    'suggestion': 'Fix recommendation',
    'auto_fix': 'fix_function_name'
})
```

### Add Custom Metrics

```python
# In calculate_financial_statements():
financial_data[year] = {
    # existing metrics...
    'your_metric': calculated_value,
}
```

## 🌐 Deployment

### Streamlit Cloud (Free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Deploy!

### Local Network

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

## 📈 Performance

- Handles datasets up to 100,000 transactions
- Processing time: <10 seconds for typical monthly GL
- Multi-year support (tested with 3+ years)

## 🐛 Troubleshooting

**Issue: Module not found**
```bash
pip install --upgrade -r requirements.txt
```

**Issue: Excel template not found**
- Ensure `3_statement_excel_completed_model.xlsx` is in project root

**Issue: Data not loading**
- Check file encoding (should be UTF-8)
- Verify column names match expected format

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional validation rules
- More financial metrics
- Data visualization
- PDF report generation
- API integrations

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Your Name - [Your LinkedIn](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Data processing with [Pandas](https://pandas.pydata.org/)
- Excel handling with [OpenPyXL](https://openpyxl.readthedocs.io/)

---

**Note**: This is a demonstration project for portfolio/interview purposes. For production use, additional security, authentication, and audit logging should be implemented.
