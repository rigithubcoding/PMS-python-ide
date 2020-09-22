import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import subprocess
import queue
import os
from threading import Thread
import shutil
import sys
from tkinter.messagebox import showwarning
import py_compile

if sys.platform=="win32":
    raise SystemError("cannot run on windows")

filename=str()
END="end"

class Console(tk.Frame):
    def __init__(self,parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.createWidgets()

        # get the path to the console.py file assuming it is in the same folder
        consolePath = os.path.join(os.path.dirname(__file__),"console.py")
        # open the console.py file (replace the path to python with the correct one for your system)
        # e.g. it might be "C:\\Python35\\python"
        self.p = subprocess.Popen(["python3",consolePath],
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

        # make queues for keeping stdout and stderr whilst it is transferred between threads
        self.outQueue = queue.Queue()
        self.errQueue = queue.Queue()

        # keep track of where any line that is submitted starts
        self.line_start = 0

        # make the enter key call the self.enter function
        self.ttyText.bind("<Return>",self.enter)

        # a daemon to keep track of the threads so they can stop running
        self.alive = True
        # start the functions that get stdout and stderr in separate threads
        Thread(target=self.readFromProccessOut).start()
        Thread(target=self.readFromProccessErr).start()

        # start the write loop in the main thread
        self.writeLoop()

    def destroy(self):
        "This is the function that is automatically called when the widget is destroyed."
        self.alive=False
        # write exit() to the console in order to stop it running
        self.p.stdin.write("exit()\n".encode())
        self.p.stdin.flush()
        # call the destroy methods to properly destroy widgets
        self.ttyText.destroy()
        tk.Frame.destroy(self)
    def enter(self,e):
        "The <Return> key press handler"
        string = self.ttyText.get(1.0, tk.END)[self.line_start:]
        self.line_start+=len(string)
        self.p.stdin.write(string.encode())
        self.p.stdin.flush()

    def readFromProccessOut(self):
        "To be executed in a separate thread to make read non-blocking"
        while self.alive:
            data = self.p.stdout.raw.read(1024).decode()
            self.outQueue.put(data)

    def readFromProccessErr(self):
        "To be executed in a separate thread to make read non-blocking"
        while self.alive:
            data = self.p.stderr.raw.read(1024).decode()
            self.errQueue.put(data)

    def writeLoop(self):
        "Used to write data from stdout and stderr to the Text widget"
        # if there is anything to write from stdout or stderr, then write it
        if not self.errQueue.empty():
            self.write(self.errQueue.get())
        if not self.outQueue.empty():
            self.write(self.outQueue.get())

        # run this method again after 10ms
        if self.alive:
            self.after(10,self.writeLoop)

    def write(self,string):
        self.ttyText.insert(tk.END, string)
        self.ttyText.see(tk.END)
        self.line_start+=len(string)

    def createWidgets(self):
        self.ttyText = tk.Text(self, wrap=tk.WORD)
        self.ttyText.pack(fill=tk.BOTH,expand=True)

def execute_prog(progname):
    command="python3 "+progname
    os.system(command)

def save(code):
    savedialog=tk.Tk()
    fnamelabel=tk.Label(savedialog, text="Enter file name: ")
    fnamelabel.pack(side="left")
    fnameentry=tk.Entry(savedialog, bd=10)
    fnameentry.pack(side="right")
    def getfilename():
        global filename
        filename=fnameentry.get()
        savedialog.destroy()
        with open(filename, "w+") as f:
            f.write(code)
            f.close()
    enterbtn=tk.Button(savedialog, text="okay", command=getfilename)
    enterbtn.pack(side="bottom")
    savedialog.geometry("500x500")
    savedialog.title("save dialog")

def close(filename):
    with open(filename, "r") as f:
        f.close()

def openfile(textbox):
    files=os.listdir()
    opendialog=tk.Tk()
    files=tk.Label(opendialog, text=files)
    fname=tk.Entry(opendialog, width=20)
    def actuallyopen():
        x=fname.get()
        with open(x, "r+") as f:
            textbox.delete(1.0, END)
            textbox.insert(1.0, f.read())
            f.close()
        opendialog.destroy()
    okaybtn=tk.Button(opendialog, text="Okay", command=actuallyopen)
    files.pack(side="left")
    fname.pack(side="right")
    okaybtn.pack(side="bottom")

def debug(myfile):
    py_compile.compile(myfile, doraise=True)

#create the window
root = tk.Tk()
root.geometry("1000x2000")
#create editor
txt = scrolledtext.ScrolledText(root, undo=True, width=50, height=30)
txt['font'] = ('consolas', '12')
#create the run and file menus
menubar=tk.Menu(root)
file = tk.Menu(menubar, tearoff = 0) 
run=tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label ='File', menu = file) 
menubar.add_cascade(label='Run', menu=run)
file.add_command(label ='New File', command = None) 
file.add_command(label ='Open', command = lambda: openfile(txt)) 
file.add_command(label ='Save', command = lambda: save(txt.get("1.0", 'end-1c'))) 
file.add_separator() 
run.add_command(label='Run', command=lambda: execute_prog(filename))
run.add_command(label="debug", command=lambda: debug(filename))
run.add_separator()
#create instance of the console class
main_console = Console(root)
#set the window title
root.title('PMS Python IDE CE')
txt.pack(expand=True, fill='both')
main_console.pack(fill=tk.BOTH,expand=True, side='right')
root.config(menu = menubar) 
root.mainloop()