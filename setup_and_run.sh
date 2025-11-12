#!/bin/bash

echo "========================================"
echo "Beverage Sales Forecasting Dashboard"
echo "Setup and Launch Script"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo

# Install/Update requirements
echo "Installing dependencies..."
pip install -r requirements.txt
echo

# Launch the app
echo "========================================"
echo "Launching Streamlit Dashboard..."
echo "========================================"
echo
echo "The dashboard will open in your browser automatically."
echo "Press Ctrl+C to stop the server."
echo

streamlit run app.py

