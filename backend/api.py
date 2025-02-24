import json
import sys
from flask import Flask, jsonify, request, redirect, session
from flask_cors import CORS, cross_origin
from mistralTest import sendReq, parseOutput
import requests

GH_CLIENT_ID = "Ov23lipp1FKM5Lltmvw0"
GH_CLIENT_SECRET = "generate one" # probably not good idea to leave this here lol
FLASK_SECRET = "generate one" # or this

app = Flask(__name__)
app.secret_key = FLASK_SECRET
CORS(app, supports_credentials=True)

@app.route('/get-resp', methods=['POST'])
@cross_origin(supports_credentials=True)
def getResp():
    data = request.json
    prompt = data.get('prompt', 'No Prompt Given')
    # will be filled in with function to gather resp
    promptResponse = json.loads(sendReq(prompt))
    promptResponse = parseOutput(promptResponse)
    return promptResponse


# Authentication Endpoints
# Called by login button, redirect to GitHub login page.
@app.route('/login/github', methods=['GET'])
@cross_origin(supports_credentials=True)
def githubLoginRequest():
    print("> githubLoginRequest()", file=sys.stderr)
    
    redirect_uri = request.host_url + "login/github/callback"
    scope = "read:user repo" # need to access user repos
    
    github_auth_code_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GH_CLIENT_ID}&redirect_uri={redirect_uri}&scope={scope}"
    )
    
    try:
        print("Redirecting to GitHub.", file=sys.stderr)
        print("< githubLoginRequest()", file=sys.stderr)
        return jsonify({
            "status": "Successful",
            "github_auth_code_url": github_auth_code_url,
            })
    except:
        print("Could not formulate request properly.", file=sys.stderr)
        print("< githubLoginRequest()", file=sys.stderr)
        return jsonify({"status": "Error"})

@app.route('/login/github/callback', methods=['GET'])
@cross_origin(supports_credentials=True)
def githubLoginCallback():
    print("> githubLoginCallback()", file=sys.stderr)
    code = request.args.get("code")  # Extract code from query params
    print("Code from Github: " + code, file=sys.stderr)
    if code:
        # Exchange token from code.
        githubAuthURL = f'https://github.com/login/oauth/access_token'
        
        headers = {
            'accept': 'application/json'
        }

        data = {
            "client_id": GH_CLIENT_ID,
            "client_secret": GH_CLIENT_SECRET,
            "code": code
        }
        
        res = requests.post(githubAuthURL, headers=headers, data=data)
    
        if res.status_code == 200:
            try:
                json_response = res.json()
                print(json_response, file=sys.stderr)
                token_str = ' '.join([json_response['token_type'], json_response['access_token']])
                session['github_token'] = token_str
                print("< githubLoginCallback()", file=sys.stderr)
                return f"""
                    <script>
                        window.close();
                    </script>
                """
            except requests.exceptions.JSONDecodeError:
                print("< githubLoginCallback()", file=sys.stderr)
                return f"""
                    <h1>Error with logging in.</h1>
                """
        else:
            return jsonify({"error": f"{res.status_code}", "response": res.text}), res.status_code

# Github Data Access Endpoints
@app.route('/github/user-info', methods=['GET'])
@cross_origin(supports_credentials=True)
def githubUserInfo():
    print("> githubUserInfo()", file=sys.stderr)
    token = session.get('github_token')
    try:
        if not token:
            print("No token found...", file=sys.stderr)
            return jsonify({"error": "No token found."}), 400
        headers = {
            'Authorization': token
        }
        
        githubUserEndpoint = "https://api.github.com/user"
        
        res = requests.get(githubUserEndpoint, headers=headers)
        if res.status_code == 200:
            try:
                json_response = res.json()
                print("< githubUserInfo()", file=sys.stderr)
                return jsonify(json_response)
            except requests.exceptions.JSONDecodeError:
                print("< githubUserInfo()", file=sys.stderr)
                return jsonify({"error": "Error getting user info."}), 400
        else:
            return jsonify({"error": f"{res.status_code}", "response": res.text}), res.status_code
        
    except:
        print("< githubUserInfo()", file=sys.stderr)    
        return jsonify({"error": "Error with flask API function."}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
    