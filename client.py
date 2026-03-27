import socket
import threading
from tkinter import *

HOST = "127.0.0.1"
PORT = 4040

root = Tk()
root.title("Coreton")
root.geometry("400x400")
root.config(bg="black")

# Chat box
chat_box = Text(root, state=DISABLED, width=50, height=15, bg="black", fg="blue")
chat_box.pack(pady=10)

# Input
entry = Entry(root, width=30, bg="black", fg="blue", font=("Pixelify Sans", 18, "bold"))
entry.pack(side=LEFT, padx=5, pady=5)

# Socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# ---------------- RECEIVE ----------------
def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode()
            root.after(0, display_message, msg)
        except:
            break

def display_message(msg):
    chat_box.config(state=NORMAL)
    chat_box.insert(END, msg + "\n")
    chat_box.config(state=DISABLED)
    chat_box.yview(END)

# ---------------- SEND ----------------
def send_message():
    msg = entry.get()
    if msg:
        client.send(msg.encode())
        
        # Show your own message
        display_message("You: " + msg)
        
        entry.delete(0, END)

# Button
sendbutton = Button(root, text="Send", command=send_message)
sendbutton.pack(side=LEFT)

# Start thread AFTER UI exists
threading.Thread(target=receive_messages, daemon=True).start()



root.mainloop()