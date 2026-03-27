from tkinter import *
from tkinter import simpledialog, messagebox
import sqlite3
import os
import sys
import requests
import threading

import gacha
import apps
import data # Needs this to grab the SERVER_URL

def get_db_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.getcwd(), "login.db")
    return "login.db"

DB_FILE = get_db_path()

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
        self.label = Label(self.master, text=f"Welcome, {self.username}!", font=("Pixelify Sans", 24, "bold"), fg="#ff80ff", bg="#1a1a1a")
        self.label.pack(pady=10)

        self.main_frame = Frame(self.master, bg="#1a1a1a")
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.left_frame = Frame(self.main_frame, bg="#1a1a1a")
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,10))

        self.right_frame = Frame(self.main_frame, bg="#1a1a1a", width=200)
        self.right_frame.pack(side=RIGHT, fill=Y)

        chat_label = Label(self.left_frame, text="Chat", font=("Pixelify Sans", 16, "bold"), fg="#00ff99", bg="#1a1a1a")
        chat_label.pack(anchor="w")

        chat_frame = Frame(self.left_frame, bg="#1a1a1a")
        chat_frame.pack(fill=BOTH, expand=True)

        self.chat_box = Text(chat_frame, state=DISABLED, bg="#121212", fg="#00ff99", font=("Pixelify Sans", 12), wrap=WORD)
        self.chat_box.pack(side=LEFT, fill=BOTH, expand=True)

        self.chat_scroll = Scrollbar(chat_frame, command=self.chat_box.yview)
        self.chat_scroll.pack(side=RIGHT, fill=Y)
        self.chat_box.config(yscrollcommand=self.chat_scroll.set)

        entry_frame = Frame(self.left_frame, bg="#1a1a1a")
        entry_frame.pack(fill=X, pady=5)

        self.entry = Entry(entry_frame, bg="#121212", fg="#00ff99", font=("Pixelify Sans", 12))
        self.entry.pack(side=LEFT, fill=X, expand=True, padx=(0,5))
        self.entry.bind("<Return>", lambda event: self.send_message())

        send_btn = Button(entry_frame, text="Send", command=self.send_message, bg="#00ff99", fg="#121212", font=("Pixelify Sans", 12, "bold"))
        send_btn.pack(side=RIGHT)

        friends_label = Label(self.right_frame, text="Friends", font=("Pixelify Sans", 16, "bold"), fg="#00ccff", bg="#1a1a1a")
        friends_label.pack(pady=(0,5))

        friends_frame = Frame(self.right_frame, bg="#1a1a1a")
        friends_frame.pack(fill=BOTH, expand=True)

        self.friends_listbox = Listbox(friends_frame, bg="#121212", fg="#00ccff", font=("Pixelify Sans", 12))
        self.friends_listbox.pack(side=LEFT, fill=BOTH, expand=True)

        self.friends_scroll = Scrollbar(friends_frame, command=self.friends_listbox.yview)
        self.friends_scroll.pack(side=RIGHT, fill=Y)
        self.friends_listbox.config(yscrollcommand=self.friends_scroll.set)
        self.friends_listbox.bind("<Double-Button-1>", self.open_chat)

        add_friend_btn = Button(self.right_frame, text="Add Friend", command=self.add_friend_ui, bg="#00ccff", fg="#121212", font=("Pixelify Sans", 12, "bold"))
        add_friend_btn.pack(pady=5, fill=X)

        self.refresh_friends()

        bottom_frame = Frame(self.master, bg="#1a1a1a")
        bottom_frame.pack(pady=10)

        gacha_btn = Button(bottom_frame, text="GACHA", command=self.command_gacha, bg="#ff80ff", fg="#121212", font=("Pixelify Sans", 14, "bold"), width=15)
        gacha_btn.pack(side=LEFT, padx=10)

        ext_btn = Button(bottom_frame, text="EXTENSIONS", command=self.command_ext, bg="#00ccff", fg="#121212", font=("Pixelify Sans", 14, "bold"), width=15)
        ext_btn.pack(side=LEFT, padx=10)

    # --- SERVER SYNCED LOGIC ---
    def refresh_friends(self):
        self.friends_listbox.delete(0, END)
        try:
            # Asks the Ngrok server for the friends list!
            res = requests.get(f"{data.SERVER_URL}/get_friends/{self.username}", timeout=5)
            if res.status_code == 200:
                for f in res.json(): 
                    self.friends_listbox.insert(END, f)
        except Exception as e:
            print(f"Friend Sync Error: {e}")

    def add_friend_ui(self):
        friend = simpledialog.askstring("Add Friend", "Enter username:")
        if friend:
            try:
                # Tells the server to link you two
                res = requests.post(f"{data.SERVER_URL}/add_friend", json={"user1": self.username, "user2": friend}, timeout=5)
                if res.status_code == 200:
                    messagebox.showinfo("Result", "Friend added successfully!")
                self.refresh_friends()
            except Exception as e:
                messagebox.showerror("Error", f"Could not reach server: {e}")

    def open_chat(self, event):
        selection = self.friends_listbox.curselection()
        if selection:
            self.current_friend = self.friends_listbox.get(selection[0])
            self.chat_box.config(state=NORMAL)
            self.chat_box.delete(1.0, END)
            
            # Message history is pulled locally from DB_FILE
            conn = sqlite3.connect(DB_FILE)
            conn.execute("""CREATE TABLE IF NOT EXISTS messages 
                            (id INTEGER PRIMARY KEY, sender TEXT, receiver TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sender, message FROM messages
                WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
                ORDER BY timestamp
            """, (self.username, self.current_friend, self.current_friend, self.username))
            
            for sender, message in cursor.fetchall():
                self.chat_box.insert(END, f"{'You' if sender == self.username else sender}: {message}\n")
            
            conn.close()
            self.chat_box.config(state=DISABLED)
            self.chat_box.yview(END)

    def send_message(self):
        if not self.current_friend:
            messagebox.showerror("Error", "Select a friend first!")
            return
        msg = self.entry.get().strip()
        if msg:
            # Saves sent message locally
            conn = sqlite3.connect(DB_FILE)
            conn.execute("""CREATE TABLE IF NOT EXISTS messages 
                            (id INTEGER PRIMARY KEY, sender TEXT, receiver TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            conn.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (self.username, self.current_friend, msg))
            conn.commit()
            conn.close()
            
            self.display_message(f"You: {msg}")
            self.entry.delete(0, END)

    def display_message(self, msg):
        self.chat_box.config(state=NORMAL)
        self.chat_box.insert(END, msg + "\n")
        self.chat_box.config(state=DISABLED)
        self.chat_box.yview(END)

    def command_gacha(self):
        gacha.open_gacha_window()

    def command_ext(self):
        apps.open_apps_window()

# ------------------- ENTRY POINT -------------------
def open_home_window(user):
    root = Tk()
    app = CoretonApp(root, user)
    root.mainloop()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    open_home_window(username)