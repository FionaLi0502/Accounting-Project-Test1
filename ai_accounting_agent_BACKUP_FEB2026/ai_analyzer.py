"""
AI Analyzer Module
Uses Claude API to generate insights and analysis
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class AIAnalyzer:
    """Generate AI-powered financial analysis using Claude"""
    
    def __init__(self):
        """Initialize Claude API client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def generate_analysis(self, context: dict, include_market: bool = True) -> str:
        """
        Generate comprehensive financial analysis
        
        Args:
            context: Dictionary containing financial data and validation results
            include_market: Whether to include market context analysis
        
        Returns:
            Formatted analysis text
        """
        
        # Prepare the prompt
        prompt = self._build_analysis_prompt(context, include_market)
        
        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract response
            analysis = message.content[0].text
            
            return analysis
        
        except Exception as e:
            return f"Error generating AI analysis: {str(e)}\n\nPlease check your API key and try again."
    
    def _build_analysis_prompt(self, context: dict, include_market: bool) -> str:
        """Build the prompt for Claude analysis"""
        
        # Extract data from context
        pl_statement = context.get('pl_statement')
        validation_results = context.get('validation_results', {})
        data_summary = context.get('data_summary', {})
        
        # Convert P&L to text format
        pl_text = "P&L Statement not available"
        if pl_statement is not None and not pl_statement.empty:
            pl_text = pl_statement.to_string()
        
        # Summarize validation issues
        total_issues = sum(len(issues) for issues in validation_results.values())
        validation_summary = f"Total data quality issues found: {total_issues}\n"
        for category, issues in validation_results.items():
            if issues:
                validation_summary += f"\n{category}:\n"
                for issue in issues[:3]:  # Limit to top 3 per category
                    validation_summary += f"  - {issue}\n"
        
        prompt = f"""You are an expert financial analyst reviewing a company's financial data. 
Your task is to generate an executive summary suitable for presentation to senior management.

**Financial Data:**
{pl_text}

**Data Quality Summary:**
{validation_summary}

**Dataset Overview:**
- Total Transactions: {data_summary.get('total_transactions', 'N/A'):,}
- Period: {data_summary.get('date_range', 'N/A')}
- Total Debits: ${data_summary.get('total_debit', 0):,.2f}
- Total Credits: ${data_summary.get('total_credit', 0):,.2f}

**Analysis Requirements:**

1. **Executive Summary** (2-3 sentences)
   - What are the most important takeaways from this data?

2. **Financial Performance Analysis**
   - Key metrics and what they indicate
   - Revenue and profitability trends
   - Cost structure observations
   - Margin analysis

3. **Variance Investigation**
   - What are the most significant variances or anomalies?
   - What could be driving these changes?
   - What questions should management investigate further?

4. **Data Quality Concerns**
   - Impact of the data quality issues identified
   - Recommendations for addressing these issues

5. **Risk Factors**
   - What financial or operational risks are evident?
   - What should management be watching closely?
"""

        if include_market:
            prompt += """
6. **Market Context** (if applicable)
   - How does this performance compare to typical industry benchmarks?
   - What external market factors might be relevant?
   - Are there industry trends that could explain the results?
"""

        prompt += """
7. **Actionable Recommendations**
   - Top 3-5 specific actions management should consider
   - Prioritize by potential impact

**Format your response in clear sections with headers. Write in a professional but accessible tone 
suitable for executives who may not have deep accounting expertise. Be specific with numbers and 
percentages where relevant. Focus on insights and implications, not just describing what the numbers are.**
"""
        
        return prompt
    
    def generate_variance_explanation(self, variance_data: dict) -> str:
        """Generate detailed explanation for specific variances"""
        
        prompt = f"""Analyze this financial variance and provide a detailed explanation:

**Variance Details:**
{json.dumps(variance_data, indent=2)}

Provide:
1. Possible root causes (3-5 specific potential reasons)
2. Related areas to investigate
3. Whether this appears to be a concern or opportunity
4. Recommended next steps for management

Keep your response concise and actionable."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            return f"Error generating variance explanation: {str(e)}"
    
    def generate_executive_summary(self, full_analysis: str) -> str:
        """Distill full analysis into a concise executive summary"""
        
        prompt = f"""Based on the following financial analysis, create a concise executive summary 
suitable for a CEO or board of directors. Limit to 4-5 bullet points covering only the most critical insights.

**Full Analysis:**
{full_analysis}

**Executive Summary (bullet points only, no more than 5):**"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=400,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            return f"Error generating executive summary: {str(e)}"
