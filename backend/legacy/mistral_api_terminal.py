import json
import logging
import os
import pickle
from dotenv import load_dotenv
import mistral_functions
load_dotenv()  # Load the .env file

# SIMULATES BACKEND api.py
# chat_input is the most recent chat msg sent by the user.
# chat_history is the list of formatted previous messages.
def sendReq(chat_input: str, chat_history : list) -> str:
    mistral_api_key = os.environ.get('MISTRAL_API_KEY', None)
    github_token = os.environ.get('GITHUB_TOKEN', None)

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
    new_chat_history = mistral_functions.use_model(chat_history=chat_history,
                                                   mistral_api_key=mistral_api_key,
                                                   github_token=github_token)

    assistantmessage_dict = mistral_functions.assistantmessage_to_dict(new_chat_history[-1])
    chat_output = assistantmessage_dict['content']
    
    logging.info("\n========== Returning message to user: ==========")
    logging.info(f"Message to be returned to user:\n{chat_output}")
    logging.debug("============================== < sendReq() ==============================")
    return chat_output, new_chat_history

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO, filename=sys.stderr)
    
    # SIMULATES SENDING MESSAGE to "/get-resp"
    while True:
        prompt = input("\nUser: ")
        
        # Load conversation.
        try:
            with open("chat_history.pkl", "rb") as file:
                chat_history = pickle.load(file)
        except:
            print("file issue or DNE")
            chat_history=[]
        
        chat_output, chat_history = sendReq(chat_input=prompt, chat_history=chat_history)
        
        print(f"\nAssistant: {chat_output.strip()}") # Print Assistant Output.
        
        # Store update Conversation.
        with open("chat_history.pkl", "wb") as file:
                pickle.dump(chat_history, file)
        