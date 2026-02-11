# 🎓 Training Guide: Handling Complex Data & Improving AI Analysis

## Overview

This guide explains how to fetch more complex data, improve validation, and enhance AI analysis quality for real-world scenarios where data is messy and full of errors.

---

## 📊 Part 1: Fetching More Complex Data

### Real-World Data Sources

#### 1. **ERP Systems** (SAP, Oracle, NetSuite)

**Manual Export:**
```sql
-- Example SAP query for GL data
SELECT
    BELNR as TransactionID,
    BUDAT as PostingDate,
    HKONT as AccountNumber,
    TXT50 as AccountName,
    DMBTR as Amount,
    SHKZG as DebitCreditIndicator,
    KOSTL as CostCenter,
    AUGDT as ClearingDate
FROM BSEG
WHERE BUDAT BETWEEN '20240101' AND '20241231'
```

**Automated Integration:**
```python
# Example: Connect to database
import pyodbc

connection_string = "DRIVER={SQL Server};SERVER=your_server;DATABASE=your_db;UID=user;PWD=pass"
conn = pyodbc.connect(connection_string)

query = """
SELECT * FROM GL_TRANSACTIONS 
WHERE POSTING_DATE >= '2024-01-01'
"""

df = pd.read_sql(query, conn)
df.to_excel('gl_export.xlsx', index=False)
```

#### 2. **Accounting Software APIs** (QuickBooks, Xero)

```python
# Example: QuickBooks API
from intuitlib.client import AuthClient
from quickbooks import QuickBooks
from quickbooks.objects import GeneralLedger

# Authenticate and fetch
qb = QuickBooks(...)
gl_data = GeneralLedger.all(qb=qb)
```

#### 3. **Multi-Entity Consolidation**

```python
# Combine multiple entities
entities = ['Entity_A.xlsx', 'Entity_B.xlsx', 'Entity_C.xlsx']
combined_df = pd.DataFrame()

for entity in entities:
    df = pd.read_excel(entity)
    df['Entity'] = entity.replace('.xlsx', '')
    combined_df = pd.concat([combined_df, df], ignore_index=True)

combined_df.to_excel('consolidated_gl.xlsx', index=False)
```

---

## 🔧 Part 2: Handling Messy Real-World Data

### Common Data Issues & Solutions

#### Issue 1: **Inconsistent Date Formats**

**Problem:**
```python
# Mixed formats in same column
dates = ['2024-01-15', '01/15/2024', '15-Jan-2024', '1/15/24']
```

**Solution in `data_processor.py`:**
```python
def _clean_dates(self, df):
    """Handle multiple date formats"""
    from dateutil import parser
    
    def parse_flexible_date(date_value):
        if pd.isna(date_value):
            return pd.NaT
        try:
            return parser.parse(str(date_value))
        except:
            return pd.NaT
    
    df['TxnDate'] = df['TxnDate'].apply(parse_flexible_date)
    return df
```

#### Issue 2: **Missing Critical Data**

**Problem:**
```python
# 30% of transactions missing cost center
# Some account names are blank
```

**Enhanced Validation:**
```python
def validate_completeness(self, df):
    """Check data completeness"""
    issues = []
    
    # Critical fields threshold
    critical_fields = {
        'AccountNumber': 0,     # 0% missing allowed
        'TxnDate': 0,
        'AccountName': 5,       # 5% missing allowed
        'CostCenter': 20,       # 20% missing allowed
        'Dept': 20
    }
    
    for field, threshold in critical_fields.items():
        if field in df.columns:
            missing_pct = (df[field].isna().sum() / len(df)) * 100
            if missing_pct > threshold:
                issues.append(
                    f"{field}: {missing_pct:.1f}% missing "
                    f"(exceeds {threshold}% threshold)"
                )
    
    return issues
```

#### Issue 3: **Unbalanced Entries**

**Problem:**
```python
# Debits don't equal credits
# Manual journal entries without offsetting entries
```

