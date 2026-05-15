from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.recommender import recommend_assessments
from app.compare import compare_assessments


app = FastAPI()


# ==========================
# Request Models
# ==========================

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


# ==========================
# Health Endpoint
# ==========================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ==========================
# Chat Endpoint
# ==========================

@app.post("/chat")
def chat(request: ChatRequest):


    # Combine all user messages
    conversation_text = " ".join(

        msg.content

        for msg in request.messages

        if msg.role == "user"

    )


    lower_text = conversation_text.lower()


    # ==========================
    # Guardrails / Refusal Logic
    # ==========================

    blocked = [

        "salary",

        "legal",

        "law",

        "prompt injection",

        "ignore previous instructions",

        "hack",

        "best programming language",

        "give interview tips"

    ]


    if any(

        word in lower_text

        for word in blocked

    ):


        return {

            "reply":

            "I can only help with SHL assessment recommendations and comparisons.",


            "recommendations":

            [],


            "end_of_conversation":

            False
        }



    # ==========================
    # Comparison Logic
    # ==========================

    if (

        "difference" in lower_text

        or

        "compare" in lower_text

    ):


        comparison = compare_assessments(
            conversation_text
        )


        return {

            "reply":
            comparison,


            "recommendations":

            [],


            "end_of_conversation":

            False
        }



    # ==========================
    # Clarification Logic
    # ==========================

    if len(

        conversation_text.split()

    ) < 3:


        return {

            "reply":

            "Could you tell me the role, skills, or experience level you are hiring for?",


            "recommendations":

            [],


            "end_of_conversation":

            False
        }



    # ==========================
    # Recommendation Logic
    # ==========================

    recommendations = recommend_assessments(

        conversation_text

    )



    if recommendations:


        return {

            "reply":

            "Here are recommended assessments.",


            "recommendations":

            recommendations,


            "end_of_conversation":

            False
        }



    # ==========================
    # No Matches Found
    # ==========================

    return {

        "reply":

        "Could not find matching assessments.",


        "recommendations":

        [],


        "end_of_conversation":

        False
    }