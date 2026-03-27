from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import os

app = Flask(__name__)
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Users Table
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password BLOB, name TEXT, age TEXT, email TEXT)")
    # Friends Table
    cursor.execute("CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, UNIQUE(user1, user2))")
    # Messages Table (The New Part)
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    u, p = data.get('username'), data.get('password')
    hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password, name, age, email) VALUES (?, ?, ?, ?, ?)", (u, hashed, data.get('name'), data.get('age'), data.get('email')))
        conn.commit(); return jsonify({"status": "Success"}), 200
    except: return jsonify({"error": "User exists"}), 400
    finally: conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    u = data.get('username')
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (u,))
    row = cur.fetchone(); conn.close()
    if row:
        pw = row[0].decode('utf-8') if isinstance(row[0], bytes) else row[0]
        return jsonify({"password": pw}), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/send_message', methods=['POST'])
def send_msg():
    data = request.json
    s, r, m = data.get('sender'), data.get('receiver'), data.get('message')
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (s, r, m))
    conn.commit(); conn.close()
    return jsonify({"status": "Sent"}), 200

@app.route('/get_messages/<u1>/<u2>', methods=['GET'])
def get_msgs(u1, u2):
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
    d = request.json
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO friends (user1, user2) VALUES (?, ?)", (d['user1'], d['user2']))
    conn.commit(); conn.close()
    return jsonify({"status": "Added"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)