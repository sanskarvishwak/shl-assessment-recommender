import json


with open("catalog.json", "r", encoding="utf-8") as file:

    catalog = json.load(file)



def compare_assessments(query):


    matches = []


    for product in catalog:

        name = product["name"].lower()


        if any(
            word in name

            for word in query.lower().split()

        ):

            matches.append(product)



    if len(matches) >= 2:


        return (

            f"{matches[0]['name']} "

            f"vs "

            f"{matches[1]['name']}\n\n"

            f"URL1:\n"

            f"{matches[0]['url']}\n\n"

            f"URL2:\n"

            f"{matches[1]['url']}\n\n"

            f"Both are SHL assessments. "

            f"Please review catalog pages for detailed differences."

        )



    return "Could not identify two assessments to compare."