from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/get-resp', methods=['GET'])
@cross_origin(supports_credentials=True)
def getResp():
    # will be filled in with function to gather resp
    return 'test resp'


if __name__ == "__main__":
    app.run(port=5000)