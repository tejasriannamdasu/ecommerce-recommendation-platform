#!/usr/bin/env python3
"""Convenience CLI wrapper: `python scripts/train_models.py`"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.ml.train_pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline()