**Advanced Validation:**
```python
def validate_balance_by_transaction(self, df):
    """Check if each transaction balances"""
    issues = []
    
    # Group by transaction ID
    if 'GLID' in df.columns:
        balance_check = df.groupby('GLID').agg({
            'Debit': 'sum',
            'Credit': 'sum'
        })
        
        balance_check['Difference'] = balance_check['Debit'] - balance_check['Credit']
        
        # Find unbalanced transactions
        unbalanced = balance_check[abs(balance_check['Difference']) > 0.01]
        
        if len(unbalanced) > 0:
            issues.append(
                f"Found {len(unbalanced)} unbalanced transactions totaling "
                f"${unbalanced['Difference'].sum():,.2f}"
            )
            
            # Detail top offenders
            top_issues = unbalanced.nlargest(5, 'Difference')
            for idx, row in top_issues.iterrows():
                issues.append(
                    f"  Transaction {idx}: Off by ${row['Difference']:,.2f}"
                )
    
    return issues
```

#### Issue 4: **Duplicate Transactions**

**Problem:**
```python
# Same transaction imported multiple times
# Manual adjustments creating duplicates
```

**Smart Duplicate Detection:**
```python
def detect_duplicates(self, df):
    """Intelligent duplicate detection"""
    issues = []
    
    # Method 1: Exact duplicates on key fields
    duplicate_cols = ['TxnDate', 'AccountNumber', 'Debit', 'Credit', 'Description']
    available_cols = [col for col in duplicate_cols if col in df.columns]
    
    exact_dupes = df[df.duplicated(subset=available_cols, keep=False)]
    
    if len(exact_dupes) > 0:
        issues.append(f"Found {len(exact_dupes)} exact duplicate transactions")
    
    # Method 2: Near duplicates (same day, account, similar amount)
    df['Amount'] = df['Debit'] + df['Credit']
    
    for (date, account), group in df.groupby(['TxnDate', 'AccountNumber']):
        if len(group) > 1:
            # Check for similar amounts (within 1%)
            amounts = group['Amount'].values
            for i in range(len(amounts)):
                for j in range(i+1, len(amounts)):
                    diff_pct = abs(amounts[i] - amounts[j]) / max(amounts[i], amounts[j])
                    if diff_pct < 0.01:
                        issues.append(
                            f"Potential duplicate on {date}, Account {account}: "
                            f"${amounts[i]:,.2f} and ${amounts[j]:,.2f}"
                        )
    
    return issues
```

#### Issue 5: **Data Type Mismatches**

**Problem:**
```python
# Account numbers stored as text: "4000-100"
# Amounts with commas: "1,234.56"
# Currency symbols: "$1,234.56"
```

**Robust Cleaning:**
```python
def _clean_data_types(self, df):
    """Clean and standardize data types"""
    
    # Clean account numbers
    if 'AccountNumber' in df.columns:
        df['AccountNumber'] = df['AccountNumber'].astype(str)
        df['AccountNumber'] = df['AccountNumber'].str.replace(r'[^0-9]', '', regex=True)
        df['AccountNumber'] = pd.to_numeric(df['AccountNumber'], errors='coerce')
    
    # Clean amounts
    for col in ['Debit', 'Credit']:
        if col in df.columns:
            # Remove currency symbols and commas
            df[col] = df[col].astype(str)
            df[col] = df[col].str.replace('$', '').str.replace(',', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0)
    
    return df
```

---

## 🤖 Part 3: Improving AI Analysis Quality

### Understanding Claude's Limitations

Claude is **NOT trained** on your specific data. Each analysis is independent. However, you can improve results through:

### 1. **Better Prompt Engineering**

**Current Approach (Basic):**
```python
prompt = f"Analyze this financial data: {data}"
```

**Improved Approach (Detailed Context):**
```python
def _build_enhanced_prompt(self, context):
    """Build detailed prompt with context"""
    
    # Industry context
    industry = context.get('industry', 'General Business')
    company_size = context.get('revenue_size', 'Mid-size')
    
    # Historical context
    prior_period = context.get('prior_period_summary')
    
    prompt = f"""You are a senior financial analyst reviewing {company_size} {industry} company data.

CURRENT PERIOD DATA:
{self._format_current_data(context)}

HISTORICAL CONTEXT:
{prior_period if prior_period else 'First period - no comparison available'}

COMPANY-SPECIFIC CONSIDERATIONS:
- Known seasonality: {context.get('seasonality', 'Unknown')}
- Recent events: {context.get('recent_events', 'None reported')}
- Key initiatives: {context.get('initiatives', 'None')}

ANALYSIS REQUIREMENTS:
1. Compare to historical trends
2. Identify anomalies considering seasonality
3. Assess variance significance (materiality threshold: 10%)
4. Provide actionable recommendations

Focus on:
- Material variances (>10% or >$50K)
- Cash flow implications
- Risks to forecast
"""
    return prompt
```

