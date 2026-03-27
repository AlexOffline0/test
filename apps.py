import os
import shutil
import urllib.request
import urllib.parse
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import threading
from functools import partial

UPLOAD_FOLDER = "uploads"
PORT = 8000
SERVER_URL = f"http://larita-attired-autumnally.ngrok-free.dev"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable for the listbox so functions can find it
listbox = None

# ---------------- SERVER ----------------
def start_server():
    try:
        handler = partial(SimpleHTTPRequestHandler, directory=UPLOAD_FOLDER)
        with TCPServer(("", PORT), handler) as httpd:
            print(f"Serving at {SERVER_URL}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")

# ---------------- UPLOAD ----------------
def upload_file():
    filepath = filedialog.askopenfilename()
    if not filepath: return
    
    if os.path.getsize(filepath) > 500 * 1024 * 1024:
        messagebox.showerror("Error", "File exceeds 500MB limit!")
        return
    
    shutil.copy(filepath, os.path.join(UPLOAD_FOLDER, os.path.basename(filepath)))
    refresh_files()

# ---------------- DOWNLOAD ----------------
def download_file():
    if not listbox: return
    selected = listbox.get(ACTIVE)
    if not selected:
        messagebox.showerror("Error", "No file selected")
        return
    
    save_path = filedialog.asksaveasfilename(initialfile=selected)
    if not save_path: return
    
    url = f"{SERVER_URL}/{urllib.parse.quote(selected)}"
    try:
        urllib.request.urlretrieve(url, save_path)
        messagebox.showinfo("Success", "Downloaded!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- DELETE ----------------
def delete_file():
    if not listbox: return
    selection = listbox.curselection()
    DELETE_PASSWORD = "7AmS|CJ<C@06"
    
    if not selection:
        messagebox.showerror("Error", "No file selected")
        return

    selected = listbox.get(selection[0])
    password = simpledialog.askstring("Authentication", "Enter delete password:", show="*")
    
    if password != DELETE_PASSWORD:
        messagebox.showerror("Error", "Unauthorized!")
        return

    if messagebox.askyesno("Confirm Delete", f"Delete '{selected}'?"):
        try:
            file_path = os.path.join(UPLOAD_FOLDER, selected)
            if os.path.exists(file_path):
                os.remove(file_path)
                refresh_files()
                messagebox.showinfo("Success", "File deleted!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ---------------- UI REFRESH ----------------
def refresh_files():
    if listbox:
        listbox.delete(0, END)
        for file in os.listdir(UPLOAD_FOLDER):
            listbox.insert(END, file)

# ---------------- MAIN WINDOW FUNCTION ----------------
def open_apps_window():
    global listbox
    
    # Use Toplevel so it opens ASIDE the main app, not replacing it
    app_win = Toplevel()
    app_win.title("Coreton Extensions")
    app_win.config(bg="black")
    app_win.geometry("400x500")

    Button(app_win, text="Upload File", font=("Pixelify Sans", 18, "bold"), command=upload_file).pack(pady=5)
    Button(app_win, text="Download Selected", command=download_file).pack(pady=5)
    Button(app_win, text="Delete Selected", command=delete_file).pack(pady=5)

    listbox = Listbox(app_win, width=50)
    listbox.config(bg="grey", font=("Pixelify Sans", 9, "bold"))
    listbox.pack(pady=10)

    Label(app_win, text=f"Server: {SERVER_URL}", fg="white", bg="black").pack()

    refresh_files()
    
    # Start server only if not already running
    if not any(t.name == "FileServerThread" for t in threading.enumerate()):
        threading.Thread(target=start_server, daemon=True, name="FileServerThread").start()

# ---------------- THE SHIELD ----------------
if __name__ == "__main__":
    # This only runs if you run apps.py directly
    root = Tk()
    Button(root, text="Open Apps", command=open_apps_window).pack()
    root.mainloop()