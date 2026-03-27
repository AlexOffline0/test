import tkinter as tk
from tkinter import messagebox, BOTH, LEFT, RIGHT, Y, X, NORMAL, DISABLED, END
import requests
import os, sys, threading, sqlite3
import gacha, apps 

SERVER_URL = "https://larita-attired-autumnally.ngrok-free.dev".strip().rstrip('/')

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "login.db")

def open_registration_window():
    reg_root = tk.Tk()
    reg_root.title("Register")
    reg_root.geometry("300x400")
    reg_root.config(bg="#1a1a1a")

    tk.Label(reg_root, text="Username:", fg="white", bg="#1a1a1a").pack()
    ent_u = tk.Entry(reg_root); ent_u.pack(pady=2)

    tk.Label(reg_root, text="Password:", fg="white", bg="#1a1a1a").pack()
    ent_p = tk.Entry(reg_root, show="*"); ent_p.pack(pady=2)

    tk.Label(reg_root, text="Name:", fg="white", bg="#1a1a1a").pack()
    ent_n = tk.Entry(reg_root); ent_n.pack(pady=2)

    tk.Label(reg_root, text="Age:", fg="white", bg="#1a1a1a").pack()
    ent_a = tk.Entry(reg_root); ent_a.pack(pady=2)

    tk.Label(reg_root, text="Email:", fg="white", bg="#1a1a1a").pack()
    ent_e = tk.Entry(reg_root); ent_e.pack(pady=2)

    def do_register():
        payload = {
            "username": ent_u.get().strip(),
            "password": ent_p.get().strip(),
            "name": ent_n.get().strip(),
            "age": ent_a.get().strip(),
            "email": ent_e.get().strip()
        }
        
        if not payload["username"] or not payload["password"]:
            return messagebox.showerror("Error", "Username and Password cannot be empty")

        try:
            res = requests.post(f"{SERVER_URL}/register", json=payload, timeout=10)
            if res.status_code == 200:
                messagebox.showinfo("Success", "Registered successfully!")
                reg_root.destroy()
            else:
                messagebox.showerror("Error", res.json().get("error", "Failed"))
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    tk.Button(reg_root, text="Create Account", command=do_register, bg="#00ff99").pack(pady=20)
    reg_root.mainloop()

# --- KEEP YOUR CoretonApp CLASS HERE EXACTLY AS IT WAS ---
# (I am leaving it out to save space, but don't delete it from your file!)