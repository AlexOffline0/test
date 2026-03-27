import tkinter as tk
from tkinter import *
from tkinter import simpledialog, messagebox
import sqlite3
import os
import sys
import bcrypt
import re
import requests  # Required for syncing
import threading # Required for playing sound without freezing UI

# Import your sub-modules
import gacha 
import apps 

# ---------------- CONFIG ----------------
# Replace this with your actual ngrok URL from your Flask server
SERVER_URL = "http://your-ngrok-url.ngrok-free.app"

# ---------------- SOUND HELPER ----------------
def play_notification():
    """ Plays notification sound using winsound for Python 3.14 compatibility """
    try:
        import winsound
        # Plays a standard Windows system sound (no file needed)
        # Or use winsound.PlaySound("notify.wav", winsound.SND_ASYNC) if you have a file
        threading.Thread(target=lambda: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS), daemon=True).start()
    except Exception as e:
        print(f"Sound error: {e}")

# ---------------- RESOURCE PATH (FOR EXE) ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------- DB PATH HELPER ----------------
def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "login.db")

DB_FILE = get_db_path()

# ------------------- API LOGIC (SYNCING) -------------------
def get_friends(user):
    """ Fetches friends from the Flask API instead of local DB """
    try:
        response = requests.get(f"{SERVER_URL}/get_friends/{user}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Sync error: {e}")
    return []

def add_friend_api(user, friend):
    """ Adds friend via Flask API """
    try:
        response = requests.post(f"{SERVER_URL}/add_friend", 
                                 json={"user1": user, "user2": friend}, 
                                 timeout=5)
        return response.json().get("status", "Error")
    except:
        return "Server unreachable"

# ------------------- DATABASE INIT (LOCAL CACHE) -------------------
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
        email TEXT NOT NULL
    )""")
    cursor.execute("CREATE TABLE IF NOT EXISTS session (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT)")
    # We keep messages local for now, or you can move them to API too
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

# ------------------- REGISTRATION WINDOW -------------------
def open_registration_window():
    reg_root = tk.Tk()
    reg_root.title("Coreton - Register")
    reg_root.geometry("350x500") 
    reg_root.config(bg="#1a1a1a")

    Label(reg_root, text="REGISTER", font=("Pixelify Sans", 18, "bold"), fg="#ff80ff", bg="#1a1a1a").pack(pady=10)
    
    # Input Fields
    entries = {}
    for field in ["Username", "Password", "Name", "Age", "Email"]:
        Label(reg_root, text=f"{field}:", fg="white", bg="#1a1a1a").pack()
        e = Entry(reg_root, show="*" if field == "Password" else "")
        e.pack(pady=2)
        entries[field] = e

    def register():
        u = entries["Username"].get().strip()
        p = entries["Password"].get().strip()
        n = entries["Name"].get().strip()
        a = entries["Age"].get().strip()
        e = entries["Email"].get().strip()

        if not all([u, p, n, a, e]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, e):
            messagebox.showerror("Error", "Invalid email!")
            return
        
        hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
        conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password, name, age, email) VALUES (?, ?, ?, ?, ?)", (u, hashed, n, a, e))
            cur.execute("DELETE FROM session")
            cur.execute("INSERT INTO session (username) VALUES (?)", (u,))
            conn.commit()
            
            messagebox.showinfo("Success", f"Welcome, {u}!")
            reg_root.destroy()
            home_root = tk.Tk()
            CoretonApp(home_root, u)
            home_root.mainloop()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username taken")
        finally:
            conn.close()

    Button(reg_root, text="Create Account", command=register, width=15, bg="#00ff99", font=("Pixelify Sans", 10, "bold")).pack(pady=20)
    reg_root.mainloop()

# ------------------- MAIN HOME APP CLASS -------------------
class CoretonApp:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.current_friend = None
        self.master.title(f"Coreton - {self.username}")
        self.master.geometry("900x600")
        self.master.config(bg="#1a1a1a")
        self.setup_ui()

    def setup_ui(self):
        Label(self.master, text=f"Welcome, {self.username}!", font=("Pixelify Sans", 24, "bold"), fg="#ff80ff", bg="#1a1a1a").pack(pady=10)
        main_frame = Frame(self.master, bg="#1a1a1a")
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        left_frame = Frame(main_frame, bg="#1a1a1a")
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,10))
        right_frame = Frame(main_frame, bg="#1a1a1a", width=200)
        right_frame.pack(side=RIGHT, fill=Y)

        self.chat_box = Text(left_frame, state=DISABLED, bg="#121212", fg="#00ff99", font=("Pixelify Sans", 12), wrap=WORD)
        self.chat_box.pack(fill=BOTH, expand=True)
        self.entry = Entry(left_frame, bg="#121212", fg="#00ff99", font=("Pixelify Sans", 12))
        self.entry.pack(fill=X, pady=5)
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.friends_listbox = Listbox(right_frame, bg="#121212", fg="#00ccff", font=("Pixelify Sans", 12))
        self.friends_listbox.pack(fill=BOTH, expand=True)
        self.friends_listbox.bind("<Double-Button-1>", self.open_chat)
        Button(right_frame, text="Add Friend", command=self.add_friend_ui, bg="#00ccff", fg="#121212", font=("Pixelify Sans", 12, "bold")).pack(fill=X)

        bottom = Frame(self.master, bg="#1a1a1a")
        bottom.pack(pady=10)
        Button(bottom, text="GACHA", command=lambda: gacha.open_gacha_window(), bg="#ff80ff", font=("Pixelify Sans", 14, "bold"), width=15).pack(side=LEFT, padx=10)
        Button(bottom, text="EXTENSIONS", command=lambda: apps.open_apps_window(), bg="#00ccff", font=("Pixelify Sans", 14, "bold"), width=15).pack(side=LEFT, padx=10)
        
        self.refresh_friends()

    def refresh_friends(self):
        self.friends_listbox.delete(0, END)
        # Now uses the API function
        friends = get_friends(self.username)
        for f in friends: 
            self.friends_listbox.insert(END, f)

    def add_friend_ui(self):
        friend = simpledialog.askstring("Add Friend", "Enter username:")
        if friend:
            res = add_friend_api(self.username, friend)
            messagebox.showinfo("Result", res)
            self.refresh_friends()

    def open_chat(self, event):
        selection = self.friends_listbox.curselection()
        if selection:
            self.current_friend = self.friends_listbox.get(selection[0])
            self.chat_box.config(state=NORMAL); self.chat_box.delete(1.0, END)
            conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
            cur.execute("SELECT sender, message FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY timestamp", (self.username, self.current_friend, self.current_friend, self.username))
            for s, m in cur.fetchall(): 
                self.chat_box.insert(END, f"{'You' if s == self.username else s}: {m}\n")
            conn.close(); self.chat_box.config(state=DISABLED); self.chat_box.yview(END)

    def send_message(self):
        msg = self.entry.get().strip()
        if msg and self.current_friend:
            conn = sqlite3.connect(DB_FILE); conn.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (self.username, self.current_friend, msg))
            conn.commit(); conn.close(); self.display_message(f"You: {msg}"); self.entry.delete(0, END)

    def display_message(self, msg):
        self.chat_box.config(state=NORMAL); self.chat_box.insert(END, msg + "\n"); self.chat_box.config(state=DISABLED); self.chat_box.yview(END)
        # Notification sound plays here
        if not msg.startswith("You:"):
            play_notification()

if __name__ == "__main__":
    init_db()
    open_registration_window()