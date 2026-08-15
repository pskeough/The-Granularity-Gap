"""
Configuration for the Gemini generation and judging runs.

The API key is read from the environment. No key is stored in this file.

    Unix/macOS:  export GEMINI_API_KEY="your-key"
    PowerShell:  $env:GEMINI_API_KEY = "your-key"

A previous revision of this file carried a literal key. That key has been revoked.
"""

import os

API_KEY = os.getenv("GEMINI_API_KEY", "").strip("\"'")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Export it before running the generation scripts."
    )

# Model configuration. Semantics and structure are unchanged from the run that
# produced results/master_results.csv.
MODELS = {
    "target": [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash-exp",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-3-pro-preview",
        "gemini-3-pro-low-thinking",
    ],
    "judge": "gemini-3-pro-preview",
}
