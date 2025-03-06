import json
import time
from github import Github, Auth
import pandas as pd
import functools
from mistralai import Mistral

############################## ORIGINAL TEST DATA ##############################
# Assuming we have the following data
data = {
    'transaction_id': ['T1001', 'T1002', 'T1003', 'T1004', 'T1005'],
    'customer_id': ['C001', 'C002', 'C003', 'C002', 'C001'],
    'payment_amount': [125.50, 89.99, 120.00, 54.30, 210.20],
    'payment_date': ['2021-10-05', '2021-10-06', '2021-10-07', '2021-10-05', '2021-10-08'],
    'payment_status': ['Paid', 'Unpaid', 'Paid', 'Paid', 'Pending']
}

# Create DataFrame
df = pd.DataFrame(data)


def retrieve_payment_status(df: pd.DataFrame, transaction_id: str) -> str:
    if transaction_id in df.transaction_id.values:
        return json.dumps({'status': df[df.transaction_id == transaction_id].payment_status.item()})
    return json.dumps({'error': 'transaction id not found.'})


def retrieve_payment_date(df: pd.DataFrame, transaction_id: str) -> str:
    if transaction_id in df.transaction_id.values:
        return json.dumps({'date': df[df.transaction_id == transaction_id].payment_date.item()})
    return json.dumps({'error': 'transaction id not found.'})

##############################################################################

def list_user_repos(github_token: str) -> str:
    print("> list_user_repos()")
    # print(github_token)
    github = Github(auth=Auth.Token(github_token))
    user = github.get_user()
    repos = user.get_repos()

    repo_list = []  # Use a list instead of a dict

    for repo in repos:
        repo_list.append({"name": repo.name, "url": repo.html_url})  # Use repo.html_url

    return {
        "type": "repo_list",  # Discriminator field to prevent the Mistral error
        "repositories": repo_list
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_payment_status",
            "description": "Get payment status of a transaction",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction id.",
                    }
                },
                "required": ["transaction_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_payment_date",
            "description": "Get payment date of a transaction",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction id.",
                    }
                },
                "required": ["transaction_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_user_repos",
            "description": "Get a list of repos from logged in user.",
            "parameters": {
                "type": "object",
                "properties": {},
                # "required": ["transaction_id"],
            },
        },
    }
]

names_to_functions = {
    'retrieve_payment_status': functools.partial(retrieve_payment_status, df=df),
    'retrieve_payment_date': functools.partial(retrieve_payment_date, df=df),
    'list_user_repos': functools.partial(list_user_repos)    
}


if __name__ == '__main__':
    github_token = ""
    api_key = ""

    model="open-mistral-nemo"
    # list_user_repos(github_token)
    # exit()
    
    messages = [{"role": "user", "content": "Hey, I need to get a list of repositories."}]
    
    messages = [
        {
                "role": "system",
                "content": """
                    Role: You are a GitHub Issue Resolution Agent. Your goal is to help users resolve issues they post on GitHub repositories, onboard them to new
                    repositories, and aid in providing documentation overview with responses. 

                    Instructions:
                       If you are given a list of repositories, make sure you list them out individually in your response, and only show the repository name.
                    """
            },
        {"role": "user", "content": "Hey, I'm looking to figure out what Github repositories I have. Could you put them in a comma seperated list?"}
    ]
    # messages = [{"role": "user", "content": "What's the status of my transaction T1001?"}]

    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model = model,
        messages = messages,
        tools = tools,
        tool_choice = "auto",
    )
    # print(response)
    # exit()
    
    messages.append(response.choices[0].message)

    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_params = json.loads(tool_call.function.arguments)
    # Inject GitHub token if the function needs it
    if function_name == "list_user_repos":
        function_params["github_token"] = github_token
    print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)
    
    function_result = names_to_functions[function_name](**function_params)
    # print(function_result)
    
    time.sleep(2)
    
    messages.append({"role":"tool", "name":function_name, "content":json.dumps(function_result), "tool_call_id":tool_call.id})

    response = client.chat.complete(
        model = model, 
        messages = messages
    )
    # print(response)
    messages.append(response.choices[0].message)
    print(response.choices[0].message.content)
    
    time.sleep(2)
    
    messages.append({"role":"user", "content":"What is the URL for the first repo you told me about?"})
    response = client.chat.complete(
        model = model, 
        messages = messages
    )
    # print(response)
    messages.append(response.choices[0].message)
    print(response.choices[0].message.content)
    
    time.sleep(2)
    
    messages.append({"role":"user", "content":"Can you break down that URL for me?"})
    response = client.chat.complete(
        model = model, 
        messages = messages
    )
    # print(response)
    messages.append(response.choices[0].message)
    print(response.choices[0].message.content)
    
    time.sleep(2)
    
    messages.append({"role":"user", "content":"My name is Carl."})
    response = client.chat.complete(
        model = model, 
        messages = messages
    )
    # print(response)
    messages.append(response.choices[0].message)
    print(response.choices[0].message.content)
    
    time.sleep(2)
    
    messages.append({"role":"user", "content":"What's my name?"})
    response = client.chat.complete(
        model = model, 
        messages = messages
    )
    # print(response)
    messages.append(response.choices[0].message)
    print(response.choices[0].message.content)
    
    # print(messages)
    
    
