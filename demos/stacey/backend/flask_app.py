# flask_app.py
import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

import config
from llm.gpt import GPT
from response_generator import generate_response
from tools.image_tool import replace_image_prompt_with_image_url_formatted_as_markdown

load_dotenv()

app = Flask(__name__)
CORS(app)

llm = GPT(os.getenv("OPENAI_API_KEY"))


@app.route('/')
def root():
    return (
        'Hi! Stacey here. Yes, the backend is up and running! '
        'If you want to talk to me here you can do '
        '<a href="chat?message=hi">/chat?message=hi</a>'
    )


@app.route('/chat', methods=['POST'])
def chat():
    """
    Sample input: {"model": "gpt-3.5-turbo", "conversation": [{"role": "user", "content": "Say hello to me"}]}
    Sample output: {"role": "assistant", "content": "Hello, how are you?"}
    """
    data = request.json
    model = data.get('model', 'gpt-3.5-turbo')
    conversation = data.get('conversation', [])

    try:
        response = generate_response(llm, model, conversation, "web")
        if response is None:
            # Handle no response scenario as per your needs, maybe just return with a 204 status.
            print("GPT decided to not respond to this")
            return '', 204

        response_content = replace_image_prompt_with_image_url_formatted_as_markdown(response['content'])
        return jsonify({"role": response["role"], "content": response_content})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


@app.route('/chat', methods=['GET'])
def chat_get():
    """
    A simpler GET endpoint for quick testing.
    """
    message = request.args.get('message')
    if not message:
        return jsonify({"error": "message parameter is required"}), 400

    conversation = [{"role": "user", "content": message}]
    try:
        response = generate_response(llm, config.default_model, conversation, "web")
        return response.content
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def run():
    app.run(port=5000, debug=False)


if __name__ == '__main__':
    run()
