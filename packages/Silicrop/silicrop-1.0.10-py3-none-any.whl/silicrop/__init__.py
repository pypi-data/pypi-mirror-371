"""
Silicrop - Package for Raman TMD data processing and visualization
"""

import os
import urllib.request
from pathlib import Path

def download_model_if_needed(model_name, url):
    """Download model if not present locally."""
    assets_dir = Path(__file__).parent / "assets"
    model_path = assets_dir / model_name
    
    if not model_path.exists():
        print(f"📥 Downloading {model_name}...")
        assets_dir.mkdir(exist_ok=True)
        urllib.request.urlretrieve(url, model_path)
        print(f"✅ {model_name} downloaded successfully")
    
    return model_path

def ensure_models_available():
    """Ensure all required models are available."""
    models = {
        "DeepLabV3_150_flatspot_0.001_350_4_weights.pth": "https://github.com/thi-mey/silicrop-models/releases/download/v1.0/DeepLabV3_150_flatspot_0.001_350_4_weights.pth",
        "DeepLabV3_200300_notch_0.001_250_4_weights.pth": "https://github.com/thi-mey/silicrop-models/releases/download/v1.0/DeepLabV3_200300_notch_0.001_250_4_weights.pth"
    }
    
    for model_name, url in models.items():
        download_model_if_needed(model_name, url)

# Version
__version__ = "1.0.10"
