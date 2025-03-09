import json
import logging
import os
import time
from dotenv import load_dotenv
from mistralai import AssistantMessage, Mistral
import mistral_functions
load_dotenv()  # Load the .env file

def use_model(chat_history: list) -> str:
    logging.info("\n============================== > use_model() ==============================")
    # Tokens/API Keys
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', None)
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)

    # Select model for use.
    client = Mistral(api_key=MISTRAL_API_KEY)
    model = "open-mistral-nemo"

    # Response from Mistral.
    logging.info("\n========== Mistral Response: ==========")
    # Send new chat w/ context to the model.
    mistral_response = client.chat.complete(
        model=model,
        messages=chat_history,
        tools=mistral_functions.github_functions_dict,
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
                assistantmessage_dict = mistral_functions.assistantmessage_to_dict(original_assistantmessage)
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
        function_params["github_token"] = GITHUB_TOKEN # Inject the Github token into the function call.
        logging.info("Function Name: ", function_name, "Function Params: ", function_params)
        
        function_result = mistral_functions.github_function_mapping[function_name](**function_params) # Run function.
        logging.info(f"Function Results: {function_result}") 
        
        # Append the "answer" to the chat history so that the model has context.
        chat_history.append({"role": "tool", "name": function_name, "content": json.dumps(function_result), "tool_call_id": tool_call.id})

        time.sleep(2) # Sleep to avoid rate limiting.
        
        # Use the model recursively until no more tool calls are required.
        chat_history = use_model(chat_history=chat_history)
        logging.info("\n============================== < use_model() ==============================")
        return chat_history
    else:
        logging.info("Unspecified pathway for model logic.")

        
# SIMULATES BACKEND api.py       
def sendReq(chat_input : str, chat_history : list) -> str:
    logging.debug("============================== > sendReq() ==============================")
    # After getting user input, structure it in a way that matches the chat history and then append it to chat history.
    # the use_model function will automatically look at the last appended message as the most recent message.
    chat_history.append({
        "role": "user",
        "content": chat_input
    })
    logging.info(f"Received message from user: {chat_history[-1]["content"]}")
    # use_model will return the updated chat history, the latest message to return and show the user will be 
    # the last one found in the chat history.
    new_chat_history = use_model(chat_history=chat_history)
        
    assistantmessage_dict = mistral_functions.assistantmessage_to_dict(new_chat_history[-1])
    chat_output = assistantmessage_dict['content']
    
    logging.info("\n========== Returning message to user: ==========")
    logging.info(f"Message to be returned to user:\n{chat_output}")
    logging.debug("============================== < sendReq() ==============================")
    return chat_output, new_chat_history
    
    

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    
    # Initialize the chat history w/ model instructions.
    # TODO: In DB, whenever a new chat is initialized, need to inject this as the first message.
    chat_history = [] # Simulate database
    chat_history.append(mistral_functions.github_assistant_instructions)
    
    # SIMULATES SENDING MESSAGE to "/get-resp"
    while True:
        prompt = input("\nUser: ")
        chat_output, chat_history = sendReq(chat_input=prompt, chat_history=chat_history)
        print(f"\nAssistant: {chat_output}") # Print Assistant Output.