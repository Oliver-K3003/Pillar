import json
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from mistralTest import sendReq, parseOutput
import requests
from db import add_new_user

app = Flask(__name__)
CORS(app, supports_credentials=True)

CLIENT_ID = "asdf"
CLIENT_SECRET = "asdf" # probably not good idea to leave this here lol

@app.route('/get-resp', methods=['POST'])
@cross_origin(supports_credentials=True)
def getResp():
    data = request.json
    prompt = data.get('prompt', 'No Prompt Given')
    # will be filled in with function to gather resp
    promptResponse = json.loads(sendReq(prompt))
    promptResponse = parseOutput(promptResponse)
    return promptResponse

@app.route('/exchange-code-for-token', methods=['GET'])
@cross_origin(supports_credentials=True)
def OAuthRedirect():
    code = request.args.get('code')
    
    # Getting token from code.
    githubAuthURL = f'https://github.com/login/oauth/access_token'
    
    headers = {
        'accept': 'application/json'
    }

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
    }
    
    res = requests.post(githubAuthURL, headers=headers, data=data)
    data = res.json()
    return jsonify(data)

@app.route('/add-user', methods=["POST"])
@cross_origin(supports_credentials=True)
def add_user():
    data = request.json
    username = data.get("username")
    accesstoken = data.get("accesstoken") or None  # Avoid null issues

    if not username:
        return jsonify({"error": "Username is required"}), 400

    add_new_user(username, accesstoken)


if __name__ == "__main__":
    app.run(port=5000)