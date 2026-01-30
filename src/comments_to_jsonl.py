import json

comments = []

with open("../data/augmented/random_comments.json", "w", encoding='utf-8') as f:
    json.dump(comments, f, indent=2, ensure_ascii=False)