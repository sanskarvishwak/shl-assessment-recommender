import json


with open(
    "catalog.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)



filtered = []


for item in data:


    name = item["name"].lower()


    if "solution" in name:

        continue


    filtered.append(
        item
    )



with open(

    "catalog.json",

    "w",

    encoding="utf-8"

) as file:


    json.dump(

        filtered,

        file,

        indent=4
    )



print(
    "Filtered:",
    len(filtered)
)