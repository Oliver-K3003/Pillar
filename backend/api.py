import os
import pickle
import sys
from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
from db import upsert_user, get_conversations_by_user, insert_new_conversation, delete_conversation
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

# Database Calls
@app.route('/db/user/add-or-update', methods=["POST"])
@cross_origin(support_credentials=True)
def upsertUser():
    data = request.json
    username = data.get('username')

    print("> upsertUser()", file=sys.stderr)
    print(username, file=sys.stderr)
    result = upsert_user(username)
    print("< upsertUser()", file=sys.stderr)
            
    if result:
        return jsonify({"message": "Successfully inserted/updated user", "userId" : result}), 200
    else:
        return jsonify({"message": "There was a problem inserting or updating the user's record"}), 400

@app.route('/db/conversation/get', methods=["GET"])
@cross_origin(support_credentials=True)
def getConversations():
    user = request.args.get('user')

    print("> getConversations()", file=sys.stderr)
    conversation_ids = get_conversations_by_user(user)
    print("< getConversations()", file=sys.stderr)

    if conversation_ids is not None:
        return jsonify({"ids": conversation_ids, "user": user}), 200
    else:
        return jsonify({"message": "There was a problem fetching conversations", "user": user}), 400  

@app.route('/db/conversation/create', methods=["POST"])
@cross_origin(support_credentials=True)
def createNewConversation():
    data = request.json
    username = data.get("username")

    print("> createNewConversation()", file=sys.stderr)
    id = insert_new_conversation(username)
    print("< createNewConversation()", file=sys.stderr)

    if id:
        return jsonify({"message": "Successfully created new conversation", "id": id}), 200
    else:
        return jsonify({"message": "There was a problem creating a new conversation"}), 400

@app.route('/db/conversation/delete', methods=["POST"])
@cross_origin(support_credentials=True)
def deleteConversation():
    data = request.json
    conversation_id = data.get("conversation_id")

    print("> deleteConversation()", file=sys.stderr)
    deleted_id = delete_conversation(conversation_id)
    print("< deleteConversation()", file=sys.stderr)

    if deleted_id is not None:
        return jsonify({"message": "Successfully deleted conversation", "id": conversation_id}), 200
    else:
        return jsonify({"message": "There was a problem deleting the conversation", "id": conversation_id}), 400    


if __name__ == "__main__":
    app.run(port=5000, debug=True)
