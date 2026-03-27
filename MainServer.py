from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "login.db"

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = query_db("SELECT password FROM users WHERE username = ?", [data['username']], one=True)
    if user:
        return jsonify({"password": list(user)[0]}) # Send hash back to app to check
    return jsonify({"error": "User not found"}), 404

@app.route('/add_friend', methods=['POST'])
def add_friend():
    data = request.json
    query_db("INSERT OR IGNORE INTO friends (user1, user2) VALUES (?, ?)", [data['user1'], data['user2']])
    return jsonify({"status": "success"})

@app.route('/get_friends/<username>', methods=['GET'])
def get_friends(username):
    rows = query_db("SELECT user2 FROM friends WHERE user1 = ? UNION SELECT user1 FROM friends WHERE user2 = ?", [username, username])
    friends = [row[0] for row in rows]
    return jsonify(friends)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)