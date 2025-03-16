import os
import pickle
import sys
from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
from mistral_api import sendReq
import requests
from github import Github, Auth
from dotenv import load_dotenv
import secrets

load_dotenv()
GH_CLIENT_ID = os.environ.get('GH_CLIENT_ID', 'BROKEN')
GH_CLIENT_SECRET = os.environ.get('GH_CLIENT_SECRET', 'BROKEN')
FLASK_SECRET = secrets.token_hex()

app = Flask(__name__)
app.secret_key = FLASK_SECRET
CORS(app, supports_credentials=True)

@app.route('/get-resp', methods=['POST'])
@cross_origin(supports_credentials=True)
def getResp():
    print("> getResp()", file=sys.stderr)
    data = request.json
    messages = data.get('msgs', 'New message & history not passed in.')
    
    chat_input = messages[-1]['usr'] # The last value of the chat array passed in is the chat input.
    
    # Send in the github token for use if needed by mistral.
    github_token = session.get('github_token')
    if not github_token:
        print("No token found...", file=sys.stderr)
        return jsonify({"error": "No token found. (User likely not logged in)."}), 401
    else:
        print(f"Got token.", file=sys.stderr)
        
    # We'll simulate the chat history being retrieved from the DB.
    # Load conversation.
    try:
        with open("chat_history.pkl", "rb") as file:
            chat_history = pickle.load(file)
    except:
        print("file issue or DNE")
        chat_history=[]
 
    # will be filled in with function to gather resp
    promptResponse, chatHistory = sendReq(chat_input=chat_input, chat_history=chat_history, github_token=github_token)
    
    # Store update Conversation.
    with open("chat_history.pkl", "wb") as file:
        pickle.dump(chatHistory, file)
    
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

# Callback function; getting token from code.
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
                session['github_token'] = json_response['access_token']
                session['username'] = githubUserInfo().get_json()['login']
                
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
# User Information
@app.route('/github/user-info', methods=['GET'])
@cross_origin(supports_credentials=True)
def githubUserInfo():
    print("> githubUserInfo()", file=sys.stderr)
    
    token = session.get('github_token')
    if not token:
        print("No token found...", file=sys.stderr)
        return jsonify({"error": "No token found. (User likely not logged in)."}), 401

    try:
        github = Github(auth=Auth.Token(token))
        user = github.get_user()
        
        json_response = {
            "flask_status" : "success",
            "avatar_url" : user.avatar_url,
            "html_url" : user.html_url,
            "login" : user.login,
        }
        
        print("< githubUserInfo()", file=sys.stderr)
        return jsonify(json_response)
    
    except Exception as e:
        print(f"< githubUserInfo() Error {e}", file=sys.stderr)    
        return jsonify({"flask_status": "Error with flask API function."}), 400
    
# API to Check Rate Limits (Also can be used to check token validity)
@app.route('/github/rate-limit', methods=['GET'])
@cross_origin(supports_credentials=True)
def githubRateLimitCheck():
    print("> githubRateLimitCheck()", file=sys.stderr)
    
    token = session.get('github_token')
    if not token:
        print("No token found...", file=sys.stderr)
        return jsonify({"error": "No token found. (User likely not logged in)."}), 401
        
    try:
        github = Github(auth=Auth.Token(token))
        rate_limit = github.get_rate_limit()
        
        json_response = {
            "flask_status" : "success",
            "rate_limit" : {
                "core" : rate_limit.core._rawData,
                "search" : rate_limit.search._rawData
            }
        }
        
        print("< githubRateLimitCheck()", file=sys.stderr)
        return jsonify(json_response)
    
    except Exception as e:
        print(f"< githubRateLimitCheck() Error {e}", file=sys.stderr)    
        return jsonify({"flask_status": "Error with flask API function."}), 400
    
# API to get list of repositories from Github associated with user.
@app.route('/github/get-user-repos', methods=['GET'])
@cross_origin(supports_credentials=True)
def githubUserRepos():
    print("> githubUserRepos()", file=sys.stderr)

    token = session.get('github_token')
    if not token:
        print("No token found...", file=sys.stderr)
        return jsonify({"error": "No token found. (User likely not logged in)."}), 401
    
    try:
        github = Github(auth=Auth.Token(token))
        github_user_repos = github.get_user().get_repos()
        user_repos = []
        for r in github_user_repos:
            user_repos.append({
                "name" : r.name,
                "owner_login" : r.owner.login,
                "description" : r.description,
                "html_url" : r.html_url,
            })

        json_response = {
            "flask_status" : "success",
            "repos" : user_repos
        }
        
        print("< githubUserRepos()", file=sys.stderr)
        return jsonify(json_response)
    
    except Exception as e:
        print(f"< githubUserRepos() Error {e}", file=sys.stderr)    
        return jsonify({"flask_status": "Error with flask API function."}), 400


if __name__ == "__main__":
    app.run(port=5000, debug=True)
