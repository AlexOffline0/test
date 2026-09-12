import tkinter as tk
from tkinter import messagebox
import bcrypt
import requests
import sys
import os

import data
import home

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def login_attempt(u, p):
    try:
        res = requests.post(f"{data.SERVER_URL}/login", json={"username": u}, timeout=10)
        if res.status_code == 200:
            stored_hash = res.json().get("password")
            if isinstance(stored_hash, str): stored_hash = stored_hash.encode('utf-8')
            return bcrypt.checkpw(p.encode("utf-8"), stored_hash)
    except: return False
    return False

# --- ADVANCED UI HELPER ---
def create_hover_button(parent, text, bg, hover_bg, fg, command, font=("Segoe UI", 11, "bold"), pady=0, ipady=0, fill="x"):
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, font=font, relief="flat", cursor="hand2", activebackground=hover_bg, activeforeground=fg)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    btn.pack(fill=fill, padx=50, pady=pady, ipady=ipady)
    return btn

def start():
    root = tk.Tk()
    root.title("Coreton")
    root.geometry("350x420")
    root.config(bg="#121212")
    root.resizable(False, False)

    try: root.iconbitmap(resource_path("AppIcon.ico")) 
    except: pass

    tk.Label(root, text="Welcome Back", fg="#ffffff", bg="#121212", font=("Segoe UI Black", 22)).pack(pady=(45, 5))
    tk.Label(root, text="Log in to continue to Coreton", fg="#888888", bg="#121212", font=("Segoe UI", 10)).pack(pady=(0, 35))

    tk.Label(root, text="USERNAME", fg="#00ff99", bg="#121212", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=50)
    u_ent = tk.Entry(root, bg="#2a2a2a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 12))
    u_ent.pack(fill="x", padx=50, pady=(5, 15), ipady=8)
    
    tk.Label(root, text="PASSWORD", fg="#00ff99", bg="#121212", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=50)
    p_ent = tk.Entry(root, show="•", bg="#2a2a2a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 12))
    p_ent.pack(fill="x", padx=50, pady=(5, 30), ipady=8)

    def try_login():
        if login_attempt(u_ent.get().strip(), p_ent.get().strip()):
            user = u_ent.get().strip()
            root.destroy()
            home.open_home_window(user) 
        else: messagebox.showerror("Error", "Invalid Login")

    create_hover_button(root, "Login", bg="#00ff99", hover_bg="#00cc7a", fg="#121212", command=try_login, pady=5, ipady=6)
    create_hover_button(root, "Need an account? Register", bg="#121212", hover_bg="#1e1e1e", fg="#ff80ff", command=data.open_registration_window, font=("Segoe UI", 10, "underline"), pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    start()