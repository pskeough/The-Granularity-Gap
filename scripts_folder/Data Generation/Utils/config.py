"""
Configuration file for the Gemini API research project.

This file contains API credentials and model configurations used throughout the project.
For secure and reproducible runs, configure your API key via environment variables
instead of editing this file directly.
"""

import os  # Standard library only; no external dependencies.

# Gemini API Key
# Preferred: set GEMINI_API_KEY in your environment, e.g.:
#   - Unix/macOS (bash/zsh): export GEMINI_API_KEY="your-key"
#   - Windows (PowerShell):  setx GEMINI_API_KEY "your-key"
#   - Windows (cmd.exe):     set GEMINI_API_KEY=your-key  (for current session)
#
# WARNING: The hard-coded key below is for local/dev use ONLY.
# - Do NOT commit a real key to any public repo or artifact (paper, thesis, etc.).
# - Before publishing/sharing this project, REMOVE or REDACT any real key value here.
# Backward compatible behavior: if GEMINI_API_KEY is not set, we fall back to the
# existing embedded value.
API_KEY = os.getenv(
    "AIzaSyDj2RKmLvBa4omYMtEMIQNN0BlTHkoT4bg",
    ""
).strip('"\'')

# Model Configuration
# Defines target models for deployment and the judge model for evaluation.
# Semantics and structure must remain unchanged for compatibility.
MODELS = {
    'target': [
        'gemini-2.0-flash-lite',
        'gemini-2.0-flash-exp',
        'gemini-2.5-flash-lite',
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-3-pro-preview',
        'gemini-3-pro-low-thinking'
    ],
    'judge': 'gemini-3-pro-preview'
}

# Additional configuration parameters can be added below as needed.
