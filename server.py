"""
Created on Jan 19, 2018

@author: me
"""
from socket import AF_INET, socket, SOCK_STREAM
from sys import argv, exit
from threading import Thread
from contextlib import suppress
from datetime import datetime
from msvcrt import getch

server = socket(AF_INET, SOCK_STREAM)
clients = {}
addresses = {}
log = []
blacklist = []
host = '0.0.0.0'
port = 7511
buff = 4096


# receive an encoded message from a client
def receive_utf8(socket, buffer):
    return socket.recv(buffer).decode('utf-8')


# encode and send a message
def send_utf8(socket, data):
    socket.sendall(data.encode('utf-8'))


# get current time in specified format
def get_time(time_format):
    return datetime.now().strftime(time_format)


# broadcast a message to all connected clients
def broadcast(message, prefix=''):
    for client in clients:
        if not client._closed:
            send_utf8(client, ' ' + prefix + message)


# add an entry to the log
def add_to_log(evt):
    entry = '[ %s ] %s' % (get_time('%d-%m-%y %H:%M:%S'), evt)
    log.append(entry)
    with open('log.txt', 'a') as lf:
        lf.write(entry + '\n')


# blacklist a client by IP
def add_to_blacklist(ip):
    blacklist.append(ip)
    with open('blacklist.txt', 'a') as bl:
        bl.write(ip + '\n')


# accept incoming connections
def accept_connections():
    while True:

        try:

            client, addr = server.accept()
            if addr[0] in blacklist:
                send_utf8(client, ' You have been blocked from the server.')
                client.close()
                continue
            add_to_log('%s has connected.' % str(addr))
            send_utf8(client, ' Please enter your name.')
            addresses[client] = addr
            Thread(target=handle_client, args=(client,)).start()

        except:

            break


# data exchange between the server and the client
def handle_client(client):
    try:

        while True:
            name = receive_utf8(client, buff)
            if name in clients.values():
                send_utf8(client, " User with the name '%s' already exists." % name)
            else:
                send_utf8(client, ' Welcome %s! Type {quit} to exit.' % name)
                break

    except Exception as e:

        add_to_log('%s: %s has disconnected.\n%s' % (type(e).__name__, str(addresses[client]), str(e)))
        return

    broadcast('%s has joined.' % name)
    clients[client] = name

    try:

        while True:

            msg = receive_utf8(client, buff)

            if msg != '{quit}':
                broadcast(msg, '%s %s ~ ' % (name, get_time('%H:%M')))
            else:
                client.close()
                add_to_log('%s has disconnected.' % str(addresses[client]))
                del clients[client]
                broadcast('%s has left.' % name)
                break

    except Exception as e:

        add_to_log('%s: %s has disconnected.\n%s' % (type(e).__name__, str(addresses[client]), str(e)))
        del clients[client]
        broadcast('%s has disconnected.' % name)


# connection management menu
def manage_connections():
    print('a. connected clients [%d]' % len(clients))
    print('b. block client')
    print('c. broadcast')
    print('d. return')

    inp = input('~ ')

    if inp == 'a':
        for key in clients.keys():
            print('%s %s' % (clients[key], addresses[key]))

    elif inp == 'b':

        ip = input('IP address to be blocked ~ ')

        for client in clients:
            if ip == addresses[client][0]:
                send_utf8(client, ' You have been banned.')
                client.close()
                broadcast('%s has been banned.' % clients[client])
        add_to_blacklist(ip)

    elif inp == 'c':

        broadcast(input('Message to broadcast ~ '))

    elif inp == 'd':

        return

    if '-ide' not in argv[1:]:
        getch()

    manage_connections()


# server management menu
def interface():
    print('Server Maintenance Interface')

    while True:

        print('Options:')
        print('1. log since startup')
        print('2. connection management')
        print('3. exit program')

        inp = input('~ ')

        if inp == '1':

            for entry in log:
                print(entry)
            print("for a full log see 'log.txt'")

        elif inp == '2':

            manage_connections()
            continue

        elif inp == '3':

            s_shutdown()
            exit()

        else:

            continue

        if '-ide' not in argv[1:]:
            getch()


# start the server
def s_start():

    try:
        server.bind((host, port))
        server.listen(5)
    except Exception as e:
        print('Error.')
        add_to_log('%s: server startup error.\n%s' % (type(e).__name__, str(e)))
        return

    with suppress(FileNotFoundError):
        blist = open('blacklist.txt', 'r')
        for ip in blist.readlines():
            blacklist.append(ip.strip())
        blist.close()

    add_to_log('Server Startup. %s' % str(argv[1:]))
    accept_thread = Thread(target=accept_connections)
    accept_thread.start()


# close the server
def s_shutdown():
    shut = input('Are you sure you want to shutdown the server? (Y/N)\n~ ').upper()
    if shut == 'N':
        print('Server shutdown revoked.')
    elif shut != 'Y':
        print('Error.')
    else:
        broadcast('Disconnecting from server...')
        for client in clients:
            client.close()
        blacklist.clear()
        server.close()
        add_to_log('Server Shutdown.')


if __name__ == '__main__':
    s_start()
    interface_thread = Thread(target=interface)
    interface_thread.start()

