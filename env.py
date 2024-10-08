from pathlib import Path

ROOT_DIR = Path(__file__).parent
RSC_DIR = ROOT_DIR / "resources"
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SOUND_DIR = DATA_DIR / "sound"
QUESTION_FILE = DATA_DIR / "questions.tsv"
WINNINGS_FILE = DATA_DIR / "winnings.json"
