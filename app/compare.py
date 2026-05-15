import os
import json
from google import genai  # Modern SDK

# ==========================
# 1. Configuration
# ==========================

# Initialize the Client
# Using the same key you provided for main.py
client = genai.Client(api_key="AIzaSyC_Yc3fv_AgiIwvE5ICdtXAovD3kWdIaK4")

def compare_assessments(query: str, catalog_data: list):
    """
    Identifies specific assessments from catalog_data mentioned in the query
    and uses Gemini to generate a grounded, evidence-based comparison.
    """
    
    # 1. Identify which assessments from our catalog are mentioned in the query
    matches = []
    query_words = query.lower().split()
    
    for product in catalog_data:
        name_lower = product["name"].lower()
        # Look for significant keyword matches (length > 3 to avoid 'the', 'and', etc.)
        if any(word in name_lower for word in query_words if len(word) > 3):
            matches.append(product)

    # 2. Case: Not enough matches to perform a comparison
    if len(matches) < 2:
        return "I found some information, but I couldn't identify two distinct assessments to compare. Could you specify the full names of the tests you'd like to see side-by-side?"

    # 3. Grounded Comparison Prompt
    # We pass the actual data from your catalog.json to the LLM
    comparison_prompt = f"""
    You are an SHL Assessment Expert. 
    Compare the following two assessments using ONLY the provided catalog details.
    
    Assessment 1: {matches[0]['name']} (URL: {matches[0]['url']})
    Assessment 2: {matches[1]['name']} (URL: {matches[1]['url']})
    
    User Question: {query}
    
    Instructions:
    - Focus on the differences in their purpose based on their names.
    - Provide the URLs for both so the user can verify.
    - Keep the tone professional and helpful for a recruiter.
    - If one is a 'Simulation' and the other is 'Short Form', explain what that typically implies.
    """

    try:
        # Use the modern generate_content method
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=comparison_prompt
        )
        return response.text
    except Exception as e:
        # Graceful fallback if the API call fails
        return (
            f"I found {matches[0]['name']} and {matches[1]['name']}. "
            f"You can find detailed differences at these links:\n"
            f"1. {matches[0]['url']}\n"
            f"2. {matches[1]['url']}"
        )

# ==========================
# 4. (Optional) Local Testing
# ==========================
if __name__ == "__main__":
    # Small test block to check if it works locally
    sample_data = [
        {"name": ".NET MVC (New)", "url": "https://shl.com/mvc"},
        {"name": ".NET MVVM (New)", "url": "https://shl.com/mvvm"}
    ]
    print(compare_assessments("Difference between MVC and MVVM", sample_data))