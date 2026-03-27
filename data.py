import tkinter as tk
from tkinter import *
from tkinter import simpledialog, messagebox
import sqlite3
import os
import sys
import bcrypt
import re
import requests
import threading

# Import your sub-modules
import gacha 
import apps 

# ---------------- CONFIG (UPDATE THIS URL!) ----------------
SERVER_URL = "https://your-ngrok-url.ngrok-free.app"

# ---------------- RESOURCE PATH ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ---------------- DB PATH (FOR LOCAL MESSAGES) ----------------
def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "login.db")

DB_FILE = get_db_path()

# ------------------- API SYNC LOGIC -------------------
def get_friends(user):
    try:
        response = requests.get(f"{SERVER_URL}/get_friends/{user}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        print("Server offline: Could not fetch friends.")
    return []

def add_friend_api(user, friend):
    try:
        response = requests.post(f"{SERVER_URL}/add_friend", 
                                 json={"user1": user, "user2": friend}, timeout=5)
        if response.status_code == 200:
            return response.json().get("status")
        return response.json().get("error", "Error")
    except:
        return "Server unreachable"

# ------------------- MAIN HOME APP CLASS -------------------
class CoretonApp:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.current_friend = None
        self.master.title(f"Coreton - {self.username}")
        self.master.geometry("900x600")
        self.master.config(bg="#1a1a1a")

        # Fix for the iconphoto error
        try:
            icon_p = resource_path("images/icon.png")
            if os.path.exists(icon_p):
                img = tk.PhotoImage(file=icon_p)
                self.master.wm_iconphoto(True, img)
        except: pass

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
        friends = get_friends(self.username)
        for f in friends: self.friends_listbox.insert(END, f)

    def add_friend_ui(self):
        friend = simpledialog.askstring("Add Friend", "Enter username:")
        if friend:
            result = add_friend_api(self.username, friend)
            messagebox.showinfo("Result", result)
            self.refresh_friends()

    def open_chat(self, event):
        selection = self.friends_listbox.curselection()
        if selection:
            self.current_friend = self.friends_listbox.get(selection[0])
            self.chat_box.config(state=NORMAL); self.chat_box.delete(1.0, END)
            conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
            cur.execute("SELECT sender, message FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY timestamp", (self.username, self.current_friend, self.current_friend, self.username))
            for s, m in cur.fetchall(): self.chat_box.insert(END, f"{'You' if s == self.username else s}: {m}\n")
            conn.close(); self.chat_box.config(state=DISABLED); self.chat_box.yview(END)

    def send_message(self):
        msg = self.entry.get().strip()
        if msg and self.current_friend:
            conn = sqlite3.connect(DB_FILE); conn.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (self.username, self.current_friend, msg))
            conn.commit(); conn.close(); self.display_message(f"You: {msg}"); self.entry.delete(0, END)

    def display_message(self, msg):
        self.chat_box.config(state=NORMAL); self.chat_box.insert(END, msg + "\n"); self.chat_box.config(state=DISABLED); self.chat_box.yview(END)
        if not msg.startswith("You:"):
            try:
                import winsound
                threading.Thread(target=lambda: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS), daemon=True).start()
            except: pass