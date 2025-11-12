"""
LLM Interpreter Module
Uses LLM to generate insights and interpretations from forecasting results
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


class LLMInterpreter:
    """Generates intelligent interpretations using LLM"""
    
    def __init__(self, api_key=None):
        """Initialize with Google Gemini API key"""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
    
    def generate_model_interpretation(self, metrics_df, best_model, actual_data, predictions_dict):
        """
        Generate comprehensive interpretation of model performance
        """
        if not self.model:
            return self._fallback_interpretation(metrics_df, best_model)
        
        # Prepare context for LLM
        context = self._prepare_context(metrics_df, best_model, actual_data, predictions_dict)
        
        prompt = f"""You are a data science consultant analyzing forecasting model results for a beverage company that launched a new flavored water product. They have 12 months of sales data and want to forecast the next 3 months.

**Data Context:**
{context}

Please provide a comprehensive analysis covering:

1. **Model Performance Analysis:**
   - How well did each model capture the sales patterns?
   - Why did the best model perform better than others?
   - What are the strengths and weaknesses of each approach?

2. **Seasonality & Trends:**
   - What seasonal patterns do you observe in the sales data?
   - Are there any notable trends (growth, decline, cyclical)?
   - How well did the models capture these patterns?

3. **Business Recommendations:**
   - Based on the forecast, what production levels should the company plan for?
   - What inventory and distribution strategies would you recommend?
   - Are there any risk factors or uncertainties to consider?

4. **Model Selection Guidance:**
   - Which model would you recommend for ongoing forecasting?
   - When should the company consider switching models?
   - What additional data might improve forecasts?

Provide actionable, business-focused insights that a non-technical stakeholder can understand."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_interpretation(metrics_df, best_model)
    
    def _prepare_context(self, metrics_df, best_model, actual_data, predictions_dict):
        """Prepare formatted context for LLM"""
        context = "**Model Performance Metrics:**\n"
        context += metrics_df.to_string(index=False)
        context += f"\n\n**Best Model:** {best_model}\n"
        
        context += f"\n**Actual Sales Data (Last 3 Months):**\n"
        context += f"Sales Values: {actual_data.tolist()}\n"
        context += f"Average: ${actual_data.mean():.2f}\n"
        context += f"Trend: {'Increasing' if actual_data[-1] > actual_data[0] else 'Decreasing'}\n"
        
        context += f"\n**Predictions Comparison:**\n"
        for model_name, preds in predictions_dict.items():
            mape = metrics_df[metrics_df['Model'] == model_name]['MAPE'].values
            mape_str = f"{mape[0]:.2f}%" if len(mape) > 0 else "N/A"
            context += f"- {model_name}: {preds.tolist()} (MAPE: {mape_str})\n"
        
        return context
    
    def _fallback_interpretation(self, metrics_df, best_model):
        """Provide basic interpretation when LLM is not available"""
        
        best_metrics = metrics_df[metrics_df['Model'] == best_model].iloc[0]
        
        interpretation = f"""
## 📊 Forecasting Analysis Report

### 🏆 Best Model: {best_model}

**Performance Metrics:**
- MAPE: {best_metrics['MAPE']:.2f}%
- WAPE: {best_metrics['WAPE']:.2f}%
- MAE: {best_metrics['MAE']:.2f}
- RMSE: {best_metrics['RMSE']:.2f}

### 📈 Model Performance Analysis

The {best_model} model achieved the best performance with a MAPE of {best_metrics['MAPE']:.2f}%. This indicates that, on average, the predictions deviate by {best_metrics['MAPE']:.2f}% from actual values.

**Model Comparison:**
"""
        for _, row in metrics_df.iterrows():
            interpretation += f"\n- **{row['Model']}**: MAPE {row['MAPE']:.2f}%, WAPE {row['WAPE']:.2f}%"
        
        interpretation += """

### 🔍 Key Insights

1. **Seasonality**: The beverage product shows seasonal patterns, with higher sales during summer months (likely due to increased demand for refreshing drinks).

2. **Trend Analysis**: The sales data demonstrates a general growth trend, indicating successful market penetration for the new product.

3. **Model Selection**: 
   - **Naïve models** provide a simple baseline but may miss complex patterns.
   - **ARIMA/SARIMA** capture temporal dependencies and seasonal patterns.
   - **Machine Learning models** (Random Forest, XGBoost) can leverage additional features like temperature and marketing spend.

### 💼 Business Recommendations

1. **Production Planning**: Increase production capacity for predicted high-demand months based on the forecast.

2. **Inventory Management**: Maintain buffer stock of 15-20% above forecast to handle demand uncertainty.

3. **Marketing Strategy**: Align marketing campaigns with seasonal trends to maximize impact.

4. **Distribution**: Optimize distribution channels based on regional demand patterns.

5. **Continuous Monitoring**: Update forecasts monthly with new data to improve accuracy.

### ⚠️ Considerations

- Weather patterns and economic conditions can impact actual sales
- Competitor actions may affect market share
- Consider multiple scenarios (optimistic, realistic, pessimistic) for robust planning

---
*Note: For enhanced AI-powered insights, configure your OpenAI API key in the .env file.*
"""
        
        return interpretation
    
    def generate_quick_insight(self, forecast_values, model_name):
        """Generate a quick insight about the forecast"""
        
        if not self.model:
            avg_forecast = forecast_values.mean()
            return f"The {model_name} model predicts an average sales of ${avg_forecast:,.0f} for the next 3 months."
        
        prompt = f"""The {model_name} forecasting model predicts the following sales for the next 3 months:
Month 1: ${forecast_values[0]:,.0f}
Month 2: ${forecast_values[1]:,.0f}
Month 3: ${forecast_values[2]:,.0f}

Provide a brief 2-3 sentence business insight about this forecast."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            avg_forecast = forecast_values.mean()
            return f"The {model_name} model predicts an average sales of ${avg_forecast:,.0f} for the next 3 months."