### 2. **Provide Examples of Good Analysis**

**Few-Shot Learning:**
```python
def _add_examples_to_prompt(self, prompt):
    """Add example analyses to guide Claude"""
    
    examples = """
EXAMPLE OF GOOD ANALYSIS:

Revenue Variance:
✓ "Revenue declined 12% MoM ($1.2M to $1.05M). Key drivers:
   1. Product A sales down 25% due to seasonal slowdown (expected)
   2. Product B up 15% from new customer wins (positive)
   3. Net effect: -12% total, in line with typical Q4 patterns"

✗ "Revenue went down" (too vague)

Cost Variance:
✓ "COGS increased 8% despite 12% revenue decline, indicating margin compression.
   Root cause investigation needed on:
   1. Unit costs (supplier pricing changes?)
   2. Product mix (shift to lower margin products?)
   3. Waste/inefficiency metrics"

✗ "Costs went up" (no investigation)
"""
    
    return prompt + "\n" + examples
```

### 3. **Iterative Analysis with Memory**

**Multi-Step Analysis:**
```python
def deep_analysis(self, context):
    """Perform multi-step analysis"""
    
    # Step 1: Initial analysis
    initial_analysis = self.client.messages.create(
        model=self.model,
        max_tokens=1000,
        messages=[{"role": "user", "content": self._build_prompt(context)}]
    )
    
    initial_text = initial_analysis.content[0].text
    
    # Step 2: Ask follow-up questions
    follow_up = f"""Based on your initial analysis:
    
{initial_text}

Now please:
1. For each variance >10%, provide 3 specific investigation steps
2. Rank all findings by urgency (High/Medium/Low)
3. Estimate financial impact of each risk you identified
"""
    
    deep_analysis = self.client.messages.create(
        model=self.model,
        max_tokens=1500,
        messages=[
            {"role": "user", "content": self._build_prompt(context)},
            {"role": "assistant", "content": initial_text},
            {"role": "user", "content": follow_up}
        ]
    )
    
    return deep_analysis.content[0].text
```

### 4. **Domain-Specific Fine-Tuning**

While you can't directly train Claude, you can create industry-specific prompts:

```python
# Create industry knowledge base
INDUSTRY_BENCHMARKS = {
    'SaaS': {
        'gross_margin_range': (70, 85),
        'r_and_d_pct': (15, 25),
        'sales_marketing_pct': (40, 60),
        'key_metrics': ['MRR', 'Churn Rate', 'CAC', 'LTV']
    },
    'Manufacturing': {
        'gross_margin_range': (25, 40),
        'r_and_d_pct': (5, 10),
        'inventory_turns': (4, 8),
        'key_metrics': ['Inventory Days', 'Capacity Utilization', 'Scrap Rate']
    }
}

def add_industry_context(self, prompt, industry):
    """Add industry-specific benchmarks"""
    benchmarks = INDUSTRY_BENCHMARKS.get(industry, {})
    
    context = f"""
INDUSTRY BENCHMARKS ({industry}):
- Typical Gross Margin: {benchmarks.get('gross_margin_range', 'Unknown')}
- R&D Spending: {benchmarks.get('r_and_d_pct', 'Unknown')}% of revenue
- Key Metrics to Watch: {', '.join(benchmarks.get('key_metrics', []))}
"""
    
    return prompt + context
```

---

## 📈 Part 4: Building a "Training" Dataset

While Claude doesn't train on your data, you can create a reference library:

### Historical Analysis Repository

