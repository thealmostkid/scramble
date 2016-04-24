#from tkinter import *
#from tkinter import ttk

import scramble.server
import scramble.__version
import threading
import Tkinter

def shutdown():
    exit()

def gui():
    root = Tkinter.Tk()
    root.title("Scramble Server")

    button = Tkinter.Button(root, text='Quit', command=shutdown)
    button.grid(column=1,row=2)

    ver = Tkinter.Label(root,
        anchor="w",
        text='version: %s' % scramble.__version.version)
    ver.grid(column=0, row=0, columnspan=2, sticky='EW')

    url = Tkinter.Label(root, anchor="w", text='The URL is http://127.0.0.1')
    url.grid(column=0, row=1, columnspan=2, sticky='EW')
    root.mainloop()

def main():
    threads = list()
    server = threading.Thread(target=scramble.server.main)
    threads.append(server)
    server.daemon = True
    server.start()
    gui()

if __name__ == '__main__':
    main()
