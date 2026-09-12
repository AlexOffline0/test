from tkinter import *
from tkinter import simpledialog, messagebox, filedialog
import sys
import os
import requests
import base64
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw

import gacha
import apps
import data  

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_hover_button(parent, text, bg, hover_bg, fg, command, width=None, font=("Segoe UI", 10, "bold"), side=None, padx=0, pady=0, ipady=0, fill=None):
    btn = Button(parent, text=text, command=command, bg=bg, fg=fg, font=font, relief="flat", cursor="hand2", activebackground=hover_bg, activeforeground=fg)
    if width: btn.config(width=width)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    btn.pack(side=side, padx=padx, pady=pady, ipady=ipady, fill=fill)
    return btn

def make_circle_image(img):
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    img.putalpha(mask)
    return img

class CoretonApp:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.current_friend = None
        self.chat_loop_id = None 
        self.group_chat_loop_id = None

        self.master.title(f"Coreton - {self.username}")
        self.master.geometry("1000x650")
        self.master.config(bg="#121212")

        try: self.master.iconbitmap(default=resource_path("AppIcon.ico"))
        except: pass

        self.setup_ui()

    def setup_ui(self):
        # --- TOP NAVIGATION BAR ---
        header_frame = Frame(self.master, bg="#121212")
        header_frame.pack(fill=X, padx=25, pady=(20, 15))
        
        Label(header_frame, text="CORETON", font=("Segoe UI Black", 22), fg="#ffffff", bg="#121212").pack(side=LEFT)
        
        self.user_profile_lbl = Label(header_frame, text=f"@{self.username}", font=("Segoe UI", 12, "bold"), fg="#00ff99", bg="#121212", cursor="hand2")
        self.user_profile_lbl.pack(side=RIGHT, pady=5, padx=(15, 0))
        self.user_profile_lbl.bind("<Button-1>", lambda e: self.open_profile_popup())
        self.user_profile_lbl.bind("<Enter>", lambda e: self.user_profile_lbl.config(fg="#ffffff")) 
        self.user_profile_lbl.bind("<Leave>", lambda e: self.user_profile_lbl.config(fg="#00ff99"))

        create_hover_button(header_frame, "Extensions", bg="#1e1e1e", hover_bg="#2a2a2a", fg="#ffffff", command=self.command_ext, side=RIGHT, padx=5, ipady=4, width=12)
        create_hover_button(header_frame, "Gacha", bg="#1e1e1e", hover_bg="#2a2a2a", fg="#ff80ff", command=self.command_gacha, side=RIGHT, padx=5, ipady=4, width=10)
        create_hover_button(header_frame, "🔍 Discover Groups", bg="#00ccff", hover_bg="#00b3e6", fg="#121212", command=self.open_groups_explorer, side=RIGHT, padx=15, ipady=4, width=18)

        self.main_frame = Frame(self.master, bg="#121212")
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 25)) 

        # --- LEFT SIDE: DM CHAT ---
        self.left_frame = Frame(self.main_frame, bg="#1e1e1e")
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0,15))

        chat_header = Frame(self.left_frame, bg="#252525")
        chat_header.pack(fill=X)
        self.chat_title = Label(chat_header, text="Select a friend to start chatting", font=("Segoe UI", 12, "bold"), fg="#888888", bg="#252525", pady=12)
        self.chat_title.pack(anchor="w", padx=20)

        chat_inner_frame = Frame(self.left_frame, bg="#1e1e1e")
        chat_inner_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        self.chat_box = Text(chat_inner_frame, state=DISABLED, bg="#1e1e1e", font=("Segoe UI", 11), wrap=WORD, relief="flat", borderwidth=0, highlightthickness=0)
        self.chat_box.pack(side=LEFT, fill=BOTH, expand=True)
        self.chat_box.tag_configure("me", justify="right", foreground="#00ff99", font=("Segoe UI", 11, "bold"))
        self.chat_box.tag_configure("them", justify="left", foreground="#ffffff", font=("Segoe UI", 11))

        self.chat_scroll = Scrollbar(chat_inner_frame, command=self.chat_box.yview)
        self.chat_scroll.pack(side=RIGHT, fill=Y)
        self.chat_box.config(yscrollcommand=self.chat_scroll.set)

        entry_frame = Frame(self.left_frame, bg="#1e1e1e")
        entry_frame.pack(fill=X, padx=20, pady=(0, 20))
        self.entry = Entry(entry_frame, bg="#2a2a2a", fg="white", insertbackground="white", font=("Segoe UI", 12), relief="flat", borderwidth=0)
        self.entry.pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0,10))
        self.entry.bind("<Return>", lambda event: self.send_message())
        create_hover_button(entry_frame, "Send", bg="#00ff99", hover_bg="#00cc7a", fg="#121212", command=self.send_message, side=RIGHT, fill=Y, padx=10)

        # --- RIGHT SIDE: FRIENDS & GROUPS ---
        self.right_frame = Frame(self.main_frame, bg="#1e1e1e", width=260)
        self.right_frame.pack(side=RIGHT, fill=Y)
        self.right_frame.pack_propagate(False)

        Label(self.right_frame, text="FRIENDS", font=("Segoe UI", 10, "bold"), fg="#888888", bg="#252525", pady=12).pack(fill=X)
        self.friends_listbox = Listbox(self.right_frame, bg="#1e1e1e", fg="#ffffff", font=("Segoe UI", 12, "bold"), relief="flat", borderwidth=0, highlightthickness=0, selectbackground="#333333", selectforeground="#00ff99", activestyle="none", cursor="hand2", height=8)
        self.friends_listbox.pack(fill=X, padx=10, pady=5)
        self.friends_listbox.bind("<Double-Button-1>", self.open_chat)
        self.friends_listbox.bind("<Button-3>", self.show_friend_menu)
        create_hover_button(self.right_frame, "➕ Add Friend", bg="#333333", hover_bg="#444444", fg="#ffffff", command=self.add_friend_ui, fill=X, padx=20, pady=(0, 10), ipady=4)

        Label(self.right_frame, text="MY GROUPS", font=("Segoe UI", 10, "bold"), fg="#888888", bg="#252525", pady=12).pack(fill=X)
        self.groups_listbox = Listbox(self.right_frame, bg="#1e1e1e", fg="#ffffff", font=("Segoe UI", 12, "bold"), relief="flat", borderwidth=0, highlightthickness=0, selectbackground="#333333", selectforeground="#00ccff", activestyle="none", cursor="hand2")
        self.groups_listbox.pack(fill=BOTH, expand=True, padx=10, pady=5)
        self.groups_listbox.bind("<Double-Button-1>", self.open_group_server) 

        self.refresh_sidebar()

    def refresh_sidebar(self):
        self.friends_listbox.delete(0, END)
        try:
            res = requests.get(f"{data.SERVER_URL}/get_friends/{self.username}", timeout=5)
            if res.status_code == 200:
                for f in res.json(): self.friends_listbox.insert(END, f"   {f}")
        except: pass

        self.groups_listbox.delete(0, END)
        try:
            res = requests.get(f"{data.SERVER_URL}/get_my_groups/{self.username}", timeout=5)
            if res.status_code == 200:
                for g in res.json(): 
                    icon = "🔥 " if g['is_campfire'] else "   "
                    self.groups_listbox.insert(END, f"{icon}{g['name']}")
        except: pass

    # -------------------------------------------------------------
    # GROUPS EXPLORER & CAMPFIRE CREATION
    # -------------------------------------------------------------
    def open_groups_explorer(self):
        grp_win = Toplevel(self.master)
        grp_win.title("Discover Groups")
        grp_win.geometry("480x600")
        grp_win.config(bg="#181818")
        grp_win.grab_set()

        Label(grp_win, text="Discover Groups", font=("Segoe UI Black", 18), fg="#ffffff", bg="#181818").pack(pady=(20, 5))
        
        search_frame = Frame(grp_win, bg="#181818")
        search_frame.pack(fill=X, padx=30, pady=10)
        search_entry = Entry(search_frame, bg="#2a2a2a", fg="white", insertbackground="white", font=("Segoe UI", 11), relief="flat")
        search_entry.pack(side=LEFT, fill=X, expand=True, ipady=8, padx=(0,10))
        
        list_frame = Frame(grp_win, bg="#1e1e1e")
        list_frame.pack(fill=BOTH, expand=True, padx=30, pady=10)
        
        grp_listbox = Listbox(list_frame, bg="#1e1e1e", fg="#ffffff", font=("Segoe UI", 12, "bold"), relief="flat", borderwidth=0, highlightthickness=0, selectbackground="#333333", selectforeground="#00ccff", activestyle="none", cursor="hand2")
        grp_listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=15, pady=10)
        
        all_groups = []

        def load_groups():
            grp_listbox.delete(0, END)
            try:
                res = requests.get(f"{data.SERVER_URL}/get_all_groups", timeout=5)
                if res.status_code == 200:
                    nonlocal all_groups
                    all_groups = res.json()
                    for g in all_groups: 
                        icon = "🔥 " if g['is_campfire'] else "   "
                        grp_listbox.insert(END, f"{icon}{g['name']}")
            except: pass

        def search_groups(event=None):
            query = search_entry.get().strip().lower()
            grp_listbox.delete(0, END)
            for g in all_groups:
                if query in g['name'].lower(): 
                    icon = "🔥 " if g['is_campfire'] else "   "
                    grp_listbox.insert(END, f"{icon}{g['name']}")

        search_entry.bind("<KeyRelease>", search_groups)
        load_groups()

        btn_frame = Frame(grp_win, bg="#181818")
        btn_frame.pack(fill=X, padx=30, pady=(10, 25))

        def join_selected():
            selection = grp_listbox.curselection()
            if not selection: return
            grp_name = grp_listbox.get(selection[0]).replace("🔥 ", "").strip()
            try:
                res = requests.post(f"{data.SERVER_URL}/join_group", json={"group_name": grp_name, "username": self.username}, timeout=5)
                if res.status_code == 200:
                    messagebox.showinfo("Success", f"Joined {grp_name}!", parent=grp_win)
                    self.refresh_sidebar()
                else: messagebox.showerror("Error", "Could not join group.", parent=grp_win)
            except: pass

        create_hover_button(btn_frame, "Join Group", bg="#00ccff", hover_bg="#00b3e6", fg="#121212", command=join_selected, side=LEFT, fill=X, expand=True, padx=(0,5), ipady=8)
        
        # HERE IS THE BUTTON INSIDE THE DISCOVER TAB
        create_hover_button(btn_frame, "➕ Create Group", bg="#333333", hover_bg="#444444", fg="#ffffff", command=self.open_create_group_ui, side=RIGHT, fill=X, expand=True, padx=(5,0), ipady=8)

    def open_create_group_ui(self):
        new_grp = Toplevel(self.master)
        new_grp.title("Create a Group")
        new_grp.geometry("380x600")
        new_grp.config(bg="#181818")
        new_grp.grab_set()

        self.new_group_b64 = None
        img_lbl = Label(new_grp, bg="#181818")
        img_lbl.pack(pady=(25, 10))

        def pick_group_icon():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                img = Image.open(path).resize((100, 100), Image.Resampling.LANCZOS)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                self.new_group_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                tk_img = ImageTk.PhotoImage(make_circle_image(img))
                new_grp.tk_avatar = tk_img 
                img_lbl.config(image=tk_img)

        create_hover_button(new_grp, "Upload Group Icon", bg="#2a2a2a", hover_bg="#3a3a3a", fg="#ffffff", command=pick_group_icon, ipady=4, padx=15, pady=(0, 15))

        Label(new_grp, text="GROUP NAME", fg="#888888", bg="#181818", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=30)
        name_ent = Entry(new_grp, bg="#2a2a2a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 12))
        name_ent.pack(fill=X, padx=30, pady=(5, 10), ipady=6)

        Label(new_grp, text="GROUP BIO", fg="#888888", bg="#181818", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=30)
        bio_ent = Text(new_grp, bg="#2a2a2a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 11), height=3)
        bio_ent.pack(fill=X, padx=30, pady=(5, 15), ipady=6)

        Label(new_grp, text="GROUP TYPE (DURATION)", fg="#ff6600", bg="#181818", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=30)
        dur_var = IntVar(value=0)
        
        Radiobutton(new_grp, text="Permanent (Normal Server)", variable=dur_var, value=0, bg="#181818", fg="white", selectcolor="#2a2a2a", activebackground="#181818", activeforeground="white", cursor="hand2", font=("Segoe UI", 10)).pack(anchor="w", padx=30, pady=2)
        Radiobutton(new_grp, text="🔥 Campfire (Self-Deletes in 1 Hour)", variable=dur_var, value=1, bg="#181818", fg="#ffcc00", selectcolor="#2a2a2a", activebackground="#181818", activeforeground="#ffcc00", cursor="hand2", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=30, pady=2)
        Radiobutton(new_grp, text="🔥 Campfire (Self-Deletes in 24 Hours)", variable=dur_var, value=24, bg="#181818", fg="#ffcc00", selectcolor="#2a2a2a", activebackground="#181818", activeforeground="#ffcc00", cursor="hand2", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=30, pady=2)

        def save_group():
            payload = {
                "name": name_ent.get().strip(),
                "description": bio_ent.get(1.0, END).strip(),
                "creator": self.username,
                "profile_pic": self.new_group_b64,
                "duration_hours": dur_var.get()
            }
            try:
                res = requests.post(f"{data.SERVER_URL}/create_group", json=payload, timeout=5)
                if res.status_code == 200:
                    messagebox.showinfo("Success", "Group Created!", parent=new_grp)
                    self.refresh_sidebar()
                    new_grp.destroy()
                else: messagebox.showerror("Error", "Name taken.", parent=new_grp)
            except: pass

        create_hover_button(new_grp, "Create Group", bg="#00ccff", hover_bg="#00b3e6", fg="#121212", command=save_group, fill=X, padx=30, pady=(15,0), ipady=8)

    # -------------------------------------------------------------
    # INSIDE A GROUP SERVER (ROLES, MODERATION, & CHAT)
    # -------------------------------------------------------------
    def open_group_server(self, event):
        sel = self.groups_listbox.curselection()
        if not sel: return
        group_name = self.groups_listbox.get(sel[0]).replace("🔥 ", "").strip()

        my_role = ["member"]
        try:
            res = requests.get(f"{data.SERVER_URL}/get_role/{group_name}/{self.username}", timeout=5)
            if res.status_code == 200: my_role[0] = res.json().get("role", "member")
        except: pass

        srv_win = Toplevel(self.master)
        srv_win.title(f"Server - {group_name}")
        srv_win.geometry("900x600")
        srv_win.config(bg="#121212")

        chan_frame = Frame(srv_win, bg="#1a1a1a", width=220)
        chan_frame.pack(side=LEFT, fill=Y)
        chan_frame.pack_propagate(False)

        Label(chan_frame, text=group_name.upper(), font=("Segoe UI Black", 14), fg="#ffffff", bg="#1a1a1a", pady=15).pack(fill=X)
        
        c_list = Listbox(chan_frame, bg="#1a1a1a", fg="#a0a0a0", font=("Segoe UI", 12, "bold"), relief="flat", borderwidth=0, highlightthickness=0, selectbackground="#333333", selectforeground="#ffffff", activestyle="none", cursor="hand2")
        c_list.pack(fill=BOTH, expand=True, padx=10, pady=5)

        def add_channel():
            if my_role[0] not in ["owner", "mod"]:
                messagebox.showerror("Unauthorized", "Only Owners or Mods can create channels.", parent=srv_win)
                return
            c_name = simpledialog.askstring("New Channel", "Channel Name (no spaces):", parent=srv_win)
            if c_name:
                c_name = c_name.strip().lower().replace(" ", "-")
                try:
                    requests.post(f"{data.SERVER_URL}/create_channel", json={"group_name": group_name, "channel_name": c_name}, timeout=5)
                    load_channels()
                except: pass

        if my_role[0] in ["owner", "mod"]:
            create_hover_button(chan_frame, "+ Create Channel", bg="#2a2a2a", hover_bg="#3a3a3a", fg="#ffffff", command=add_channel, fill=X, padx=15, pady=15, ipady=6)

        chat_frame = Frame(srv_win, bg="#1e1e1e")
        chat_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        header = Frame(chat_frame, bg="#252525")
        header.pack(fill=X)
        c_title = Label(header, text="# general", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#252525", pady=12)
        c_title.pack(anchor="w", padx=20)

        box_frame = Frame(chat_frame, bg="#1e1e1e")
        box_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        c_box = Text(box_frame, state=DISABLED, bg="#1e1e1e", font=("Segoe UI", 11), wrap=WORD, relief="flat", borderwidth=0, highlightthickness=0)
        c_box.pack(side=LEFT, fill=BOTH, expand=True)
        
        c_box.tag_configure("msg", foreground="#ffffff", font=("Segoe UI", 11))
        c_box.tag_configure("owner", foreground="#ffd700", font=("Segoe UI", 11, "bold")) 
        c_box.tag_configure("mod", foreground="#ff4444", font=("Segoe UI", 11, "bold"))   
        c_box.tag_configure("member", foreground="#00ccff", font=("Segoe UI", 11, "bold"))

        scroll = Scrollbar(box_frame, command=c_box.yview)
        scroll.pack(side=RIGHT, fill=Y)
        c_box.config(yscrollcommand=scroll.set)

        def show_context_menu(event):
            if my_role[0] not in ["owner", "mod"]: return
            index = c_box.index(f"@{event.x},{event.y}")
            tags = c_box.tag_names(index)
            m_id = None
            for t in tags:
                if t.startswith("msg_"):
                    m_id = t.split("_")[1]
                    break
            if m_id:
                menu = Menu(srv_win, tearoff=0, bg="#2a2a2a", fg="white", activebackground="#ff4444", activeforeground="white", relief="flat", borderwidth=0)
                menu.add_command(label="🗑️ Delete Message", command=lambda: delete_msg(m_id))
                menu.tk_popup(event.x_root, event.y_root)

        def delete_msg(m_id):
            try:
                requests.post(f"{data.SERVER_URL}/delete_message", json={"group_name": group_name, "message_id": m_id, "requester": self.username}, timeout=5)
                refresh_g_chat()
            except: pass

        c_box.bind("<Button-3>", show_context_menu)

        ent_frame = Frame(chat_frame, bg="#1e1e1e")
        ent_frame.pack(fill=X, padx=20, pady=(0, 20))
        c_ent = Entry(ent_frame, bg="#2a2a2a", fg="white", insertbackground="white", font=("Segoe UI", 12), relief="flat")
        c_ent.pack(side=LEFT, fill=X, expand=True, ipady=10, padx=(0,10))
        
        current_channel = ["general"]

        def send_g_msg(e=None):
            msg = c_ent.get().strip()
            if msg and current_channel[0]:
                try:
                    requests.post(f"{data.SERVER_URL}/send_group_message", json={"group_name": group_name, "channel_name": current_channel[0], "sender": self.username, "message": msg}, timeout=5)
                    c_ent.delete(0, END)
                    refresh_g_chat()
                except: pass
        
        c_ent.bind("<Return>", send_g_msg)
        create_hover_button(ent_frame, "Send", bg="#00ccff", hover_bg="#00b3e6", fg="#121212", command=send_g_msg, side=RIGHT, fill=Y, padx=10)

        def load_channels():
            c_list.delete(0, END)
            try:
                res = requests.get(f"{data.SERVER_URL}/get_channels/{group_name}", timeout=5)
                if res.status_code == 200:
                    for c in res.json(): c_list.insert(END, f" # {c}")
            except: pass

        def select_channel(event):
            sel = c_list.curselection()
            if sel:
                current_channel[0] = c_list.get(sel[0]).strip().replace("# ", "")
                c_title.config(text=f"# {current_channel[0]}")
                refresh_g_chat()

        c_list.bind("<Double-Button-1>", select_channel)

        def refresh_g_chat():
            if not current_channel[0]: return
            try:
                res = requests.get(f"{data.SERVER_URL}/get_group_messages/{group_name}/{current_channel[0]}", timeout=5)
                if res.status_code == 200:
                    c_box.config(state=NORMAL)
                    c_box.delete(1.0, END)
                    for msg_data in res.json():
                        m_id = msg_data["id"]
                        sender = msg_data["sender"]
                        msg = msg_data["message"]
                        role = msg_data["role"]
                        
                        id_tag = f"msg_{m_id}"
                        prefix = "👑 " if role == "owner" else "🛡️ " if role == "mod" else ""
                        
                        c_box.insert(END, f"{prefix}{sender}\n", (role, id_tag))
                        c_box.insert(END, f"{msg}\n\n", ("msg", id_tag))
                        
                    c_box.config(state=DISABLED)
                    c_box.yview(END)
            except: pass
            
            if self.group_chat_loop_id: srv_win.after_cancel(self.group_chat_loop_id)
            self.group_chat_loop_id = srv_win.after(3000, refresh_g_chat)

        load_channels()
        refresh_g_chat()

        srv_win.protocol("WM_DELETE_WINDOW", lambda: [srv_win.after_cancel(self.group_chat_loop_id) if self.group_chat_loop_id else None, srv_win.destroy()])

    # -------------------------------------------------------------
    # DM CHAT LOGIC & RIGHT-CLICK MENUS
    # -------------------------------------------------------------
    def add_friend_ui(self):
        friend = simpledialog.askstring("Add Friend", "Enter username:")
        if friend:
            try:
                res = requests.post(f"{data.SERVER_URL}/add_friend", json={"user1": self.username, "user2": friend.strip()}, timeout=5)
                if res.status_code == 200: self.refresh_sidebar()
            except: pass

    def show_friend_menu(self, event):
        index = self.friends_listbox.nearest(event.y)
        if index < 0: return
        self.friends_listbox.selection_clear(0, END)
        self.friends_listbox.selection_set(index)
        friend_username = self.friends_listbox.get(index).strip()

        menu = Menu(self.master, tearoff=0, bg="#2a2a2a", fg="white", activebackground="#444444", activeforeground="white", relief="flat", borderwidth=0)
        menu.add_command(label="👤 View Profile", command=lambda: self.view_friend_profile_by_name(friend_username))
        menu.add_separator()
        menu.add_command(label="❌ Unfriend", command=lambda: self.remove_friend(friend_username), foreground="#ff4444")
        menu.tk_popup(event.x_root, event.y_root)

    def remove_friend(self, friend_username):
        if messagebox.askyesno("Unfriend", f"Are you sure you want to remove @{friend_username}?", parent=self.master):
            try:
                requests.post(f"{data.SERVER_URL}/remove_friend", json={"user1": self.username, "user2": friend_username}, timeout=5)
                self.refresh_sidebar()
                if self.current_friend == friend_username:
                    self.current_friend = None
                    self.chat_title.config(text="Select a friend to start chatting")
                    self.chat_box.config(state=NORMAL)
                    self.chat_box.delete(1.0, END)
                    self.chat_box.config(state=DISABLED)
            except: pass

    def view_friend_profile_by_name(self, friend_username):
        view_win = Toplevel(self.master)
        view_win.title(f"{friend_username}'s Profile")
        view_win.geometry("320x450")
        view_win.config(bg="#181818")
        try:
            res = requests.get(f"{data.SERVER_URL}/get_profile/{friend_username}", timeout=5)
            if res.status_code == 200:
                prof_data = res.json()
                img_label = Label(view_win, bg="#181818"); img_label.pack(pady=(30, 15))
                if prof_data.get("profile_pic"):
                    img_data = base64.b64decode(prof_data["profile_pic"])
                    img = Image.open(BytesIO(img_data)).resize((120, 120), Image.Resampling.LANCZOS)
                    view_win.tk_avatar = ImageTk.PhotoImage(make_circle_image(img)) 
                    img_label.config(image=view_win.tk_avatar)
                else: Label(view_win, text="No Avatar", fg="#555555", bg="#2a2a2a", width=14, height=7).pack(pady=(30, 15))
                Label(view_win, text=prof_data.get("name") or friend_username, fg="#ffffff", bg="#181818", font=("Segoe UI", 20, "bold")).pack()
                Label(view_win, text=f"@{friend_username}", fg="#00ff99", bg="#181818", font=("Segoe UI", 11)).pack(pady=(0,20))
                Label(view_win, text=prof_data.get("bio") or "No bio available.", fg="#cccccc", bg="#202020", font=("Segoe UI", 11), wraplength=280).pack(fill=BOTH, expand=True, padx=20, pady=(0, 20), ipady=15)
        except: pass

    def open_profile_popup(self):
        prof_win = Toplevel(self.master)
        prof_win.title("Edit Profile")
        prof_win.geometry("350x520")
        prof_win.config(bg="#181818")
        self.current_b64_image = None
        self.profile_image_label = Label(prof_win, bg="#181818")
        self.profile_image_label.pack(pady=(25, 10))

        def pick_avatar():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                img = Image.open(path).resize((120, 120), Image.Resampling.LANCZOS)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                self.current_b64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                prof_win.tk_avatar = ImageTk.PhotoImage(make_circle_image(img)) 
                self.profile_image_label.config(image=prof_win.tk_avatar)

        create_hover_button(prof_win, "Change Avatar", bg="#2a2a2a", hover_bg="#3a3a3a", fg="#ffffff", command=pick_avatar, ipady=4, padx=15, pady=(0, 20))
        Label(prof_win, text="DISPLAY NAME", fg="#888888", bg="#181818", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=30)
        name_entry = Entry(prof_win, bg="#2a2a2a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 12))
        name_entry.pack(fill=X, padx=30, pady=(5, 20), ipady=6)
        Label(prof_win, text="ABOUT ME", fg="#888888", bg="#181818", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=30)
        bio_text = Text(prof_win, bg="#2a2a2a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 11), height=5)
        bio_text.pack(fill=X, padx=30, pady=(5, 25), ipady=6)

        try:
            res = requests.get(f"{data.SERVER_URL}/get_profile/{self.username}", timeout=5)
            if res.status_code == 200:
                prof_data = res.json()
                if prof_data.get("name"): name_entry.insert(0, prof_data["name"])
                if prof_data.get("bio"): bio_text.insert(1.0, prof_data["bio"])
                if prof_data.get("profile_pic"):
                    self.current_b64_image = prof_data["profile_pic"]
                    img_data = base64.b64decode(self.current_b64_image)
                    prof_win.tk_avatar = ImageTk.PhotoImage(make_circle_image(Image.open(BytesIO(img_data)))) 
                    self.profile_image_label.config(image=prof_win.tk_avatar)
        except: pass
        
        def save_changes():
            payload = {"username": self.username, "name": name_entry.get().strip(), "bio": bio_text.get(1.0, END).strip(), "profile_pic": self.current_b64_image}
            try:
                requests.post(f"{data.SERVER_URL}/update_profile", json=payload, timeout=5)
                prof_win.destroy()
            except: pass

        create_hover_button(prof_win, "Save Changes", bg="#00ff99", hover_bg="#00cc7a", fg="#121212", command=save_changes, fill=X, padx=30, ipady=8)

    def open_chat(self, event):
        selection = self.friends_listbox.curselection()
        if selection:
            self.current_friend = self.friends_listbox.get(selection[0]).strip()
            self.chat_title.config(text=f"@{self.current_friend}")
            self.refresh_chat_loop()

    def refresh_chat_loop(self):
        if not self.current_friend: return
        try:
            res = requests.get(f"{data.SERVER_URL}/get_messages/{self.username}/{self.current_friend}", timeout=5)
            if res.status_code == 200:
                self.chat_box.config(state=NORMAL)
                self.chat_box.delete(1.0, END)
                for sender, message in res.json():
                    if sender == self.username: self.chat_box.insert(END, f"{message}\n\n", "me")
                    else: self.chat_box.insert(END, f"{sender}: {message}\n\n", "them")
                self.chat_box.config(state=DISABLED)
                self.chat_box.yview(END)
        except: pass
        if self.chat_loop_id is not None: self.master.after_cancel(self.chat_loop_id)
        self.chat_loop_id = self.master.after(3000, self.refresh_chat_loop)

    def send_message(self):
        if not self.current_friend: return
        msg = self.entry.get().strip()
        if msg:
            try:
                requests.post(f"{data.SERVER_URL}/send_message", json={"sender": self.username, "receiver": self.current_friend, "message": msg}, timeout=5)
                self.entry.delete(0, END)
                self.refresh_chat_loop() 
            except: pass

    def command_gacha(self): gacha.open_gacha_window()
    def command_ext(self): apps.open_apps_window()

def open_home_window(user):
    root = Tk()
    try: root.iconbitmap(default=resource_path("AppIcon.ico"))
    except: pass
    app = CoretonApp(root, user)
    root.mainloop()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    open_home_window(username)