import json
from flask import Flask, request
from flask_cors import CORS, cross_origin
from mistralTest import sendReq, parseOutput


app = Flask(__name__)
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


if __name__ == "__main__":
    app.run(port=5000)