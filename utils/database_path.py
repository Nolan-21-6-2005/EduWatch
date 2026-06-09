from pathlib import Path

def getdatabase_path():
    BASE_DIR = Path(__file__).resolve().parent.parent 
    DB_PATH = BASE_DIR / "data_model" / "eduwatch.db"
    return DB_PATH
    
