import json

with open("catalog.json", "r", encoding="utf-8") as file:
    data = json.load(file)


for item in data:
    item["test_type"] = "K"


with open("catalog.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)


print("catalog updated")