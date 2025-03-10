from platform import release
from psycopg2 import pool
from flask import jsonify
import sys

PG_URI="dbname=pillar user=postgres password=pillar host=localhost port=5432"

conn_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10, 
    dsn=PG_URI
)

def get_connection():
    print("Establishing db connection...")
    return conn_pool.getconn()

def release_connection(conn):
    conn_pool.putconn(conn)

def upsert_user(username, accesstoken):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, accesstoken) VALUES (%s, %s)  ON CONFLICT (username) DO UPDATE SET accesstoken = EXCLUDED.accesstoken RETURNING id", (username, accesstoken))
        id = cursor.fetchone()[0]  
        conn.commit()  # Ensure changes are saved
        if id:
            return True
        else: 
            conn.rollback()
            return False

    except Exception as e:
        conn.rollback()
        print(f"Error inserting or updating user record: {str(e)}")
        return False

    finally:
        cursor.close()
        release_connection(conn)

def insert_new_conversation(username):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO conversations (username) VALUES (%s) RETURNING id", (username,))
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

def insert_new_messages(conversation_id, prompt, response):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT into messages (conversation_id, prompt, response) VALUES (%s, %s, %s) RETURNING id", (conversation_id, prompt, response))
        id = cursor.fetchall()
        conn.commit()
        return id

    except Exception as e:
        print(f"Error inserting messages for conversation {conversation_id} {str(e)}")
        return []

    finally:
        cursor.close()
        release_connection(conn)         

def get_messages_by_conversation(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT prompt, response from messages WHERE conversation_id = %s", (conversation_id,))
        messages = cursor.fetchall()
        return messages

    except Exception as e:
        print(f"Error getting messages for conversation {conversation_id} {str(e)}")
        return []

    finally: 
        cursor.close()
        release_connection(conn)    
        