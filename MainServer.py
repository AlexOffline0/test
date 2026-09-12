from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import os

app = Flask(__name__)
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL,
        name TEXT, age TEXT, email TEXT
    )""")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
        cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
        print("[DEBUG] Upgraded database to include Profiles!")
    except: pass 

    # 2. Friends Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1 TEXT NOT NULL,
        user2 TEXT NOT NULL,
        UNIQUE(user1, user2)
    )""")
    
    # 3. Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # --- NEW: GROUPS TABLES ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_members (
        group_name TEXT NOT NULL,
        username TEXT NOT NULL,
        UNIQUE(group_name, username)
    )""")
    # --------------------------
    
    conn.commit()
    conn.close()
    print(f"\n[DEBUG] Server Database is ready and located at: {DB_FILE}")

# --- ACCOUNT ROUTES ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    u, p = data.get('username'), data.get('password')
    if not u or not p: return jsonify({"error": "Missing fields"}), 400
    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
    
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password, name, age, email) VALUES (?, ?, ?, ?, ?)", 
                   (u, hashed, data.get('name', ''), data.get('age', ''), data.get('email', '')))
        conn.commit()
        return jsonify({"status": "Success"}), 200
    except: return jsonify({"error": "Username already exists"}), 400
    finally: conn.close()

@app.route('/login', methods=['POST'])
def login():
    u = request.json.get('username')
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (u,))
    row = cur.fetchone(); conn.close()
    
    if row:
        pw = row[0].decode('utf-8') if isinstance(row[0], bytes) else row[0]
        return jsonify({"password": pw}), 200
    return jsonify({"error": "User not found"}), 404

# --- PROFILE ROUTES ---
@app.route('/get_profile/<username>', methods=['GET'])
def get_profile(username):
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT name, bio, profile_pic FROM users WHERE username = ?", (username,))
    row = cur.fetchone(); conn.close()
    if row: return jsonify({"name": row[0], "bio": row[1], "profile_pic": row[2]}), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    u, n, b, p = data.get('username'), data.get('name'), data.get('bio'), data.get('profile_pic')
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET name = ?, bio = ?, profile_pic = ? WHERE username = ?", (n, b, p, u))
        conn.commit()
        return jsonify({"status": "Success"}), 200
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally: conn.close()

# --- SYNC ROUTES ---
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (data.get('sender'), data.get('receiver'), data.get('message')))
    conn.commit(); conn.close()
    return jsonify({"status": "Sent"}), 200

@app.route('/get_messages/<u1>/<u2>', methods=['GET'])
def get_messages(u1, u2):
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT sender, message FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY timestamp ASC", (u1, u2, u2, u1))
    rows = cur.fetchall(); conn.close()
    return jsonify(rows)

@app.route('/get_friends/<username>', methods=['GET'])
def get_friends(username):
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT user2 FROM friends WHERE user1 = ? UNION SELECT user1 FROM friends WHERE user2 = ?", (username, username))
    res = [r[0] for r in cur.fetchall()]; conn.close()
    return jsonify(res)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    data = request.json
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO friends (user1, user2) VALUES (?, ?)", (data.get('user1'), data.get('user2')))
    conn.commit(); conn.close()
    return jsonify({"status": "Added"}), 200

# --- NEW: GROUP ROUTES ---
@app.route('/get_all_groups', methods=['GET'])
def get_all_groups():
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT name, description FROM groups")
    rows = cur.fetchall(); conn.close()
    return jsonify([{"name": r[0], "description": r[1]} for r in rows])

@app.route('/create_group', methods=['POST'])
def create_group():
    data = request.json
    g_name, desc, creator = data.get('name'), data.get('description'), data.get('creator')
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO groups (name, description) VALUES (?, ?)", (g_name, desc))
        cur.execute("INSERT INTO group_members (group_name, username) VALUES (?, ?)", (g_name, creator))
        conn.commit()
        return jsonify({"status": "Success"}), 200
    except: return jsonify({"error": "Group name already exists"}), 400
    finally: conn.close()

@app.route('/join_group', methods=['POST'])
def join_group():
    data = request.json
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    try:
        cur.execute("INSERT OR IGNORE INTO group_members (group_name, username) VALUES (?, ?)", (data.get('group_name'), data.get('username')))
        conn.commit()
        return jsonify({"status": "Joined"}), 200
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally: conn.close()

if __name__ == '__main__':
    init_db()
    print("\n[DEBUG] Server is online and listening on Port 5000!")
    app.run(host='0.0.0.0', port=5000)