import os
import json
import sys
from mistralai import Mistral
from dotenv import load_dotenv

def sendReq(userContent : str) -> str:
    load_dotenv()  # Load the .env file

    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', 'BROKEN')
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    model="open-mistral-nemo"

    chatResponse = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a GitHub issue assistant, you must always answer with suggestions to solve given problems. Return the message split into a body, examples, and supporting information as a short JSON object. Examples and supporting information should be arrays and all text and links should be formatted in markdown format."
            },
            {
                "role": "user",
                "content": userContent,
            },
        ]
    )

    return chatResponse.choices[0].message.content


def parseOutput(output: dict) -> str:
    outputStr = f'{output.get("body")}\n'

    for ex in output.get('examples'):
        outputStr = outputStr+f'{ex}\n'

    if output.get('supporting_information'):
        for si in output.get('supporting_information'):
            outputStr = outputStr+f'{si}\n'

    return outputStr

# print(chatResponse.choices[0].message.content)


if __name__ == '__main__':
    msg = 'What is functional programming?'

    resp = sendReq(msg)

    print(parseOutput(json.loads(resp)))
