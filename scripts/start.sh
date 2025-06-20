#!/bin/bash
# Market Prediction System v2.3.0 Startup Script

echo "Starting Market Prediction System v2.3.0..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please copy .env.example to .env and add your API keys."
    echo "You can still run the system, but it will need API keys from environment variables."
fi

# Start the application
echo "Starting Market Prediction System..."
python market_predictor.py
