# Quantum Key Distribution simulation: BB84 protocol
# by Manuel Maiuolo (manuelmaiuolo@gmail.com)
# BB84_client.py - version 1.0

import socket
from threading import Thread, Event
from CUlib import *

class BB84Client:
    def __init__(self, client_name, function_handle_response, menu_functions):
        self.host = "127.0.0.1"
        self.port = SERVER_PORT
        self.client_name = client_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected = False
        self.ready = False
        self.waiting = False
        
        self.function_handle_response = function_handle_response
        self.menu_max_choices, self.menu_choice, self.show_menu = menu_functions
        
        self.th_handle_responses = Thread(target = self.handle_responses)
        self.th_handle_menu = Thread(target = self.handle_menu)
        
    def connect(self):
        try:
            # connect and send client name to server
            self.socket.connect((self.host, self.port))
            send(self.socket, self.client_name)
            print(f"Connection attempt to server as {self.client_name}...")
            # wait to be connected
            response = receive(self.socket)
            if response != TXT_CLIENT_CONNECTED:
                self.disconnect(response)
            # if here: server is ready to take requests
            self.connected = True
            print("Connected succesfully!\nWaiting for all necessary clients...")

            self.th_handle_responses.start()
            if self.menu_max_choices > 0:  # if there is at least one action in the menu
                self.th_handle_menu.start()

        except Exception as e:
            # connection failed: disconnect and close client
            self.disconnect(e)

    def disconnect(self, log):
        # print message, close socket and wait for input to close console
        print(log)
        self.socket.close()
        self.connected = False
        input("Press [Enter] to exit . . .")
        exit()

    def send_message(self, msg):
        send(self.socket, msg)

    def handle_menu(self):
        while self.connected:  # main loop
            while self.connected:  # input loop
                valid = True
                try:
                    choice = int(input()) - 1
                except ValueError:
                    choice = -1
                #except Exception:  # already disconnected
                #    exit()
                finally:
                    if not self.connected:
                        break
                    if self.ready and (not self.waiting):
                        if (choice < 0) or (choice >= self.menu_max_choices):
                            print("Enter a number that represents a choice!",
                                  f"(integer from 1 to {self.menu_max_choices})", end="\n > ")
                            valid = False  # loop again: new choice needed
                    # else: not ready <-> client is waiting <-> input was not expected -> print nothing
                        
                if self.ready and (not self.waiting) and valid:
                    break
                # else: input again
            # end of input loop

            if not self.connected:
                break
            # if here: menu option chosen and server is actually ready
            request = self.menu_choice(choice)
            clear()
            wait_to_continue = False
            if request is not None:
                request_type, request_info, wait_to_continue = request
                if request_info is not None:
                    # send type of action
                    self.send_message(request_type)
                    # send info about action
                    if request_info == '':
                        request_info = '.'
                    self.send_message(request_info)
                    print("Request sent to server!", end="\n\n")
                else:
                    print("Request NOT sent to server: no information would be sent!", end="\n\n")
            
            if not wait_to_continue:
                self.show_menu()
            else:
                self.waiting = True
                self.send_message(TXT_WAIT)

    def handle_responses(self):
        while self.connected:
            try:
                response = receive(self.socket)
                while response != '':  # loop to manage multiple requests for direct messages
                    
                    if response.find(TXT_NOT_READY) == 0:
                        response = response[len(TXT_NOT_READY):]
                        self.ready = False
                        clear()
                        print("Waiting for all necessary clients...")
                        
                    elif response.find(TXT_READY) == 0:
                        response = response[len(TXT_READY):]
                        self.ready = True
                        clear()
                        self.show_menu()
                        
                    elif response.find(TXT_WAIT) == 0:
                        response = response[len(TXT_WAIT):]
                        self.waiting = True
                        clear()
                        print("[Simulation in progress]")
                        
                    elif response.find(TXT_CONTINUE) == 0:
                        response = response[len(TXT_CONTINUE):]
                        self.waiting = False
                        clear()
                        self.show_menu()
                    # possible other elifs
                    else:
                        self.function_handle_response(response)
                        response = ''
                    
            except ConnectionResetError:
                self.disconnect("The server has been closed.")
                break


if __name__ == '__main__':

    print("This is an abstract script! Please, execute BB84_Alice.py, BB84_Bob.py or BB84_Eve.py instead.")
    input("Press [Enter] to exit . . .")






