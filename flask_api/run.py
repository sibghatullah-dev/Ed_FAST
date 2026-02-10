"""
Flask API Startup Script
Run this to start the EdFast API server
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from parent directory .env file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(parent_dir, '.env')
load_dotenv(env_file)

# Add parent directory to path for imports
sys.path.insert(0, parent_dir)

from app import app

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" " * 20 + "EdFast API Server")
    print("=" * 60)
    print(f"\n🚀 Starting server on http://localhost:5000")
    print(f"📚 API Documentation: http://localhost:5000/api/v1")
    print(f"💚 Health Check: http://localhost:5000/api/v1/health")
    print("\n" + "=" * 60 + "\n")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    )




