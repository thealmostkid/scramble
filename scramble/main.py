#from tkinter import *
#from tkinter import ttk

import scramble.__version
import Tkinter

def shutdown():
    exit()

def main():
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

if __name__ == '__main__':
    main()
