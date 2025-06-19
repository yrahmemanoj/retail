#!/bin/bash

# Retail Sales EDA - Development Server Launcher
# This script provides multiple options for running the development server

echo "🚀 Retail Sales EDA - Development Server"
echo "========================================"

# How to Run the Development Server

# - **On Windows:**  
#   Double-click or run `run_server.bat` in Command Prompt.
# 
# - **On Mac/Linux:**  
#   Open Terminal and run:
#   ```sh
#   chmod +x run_server.sh
#   ./run_server.sh
#   ```

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
NODE_AVAILABLE=false
if command -v node &> /dev/null && command -v npx &> /dev/null; then
    NODE_AVAILABLE=true
fi

echo ""
echo "Available server options:"
echo "1. Python HTTP Server (recommended)"
if [ "$NODE_AVAILABLE" = true ]; then
    echo "2. Node.js serve (if you have Node.js)"
fi
echo "3. Run EDA Analysis First"
echo "4. Exit"
echo ""

read -p "Choose an option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🐍 Starting Python HTTP Server..."
        echo "Dashboard will be available at: http://localhost:8000/dashboard/"
        echo "Press Ctrl+C to stop the server"
        echo ""
        $PYTHON_CMD -m http.server 8000
        ;;
    2)
        if [ "$NODE_AVAILABLE" = true ]; then
            echo ""
            echo "📦 Starting Node.js serve..."
            echo "Dashboard will be available at the URL shown below"
            echo "Press Ctrl+C to stop the server"
            echo ""
            npx serve . -p 8000
        else
            echo "❌ Node.js is not available. Please choose option 1."
            exit 1
        fi
        ;;
    3)
        echo ""
        echo "🔍 Running EDA Analysis..."
        echo "This may take a few minutes depending on your data size..."
        echo ""
        
        # Check if the EDA module exists
        if [ -f "eda/run.py" ]; then
            $PYTHON_CMD eda/run.py
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "✅ EDA Analysis completed successfully!"
                echo ""
                echo "Now you can start the server:"
                echo "1. Run this script again and choose option 1 or 2"
                echo "2. Or manually run: $PYTHON_CMD -m http.server 8000"
                echo "3. Then open: http://localhost:8000/dashboard/"
            else
                echo ""
                echo "❌ EDA Analysis failed. Please check the error messages above."
            fi
        else
            echo "❌ EDA module not found. Please ensure you're in the correct directory."
            exit 1
        fi
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *
        echo "❌ Invalid option. Please choose 1-4."
        exit 1
        ;;
esac