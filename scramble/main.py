#!/usr/bin/env python
import scramble.engine
import scramble.server
import scramble.__version

import docopt
import os
import socket
import sys
import tempfile
import threading
import time
import Tkinter

def shutdown():
    sys.exit()

def gui(stats_file_name):
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
            'stats': stats_file_name, 'ip': str(ip_addr)}
    text = '''
Start a test:
http://{host}:{port}/
or
http://{ip}:{port}/

Admin page:
http://{ip}:{port}/admin

Stats file:
{stats}
'''.format(**text_params)

    url = Tkinter.Label(root, anchor="w",
            text=text)
    url.grid(column=0, row=1, columnspan=2, sticky='EW')
    root.mainloop()

def stats_thread(engine, stats_file_name):
    while True:
        with open(stats_file_name, 'w') as output:
            for stat in engine.stats:
                output.write('%s\n' % ','.join(stat))
        time.sleep(60)

def main():
    print sys.argv
    usage_vars = {
        'gui': '--gui',
        'port': '--port',
        }
    usage = """Scramble server.

Usage:
  scramble

""".format(**usage_vars)

    foo="""
  main.py {port} <port> [{gui}]
  main.py (-h | --help)
  main.py --version
Options:
  -h --help  Show this screen.
  --version  Show version.
  {port}=<port>  Port to serve on.
  {gui}  Launch a local gui.
""".format(**usage_vars)
    #arguments = docopt.docopt(usage, scramble.__version.version)
    #print(arguments)
    #exit()
    port = int(sys.argv[2])
    gui = False
    engine = scramble.engine.Engine()

    server = threading.Thread(target=scramble.server.main, args=[engine, port])
    server.daemon = True
    server.start()

    (stats_fd, stats_file) = tempfile.mkstemp(prefix='scramble_stats', suffix='.csv')
    os.close(stats_fd)
    stats = threading.Thread(target=stats_thread, args=[engine, stats_file])
    stats.daemon = True
    stats.start()

    if gui:
        gui(stats_file)
    else:
        server.join()

if __name__ == '__main__':
    main()
