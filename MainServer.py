from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import os

app = Flask(__name__)
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL,
        name TEXT, age TEXT, email TEXT
    )""")
    # Friends table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1 TEXT NOT NULL,
        user2 TEXT NOT NULL,
        UNIQUE(user1, user2)
    )""")
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    # --- DEBUG PRINT: Shows exactly what the app sent ---
    print(f"\n[DEBUG] REGISTRATION DATA RECEIVED: {request.json}")
    
    data = request.json
    if not data:
        return jsonify({"error": "No data received at all"}), 400

    u = data.get('username')
    p = data.get('password')
    
    if not u or not p:
        print("[DEBUG] ERROR: Username or Password was empty!")
        return jsonify({"error": "Username and Password required"}), 400

    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
    
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password, name, age, email) VALUES (?, ?, ?, ?, ?)", 
                   (u, hashed, data.get('name', ''), data.get('age', ''), data.get('email', '')))
        conn.commit()
        print(f"[DEBUG] SUCCESS: User '{u}' added to database.")
        return jsonify({"status": "Success"}), 200
    except sqlite3.IntegrityError:
        print(f"[DEBUG] ERROR: User '{u}' already exists in database.")
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    # --- DEBUG PRINT: Shows exactly what the app sent ---
    print(f"\n[DEBUG] LOGIN DATA RECEIVED: {request.json}")
    
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
        
    u = data.get('username')
    if not u: 
        print("[DEBUG] ERROR: Login missing username!")
        return jsonify({"error": "Missing username"}), 400
    
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (u,))
    row = cur.fetchone(); conn.close()
    
    if row:
        pw = row[0].decode('utf-8') if isinstance(row[0], bytes) else row[0]
        print(f"[DEBUG] SUCCESS: User '{u}' found, sending password hash.")
        return jsonify({"password": pw}), 200
        
    print(f"[DEBUG] ERROR: User '{u}' not found in database.")
    return jsonify({"error": "User not found"}), 404

@app.route('/get_friends/<username>', methods=['GET'])
def get_friends(username):
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT user2 FROM friends WHERE user1 = ? UNION SELECT user1 FROM friends WHERE user2 = ?", (username, username))
    res = [r[0] for r in cur.fetchall()]; conn.close()
    return jsonify(res)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    d = request.json
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO friends (user1, user2) VALUES (?, ?)", (d['user1'], d['user2']))
    conn.commit(); conn.close()
    return jsonify({"status": "Added"})

if __name__ == '__main__':
    init_db()
    print("\n[DEBUG] Server is online and ready!")
    app.run(host='0.0.0.0', port=5000)