##########################################################################################
##      FyreFly Messaging, Server Framework
##
##      Version 0.2a
##      Copyright (C) 2019 - Aaron Edwards
##
##      Email: edwardsaaron94@gmail.com
##
##      This program is built in Python 3.5.1 (v3.5.1:37a07cee5969, Dec  6 2015, 01:38:48)
##
##########################################################################################

######################################## IMPORTS #########################################

## @Socket is used for low-level networking interfaces.
## @Threading is used for handling multiple tasks at once. Clients/Connections/Cmds
## @os is being used for clearing the screen, and a killing a thread... not the best idea I know :/
## @time is being used for nothing as of yet but will be implemented for something at some stage.
import socket
from _thread import *
import threading
import os
import time

######################################## GLOBALS #########################################

## These are the global variables used by the server.
## HOST is '' so when the socket.bind() function is called it will attach to the localhost.
## PORT is the port the server will be running on.
##      PORT can be any port you choose.
## BUFFER_SIZE is used by socket.recv() to determine the max amount of data
##      allowed to pass through the socket.
## ADDR is just a tuple of HOST,PORT to make the socket.bind() function easier to read.

HOST = ''
PORT = 33000
BUFFER_SIZE = 1024
ADDR = (HOST, PORT)

## These two dictionaries are used to store information about a client
## @CLIENTS holds {socket: client_name}
## @ADDRESSES hold {socket: (IP, PORT)}

CLIENTS = {}
ADDRESSES = {}

## The General Banner Header for start up and clear screen.
BANNER = '''
#################################################
##                                             ##
##         FyreFly Messaging - SERVER          ##
##                                             ##
##                Version 0.2a                 ##
##     Copyright (C) 2019 - Aaron Edwards      ##
##                                             ##
##       Email: edwardsaaron94@gmail.com       ##
##                                             ##
#################################################\n
[*] Type 'help' to see a list of available server commands.'''

## This creates a server socket on startup and binds it to the (HOST,PORT) a.k.a. ADDR.
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)

######################################### FUNCTIONS #########################################

## This is called when the User Clears the screen
def clear():
    
    ## Checks to see if operating system is Windows, if not it will use the other clearscreen variant.
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

## This thread is always running to check whether new connections have been established
## By the client applications.
def accept_connections():

    ## This generates a new thread for the server menu commands and starts it.
    MENU_THREAD = threading.Thread(target=server_cmds)
    MENU_THREAD.start()

    ## Always waiting to accept the new connections.
    ## Will be updated to only accept a certain connection limit.
    while True:

        ## This accepts a message and creates a socket object and tuple which is the
        ## Clients IP and Port numbers.
        ## Then a message is printed to the server terminal telling the User that a new
        ## Connection has been made.
        client_socket, client_address = SERVER.accept()
        print("[*] {}:{} has connected.".format(client_address[0], client_address[1]))

        ## Once the client connectivity has been established, the server will send client
        ## A message to welcome them to the server, and also a request to get their name
        ## For use in the chat room
        client_socket.send("[*] Greetings! Welcome to FyreFly!\n[*] Please enter your name to get started.".encode())

        ## This section adds the relevant socket information to the ADDRESSES
        ## dictionary = (<IP>,<PORT>).
        ## After that a new thread for handling that client is generated and started.
        ADDRESSES[client_socket] = client_address
        CLIENT_THREAD = threading.Thread(target=handle_client, args=(client_socket,))
        CLIENT_THREAD.start()


## This is the thread that listens for all incoming data by a single client.
def handle_client(client):

    ## Initially gets the name the client sends after loading the application and connecting
    ## To the server and welcomes them to the chat room.
    client_name = client.recv(BUFFER_SIZE).decode()
    client.send("\n[*] Welcome {}!\n[*] If you ever want to exit: type <quit> in the chat.".format(client_name).encode())

    ## This calls the broadcast function to notify Who has joined the chat room.
    message = "\n[*] {} Has joined the chat room!".format(client_name)
    broadcast(message)

    ## This adds the clients name to the CLIENTS dictionary
    CLIENTS[client] = client_name

    ## After the above steps are finished it will forever loop until the user
    ## Sends a request to quit.
    while True:
        ## This tries to constantly listen for data being sent over the connected client Socket
        try:
            message = client.recv(BUFFER_SIZE).decode()

            ## Once the user has sent a message, the server will check to see if it is not
            ## A <quit> request. If it is not it will call the broadcast function to send
            ## The clients message into the chatroom. If it is a <quit> request it will
            ## Call the close_connection function and drop the user from the server and
            ## Close the thread.
            if message != "<quit>":
                broadcast(message, "\n"+client_name+': ')
            else:
                close_connection(client)
                break
        except:
            continue


## This is called after every message has been received by a client.
## It will send a message to all clients in the CLIENTS dictionary
## And format the broadcast with the clients name followed by the message.
def broadcast(message, prefix=''):
    try:
        for user in CLIENTS:
            user.send("{}{}".format(prefix, message).encode())
    except:
        pass


