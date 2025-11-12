# 🚀 Quick Start Guide

## Get Started in 3 Simple Steps!

### Step 1: Setup Environment ⚙️

**Windows Users:**
```bash
# Double-click the file:
setup_and_run.bat
```

OR manually:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

**Mac/Linux Users:**
```bash
# Make script executable and run:
chmod +x setup_and_run.sh
./setup_and_run.sh
```

OR manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Step 2: Configure the Dashboard 📊

1. The dashboard opens automatically at `http://localhost:8501`
2. In the **sidebar**, select:
   - ✅ Data Source (use sample or upload your own)
   - ✅ Models to train (select all for comparison)
   - ✅ Test size (3 months recommended)
   - ✅ Forecast horizon (3 months default)

3. **(Optional)** Enable AI Insights:
   - Check "Enable AI-Powered Insights"
   - Enter your OpenAI API key
   - Get intelligent interpretations!

### Step 3: Run Analysis 🔮

1. Click **"🚀 Run Analysis"** button in sidebar
2. Navigate through 5 tabs:
   - 📈 **Data Overview**: Explore your sales data
   - 🔮 **Forecasting Models**: Compare model predictions
   - 📊 **Performance Metrics**: See which model wins
   - 🎯 **Future Forecast**: Predict next 3 months
   - 🧠 **AI Insights**: Get intelligent recommendations

## 🎯 What You'll Get

### ✅ Multiple Forecasting Models
- Naïve Baseline
- ARIMA (Time Series)
- Random Forest (ML)
- XGBoost (Advanced ML)

### ✅ Comprehensive Metrics
- MAPE: Average percentage error
- WAPE: Weighted percentage error
- MAE: Mean absolute error
- RMSE: Root mean squared error

### ✅ Beautiful Visualizations
- Historical sales trends
- Actual vs predicted comparison
- Model performance charts
- Future forecast with confidence intervals
- Residual analysis
- Feature importance plots

### ✅ AI-Powered Insights (Optional)
- Model performance analysis
- Seasonality detection
- Business recommendations
- Risk assessment

## 💡 Pro Tips

1. **Start Simple**: Use the sample data first to understand the workflow
2. **Compare Models**: Train all 4 models to see which works best for your data
3. **Check Metrics**: Lower MAPE = Better model
4. **Use AI Insights**: Get expert-level interpretation automatically
5. **Export Results**: Download metrics and forecasts as CSV files

## 📝 Custom Data Format

If uploading your own data, use this format:

```csv
Month,Sales,Temperature,Marketing_Spend,Holiday_Season
2024-01,15234,42,5000,0
2024-02,16789,45,5200,0
```

**Required**: Month (YYYY-MM), Sales (numeric)
**Optional**: Any additional features

## ❓ Need Help?

### Common Issues:

**Q: Dashboard won't start**
A: Make sure you're in the virtual environment and all packages are installed

**Q: Models showing poor accuracy**
A: Ensure you have at least 12 months of data and no missing values

**Q: AI insights not working**
A: Verify your OpenAI API key is valid and has available credits

**Q: Can't upload data**
A: Check CSV format matches the required structure

## 🎓 Learning Path

Follow this sequence for best results:

1. **Start** → Run with sample data
2. **Explore** → Understand each tab
3. **Compare** → See which model performs best
4. **Interpret** → Read AI insights
5. **Apply** → Use your own data
6. **Optimize** → Add more features to improve accuracy

## 📚 Key Concepts

### MAPE (Mean Absolute Percentage Error)
- Measures average % difference between actual and predicted
- Lower is better
- 10% MAPE = Very good
- 20% MAPE = Acceptable
- 30%+ MAPE = Needs improvement

### Seasonality
- Regular patterns that repeat over time
- Example: Higher sales in summer months
- Important for beverage products!

### Lag Features
- Uses past values to predict future
- Lag 1 = Last month's sales
- Lag 3 = Sales from 3 months ago

### Model Selection
- **Naïve**: Good baseline, simple
- **ARIMA**: Best for pure time series with trends
- **Random Forest**: Great when you have extra features
- **XGBoost**: Usually best overall, handles complexity

## 🎯 Business Use Cases

This dashboard helps you:
- 📦 Plan production volumes
- 🏪 Optimize inventory levels
- 🚚 Schedule distribution
- 💰 Budget for resources
- 📈 Track demand trends
- ⚠️ Identify risks early

## 🔐 API Key Setup (Optional)

To enable AI insights:

1. Get OpenAI API key from: https://platform.openai.com/api-keys
2. Either:
   - Enter it in the sidebar when running the app, OR
   - Create `.env` file with: `OPENAI_API_KEY=your_key_here`

## ⏱️ Expected Runtime

- Data loading: < 1 second
- Model training: 5-10 seconds
- AI insights generation: 10-15 seconds
- Total time: ~30 seconds per analysis

## 📊 Sample Output

After running analysis, you'll see:
- ✅ Best performing model identified
- ✅ Detailed metrics comparison
- ✅ 3-month forecast with confidence intervals
- ✅ Production planning recommendations
- ✅ AI-generated business insights

---

**Ready to start? Run the setup script and begin forecasting! 🚀**

Need more details? Check `README.md` for complete documentation.

