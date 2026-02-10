#!/bin/bash
# EdFast Flask API - Installation and Startup Script (Linux/Mac)

echo "============================================================"
echo "            EdFast Flask API - Setup"
echo "============================================================"
echo ""

echo "[Step 1/3] Installing Flask API dependencies..."
cd flask_api
pip install Flask Flask-CORS Flask-JWT-Extended python-dotenv
cd ..

echo ""
echo "[Step 2/3] Installing main EdFast dependencies..."
pip install -r requirements.txt

echo ""
echo "[Step 3/3] Starting Flask API server..."
echo ""
echo "API will be available at: http://localhost:5000"
echo "Documentation: http://localhost:5000/api/v1"
echo ""

cd flask_api
python run.py




