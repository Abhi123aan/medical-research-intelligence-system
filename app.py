"""
Streamlit wrapper for Hugging Face Spaces deployment
Routes to the main app in apps/web/app.py
"""
import subprocess
import sys
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))
from apps.web.app import *

# Ensure the app directory is in the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the main Streamlit app
from apps.web import app as main_app

# The main app module will automatically run when imported
