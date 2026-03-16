import os 
import torch.nn as nn
from pathlib import Path
# 1. Define the directory
base_path = Path(__file__).resolve().parent.parent / "data" / "training_data"
base_path.mkdir(parents=True, exist_ok=True)
(base_path / "data.csv").touch(exist_ok=True)


print(f"Success! File created at: {base_path.absolute()}")