# import json
# from pathlib import Path
# import requests

# # PROJECT_ROOT = Path(__file__).resolve().parents[1]
# # DATA_DIR = PROJECT_ROOT / "data" / "raw"

# # comments = []
# # with open(DATA_DIR / "random_comments.json", "w", encoding='utf-8') as f:
# #     json.dump(comments, f, indent=2, ensure_ascii=False)

# url='http://127.0.0.1:8080/synergy_inmoment.json'
# url="https://github.com/himmng/agentic_ai/blob/main/data/raw/synergy_inmoment.json"
# data = requests.get(url).json()
# print(data)

import requests
import json

import requests

url = "https://raw.githubusercontent.com/himmng/agentic_ai/main/data/raw/synergy_inmoment.json"
response = requests.get(url)
data = response.json()  # works if JSON array
print(data)
