# Quantum Key Distribution simulation: BB84 protocol
# by Manuel Maiuolo (manuelmaiuolo@gmail.com)
# BB84_Alice.py - version 1.0

from random import randint
from BB84_client import BB84Client
from BB84lib import *
from CUlib import *

class AliceActions():
    ## Direct actions
    # Local
    GENERATE_BITS = "generate two random strings of n-bits: a, b"
    PREPARE_QUBITS = "prepare n qubits accordingly to a and b"
    CLEAR = "clear the CLI screen"
    CHANGE_INFO_SHOW_METHOD = "change how Alice's current information are shown"
    
    # Server
    SEND_QUBITS = "send quantum state to Bob via public quantum channel"

    ## Indirect actions
    SEND_B = "SEND_B"
    RECEIVE_B1 = "RECEIVE_B1"
    SEND_SOME_A = "SEND_SOME_A"
    

class Alice(BB84Client):
    def __init__(self):
        
        self.menu_structure = [
            AliceActions.GENERATE_BITS,
            AliceActions.PREPARE_QUBITS,
            AliceActions.SEND_QUBITS,
            AliceActions.CLEAR,
            AliceActions.CHANGE_INFO_SHOW_METHOD
            ]
        
        menu_functions = (len(self.menu_structure), self.menu_choice, self.show_menu)
        super().__init__("Alice", self.handle_response, menu_functions)
        
        self.a = ""
        self.b = ""
        self.basis = []
        self.qubits = []

        self.info_show_method_compact = False
        
        self.up_to_date = True
        self.is_bob_up_to_date = True


    def handle_response(self, response):

        if response.find(AliceActions.SEND_B) == 0:
            self.send_message(AliceActions.SEND_B)
            if self.is_bob_up_to_date:  # Bob is up to date with Alice
                if self.b == '':
                    self.send_message('.')
                else:
                    self.send_message(self.b)
            else:  # Bob is not up to date with Alice
                self.send_message(',')

        elif response.find(AliceActions.RECEIVE_B1) == 0:
            self.__receive_b1(response[len(AliceActions.RECEIVE_B1):])

        elif response.find(AliceActions.SEND_SOME_A) == 0:
            self.__send_some_a(response[len(AliceActions.SEND_SOME_A):])
            
        # else: another message from server -> not important if not considered


    def __generate_bits(self):
        print("Enter the number 'n' of bits for each string", end="\n > ")
        # 0 is valid <-> reset a and b
        n = input_int(0, 50, "Error: enter an integer between 0 and 50\n > ")
        self.a, self.b = "", ""
        # start (pseudo-)random bit generation:
        for _ in range(n):
            self.a += str(randint(0, 1))
            self.b += str(randint(0, 1))
        # done
        self.up_to_date = False
        self.is_bob_up_to_date = False


    def __prepare_qubits(self):
        self.basis = []
        self.qubits = []
        n = len(self.a)  # due to construction: == len(self.b)
        for i in range(n):  # bit by bit
            # basis
            basis = Basis()
            basis.set_from_b(self.b[i])
            self.basis.append(basis)
            # qubit
            qubit = Qubit()
            qubit.set_from_a_and_basis(self.a[i], basis)
            self.qubits.append(qubit)
        # done
        self.up_to_date = True


    def __receive_b1(self, b1):
        new_a = ''  # will be the new string a after the removals, but with spaces
        new_b = ''  # will be the new string b after the removals
        
        for i in range(len(b1)):
            if b1[i] == self.b[i]:
                new_a += self.a[i]
                new_b += self.b[i]
            else:
                new_a += ' '
        
        print("[Process] discard qubits where Bob measured in different basis than Alice prepared")
        print_in_table([
            ["string a", self.a],
            ["string b", self.b],
            ["Bob's string b'", b1],
            ["new string a", new_a]
            ])
        print()

        self.a = new_a.replace(' ', '')
        self.b = new_b
        # update also basis and qubits
        self.__prepare_qubits()
        
        self.show_information(_end='\n > ')


    def __send_some_a(self, req_a):
        if (len(req_a) != len(self.a)) or (not self.is_bob_up_to_date):  # request not up to date
            self.send_message(AliceActions.SEND_SOME_A)
            self.send_message('.')
            return
        
        # create obfuscated string a: only requested bits are shown
        info_a = ''
        i = 0
        for ch in req_a:
            if ch == '?':
                info_a += self.a[i]
            else:  # ch == 'x'
                info_a += 'x'
            i += 1

        # send obfuscated string a to server for comparison with bits in string a' from Bob
        self.send_message(AliceActions.SEND_SOME_A)
        self.send_message(info_a)
    

    def menu_choice(self, choice):
        wait_to_continue = False

        if choice == self.menu_structure.index(AliceActions.GENERATE_BITS):
            # generate bits
            self.__generate_bits()
            return None
        
        elif choice == self.menu_structure.index(AliceActions.PREPARE_QUBITS):
            # prepare qubits
            self.__prepare_qubits()
            return None
        
        elif choice == self.menu_structure.index(AliceActions.SEND_QUBITS):
            # send qubits
            info = quantum_list_to_compact_string(self.qubits)
            # Bob will be up to date (even if Eve eavesdrops, because from Eve to Bob is automatic)
            self.is_bob_up_to_date = self.up_to_date
                
        elif choice == self.menu_structure.index(AliceActions.CLEAR):
            # clear CLI screen and show menu again
            clear()
            self.show_menu()
            return None
                
        elif choice == self.menu_structure.index(AliceActions.CHANGE_INFO_SHOW_METHOD):
            # change how informations are shown
            self.info_show_method_compact = not self.info_show_method_compact
            clear()
            self.show_menu()
            return None
            
        else:  # not a valid choice
            return None
        
        return self.menu_structure[choice], info, wait_to_continue


    def show_information(self, _end="\n"):
        method = 'compact' if self.info_show_method_compact else 'normal'
        print(f"[Alice's current information ({method} method)]")

        if self.info_show_method_compact:  # compact method
            print_in_table([
                ["string a", self.a],
                ["string b", self.b],
                ["basis", quantum_list_to_compact_string(self.basis)],
                ["encoded qubits", quantum_list_to_compact_string(self.qubits)]
                ], min_cols = 2)
        else:  # normal method
            print_in_table([
                ["string a", list(self.a)],
                ["string b", list(self.b)],
                ["basis", self.basis],
                ["encoded qubits", self.qubits]
                ], min_cols = 2)
        
        if not self.up_to_date:
            print(" Note: basis and qubits are not updated to last generated a and b. Select action",
                  self.menu_structure.index(AliceActions.PREPARE_QUBITS) + 1,
                  "from the menu!")
        elif not self.is_bob_up_to_date:
            print(" Note: Bob is unaware of the changes made locally by Alice. Select action",
                  self.menu_structure.index(AliceActions.SEND_QUBITS) + 1,
                  "from the menu!")
            
        print(end=_end)


    def show_menu(self, prefix = ''):
        print(prefix, end='')
        self.show_information()
        print("[Alice's direct actions]")
        print_menu_options(self.menu_structure)
        print("------\nEnter the number of the action to be performed", end="\n > ")


if __name__ == "__main__":

    set_title("Alice")
    alice = Alice()
    alice.connect()
