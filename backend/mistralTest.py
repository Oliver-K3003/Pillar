import os
import json
from mistralai import Mistral


def sendReq(userContent: str) -> str:

    apiKey = os.environ.get('MISTRAL_API_KEY', 'BROKEN')
    model = "open-mistral-nemo"

    client = Mistral(api_key=apiKey)

    chatResponse = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a GitHub issue assistant, you must always answer with suggestions to solve given problems. Return the message split into a body, examples, and supporting information as a short JSON object. Examples and supporting information should be arrays and all text and links should be formatted in markdown format"
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
