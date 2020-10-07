from tkinter import *
import os

def term():
	root = Tk()
	root.geometry("1000x800")
	termf = Frame(root, height=400, width=500)

	termf.pack(fill=BOTH, expand=YES)
	wid = termf.winfo_id()
	os.system('xterm -into %d -geometry 180x90 -sb &' % wid)

	root.mainloop()

