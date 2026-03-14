#!/bin/bash

# CampusAid Quick Setup Script
# This script sets up both backend and frontend

echo "=================================="
echo "  CampusAid Setup Script"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Python version: $(python --version)"
echo "✅ Node.js version: $(node --version)"
echo ""

# Backend Setup
echo "=================================="
echo "  Setting up Backend"
echo "=================================="
echo ""

cd backend

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Train ML model
echo "🤖 Training ML model..."
python train_classifier.py

echo "✅ Backend setup complete!"
echo ""

cd ..

# Frontend Setup
echo "=================================="
echo "  Setting up Frontend"
echo "=================================="
echo ""

cd frontend/campusaid

# Install dependencies
echo "📥 Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"
echo ""

cd ../..

# Final instructions
echo "=================================="
echo "  Setup Complete!"
echo "=================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Start Backend (Terminal 1):"
echo "   cd backend"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   .venv\\Scripts\\activate"
else
    echo "   source .venv/bin/activate"
fi
echo "   python app/main.py"
echo ""
echo "2. Start Frontend (Terminal 2):"
echo "   cd frontend/campusaid"
echo "   npm run dev"
echo ""
echo "3. Open browser:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Demo Users:"
echo "  student1 / student123"
echo "  worker1 / worker123"
echo "  admin1 / admin123"
echo "  warden1 / warden123"
echo ""
echo "=================================="
