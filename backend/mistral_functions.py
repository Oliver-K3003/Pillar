import functools
import json
import logging
import os
import time
from dotenv import load_dotenv
from github import Github, Auth
from mistralai import AssistantMessage, Mistral
load_dotenv()

##### Logic for the Mistral model #####
def use_model(chat_history: list, mistral_api_key: str, github_token: str) -> str:
    logging.info("\n============================== > use_model() ==============================")
    # Select model for use.
    client = Mistral(api_key=mistral_api_key)
    model = "open-mistral-nemo"
    
    # Check chat history to see if instructions have been already added, if not, append to beginning.
    if chat_history and not chat_history[0].get("role") == "system":
        chat_history.insert(0, github_assistant_instructions)
        print("Appending")

    # Response from Mistral.
    logging.info("\n========== Mistral Response: ==========")
    # Send new chat w/ context to the model.
    mistral_response = client.chat.complete(
        model=model,
        messages=chat_history,
        tools=github_functions_dict,
        tool_choice="auto",
        n=1
    )
    for key, value in vars(mistral_response).items():
        logging.info(f"{key}: {value}")
    
    logging.info("\n========== Decompose Choices: ==========")
    all_choices_dict = []
    original_assistantmessage = None # We need to save the original version of the AssistantMessage to append to chat history.
    
    for choice in mistral_response.choices:
        choice_dict = {}
        for item in choice:
            key = item[0]
            value = item[1]
            
            # If the parameter is of type "AssistantMessage", it requires further breakdown into another dict.
            if(type(value) == AssistantMessage):
                original_assistantmessage = value # Save original for chat history.
                assistantmessage_dict = assistantmessage_to_dict(original_assistantmessage)
                value = assistantmessage_dict # Make value the new dict.

            choice_dict[key] = value
        all_choices_dict.append(choice_dict)
        
    logging.info(all_choices_dict)
    
    # Executing first choice.
    first_choice = all_choices_dict[0]
    finish_reason = first_choice['finish_reason'] # See what the reasoning for the model's return is.
    
    message = first_choice['message'] 
    content = message['content'] # Get contents of the first choice.
    prefix = message['prefix']
    role = message['role']
    tool_calls = message['tool_calls']
    
    # Model is done thinking; return message to chat.
    chat_history.append(original_assistantmessage) # Append the selected action/message to chat history.
    
    # If model is done finding information, send the whole chat back w/ the new message to the user.
    if finish_reason == 'stop' and role == 'assistant' and tool_calls == None:
        logging.info("\n============================== < use_model() ==============================")
        return chat_history
    # Model needs to use a tool
    if finish_reason == 'tool_calls':
        logging.info("\n========== Model is making a function call: ==========")
        # Get selected tool (function)
        tool_call = tool_calls[0]
        function_name = tool_call.function.name
        function_params = json.loads(tool_call.function.arguments)
        function_params["github_token"] = github_token # Inject the Github token into the function call.
        logging.info("Function Name: ", function_name, "Function Params: ", function_params)
        
        try:
            if function_name in github_function_mapping:
                function_result = github_function_mapping[function_name](**function_params) # Run function.
                logging.info(f"Function Results: {function_result}")
            else:
                function_result = {"error": f"Function '{function_name}' not implemented."}
        except Exception as e:
            function_result = {"error": f"An error occurred: {e}"}
            logging.error(f"Exception in function {function_name}: {e}")
        
        # Append the "answer" to the chat history so that the model has context.
        chat_history.append({"role": "tool", "name": function_name, "content": json.dumps(function_result), "tool_call_id": tool_call.id})

        time.sleep(2) # Sleep to avoid rate limiting.
        
        # Use the model recursively until no more tool calls are required.
        chat_history = use_model(chat_history=chat_history, mistral_api_key=mistral_api_key, github_token=github_token)
        logging.info("\n============================== < use_model() ==============================")
        return chat_history
    else:
        logging.info("Unspecified pathway for model logic.")

##### Functions to Call Github #####
def list_user_repos(github_token: str) -> str:
    logging.info("> list_user_repos()")
    github = Github(auth=Auth.Token(github_token))
    user = github.get_user()
    repos = user.get_repos()

    repo_list = []  # Use a list instead of a dict

    for repo in repos:
        # Use repo.html_url
        repo_list.append({"name": repo.name, "owner" : repo.owner.login, "url": repo.html_url})

    logging.info("< list_user_repos()")
    return {
        "type": "repo_list",  # Discriminator field to prevent the Mistral error
        "repositories": repo_list
    }


def list_repo_issues(github_token: str, repo_name: str, repo_owner: str) -> str:
    logging.info("> list_repo_issues()")

    # Get the repository object
    github = Github(auth=Auth.Token(github_token))
    try:
        repo = github.get_repo(f"{repo_owner}/{repo_name}")
    except Exception as e:
        logging.error(f"Error fetching repo: {e}")
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

    logging.info("< list_repo_issues()")
    return {
        "type": "issue_list",  # Discriminator field to prevent Mistral error
        "repository": repo_name,
        "issues": issue_list
    }


##### Function mappings for model context #####
github_function_mapping = {
    'list_user_repos': functools.partial(list_user_repos),
    'list_repo_issues': functools.partial(list_repo_issues)
}

github_functions_dict = [
    {
        "type": "function",
        "function": {
            "name": "list_user_repos",
            "description": "Get a list of repos from logged in user.",
            "parameters": {
                "type": "object",
                "properties": {},
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
                    },
                    "repo_owner": {
                        "type": "string",
                        "description": "The username of the owner of the repository from where to get issues from.",
                    }
                },
                "required": ["repo_name", "repo_owner"],
            },
        },
    }
]


##### prompt engineering for assistant #####
github_assistant_instructions = {
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

# helper function to convert assistantmessage objects to dictionaries for easy usage when looking for msgs
def assistantmessage_to_dict(am: AssistantMessage) -> dict:
    assistantmessage_dict = {}
    for i in am:
        am_key = i[0]
        am_val = i[1]
        assistantmessage_dict[am_key] = am_val
    return assistantmessage_dict


if __name__ == '__main__':

    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)
    github = Github(auth=Auth.Token(GITHUB_TOKEN))