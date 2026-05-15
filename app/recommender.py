import json
import re


with open("catalog.json", "r", encoding="utf-8") as file:
    catalog = json.load(file)



def clean(text):

    return re.sub(
        r'[^a-zA-Z0-9 ]',
        '',
        text.lower()
    )



def recommend_assessments(user_query):


    query = clean(user_query)

    recommendations = []


    for product in catalog:


        name = clean(
            product["name"]
        )


        score = 0


        for word in query.split():

            if word in name:

                score += 1



        if score > 0:


            recommendations.append({

                "name":
                product["name"],


                "url":
                product["url"],


                "test_type":
                product.get(
                    "test_type",
                    "K"
                ),


                "_score":
                score
            })



    recommendations.sort(

        key=lambda x:
        x["_score"],

        reverse=True
    )



    for r in recommendations:

        del r["_score"]



    return recommendations[:10]