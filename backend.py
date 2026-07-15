from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)
from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def is_dish_query(text):
    """
    Simple logic:
    If input has commas → ingredients
    If short phrase (1-3 words) → likely dish name
    """
    if "," in text:
        return False
    if len(text.split()) <= 3:
        return True
    return False


@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    data = request.json
    user_input = data.get("ingredients")

    if not user_input:
        return jsonify({"error": "No input provided"})

    # 🔥 Decide mode
    if is_dish_query(user_input):
        prompt = f"""
        The user wants a recipe for the dish: {user_input}.

        Give:
        - Authentic Indian recipe
        - Ingredients list
        - Step-by-step cooking instructions
        - Cooking tips if possible
        """
    else:
        prompt = f"""
        I have these ingredients: {user_input}.

        Suggest 2 Indian recipes that can be made using these.
        Include:
        - Recipe name
        - Ingredients (mention missing ones separately)
        - Steps
        """

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        result = response.json()

        print(result)

        if "choices" in result:
            recipe = result['choices'][0]['message']['content']
            return jsonify({"recipe": recipe})
        else:
            return jsonify({"error": result})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)