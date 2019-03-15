##########################################################################################
##      FyreFly Messaging, Client Framework
##
##      Version 0.1a
##      Copyright (C) 2019 - Aaron Edwards
##
##      Email: edwardsaaron94@gmail.com
##
##      This program is built in Python 3.5.1 (v3.5.1:37a07cee5969, Dec  6 2015, 01:38:48)
##
##########################################################################################



######################################## IMPORTS #########################################

## @Socket is used for establishing a connection to the Server.
## @_thread/threading is used to handle multiple tasks at once.
## @os is used only for clearing the screen and exiting if no connection is found.
## @time is used in the connection phase of the client.
import socket
from _thread import *
import threading
import os
import time

######################################## GLOBALS #########################################

## HOST is the IP address you'll use to connect to the server.
##      Conversely this can be changed to accept a user input for an IP address.
##      This is just 'localhost' to run on your local machine.
## PORT is the port number the client will go through to connect to the server.
##      Again this variable can be changed to suit your needs.
## BUFFER_SIZE is used by socket.recv() to determine the max amount of data
##      allowed to pass through the socket.
## CONNECTED is used only to determine if the socket.connect() was successful

HOST = 'localhost'
PORT = 33000
BUFFER_SIZE = 1024
ADDR = (HOST, PORT)
CONNECTED = True


## Creates Socket on load.
CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

######################################### FUNCTIONS #########################################

## Called initially to try and connect to the server
## Tries connecting 5 times and if it still cannot connect it quits with a message
## If it does connect then it will start the recieve() thread.
def connect_to_server(count):

    ## Connection Status
    connected = False

    ## Tries to connect to the server, If it connects fine, the connected status will now be True.
    try:
        CLIENT.connect(ADDR)
        connected = True

    ## If the client fails to connect to the server, it will try 5 more times.
    ## Each time it will wait for one second to act as a 'time buffer' so if the
    ## Server came online in that time, it can connect.
    except:
        if count != 6:
            print("[*] Could not contact FyreFly Server, Try {}/5\n".format(count))
            count += 1
            time.sleep(1)
            connect_to_server(count)

        ## This will exit the program after 5 attempts to connect have been made.
        else:
            print('[*] Could not contact the FyreFly Server at this time.\n[*] The server may be offline or down for maintenance\n[*] Sorry for the inconvenience.')
            os.sys.exit()

    ## If connection status is True, then a new thread is created to listen to the server
    ## For instructions on what to do.
    if connected:
        print("[*] Connected to FyreFly Messaging Server.")
        input('[*] Press enter to continue...')
        RECEIVE_THREAD = threading.Thread(target=receive)
        RECEIVE_THREAD.start()


## This thread handles the task of receiving messages from the server/other clients.
def receive():
    ## Just makes sure the client is connected to the server.
    if CONNECTED:

        ## This creates a buffer of all the messages received by the server.
        MESSAGE_LOG = ''

        ## This creates a new thread for sending messages and also starts it.
        SEND_THREAD = threading.Thread(target=send_msg)
        SEND_THREAD.start()

        ## Always checks to see if a message is recieved from the server.
        while True:

            ## This tries to listen for a message from the server
            try:
                ## This gets the message and then adds it to the message buffer.
                message = CLIENT.recv(BUFFER_SIZE).decode()
                MESSAGE_LOG += message

                ## This checks to see if the messaged typed is not the <quit> request
                ## Command. If it isnt then it clears the screen and prints the entirety
                ## Of the message buffer.
                if message != '<quit>':
                    os.system('cls')
                    print(MESSAGE_LOG)

                ## This states that if the client does want to send a <quit> request,
                ## It will close the socket and exit this thread.
                else:
                    CLIENT.close()
                    break

            ## Possible client has left the chat
            except OSError:
                break
    else:
        pass

## This thread is used to handle the task of sending messages to the chat room.
def send_msg():

    ## Is always asking for an input
    while True:

        ## Get message
        message = input(">> ")

        ## Try and send the message to the server.
        try:
            ## If the message is not a <quit> request, it will send the contents of
            ## The message to the server and then wait for another input.
            if message != '<quit>':
                CLIENT.send(message.encode())

            ## If it is a <quit> request, send it off and then quit this thread.
            else:
                CLIENT.send(message.encode())
                break

        ## This will only be displayed after the server has Acknowledged the <quit> request
        ## Or if the server has been shutdown while the client is still connected.
        except:
            print("Connection to server lost")
            break

## Clear Screen and Starts the connection test to see if the server is online.
def Main():
    os.system('cls')
    connect_to_server(1)

if __name__ == '__main__':
    Main()


