```python
class AnalysisRepository:
    """Store and retrieve historical analyses"""
    
    def __init__(self):
        self.analyses = []
        self.load_from_file()
    
    def store_analysis(self, period, data, ai_response, actual_outcome):
        """Store analysis with outcome"""
        self.analyses.append({
            'period': period,
            'data_snapshot': data,
            'ai_analysis': ai_response,
            'actual_outcome': actual_outcome,  # What actually happened
            'accuracy_score': self._calculate_accuracy(ai_response, actual_outcome)
        })
        self.save_to_file()
    
    def get_similar_scenarios(self, current_data):
        """Find similar past scenarios"""
        # Use similarity metrics to find comparable situations
        similar = []
        
        for past in self.analyses:
            similarity = self._calculate_similarity(current_data, past['data_snapshot'])
            if similarity > 0.7:
                similar.append(past)
        
        return similar
    
    def build_context_from_history(self, current_data):
        """Use historical data to enhance current analysis"""
        similar_scenarios = self.get_similar_scenarios(current_data)
        
        if not similar_scenarios:
            return ""
        
        context = "SIMILAR PAST SCENARIOS:\n"
        for scenario in similar_scenarios[:3]:
            context += f"""
Period: {scenario['period']}
What AI predicted: {scenario['ai_analysis'][:200]}...
What actually happened: {scenario['actual_outcome']}
Accuracy: {scenario['accuracy_score']:.0%}
"""
        
        return context
```

---

## 🎯 Part 5: Validation Rule Library

Create comprehensive validation rules for your specific business:

```python
# custom_validations.py

class CustomValidationRules:
    """Company-specific validation rules"""
    
    def __init__(self, company_config):
        self.config = company_config
    
    def validate_approval_limits(self, df):
        """Check transactions exceed approval limits"""
        issues = []
        
        approval_limits = self.config.get('approval_limits', {
            'Manager': 10000,
            'Director': 50000,
            'VP': 100000,
            'CFO': float('inf')
        })
        
        # Check if transactions have proper approval
        for idx, row in df.iterrows():
            amount = abs(row['Debit'] - row['Credit'])
            approver = row.get('ApprovedBy', 'None')
            
            required_level = self._get_required_approval_level(amount, approval_limits)
            
            if not self._has_sufficient_approval(approver, required_level):
                issues.append(
                    f"Transaction {row['GLID']} (${amount:,.2f}) "
                    f"requires {required_level} approval, has {approver}"
                )
        
        return issues
    
    def validate_account_restrictions(self, df):
        """Check accounts used correctly"""
        issues = []
        
        # Define restricted accounts
        restricted = {
            '1000-1099': 'Cash accounts - requires bank rec',
            '9000-9999': 'Closing accounts - only for year-end'
        }
        
        current_month = df['TxnDate'].max().month
        
        for account_range, restriction in restricted.items():
            start, end = map(int, account_range.split('-'))
            
            violations = df[
                (df['AccountNumber'] >= start) & 
                (df['AccountNumber'] <= end)
            ]
            
            if 'year-end' in restriction and current_month not in [12, 1]:
                if len(violations) > 0:
                    issues.append(
                        f"{len(violations)} transactions in {account_range}: {restriction}"
                    )
        
        return issues
```

---

## 💡 Best Practices Summary

### For Data Quality:
1. **Start with data profiling** - understand what you're getting
2. **Build incrementally** - add validation rules as you find issues
3. **Use statistical methods** - outlier detection, z-scores
4. **Document exceptions** - track known issues and workarounds

### For AI Quality:
1. **Provide context** - industry, history, company-specific info
2. **Use examples** - show what good analysis looks like
3. **Iterate** - multi-step analysis for complex scenarios
4. **Validate outputs** - check AI recommendations against reality
5. **Build a library** - save good analyses as templates

### For Continuous Improvement:
1. **Track accuracy** - measure how often AI insights are correct
2. **Learn from errors** - when AI misses something, understand why
3. **Refine prompts** - improve based on what works
4. **Expand validations** - add rules for newly discovered issues
5. **Share learnings** - document what works for your specific use case

---

## 🚀 Next Steps

1. **Test with your real data** - see what breaks
2. **Add custom validations** - build rules for your specific needs
3. **Enhance prompts** - add industry context
4. **Build historical library** - track analyses over time
5. **Measure and improve** - use metrics to guide enhancements
