import functools
import json
import logging
import os
import time
from dotenv import load_dotenv
from github import Github, Auth
from mistralai import AssistantMessage, Mistral
load_dotenv()

##### Logic for the LLM #####
def use_model(chat_history: list, llm_api_key: str, github_token: str) -> str:
    logging.info("\n============================== > use_model() ==============================")
    # Select model for use.
    client = Mistral(api_key=llm_api_key)
    model = "open-mistral-nemo"
    
    # Check chat history to see if instructions have been already added, if not, append to beginning.
    if chat_history and not chat_history[0].get("role") == "system":
        chat_history.insert(0, github_assistant_instructions)
        print("Appending")

    # Response from LLM.
    logging.info("\n========== LLM Response: ==========")
    # Send new chat w/ context to the model.
    llm_response = client.chat.complete(
        model=model,
        messages=chat_history,
        tools=github_functions_dict,
        tool_choice="auto",
        n=1
    )
    for key, value in vars(llm_response).items():
        logging.info(f"{key}: {value}")
    
    logging.info("\n========== Decompose Choices: ==========")
    all_choices_dict = []
    original_assistantmessage = None # We need to save the original version of the AssistantMessage to append to chat history.
    
    for choice in llm_response.choices:
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
        chat_history = use_model(chat_history=chat_history, llm_api_key=llm_api_key, github_token=github_token)
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
        repo_list.append({
            "name": repo.name,
            "owner": repo.owner.login,
            "html_url": repo.html_url,
            "url" : repo.url
        })

    logging.info("< list_user_repos()")
    return {
        "type": "repo_list",
        "repositories": repo_list
    }


def list_open_repo_issues(github_token: str, repo_name: str, repo_owner: str) -> str:
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
            "html_url": issue.html_url,
            "url": issue.url,
        })

    logging.info("< list_repo_issues()")
    return {
        "type": "issue_list",
        "repository": repo_name,
        "issues": issue_list
    }


def get_assigned_issues(github_token: str) -> str:
    logging.info("> get_assigned_issues")

    github = Github(auth=Auth.Token(github_token))
    try:
        assigned_issues = github.get_user().get_issues()
    except Exception as e:
        logging.error(f"Error fetching repo: {e}")
        return {
            "type": "error",
            "message": f"Cannot get assigned issues for '{github.get_user().login}'."
        }

    issue_list = []
    for issue in assigned_issues:
        issue_list.append({
            "repo": issue.repository_url,
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "html_url": issue.html_url,
            "url": issue.url
        })
    if len(issue_list) == 0:
        issue_list = "No assigned issues found for the user."
    
    logging.info("< list_repo_issues()")
    return {
        "type": "issue_list",
        "assigned_issues": issue_list
    }

# Issue comments
def get_issue_comments(github_token: str, repo_owner: str, repo_name: str, issue_num: str) -> str:
    logging.info("> get_issue_comments")
    github = Github(auth=Auth.Token(github_token))
    
    try:
        repo = github.get_repo(f"{repo_owner}/{repo_name}")
        issue = repo.get_issue(int(issue_num))
        comments = issue.get_comments()
    except Exception as e:
        logging.error(f"Error fetching repo: {e}")
        return {
            "type": "error",
            "message": f"Cannot get issue comments for issue {issue_num} from {repo_name}."
        }
        
    all_comments = []
    for c in comments:
        all_comments.append({
            "commenter" : c.user.login,
            "content" : c.body,
            "html_url": c.html_url,
            "url" : c.url
        })
        
    if len(all_comments) == 0:
        all_comments = "No assigned issues found for the user."
        
    logging.info("< get_issue_comments")
    return {
        "type": "issue_comment_list",
        "comments": all_comments
    }
#


##### Function mappings for model context #####
github_function_mapping = {
    'list_user_repos': functools.partial(list_user_repos),
    'list_repo_issues': functools.partial(list_open_repo_issues),
    'get_assigned_issues' : functools.partial(get_assigned_issues),
    'get_issue_comments' : functools.partial(get_issue_comments),
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
    }, 
    {
        "type": "function",
        "function": {
            "name": "get_assigned_issues",
            "description": "When a user is authenticated, gets the list of issues that are assigned to them.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_issue_comments",
            "description": "Given a repo name in the format 'owner/repo', and the issue number, return the comments for a the issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_owner": {
                        "type": "string",
                        "description": "The username of the owner of the repository from where to get issues from.",
                    },
                    "repo_name": {
                        "type": "string",
                        "description": "The repository where to get issues from.",
                    },                    
                    "issue_num": {
                        "type": "string",
                        "description": "The issue number that the user would like the get the comments from.",
                    }
                },
                "required": ["repo_name", "issue_num"],
            },
        },
    },
]


##### prompt engineering for assistant #####
github_assistant_instructions = {
    "role": "system",
    "content": """
        Role: You are a GitHub Issue Resolution Agent. 
        Goals: Your goal is to help users resolve issues they have on GitHub, onboard them to new repositories if they ask for onboarding help, and aid in providing documentation overview with responses.        

        Instructions for Formatting Responses:
            - ***Always respond in GitHub-flavored Markdown, this of utmost importance and should never be broken under any circumstances***.
            - Use the following formatting:
                - `###` for section headings.
                - `-` for bullet points.
                - Surround code with the character ` for short snippets of code.
                - Surround code with ``` for longer examples.
            - If there are more than 5 items in a list ***ONLY SHOW THE FIRST FIVE***, then the rest if the user agrees to. You don't need to tell the user how many items are in the list if it is less than the max number that you can show.
        
        Behaviour:
            - Do not suggest actions that require write access, such as creating comments or pull requests.
            - You must provide brief responses that address the user's issues without being too verbose.
            - If there is a list of items, only show the first five of them, and ask the user if they would like to see more of the long list, and show the rest upon request by the user's response.
            - If you are showing a list of items, only show their titles and subtitles. Do not show further details until an item from that list itself is selected.
            - If the user is asking for help with a specific GitHub repository, and they do not specify or there is no context history, check the list of repositories they have access to.
            - When deciding a repository to work on, make sure you ask and confirm which repository they would like to work on.
            - After retriving issues from Github as spotified by the user, verify with them to ensure that it is the issue they would like to work on.
            - Only assist with issues related to software development and Github issues.
            - Include relevant GitHub links, documentation, or command-line instructions.
            - Suggest potential pull request changes, code snippets, or workarounds.
            - If a user requests onboarding for a repository, do a scan of the file layout of the repository and provide a repository overview of key files, first steps, and relevant documentation.
            - When receiving information from a GitHub API call, links with parameter "html_url" are the links for users to view, while "url" is used for future API endpoint calls for further tool usage.
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
    
    print(get_issue_comments(GITHUB_TOKEN, "Oliver-K3003/Pillar", "7"))
    
