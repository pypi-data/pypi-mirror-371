import json
from pathlib import Path

if not  (Path(__file__).parent / "login.json").exists():
    with open(Path(__file__).parent / "login.json", "x+") as f:
        json.dump({"username": "", "password": ""}, f, indent=4)