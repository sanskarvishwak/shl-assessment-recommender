import json
import numpy as np
import faiss

from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

from google import genai
from sentence_transformers import SentenceTransformer


# =====================
# FastAPI App
# =====================

app = FastAPI()


# =====================
# Gemini API
# =====================

API_KEY = "YOUR_GEMINI_API_KEY"

client = genai.Client(
    api_key=API_KEY
)


# =====================
# Embedding Model
# =====================

embed_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# =====================
# Load Catalog + FAISS
# =====================

index = None
catalog = []


try:

    index = faiss.read_index(
        "catalog.index"
    )


    with open(
        "catalog.json",
        "r",
        encoding="utf-8"
    ) as file:

        catalog = json.load(
            file
        )


    print(
        "Loaded catalog and FAISS index"
    )


except Exception as e:


    print(
        f"Startup error: {e}"
    )



# =====================
# Request Models
# =====================

class Message(BaseModel):

    role: str
    content: str



class ChatRequest(BaseModel):

    messages: List[Message]



# =====================
# Retrieval Function
# =====================

def get_catalog_matches(
    query,
    k=5
):


    if (

        index is None

        or

        len(catalog) == 0

    ):

        return []



    vector = embed_model.encode(
        [query]
    )


    vector = np.array(
        vector
    ).astype(
        "float32"
    )



    distances, indices = index.search(
        vector,
        k
    )



    results = []


    for idx in indices[0]:


        if (

            idx >= 0

            and

            idx < len(catalog)

        ):


            item = catalog[idx]


            results.append({

                "name":
                item["name"],


                "url":
                item["url"],


                "test_type":
                item.get(
                    "test_type",
                    "K"
                )

            })


    return results



# =====================
# Root Endpoint
# =====================

@app.get("/")

def home():

    return {

        "message":

        "SHL Assessment API running"
    }



# =====================
# Health Endpoint
# =====================

@app.get("/health")

def health():

    return {

        "status":

        "ok"
    }



# =====================
# Chat Endpoint
# =====================

@app.post("/chat")

async def chat(
    request:
    ChatRequest
):


    history = "\n".join(

        [

            f"{m.role}: {m.content}"

            for m in request.messages

        ]

    )



    prompt = f"""

You are an SHL assessment assistant.

Conversation:

{history}


Return ONLY JSON:

{{
"intent":
"SEARCH" |
"CLARIFY" |
"COMPARE" |
"REFUSE",

"content":
"..."
}}

"""



    try:


        response = client.models.generate_content(

            model="gemini-2.0-flash",

            contents=prompt,

            config={

                "response_mime_type":

                "application/json"

            }

        )



        decision = json.loads(
            response.text
        )



        intent = decision.get(
            "intent",
            "CLARIFY"
        )


        content = decision.get(
            "content",
            ""
        )



        recommendations = []

        end = False



        if intent == "SEARCH":


            recommendations = get_catalog_matches(
                content
            )


            reply = (

                "Here are recommended assessments."
            )


            end = True



        elif intent == "COMPARE":


            recommendations = get_catalog_matches(
                content,
                k=2
            )


            reply = (

                "Comparison results."
            )


            end = False



        elif intent == "REFUSE":


            reply = (

                "I only help with SHL assessments."
            )


            end = False



        else:


            reply = content


            end = False



        return {

            "reply":
            reply,


            "recommendations":
            recommendations,


            "end_of_conversation":
            end
        }



    except Exception as e:


        query = request.messages[
            -1
        ].content



        recommendations = get_catalog_matches(
            query
        )



        if recommendations:


            return {

                "reply":

                "Gemini unavailable. Showing recommendations from catalog.",


                "recommendations":

                recommendations,


                "end_of_conversation":

                True
            }



        return {

            "reply":

            "Could you provide more role or skill details?",


            "recommendations":

            [],


            "end_of_conversation":

            False
        }