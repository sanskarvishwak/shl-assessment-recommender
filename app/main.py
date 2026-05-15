import json
import numpy as np
import faiss

from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

from google import genai
from sentence_transformers import SentenceTransformer


app = FastAPI()


# ======================
# Gemini
# ======================

API_KEY = "YOUR_GEMINI_API_KEY"

client = genai.Client(
    api_key=API_KEY
)


# ======================
# Embeddings
# ======================

embed_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ======================
# Load Catalog + Index
# ======================

catalog = []
index = None


try:

    with open(
        "catalog.json",
        "r",
        encoding="utf-8"
    ) as file:

        catalog = json.load(file)


    index = faiss.read_index(
        "catalog.index"
    )


    print(
        "Catalog loaded"
    )


except Exception as e:

    print(
        f"Startup error: {e}"
    )



# ======================
# Request Models
# ======================

class Message(BaseModel):

    role: str
    content: str



class ChatRequest(BaseModel):

    messages: List[Message]



# ======================
# Retrieval
# ======================

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



# ======================
# Routes
# ======================

@app.get("/")

def home():

    return {

        "message":

        "SHL API running"
    }



@app.get("/health")

def health():

    return {

        "status":

        "ok"
    }



# ======================
# Chat
# ======================

@app.post("/chat")

async def chat(
    request:
    ChatRequest
):


    query = request.messages[
        -1
    ].content


    query_lower = query.lower()



    vague_words = [

        "hire",

        "someone",

        "assessment",

        "employee",

        "test"

    ]



    if (

        len(query_lower.split()) < 4

        or

        any(

            x in query_lower

            for x in vague_words

        )

    ):


        return {

            "reply":

            "Could you specify role, skills, experience level, or job requirements?",


            "recommendations":

            [],


            "end_of_conversation":

            False
        }



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
            "SEARCH"
        )


        content = decision.get(
            "content",
            query
        )



        if intent == "REFUSE":


            return {

                "reply":

                "I only help with SHL assessments.",


                "recommendations":

                [],


                "end_of_conversation":

                False
            }



        recommendations = get_catalog_matches(
            content
        )



        if intent == "COMPARE":


            return {

                "reply":

                "Comparison results.",


                "recommendations":

                recommendations[:2],


                "end_of_conversation":

                False
            }



        return {

            "reply":

            "Here are recommended assessments.",


            "recommendations":

            recommendations,


            "end_of_conversation":

            True
        }



    except:


        recommendations = get_catalog_matches(
            query
        )



        if recommendations:


            return {

                "reply":

                "Gemini unavailable. Showing catalog recommendations.",


                "recommendations":

                recommendations,


                "end_of_conversation":

                True
            }



        return {

            "reply":

            "Could you provide more details?",


            "recommendations":

            [],


            "end_of_conversation":

            False
        }