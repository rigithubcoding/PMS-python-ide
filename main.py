from tkinter import *
import tkinter.scrolledtext as scrolledtext
from tkinter.filedialog import *
from tkinter import ttk
import subprocess
import queue
import os
from threading import Thread
import shutil
import sys
from tkinter.messagebox import showwarning
import py_compile
from typing import List, Any, Union
import pickle, sklearn
import term
from idlelib.tooltip import *
import re
import keyboard
import time
import getpass

filename=str()
file=None
if sys.platform=='darwin' or sys.platform=='win32' and getpass.getusername()!='monik':
    raise SystemError("PMS does not run on this OS")
    time.sleep(90)
    exit()

class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                            ("active", "pressed", "!disabled", "img_closepressed"),
                            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe", 
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top", 
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top", 
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                        })
                    ]
                })
            ]
        })
    ])

class Console(Frame):
    def __init__(self,parent=None):
        Frame.__init__(self, parent)
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
        Frame.destroy(self)
    def enter(self,e):
        "The <Return> key press handler"
        string = self.ttyText.get(1.0, END)[self.line_start:]
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
        self.ttyText.insert(END, string)
        self.ttyText.see(END)
        self.line_start+=len(string)

    def createWidgets(self):
        self.ttyText = Text(self, wrap=WORD)
        self.ttyText.pack(fill=BOTH,expand=True)


def main(master):
    tip = ListboxToolTip(master, ["Hello", "world"])

def execute_prog(progname):
    command="python3 "+progname
    os.system(command)

def save(code):
    '''
    savedialog=Tk()
    fnamelabel=Label(savedialog, text="Enter file name: ")
    fnamelabel.pack(side="left")
    fnameentry=Entry(savedialog, bd=10)
    fnameentry.pack(side="right")
    def getfilename():
        global filename
        filename=fnameentry.get()
        savedialog.destroy()
        with open(filename, "w+") as f:
            f.write(code)
            f.close()
    enterbtn=Button(savedialog, text="okay", command=getfilename)
    enterbtn.pack(side="bottom")
    savedialog.geometry("500x500")
    savedialog.title("save dialog")
    '''
    filepath = asksaveasfilename(
        defaultextension="py",
        filetypes=[("Python Files", "*.py"), ("All Files", "*.*"), ("Bash files", ".sh")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = txt.get(1.0, END)
        output_file.write(text)

def close(f):
    f.close()

def openfile(textbox=None):
    global file
    try:
        notebook.forget(txt)
        file = askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        txt.delete(1.0, END)
        with open(file, "r") as input_file:
            text = input_file.read()
            txt.insert(END, text)
        root.title(f"Text Editor Application - {file}")
        notebook.add(txt, text=file)
    except:
        file = askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        txt.delete(1.0, END)
        with open(file, "r") as input_file:
            text = input_file.read()
            txt.insert(END, text)
        root.title(f"Text Editor Application - {file}")
        notebook.add(txt, text=file)
    '''
    file = askopenfile(mode="r", initialdir="/home", title="select file", filetypes=(("Python Files", "*.py"), ("All Files", "*.*"), ("Bash Files", "*.sh")))
    root.title('PMS Python IDE CE - '+file.name)
    txt.insert(1.0, file.read())
    txt.insert(END, file.read())
    file.close()
    '''
    '''
    with open(file, "w+") as f:
        txt.insert(1.0, f.read())
        txt.insert(END, f.read())
    ''' 
    '''
    files=os.listdir()
     opendialog=Tk()
     files=Label(opendialog, text=files)
     fname=Entry(opendialog, width=20)
     def actuallyopen():
         x=fname.get()
         with open(x, "r+") as f:
             textbox.delete(1.0, END)
             textbox.insert(1.0, f.read())
             f.close()
         opendialog.destroy()
     okaybtn=Button(opendialog, text="Okay", command=actuallyopen)
     files.pack(side="left")
     fname.pack(side="right")
     okaybtn.pack(side="bottom")
     '''
def new():
    notebook.add(txt,text='New File')

def debug(myfile):
    (py_compile.compile(myfile, doraise=True))

def close_tab_in_editor():
    notebook.forget(notebook.select())
#create the window
root = Tk()
#root.geometry is widthxheight
root.geometry("2000x2000")
#create editor

def nexttab():
    try:
        notebook.select(int(notebook.index('current'))+1)
    except:
        notebook.select(0)

def find():
    def okay():
        pattern=pattern.get()
        re.findall(pattern, txt.get("1.0", END))
    new=Tk()
    new.geometry("500x100")
    label=Label(new, text="Enter your search pattern here:").pack(side=LEFT)
    pattern=Entry(new, width=50)
    okaybtn=Button(new, text="Okay", command=okay)
    new.mainloop()

notebook = CustomNotebook(width=2000, height=600)
notebook.pack(side=TOP)
txt = scrolledtext.ScrolledText(notebook, undo=True, width=30, height=30)
txt['font'] = ('consolas', '12')
aimodel=open("ai.pkl", "rb")
model=pickle.load(aimodel)
def highlight():
    predictions=model.predict(txt.get().split())
    for prediction in predictions:
        if prediction=='builtin':
            pass
notebook.add(txt, text='New File')
#create the run and file menus
menubar=Menu(root)
file = Menu(menubar, tearoff = 0) 
run=Menu(menubar, tearoff=0)
nav=Menu(menubar, tearoff=0)
menubar.add_cascade(label ='File', menu = file) 
menubar.add_cascade(label='Run', menu=run)
menubar.add_cascade(label="Navigate", menu=nav)
file.add_command(label ='New File', command = new) 
file.add_command(label ='Open', command = lambda: openfile(txt)) 
file.add_command(label ='Save', command = lambda: save(txt.get("1.0", 'end-1c'))) 
file.add_separator() 
run.add_command(label='Run', command=lambda: execute_prog(filename))
run.add_command(label="Debug", command=lambda: debug(filename))
run.add_command(label="New Terminal", command=term.term)
run.add_separator()
nav.add_command(label="Find in current file", command=find)
nav.add_separator()
#create instance of the console class
main_console = Console(root)
#set the window title
root.title('PMS Python IDE CE')
#pack elements
#txt.pack(expand=True, fill='both')
main_console.pack(fill=BOTH,expand=True, side='right')
#configure tkinter to use menu as the menubar
root.config(menu = menubar)
#add keyboard shortcuts
keyboard.add_hotkey('ctrl + n', new) 
keyboard.add_hotkey('ctrl + o', openfile)
keyboard.add_hotkey('ctrl + s', save, args=txt.get("1.0", 'end-1c'))
keyboard.add_hotkey('ctrl + w', close_tab_in_editor)
keyboard.add_hotkey('ctrl + t', nexttab)
#run the program
root.mainloop()
