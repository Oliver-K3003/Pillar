from platform import release
from psycopg2 import pool
from flask import jsonify
import sys

PG_URI=""

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

if __name__ == "__main__":
    print(insert_new_conversation("the-clam"))