import json

with open("catalog.json", "r", encoding="utf-8") as file:
    catalog = json.load(file)


def recommend_assessments(user_query):

    print("USER QUERY:", user_query)

    query_words = user_query.lower().split()

    recommendations = []

    for product in catalog:

        name = product["name"].lower()

        print("Checking:", name)   # DEBUG

        score = 0

        for word in query_words:

            if word in name:
                score += 1


        if score > 0:

            recommendations.append({
                "name": product["name"],
                "url": product["url"],
                "score": score
            })


    print("Recommendations:", recommendations)

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return recommendations[:10]