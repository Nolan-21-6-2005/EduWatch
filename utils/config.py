from pathlib import Path

# Thư mục gốc của project Stable
BASE_DIR = Path(__file__).resolve().parents[1]

# Thư mục chứa dữ liệu của project
DATA_DIR = BASE_DIR / "data_model"

# Thư mục avatar
AVATAR_DIR = DATA_DIR / "avatar"

# Database
DATABASE_PATH = DATA_DIR / "eduwatch.db"


# Đảm bảo thư mục avatar tồn tại
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
