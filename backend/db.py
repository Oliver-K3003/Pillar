import pickle
from platform import release
from psycopg2 import pool
from flask import jsonify
import sys
import llm_functions

PG_URI="dbname=defaultdb user=doadmin password=AVNS_IYST4j1Vy65B-P-mnuv host=db-postgresql-nyc3-97992-do-user-19817785-0.e.db.ondigitalocean.com port=25060"

conn_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10, 
    dsn=PG_URI
)

def get_connection():
    print("Establishing db connection...", file=sys.stderr)
    return conn_pool.getconn()

def release_connection(conn):
    conn_pool.putconn(conn)

def upsert_user(username):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Attempt to insert user
        cursor.execute(
            "INSERT INTO users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING RETURNING id", 
            (username,)
        )
        result = cursor.fetchone()
        
        if result is None:
            # If no new row was inserted, fetch existing user ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
        
        conn.commit()
        
        if result:
            return result[0]  # Return user ID
        else:
            return None  # Should not happen unless there's an issue
        
    except Exception as e:
        conn.rollback()
        print(f"Error inserting or updating user record: {str(e)}", file=sys.stderr)
        return None
    
    finally:
        cursor.close()
        release_connection(conn)

def get_conversations_by_user(username):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id from conversations WHERE username = %s", (username,))
        conversation_ids = cursor.fetchall()
        return conversation_ids

    except Exception as e:
        print(f"Error getting conversation records for {username} {str(e)}")
        return []    

    finally:
        cursor.close()
        release_connection(conn) 

def insert_new_conversation(username):
    conn = get_connection()
    cursor = conn.cursor()
    
    chat_history = [llm_functions.github_assistant_instructions]
    empty_history = pickle.dumps(chat_history)

    try:
        cursor.execute(
            "INSERT INTO conversations (username, conversation_history) VALUES (%s, %s) RETURNING id",
            (username, empty_history)
        )
        id = cursor.fetchone()[0]
        conn.commit()

        return id

    except Exception as e:
        conn.rollback()
        print(f"Error inserting new conversation into database {str(e)}", file=sys.stderr)
        return None
    
    finally:
        cursor.close()
        release_connection(conn)
        
def delete_conversation(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if isinstance(conversation_id, list):
            conversation_id = conversation_id[0] 

        cursor.execute("DELETE from conversations WHERE id = %s RETURNING id", (conversation_id,))
        id = cursor.fetchone()[0]
        conn.commit()
        return id

    except Exception as e:
        print(f"Error deleting conversation record from database, id: {conversation_id} {str(e)}")
        return []

    finally: 
        cursor.close()
        release_connection(conn)

def get_conversation_history(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT conversation_history FROM conversations WHERE id = %s", (conversation_id,))
        result = cursor.fetchone()
        
        if result and result[0]:  # Ensure result is not None or empty
            history = pickle.loads(result[0])
            return history
        return []  # Return empty list if no data

    except Exception as e:
        print(f"Error retrieving conversation history: {str(e)}", file=sys.stderr)
        return []
    
    finally:
        cursor.close()
        release_connection(conn)

def store_conversation_history(conversation_id, new_chat_history):
    print("> store_conversation_history()", file=sys.stderr)
    conn = get_connection()
    cursor = conn.cursor()
    
    print(new_chat_history, file=sys.stderr)    
    chat_history = pickle.dumps(new_chat_history)
    
    try:
        cursor.execute(
            "UPDATE conversations SET conversation_history = %s WHERE id = %s RETURNING id",
            (chat_history, conversation_id)
        )
        id = cursor.fetchone()  # Fetch the returned id

        if id is None:  # Check if row exists
            print(f"Error: No row found with id {conversation_id}", file=sys.stderr)
            conn.rollback()
            return False  # No row updated

        conn.commit()
        return True  # Success

    except Exception as e:
        conn.rollback()
        print(f"Error updating conversation history: {str(e)}", file=sys.stderr)
        return False  # Failure
    
    finally:
        cursor.close()
        release_connection(conn)