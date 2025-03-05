import os
from mistralai import Mistral
from dotenv import load_dotenv

def sendReq(userContent : str, githubToken : str) -> str:
    load_dotenv()  # Load the .env file

    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', 'BROKEN')
    client = Mistral(api_key=MISTRAL_API_KEY)

    model="open-mistral-nemo"

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
                       - If the user is asking for help with their specific Github repositories, then you need to ask them for that information. Otherwise, you cannot hallucinate and make up repositories.
                       - If applicable, provide step-by-step debugging guidance.
                       - You must give brief responses.
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
