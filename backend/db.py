from psycopg2 import pool

PG_URI="dbname=pillar user=postgres password= host=localhost port=5432"

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

def add_new_user(username, accesstoken):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, accesstoken) VALUES (%s, %s) RETURNING id", (username, accesstoken))
        id = cursor.fetchone()[0]  
        conn.commit()  # Ensure changes are saved

        return jsonify({"message": "User added successfully", "user_id": id}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500  # Return actual error

    finally:
        cursor.close()
        release_connection(conn)