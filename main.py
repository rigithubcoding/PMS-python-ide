from tkinter import *
from idlelib import pyshell

root = Tk()
Label(root, text='Root id is '+str(id(root))).pack()
root.update()
def later():
    pyshell.main(tkroot=root)
    Label(root, text='Use_subprocess = '+str(pyshell.use_subprocess)).pack()

root.after(0, later)
root.mainloop()
