import os
import sys
from mistralai import Mistral
from dotenv import load_dotenv
import mistral_functions

def sendReq(chat_input: str, chat_history: list, github_token: str) -> str:
    print("> sendReq()", file=sys.stderr)

    # Chat history is not just the string conversation that we see in the UI, but includes a lot 
    # more text information. Therefore we need to store it seperately or make it easy for the UI
    # component to extract the parts that should be visible.
    
    # Start by appending the most recently received 'chat_input', to the chat history.
    chat_history.append({
        "role": "user",
        "content": chat_input
    })
    
    # Pass the new chat history with the 'chat_input' to the model, then it will return with its
    # response added to the chat history.
    load_dotenv()  # Load the .env file
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', 'BROKEN')
    new_chat_history = mistral_functions.use_model(chat_history=chat_history,
                                                   mistral_api_key=MISTRAL_API_KEY,
                                                   github_token=github_token)
    
    # Extract the text response from the model, in addition to the chat history.
    assistantmessage_dict = mistral_functions.assistantmessage_to_dict(new_chat_history[-1])
    chat_output = assistantmessage_dict['content']
    
    return chat_output, new_chat_history