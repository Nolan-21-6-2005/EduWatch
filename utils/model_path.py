from pathlib import Path

def getmodel_path():
    BASE_DIR = Path(__file__).resolve().parent.parent 
    MODEL_PATH = BASE_DIR / "AI_model" / "yolo_eduwatch.pt"
    return MODEL_PATH
    
