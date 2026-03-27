#5 selected(3 common in row=*5 money, 3rare in row=*200 money)=gacha
Coins = (100)
PerSpin=(10)





from tkinter import *
def click():
    global Coins
    Coins-=10
    label.config(text=Coins)
    


window = Tk()#start window
window.geometry("420x420")
window.title("App")

icon = PhotoImage(file='Coreton\images\AppIcon.png')
window.iconphoto(True,icon)
window.config(background="#000000")



button = Button(window,text="funny button")
button.config(command=click)
button.pack()

import random
rol3=random.randint(0,5)
if(rol3==0):photo3=PhotoImage(file='Coreton/images/gachaImage.png')
else:photo3=PhotoImage(file=f'Coreton/images/gachaImage{rol3}.png')

rol1=random.randint(0,5)
if(rol1==0):photo1=PhotoImage(file='Coreton/images/gachaImage.png')
else:photo1=PhotoImage(file=f'Coreton/images/gachaImage{rol1}.png')

rol2=random.randint(0,5)
if(rol2==0):photo2=PhotoImage(file='Coreton/images/gachaImage.png')
else:photo2=PhotoImage(file=f'Coreton/images/gachaImage{rol2}.png')

rol5=random.randint(0,5)
if(rol5==0):photo5=PhotoImage(file='Coreton/images/gachaImage.png')
else:photo5=PhotoImage(file=f'Coreton/images/gachaImage{rol5}.png')

rol4=random.randint(0,5)
if(rol4==0):photo4=PhotoImage(file='Coreton/images/gachaImage.png')
else:photo4=PhotoImage(file=f'Coreton/images/gachaImage{rol4}.png')

rolimg1=Label(window,image=photo1)
rolimg1.place(x=0,y=0)
rolimg2=Label(window,image=photo2)
rolimg2.place(x=116,y=0)
rolimg3=Label(window,image=photo3)
rolimg3.place(x=232,y=0)
rolimg4=Label(window,image=photo4)
rolimg4.place(x=348,y=0)
rolimg5=Label(window,image=photo5)
rolimg5.place(x=464,y=0)

label = Label(window, text=Coins)
label.pack()

window.mainloop()