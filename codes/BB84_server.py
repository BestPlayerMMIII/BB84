# Quantum Key Distribution simulation: BB84 protocol
# by Manuel Maiuolo (manuelmaiuolo@gmail.com)
# BB84_server.py - version 1.0

import socket
import threading
from CUlib import *
from random import randint

from BB84_Alice import AliceActions as ACT_ALICE
from BB84_Bob import BobActions as ACT_BOB
from BB84_Eve import EveActions as ACT_EVE


class ServerActions:
    SEND_B = "make Alice and Bob announce the strings b and b' via public classical channel"
    DETECT_EAVESDROPPING = "try to detect the presence of Eve thanks to a possible inconsistency in the strings a and a'"
    CLEAR = "clear the CLI screen"


class BB84Server:
    def __init__(self):

        self.b = self.b1 = self.a = self.a1 = None
        self.menu_structure = [
            ServerActions.SEND_B,
            ServerActions.DETECT_EAVESDROPPING,
            ServerActions.CLEAR
            ]
        self.is_simulation_running = False
        
        # prepare for socket programming
        self.host = 'localhost'
        self.port = SERVER_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # used to store connected clients: can reject multiple connections and know when Alice & Bob are ready
        # client is stored as tuple: (socket, address as string)
        self.clients = {'Alice': None, 'Bob': None, 'Eve': None}
        # mutex for threading
        self.lock = threading.Lock()
        
        # thread to manage input
        self.tr_handle_input = threading.Thread(target = self.handle_input)
        # event for waiting when trying to get info from clients
        self.alice_info_event = threading.Event()
        self.bob_info_event = threading.Event()

        
    def get_client_socket(self, client_name):
        if self.clients[client_name] is None:
            return None
        else:
            return self.clients[client_name][0]

    ## region BB84: INTERESTING PART ABOUT BB84 PROTOCOL MANAGEMENT: quantum and classical channels

    def alice_request(self, request_type, request_info):
        bob_socket = self.get_client_socket('Bob')
        eve_socket = self.get_client_socket('Eve')
        
        if request_type == ACT_ALICE.SEND_QUBITS:
            print("[Server] Alice is sending qubits on the public quantum channel...", end="\n > ")

            # need to ServerActions.SEND_B before ServerActions.DETECT_EAVESDROPPING
            self.b = self.b1 = self.a = self.a1 = None
            
            if eve_socket is not None:
                print("[Server] Eve is eavesdropping!", end="\n > ")
                send(eve_socket, ACT_EVE.RECEIVE_QUBITS + request_info)
            else:
                print("[Server] Bob is processing the received qubits.", end="\n > ")
                send(bob_socket, ACT_BOB.RECEIVE_QUBITS + request_info)

        elif request_type == ACT_ALICE.SEND_B:
            if request_info == ',':
                # Bob is not up to date with Alice
                self.b = None
            else:
                self.b = request_info
                print("[Server] Alice announced the string b via public classical channel: [", self.b, "]", sep='', end="\n > ")
            # finally
            self.alice_info_event.set()

        elif request_type == ACT_ALICE.SEND_SOME_A:
            if request_info == '':
                self.a = None
            else:
                self.a = request_info
                print("[Server] Alice announced the requested bits from string a: [", self.a, "]", sep='', end="\n > ")
            # finally
            self.alice_info_event.set()


    def bob_request(self, request_type, request_info):
        
        if request_type == ACT_BOB.SEND_B1:
            self.b1 = request_info
            print("[Server] Bob  announced the string b' via public classical channel: [", self.b1, "]", sep='', end="\n > ")
            self.bob_info_event.set()

        elif request_type == ACT_BOB.SEND_SOME_A1:
            if request_info == '':
                self.a1 = None
            else:
                self.a1 = request_info
                print("[Server] Bob  announced the requested bits from string a': [", self.a1, "]", sep='', end="\n > ")
            # finally
            self.bob_info_event.set()


    def eve_request(self, request_type, request_info):
        bob_socket = self.get_client_socket('Bob')
        
        if request_type == ACT_EVE.SEND_QUBITS:
            if bob_socket is not None:
                print("[Server] Eve is sending qubits to Bob via public quantum channel...", end="\n > ")
                send(bob_socket, ACT_BOB.RECEIVE_QUBITS + request_info)
            else:
                print("[Server] Eve tried to send qubits to Bob, but Bob is not connected!", end="\n > ")


    ## end region BB84
        
    def start(self):
        # start server
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.show_menu()
        self.tr_handle_input.start()
        # listen to connection attempts
        while True:
            # wait until connection attempt from a client
            client_socket, client_address = self.socket.accept()
            # get client name: can be Alice, Bob or Eve
            client_name = receive(client_socket)
            # prepare and start thread to handle new client
            th_handle_client = threading.Thread(target = self.handle_client, args = (client_name, (client_socket, f'{client_address}'),))
            th_handle_client.start()


    def __send_b(self):
        # prepare sockets
        alice_socket = self.get_client_socket('Alice')
        bob_socket = self.get_client_socket('Bob')
            
        if (alice_socket is None) or (bob_socket is None):  # Alice or Bob are not connected -> invalid choice
            print("[Server] Alice and Bob are not both connected!", end="\n > ")
            return
        # else: Alice and Bob are connected
        
        # prepare (clear) events
        self.alice_info_event.clear()
        self.bob_info_event.clear()

        # ask to send strings b and b'
        send(alice_socket, ACT_ALICE.SEND_B)
        send(bob_socket, ACT_BOB.SEND_B1)

        # wait until both strings b and b' are arrived
        self.alice_info_event.wait()
        self.bob_info_event.wait()

        if self.b is None:  # Bob is not up to date with Alice
            print("[Server] Alice has made some changes and has not yet sent the new quantum state to Bob!",
                  "Make sure to follow all the desired steps in the correct order.", end="\n > ")
            return

        length_b = len(self.b)
        length_b1 = len(self.b1)
        if length_b == 0 or length_b1 == 0:
            print("[Server] The two strings must have at least one bit!",
                  "Make sure to follow all the desired steps in the correct order.", end="\n > ")
            return
        if (length_b != length_b1):
            print("[Server] The two strings do not have the same length!",
                  "Make sure to follow all the desired steps in the correct order.", end="\n > ")
            return
        
        # if here: b and b' can be compared -> send b' to Alice and b to Bob
        send(alice_socket, ACT_ALICE.RECEIVE_B1 + self.b1)
        send(bob_socket, ACT_BOB.RECEIVE_B + self.b)
        print("[Server] String b' sent to Alice. String b sent to Bob.", end="\n > ")


    def __detect_eavesdropping(self):
        # prepare sockets
        alice_socket = self.get_client_socket('Alice')
        bob_socket = self.get_client_socket('Bob')
            
        if (alice_socket is None) or (bob_socket is None):  # Alice or Bob are not connected -> invalid choice
            print("[Server] Alice and Bob are not both connected!", end="\n > ")
            return
        # else: Alice and Bob are connected
        
        error_sentence = "Before trying to detect Eve: " + ServerActions.SEND_B + ". Also make sure to have followed all the desired steps in the correct order."
        if (self.b is None) or (self.b1 is None):
            print("[Server]", error_sentence, end="\n > ")
            return
        len_b = len(self.b)
        len_b1 = len(self.b1)
        if (len_b == 0) or (len_b1 == 0):
            print("[Server] Strings b and b' must have at least one bit!", error_sentence, end="\n > ")
            return
        if len_b != len_b1:
            print("[Server] Strings b and b' do not have the same length!", error_sentence, end="\n > ")
            return
        # if here: b and b' are valid
        
        # count how many bits there will be in common key -> if 0: Eve detection will be impossible
        len_a = 0
        for i in range(len_b):
            if (self.b[i] == self.b1[i]):
                len_a += 1

        if len_a == 0:
            print("[Server] Strings b and b' are different bit by bit, for every bit, so the key is empty.",
                  "Try again the whole process.", end="\n > ")
            return
        # if here: the common key will have length == len_a
        
        print("[Server] Trying to detect Eve... Alice and Bob shared strings b and b' respectively:")
        print_in_table([
            ["string b", self.b],
            ["string b'", self.b1]
            ])
        print("Alice and Bob have created locally the key from strings a and a',",
              "discarding bits relating to qubits where Bob measured in different basis than Alice prepared.")
        print(f"Enter the number of bits to share (from the common key), from 1 to {len_a}", end="\n > ")
        bits_count = input_int(1, len_a, f"Error: enter a valid number! (integer between 1 and {len_a})\n > ")
        
        # calculate and show percentage of success in detection of eavesdropping 
        p_detect = 1 - (0.75) ** bits_count
        p_detect_percent = int(10000 * p_detect) / 100  # precision: xx.xx%
        print(f" > The percentage of success in detection of eavesdropping is {p_detect_percent}%", end="\n > ") 

        # select random positions
        # at the same time -> create string <key-request>: '?' in desired positions, 'x' in other positions
        possible_positions = [i for i in range(len_a)]
        key_request = 'x' * len_a
        for _ in range(bits_count):
            i = randint(0, len(possible_positions) - 1)
            pos = possible_positions.pop(i)
            key_request = key_request[:pos] + '?' + key_request[pos+1:]

        ## send key-request to Alice and Bob        
        # prepare (clear) events
        self.alice_info_event.clear()
        self.bob_info_event.clear()

        # ask to send key a and a' filled with info
        send(alice_socket, ACT_ALICE.SEND_SOME_A + key_request)
        send(bob_socket, ACT_BOB.SEND_SOME_A1 + key_request)

        # wait until both strings a and a' are arrived
        self.alice_info_event.wait()
        self.bob_info_event.wait()

        if (self.a is None) or (self.a1 is None):
            print("[Server] Strings a and/or a' changed!", ServerActions.SEND_B, end="\n > ")
            return

        # check received strings and print conclusion
        if self.a == self.a1:
            print("[Server] The checked bits in the strings a and a' are the same (as they should be).",
                  "Therefore, no eavesdropping by Eve is detected...", sep='\n', end="\n > ")
        else:
            print("[Server] The checked bits in the strings a and a' are NOT the same!",
                  "Therefore, eavesdropping by Eve is detected!", sep='\n', end="\n > ")


    def handle_input(self):
        while True:
            # input global action from server cli
            while True:
                choice = input_int(1, len(self.menu_structure), " > ") - 1
                if self.is_simulation_running:
                    print("[Simulation in progress]", end="\n > ")
                else:
                    break

            # make Alice and Bob announce the strings b and b' via public classical channel
            if choice == self.menu_structure.index(ServerActions.SEND_B):
                print(end=" > ")
                self.__send_b()
                
            elif choice == self.menu_structure.index(ServerActions.DETECT_EAVESDROPPING):
                print(end=" > ")
                self.__detect_eavesdropping()
                
            elif choice == self.menu_structure.index(ServerActions.CLEAR):
                self.show_menu()
            

    def handle_client(self, client_name, client_info):
        # use mutex: prevents concurrent access and helps maintain the integrity of the data structures for class variables
        with self.lock:
            client_socket, client_address = client_info
            # reject connection if client of the same type is already connected
            try:
                if self.clients[client_name] is not None:
                    send(client_socket, f"{client_name} is already connected!")
                    client_socket.close()
                    return
            except KeyError:
                print(f"[Server] {client_name} is not a valid client!", end='\n > ')
                return
            # else store new client and tell client it's connected
            send(client_socket, TXT_CLIENT_CONNECTED)
            self.clients[client_name] = client_info
            # if Alice and Bob are connected: send "ready" message to all connected clients
            if (self.clients['Alice'] is not None) and (self.clients['Bob'] is not None):
                self.broadcast(TXT_READY)
            # show server menu
            self.show_menu()

        # now handle client
        
        # client that asks to wait is the one that must ask to continue; it is called "client-in-simulation"
        client_in_simulation = False
                        
        while True:
            try:
                request_type = receive(client_socket)
                if not request_type:  # handle disconnection
                    raise ConnectionResetError
                else:
                    # manage direct messages
                    if request_type == TXT_WAIT:
                        self.broadcast(TXT_WAIT)
                        client_in_simulation = True
                        self.is_simulation_running = True
                    elif request_type == TXT_CONTINUE:
                        self.broadcast(TXT_CONTINUE)
                        client_in_simulation = False
                        self.is_simulation_running = False

                    else:
                        # get info parameters about request as string
                        request_info = receive(client_socket)
                        if not request_info:  # handle disconnection
                            raise ConnectionResetError
                        if request_info == '.':
                            request_info = ''
                        # handle request
                        if client_name == 'Alice':
                            self.alice_request(request_type, request_info)
                        elif client_name == 'Bob':
                            self.bob_request(request_type, request_info)
                        else:  # client_name == 'Eve'
                            self.eve_request(request_type, request_info)
                    
            except ConnectionResetError:
                # client disconnected
                with self.lock:
                    self.clients[client_name] = None
                client_socket.close()
                # if was client-in-simulation: make all continue again
                self.broadcast(TXT_CONTINUE)
                # if this disconnection was Alice or Bob: not all necessary clients are connected -> send "not ready" message to all
                if (client_name == 'Alice') or (client_name == 'Bob'):
                    self.broadcast(TXT_NOT_READY)
                # show server menu
                self.show_menu()

                break


    def broadcast(self, message):
        # send message to all connected clients
        connected_clients = self.get_connected_clients()
        for connected_client in connected_clients:
            send(self.clients[connected_client][0], message)


    def get_connected_clients(self):
        # return names of the connected clients (in list)
        return [client_type for client_type, client_info in self.clients.items() if client_info is not None]
    

    def show_menu_head(self):
        # show the head of the menu in the console
        clear()
        print(f"[Server active on {self.host}:{self.port}]")
        # show clients' status in a nice box
        lines = []
        for client_name, client_info in self.clients.items():
            if client_info is None:
                lines.append(f"{client_name} is NOT connected")
            else:
                lines.append(f"{client_name} is connected: {client_info[1]}")
        print_in_box(lines)


    def show_menu(self):
        self.show_menu_head()
        print("\n[Global actions]")
        print_menu_options(self.menu_structure)
        print("----", end='\n > ')


if __name__ == "__main__":
    
    set_title("Server")
    server = BB84Server()
    server.start()








