"""Script for update token file"""
import sys
from pathlib import Path

with open(Path(__file__).resolve().parent / "source/conf/token", 'w', encoding="utf-8") as file:
    file.write(sys.argv[1])
