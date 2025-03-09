import functools
import logging
from github import Github, Auth
from mistralai import AssistantMessage

##### Functions to Call Github #####
def list_user_repos(github_token: str) -> str:
    logging.info("> list_user_repos()")
    github = Github(auth=Auth.Token(github_token))
    user = github.get_user()
    repos = user.get_repos()

    repo_list = []  # Use a list instead of a dict

    for repo in repos:
        # Use repo.html_url
        repo_list.append({"name": repo.name, "url": repo.html_url})

    logging.info("< list_user_repos()")
    return {
        "type": "repo_list",  # Discriminator field to prevent the Mistral error
        "repositories": repo_list
    }


def list_repo_issues(github_token: str, repo_name: str) -> str:
    logging.info("> list_repo_issues()")

    github = Github(auth=Auth.Token(github_token))
    user = github.get_user()

    # Get the repository object
    try:
        repo = user.get_repo(repo_name)
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