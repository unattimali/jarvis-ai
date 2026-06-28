from flask import Flask, request, jsonify
from flask_cors import CORS
from ollama import chat

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

@app.route("/chat", methods=["POST"])
def chat_with_ai():

    data = request.json
    user_message = data["message"]

    response = chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return jsonify({
        "reply": response["message"]["content"]
    })

if __name__ == "__main__":
    app.run(debug=True)