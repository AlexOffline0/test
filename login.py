import tkinter as tk
from tkinter import messagebox
import sqlite3
import bcrypt
import os
import sys
import requests # Added for syncing
import data 

# ---------------- LOGIN LOGIC (SERVER SYNC) ----------------
def login_user(username, password):
    try:
        # Ask the Flask server for this user's password hash
        response = requests.post(f"{data.SERVER_URL}/login", 
                                 json={"username": username}, 
                                 timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            stored_hash = result.get("password")
            
            # Convert string from JSON back to bytes for bcrypt
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
                
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                return True
        return False
    except Exception as e:
        messagebox.showerror("Connection Error", "Could not connect to the server. Is Ngrok running?")
        return False

# ---------------- GUI (NO UI CHANGES) ----------------
def open_login_window():
    root = tk.Tk()
    root.title("Coreton")
    root.geometry("300x230") # Adjusted slightly to fit the Register button
    root.resizable(False, False)
    root.config(bg="black")

    # Keep your exact UI elements
    tk.Label(root, text="Username:", bg="black", fg="green", font=("Pixelify Sans", 9, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_username = tk.Entry(root, bg="black", fg="green", font=("Pixelify Sans", 9, "bold"))
    entry_username.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Password:", bg="black", fg="green", font=("Pixelify Sans", 9, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_password = tk.Entry(root, show="*", bg="black", fg="green", font=("Pixelify Sans", 9, "bold"))
    entry_password.grid(row=1, column=1, padx=5, pady=5)

    def on_login_click():
        username = entry_username.get().strip()
        password = entry_password.get().strip()

        if login_user(username, password):
            root.destroy()
            # Launch the Home screen from data.py
            h_root = tk.Tk()
            data.CoretonApp(h_root, username)
            h_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    # Your Login Button
    tk.Button(
        root,
        text="Login",
        width=20,
        command=on_login_click,
        bg="black",
        fg="green",
        font=("Pixelify Sans", 9, "bold")
    ).grid(row=2, column=0, columnspan=2, pady=10)

    # Register Button added to match login.py flow
    tk.Button(
        root,
        text="Register",
        width=20,
        command=lambda: [root.destroy(), data.open_registration_window()],
        bg="black",
        fg="#ff80ff",
        font=("Pixelify Sans", 9, "bold")
    ).grid(row=3, column=0, columnspan=2, pady=5)

    root.mainloop()

if __name__ == "__main__":
    open_login_window()