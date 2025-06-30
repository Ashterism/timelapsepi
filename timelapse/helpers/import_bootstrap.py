

# Helper script to ensure all scripts can resolve imports from project root
import sys
from pathlib import Path

# Always add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))