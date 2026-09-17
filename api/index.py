import sys
import os

# Ensure root directory is on PYTHONPATH for Vercel serverless environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
