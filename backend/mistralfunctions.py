import json
import os
import time
from github import Github, Auth
import pandas as pd
import functools
from dotenv import load_dotenv
from mistralai import AssistantMessage, Mistral


def list_user_repos(github_token: str) -> str:
    print("> list_user_repos()")
    # print(github_token)
    github = Github(auth=Auth.Token(github_token))
    user = github.get_user()
    repos = user.get_repos()

    repo_list = []  # Use a list instead of a dict

    for repo in repos:
        # Use repo.html_url
        repo_list.append({"name": repo.name, "url": repo.html_url})

    print("< list_user_repos()")
    return {
        "type": "repo_list",  # Discriminator field to prevent the Mistral error
        "repositories": repo_list
    }
    
def list_repo_issues(github_token: str, repo_name: str) -> str:
    print("> list_repo_issues()")
    
    github = Github(auth=Auth.Token(github_token))
    user = github.get_user()
    
    # Get the repository object
    try:
        repo = user.get_repo(repo_name)
    except Exception as e:
        print(f"Error fetching repo: {e}")
        return {
            "type": "error",
            "message": f"Cannot find repository '{repo_name}'."
        }

    # Fetch open issues
    issues = repo.get_issues(state='open')

    issue_list = []
    for issue in issues:
        issue_list.append({
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "url": issue.html_url
        })

    print("< list_repo_issues()")
    return {
        "type": "issue_list",  # Discriminator field to prevent Mistral error
        "repository": repo_name,
        "issues": issue_list
    }


tools = [
    {
        "type": "function",
        "function": {
            "name": "list_user_repos",
            "description": "Get a list of repos from logged in user.",
            "parameters": {
                "type": "object",
                "properties": {},
                # "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_repo_issues",
            "description": "Get the open issues from a repository, given the repository's name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "The repository where to get issues from.",
                    }
                },
                "required": ["repo_name"],
            },
        },
    }
]

names_to_functions = {
    'list_user_repos': functools.partial(list_user_repos),
    'list_repo_issues': functools.partial(list_repo_issues)
}

if __name__ == '__main__':
    load_dotenv()  # Load the .env file

    
    
    
    # Tokens/API Keys
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', 'BROKEN')
    GITHUB_TOKEN = os.enivron.get('GITHUB_TOKEN', 'BROKEN')

    # Init Mistral
    client = Mistral(api_key=MISTRAL_API_KEY)
    model = "open-mistral-nemo"
    chat_history = []
    
    # Model instructions.
    model_instructions = {
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
               - After retriving issues from Github specified by the user, ensure that you ask them if it is the correct issue that they would like addressed.
               - If the user is asking for help that is not related to GitHub repositories, ensure that you indicate that you are only there to assist with GitHub issues.
               - Include relevant GitHub links, documentation, or command-line instructions.
               - Suggest potential pull request changes, code snippits, or workarounds.
               - When onboarding a new user, provide a repository overview, key files, first steps, and relevant documentation.
            """
    }
    
    # Initialize the messages array with model instructions.
    chat_history.append(model_instructions)
    
    # Message 1 to system.
    chat_history.append(
        {   
            "role": "user",
            "content": "Can I get a list of my repositories?"
        }
    )
    
    # Get response for message 1.
    response = client.chat.complete(
        model=model,
        messages=chat_history,
        tools=tools,
        tool_choice="auto",
    )
    
    # Response analysis
    print("ChatCompletionResponse Breakdown:")
    for key, value in vars(response).items():
        print(f"{key}: {value}")
    print("\n")
    print(response.choices[0].message)

    chat_history.append(response.choices[0].message)

    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_params = json.loads(tool_call.function.arguments)
    # Inject GitHub token if the function needs it
    if function_name == "list_user_repos":
        function_params["github_token"] = GITHUB_TOKEN
    print("\nfunction_name: ", function_name,
          "\nfunction_params: ", function_params)

    function_result = names_to_functions[function_name](**function_params)
    # print(function_result)

    chat_history.append({"role": "tool", "name": function_name, "content": json.dumps(function_result), "tool_call_id": tool_call.id})

    time.sleep(2)
    
    response = client.chat.complete(
        model=model,
        messages=chat_history,
        tools=tools,
        tool_choice="auto",
    )
    # print(response)
    chat_history.append(response.choices[0].message)
    print(response.choices[0].message.content)

    time.sleep(2)
    
    # Message 3 to system.
    chat_history.append(
        {   
            "role": "user",
            "content": "What issues are open on the repository PillarTestRepo?"
        }
    )
    
    # Get response for message 1.
    response = client.chat.complete(
        model=model,
        messages=chat_history,
        tools=tools,
        tool_choice="auto",
    )
    
    # Response analysis
    print("ChatCompletionResponse Breakdown:")
    for key, value in vars(response).items():
        print(f"{key}: {value}")
    print("\n")
    print(response.choices[0].message)

    chat_history.append(response.choices[0].message)

    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_params = json.loads(tool_call.function.arguments)
    # Inject GitHub token if the function needs it
    if function_name == "list_repo_issues":
        function_params["github_token"] = GITHUB_TOKEN
    print("\nfunction_name: ", function_name,
          "\nfunction_params: ", function_params)

    function_result = names_to_functions[function_name](**function_params)
    # print(function_result)

    chat_history.append({"role": "tool", "name": function_name, "content": json.dumps(function_result), "tool_call_id": tool_call.id})
    
    time.sleep(2)
    
    response = client.chat.complete(
        model=model,
        messages=chat_history,
        tools=tools,
        tool_choice="auto",
    )
    # print(response)
    chat_history.append(response.choices[0].message)
    print(response.choices[0].message.content)    
    
    chat_history.append(
        {"role": "user", "content": "Yes, how would I go about fixing it?"})
    response = client.chat.complete(
        model=model,
        messages=chat_history,
        tools=tools,
        tool_choice="auto",
    )
    # print(response)
    chat_history.append(response.choices[0].message)
    print(response.choices[0].message.content)

    time.sleep(2)
    
    # chat_history.append(
    #     {"role": "user", "content": "Can you break down that URL for me?"})
    # response = client.chat.complete(
    #     model=model,
    #     messages=chat_history,
    #     tools=tools,
    #     tool_choice="auto",
    # )
    # # print(response)
    # chat_history.append(response.choices[0].message)
    # print(response.choices[0].message.content)

    # time.sleep(2)

    # chat_history.append(
    #     {"role": "user", "content": "Do I have a repository titled \"Pillar\" on my Github?"})
    # response = client.chat.complete(
    #     model=model,
    #     messages=chat_history,
    #     tools=tools,
    #     tool_choice="auto",
    # )
    # # print(response)
    # chat_history.append(response.choices[0].message)
    # print(response.choices[0].message.content)

    print("\n================================================================================")

    # Process messages while handling different data types
    summary = []
    for message in chat_history:
        extracted = None
        if isinstance(message, dict):  # If it's a dictionary, process normally
            extracted = {"role": message.get("role"), "content": message.get("content")}
            print(message)
        elif isinstance(message, AssistantMessage):  # If it's an AssistantMessage object
            # Access attributes directly
            extracted = {"role": message.role, "content": message.content}
            print(message)

        if extracted:  # Ignore None values
            if extracted['role'] in ['user', 'assistant']:
                # print(extracted)
                # print("\n")
                summary.append(f"{extracted['role'].capitalize()}: {extracted['content']}")

    # Print the extracted summary
    print("\n\n".join(summary))
