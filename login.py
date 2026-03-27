import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
import os
import sys

# Import your other scripts directly
import data 
import home

# ---------------- DB PATH ----------------
def get_db_path():
    import sys, os
    # If running as an EXE
    if getattr(sys, 'frozen', False):
        # Look in the same folder as the .exe file
        base_path = os.path.dirname(sys.executable)
    else:
        # Look in the folder where the .py script is
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, "login.db")

DB_FILE = get_db_path()

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT NOT NULL,
        can_delete INTEGER DEFAULT 0
    )""")
    cursor.execute("CREATE TABLE IF NOT EXISTS session (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT)")
    # Ensure friends/messages tables exist for home.py
    cursor.execute("CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY AUTOINCREMENT, user1 TEXT, user2 TEXT, UNIQUE(user1, user2))")
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()

# ---------------- SESSION ----------------
def get_logged_in_user():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM session LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_session(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM session")
    cursor.execute("INSERT INTO session (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

# ---------------- LOGIN LOGIC ----------------
def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode("utf-8"), result[0]):
        return True
    return False

# ---------------- GUI ----------------
def open_login_window():
    root = tk.Tk()
    root.title("Coreton - Login")
    root.geometry("300x250") # Slightly taller for the new button
    root.resizable(False, False)
    root.config(bg="black")

    tk.Label(root, text="Username:", bg="black", fg="green", font=("Pixelify Sans", 9, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_username = tk.Entry(root, bg="black", fg="green", font=("Pixelify Sans", 9, "bold"))
    entry_username.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Password:", bg="black", fg="green", font=("Pixelify Sans", 9, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_password = tk.Entry(root, show="*", bg="black", fg="green", font=("Pixelify Sans", 9, "bold"))
    entry_password.grid(row=1, column=1, padx=5, pady=5)

    def on_login_click():
        u = entry_username.get().strip()
        p = entry_password.get().strip()
        if login_user(u, p):
            save_session(u)
            root.destroy()
            # DIRECT CALL to home.py instead of home.exe
            home.open_home_window(u)
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def on_register_click():
        root.destroy()
        # DIRECT CALL to data.py instead of data.exe
        data.open_registration_window()

    # Login Button
    tk.Button(root, text="Login", width=20, command=on_login_click, bg="black", fg="green", font=("Pixelify Sans", 9, "bold")).grid(row=2, column=0, columnspan=2, pady=10)

    # NEW: Register Button
    tk.Button(root, text="Go to Registration", width=20, command=on_register_click, bg="black", fg="#ff80ff", font=("Pixelify Sans", 9, "bold")).grid(row=3, column=0, columnspan=2, pady=5)
    
    root.mainloop()


# ---------------- STARTUP LOGIC ----------------
if __name__ == "__main__":
    init_db()
    logged_in_user = get_logged_in_user()

    if logged_in_user:
        # Go straight to home via function
        home.open_home_window(logged_in_user)
    else:
        # Show login/registration
        open_login_window()