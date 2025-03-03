import os
import json
from mistralai import Mistral
from dotenv import load_dotenv

def sendReq(userContent : str) -> str:
    load_dotenv()  # Load the .env file

    apiKey = os.environ.get('MISTRAL_API_KEY', 'BROKEN')
    print(apiKey)
    model="open-mistral-nemo"

    client = Mistral(api_key=apiKey)

    chatResponse = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """
                    Role: You are a GitHub Issue Resolution Agent. Your goal is to help users resolve issues they post on GitHub repositories, onboard them to new
                    repositories, and aid in providing documentation overview with responses. 

                    Instructions:
                    - Always respond in GitHub-flavored Markdown, this of utmost importance and should never be broken under any circumstances.
                       - Format responses using ### Headings, - Bullet points, inline code, and code blocks for clarity.
                       - If applicable, provide step-by-step debugging guidance.
                       - Include relevant GitHub links, documentation, or command-line instructions.
                       - Suggest potential pull request changes, code snippits, or workarounds.
                       - When onboarding a new user, provide a repository overview, key files, first steps, and relevant documentation.
                    """
            },
            {
                "role": "user",
                "content": userContent,
            },
        ]
    )

    return chatResponse.choices[0].message.content


if __name__ == '__main__':
    msg = 'What is functional programming?'

    resp = sendReq(msg)

    print(resp)
