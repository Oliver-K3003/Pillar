import os
import json
import pandas as pd
import sys
from github import Github, Auth
from mistralai import Mistral, Tool
from dotenv import load_dotenv
import functools

# List user repositories.
def list_user_repos(github_token : str) -> dict:
    print("> list_user_repos()", file=sys.stderr)
    print(github_token, file=sys.stderr)
    github = Github(auth=Auth.Token(github_token))
    user = github.get_user()
    repos = user.get_repos()
    
    repo_list = []
    for repo in repos:
        repo_list.append({"name" : repo.name, "url" : repo.url})
    
    return {"status": "success", "repositories": repo_list}


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
                       - If the user is asking for help with their specific Github repositories, then you need to ask them for that information and then end the response there. Otherwise, you cannot hallucinate and make up repositories.
                       - If applicable, provide step-by-step debugging guidance.
                       - You must give brief responses.
                       - If the user is asking for help that is not related to GitHub repositories, ensure that you indicate that you are only there to assist with GitHub issues.
                       - Include relevant GitHub links, documentation, or command-line instructions.
                       - Suggest potential pull request changes, code snippits, or workarounds.
                       - When onboarding a new user, provide a repository overview, key files, first steps, and relevant documentation.
                    """
            },
            {
                "role": "user",
                "content": userContent,
            },
        ],
        tools=tools_with_args,
        tool_choice="auto"
    )
    print(chatResponse, file=sys.stderr)

    return chatResponse.choices[0].message.content

if __name__ == '__main__':
    msg = 'What is functional programming?'

    resp = sendReq(msg)

    print(resp)
