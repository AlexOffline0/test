from tkinter import *
import random
import os
import sys

def open_gacha_window():
    # Use Toplevel so it doesn't crash the main app
    window = Toplevel() 
    window.geometry("600x420") # Adjusted width to fit 5 images
    window.title("Gacha")
    window.config(background="#000000")

    # Helper function to find images whether running as script or EXE
    def get_asset_path(relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    # Load Icon
    try:
        icon_path = get_asset_path('Coreton/images/AppIcon.png')
        icon = PhotoImage(file=icon_path)
        window.iconphoto(True, icon)
    except:
        print("Icon not found")

    # --- GACHA LOGIC ---
    photos = []
    for i in range(5):
        rol = random.randint(0, 5)
        img_name = 'gachaImage.png' if rol == 0 else f'gachaImage{rol}.png'
        img_path = get_asset_path(f'Coreton/images/{img_name}')
        
        try:
            photo = PhotoImage(file=img_path)
            photos.append(photo) # Keep reference so image shows up
            lbl = Label(window, image=photo, bg="black")
            lbl.place(x=i*116, y=0)
        except:
            Label(window, text=f"Missing {rol}", fg="white", bg="black").place(x=i*116, y=0)

    # Logic for matches (Your existing logic)
    # Note: To use rol1, rol2, etc., you'd store them in a list
    
    # We keep a reference to photos so they don't get garbage collected
    window.image_refs = photos 

# Allow testing this file individually
if __name__ == "__main__":
    root = Tk()
    btn = Button(root, text="Test Gacha", command=open_gacha_window)
    btn.pack()
    root.mainloop()