## This function is called any time a Client or Connection needs to be closed
## It will recieve a kicked=bool argument to check it was server or client initiated.
def close_connection(client, kicked=False):

    ## This is for when a client initiates a connection close request from chat.
    ## It will send the <quit> message to the client telling them it is okay to quit.
    ## It also notifies the chat room who has left.
    ## It notifies the server User too on Who:IP:Port has disconnected.
    if not kicked:
        client.send("<quit>".encode())
        broadcast("\n[*] {} has left the chat room.".format(CLIENTS[client]))
        print('[*] Client: \'{}\' ~ {} : {} Has disconnected.'.format(CLIENTS[client], ADDRESSES[client][0], ADDRESSES[client][1]))

    ## This is for when the server User initiates the kick command
    ## It will print to the server that the user has been kicked successfully
    else:
        print('[*] Client: \'{}\' ~ {} : {} Has been kicked.'.format(CLIENTS[client], ADDRESSES[client][0], ADDRESSES[client][1]))

    ## This closes the requested client connection.
    ## And removes it from the ADDRESSES/CLIENTS dictionaries so
    ## It wont show as a current connection anymore.
    client.close()
    del ADDRESSES[client]
    del CLIENTS[client]


## This thread deals with the Menu operations/commands of the server while all Clients
## And connections are being dealt with in different threads.
def server_cmds():
    while True:
        ## Gets an option from the User and goes through various IF/ELIF statements
        ## Depending on input.
        cmd = input('>> ')

        ## This option just shows a list of all the available server commands.
        if cmd.lower() == 'help':
            print('[*] BC - Broadcast a message to the chat room.')
            print('[*] CLS - Clear the screen.')
            print('[*] HELP - Provides Help information for Server Commands.')
            print('[*] KICK - Kick a client from the server.')
            print('[*] LS - Lists the current connections.')

        ## This option allows the User of the server terminal to send a message directly into
        ## The chat room for everyone to see. The Clients will see: SERVER: <message>
        elif cmd.lower() == 'bc':
            message = input('What would you like to broadcast?\n>> ')
            broadcast(message, "\nSERVER: ")

        ## The User can clear the screen on the server terminal whenever they like and the banner
        ## Will always be displayed after clearing.
        elif cmd.lower() == 'cls':
            clear()
            print(BANNER)

        ## This command allows the User to get a list of all the active clients in the chat room
        ## And all the connections that havent made a name to enter the chat yet (base connection).
        elif cmd.lower() == 'ls':
            for client in ADDRESSES:
                try:
                    print('[*] Client: \'{}\' ~ {} : {}'.format(CLIENTS[client], ADDRESSES[client][0], ADDRESSES[client][1]))
                except:
                    print('[*] Connection: {} : {}'.format(ADDRESSES[client][0], ADDRESSES[client][1]))

        ## If the User decides to kick a person from the chat for whatever reason the server
        ## Will loop through all the clients connected to the room only.
        ## If the server finds a connection that isnt in the chat it will skip it and move on until
        ## All objects are checked.
        elif cmd.lower() == 'kick':
            print('[*] Who would you like to kick from chat?\n')
            i = 0
            connection = []
            for client in ADDRESSES:
                try:
                    print('[{}] {}'.format(i+1, CLIENTS[client]))
                    i += 1
                    connection.append(client)
                except:
                    continue

            ## The User will pick a number from the list of active clients in the chat room
            ## That client will have a message sent to them and then the client socket is then
            ## closed and removes that object using close_connection.
            kick = input('\n>> ')
            try:
                connection[int(kick)-1].send('\n[*] Sorry but you have been kicked from the server. \n[*] The Server Admin obviously doesnt like you. :('.encode())
                broadcast('\n[*] {} Has been kicked from the server!'.format(CLIENTS[connection[int(kick)-1]]))
                close_connection(connection[int(kick)-1], kicked=True)
            except:
                print("[*] Cannot close connection!")

        ## When the User decides to quit the Server Application
        ## It loops through all the currently connected clients and closes each socket
        ## It will loop through clients in the chat, and also clients that are just base connected
        elif cmd.lower() == 'quit':
            for client in ADDRESSES:
                try:
                    print('[*] Closing Client: \'{}\' ~ {} : {}'.format(CLIENTS[client], ADDRESSES[client][0], ADDRESSES[client][1]))
                except:
                    print('[*] Closing Connection: {} : {}'.format(ADDRESSES[client][0], ADDRESSES[client][1]))
                client.close()
            os._exit(1)

        ## If the User doesnt type a valid command it will tell them.
        elif cmd != '':
            print('[*] Not a valid server command')


## Puts the server into listening mode
## Starts the thread on accepting all client connections to the server.
def Main():
    SERVER.listen(5)
    ACCEPT_THREAD = threading.Thread(target=accept_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()


## Clear the screen on start and display the main Banner.
## Then jumps to the main TCP related stuff.
if __name__ == '__main__':
    clear()
    print(BANNER)
    Main()












