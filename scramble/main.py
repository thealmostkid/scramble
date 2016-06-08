#!/usr/bin/env python
import scramble.server
import scramble.__version
import socket
import sys
import threading
import Tkinter

def shutdown():
    sys.exit()

def gui():
    root = Tkinter.Tk()
    root.title("Scramble Server")

    button = Tkinter.Button(root, text='Quit', command=shutdown)
    button.grid(column=1,row=2)

    ver = Tkinter.Label(root,
        anchor="w",
        text='version: %s' % scramble.__version.version)
    ver.grid(column=0, row=0, columnspan=2, sticky='EW')

    try:
        host_name = socket.getfqdn()
        ip_addr = None
        for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]:
            s.connect(('8.8.8.8', 53))
            addr = s.getsockname()[0]
            s.close()
            if not addr.startswith('127.'):
                ip_addr = addr
                continue
    except:
        ip_addr = None
    if ip_addr is None:
        ip_addr = "Failed to determine IP address"

    text_params = {'host': host_name, 'port': str(scramble.server.SERVER_PORT),
            'ip': str(ip_addr)}
    text = '''
Start a test:
http://{host}:{port}/
or
http://{ip}:{port}/

Admin page:
http://{ip}:{port}/admin
'''.format(**text_params)

    url = Tkinter.Label(root, anchor="w",
            text=text)
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
