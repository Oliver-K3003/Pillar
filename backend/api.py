import json
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from mistralTest import sendReq, parseOutput
import requests

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
    
    if res.status_code == 200:
        try:
            json_response = res.json()
            return jsonify(json_response)
        except requests.exceptions.JSONDecodeError:
            return jsonify({"error": "error", "response": res.text}), 500
    else:
        return jsonify({"error": f"{res.status_code}", "response": res.text}), res.status_code

    data = res.json()
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5000)