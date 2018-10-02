"""
Created on Jan 19, 2018

@author: me
"""
from socket import AF_INET, socket, SOCK_STREAM, gethostname
from threading import Thread
from sys import exit
import tkinter as tk

client_socket = socket(AF_INET, SOCK_STREAM)
# host = '94.30.159.15'
host = gethostname()
port = 7511
buff = 4096


def receive_utf8(socket, buffer):
    return socket.recv(buffer).decode('utf-8')


def send_utf8(socket, data):
    socket.sendall(data.encode('utf-8'))


def on_closing(event=None):
    my_msg.set('{quit}')
    send()


def receive(recv_buff):
    while True:

        try:

            msg = receive_utf8(client_socket, recv_buff)
            if msg:
                msg_list.insert(tk.END, msg)
            else:
                msg_list.insert(tk.END, ' Unable to connect.')
                top.protocol('WM_DELETE_WINDOW', top.destroy)
                break

        except Exception:

            break


def send(event=None):
    msg = my_msg.get()
    my_msg.set('')
    try:
        send_utf8(client_socket, msg)
    except:
        pass

    if msg == '{quit}':
        client_socket.close()
        top.destroy()


top = tk.Tk()
top.title('Chat')

msg_frame = tk.Frame(top)
my_msg = tk.StringVar()
my_msg.set('')

yscrollbar = tk.Scrollbar(msg_frame)
xscrollbar = tk.Scrollbar(msg_frame, orient=tk.HORIZONTAL)
msg_list = tk.Listbox(msg_frame, height=15, width=50,
                      yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
msg_list.pack(expand=tk.TRUE, side=tk.LEFT, fill=tk.BOTH)
yscrollbar.config(command=msg_list.yview)
xscrollbar.config(command=msg_list.xview)
msg_frame.pack(expand=tk.TRUE, fill=tk.BOTH)

entry_field = tk.Entry(top, textvariable=my_msg)
entry_field.bind('<Return>', send)
entry_field.pack()

send_button = tk.Button(top, text='Send', command=send)
send_button.pack()

top.protocol('WM_DELETE_WINDOW', on_closing)


if __name__ == '__main__':

    try:
        client_socket.connect((host, port))
    except Exception as e:
        from tkinter import messagebox

        top.withdraw()
        messagebox.showerror(type(e).__name__, 'Unable to connect: %s' % str(e))
        exit()

    receive_thread = Thread(target=receive, args=(buff,))
    receive_thread.start()
    tk.mainloop()
