import json
import os
import sys
from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
from mistral_api import sendReq, parseOutput
import requests
from github import Github, Auth
from dotenv import load_dotenv

load_dotenv()
GH_CLIENT_ID = os.environ.get('GH_CLIENT_ID', 'BROKEN')
GH_CLIENT_SECRET = os.environ.get('GH_CLIENT_SECRET', 'BROKEN')
FLASK_SECRET = os.environ.get('FLASK_SECRET', 'BROKEN')

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
                session['github_token_type'] = json_response['token_type']
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


# data = request.json
#     prompt = data.get('prompt', 'No Prompt Given')



if __name__ == "__main__":
    app.run(port=5000, debug=True)
    