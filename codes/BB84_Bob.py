# Quantum Key Distribution simulation: BB84 protocol
# by Manuel Maiuolo (manuelmaiuolo@gmail.com)
# BB84_Bob.py - version 1.0

from BB84_client import BB84Client
from BB84lib import *
from CUlib import *
from time import sleep as WaitSeconds

class BobActions():
    ## Direct actions
    # Local
    SET_RECEIVING_QUBITS_RATE = "set the rate at which to show received qubits from Alice"
    CLEAR = "clear the CLI screen"
    CHANGE_INFO_SHOW_METHOD = "change how Bob's current information are shown"

    # Server: None

    ## Indirect actions
    RECEIVE_QUBITS = "RECEIVE_QUBITS"
    SEND_B1 = "SEND_B1"
    RECEIVE_B = "RECEIVE_B"
    SEND_SOME_A1 = "SEND_SOME_A1"
    

class Bob(BB84Client):
    def __init__(self):
        
        self.menu_structure = [
            BobActions.SET_RECEIVING_QUBITS_RATE,
            BobActions.CLEAR,
            BobActions.CHANGE_INFO_SHOW_METHOD
            ]

        menu_functions = (len(self.menu_structure), self.menu_choice, self.show_menu)
        super().__init__("Bob", self.handle_response, menu_functions)
        
        self.a1 = ""
        self.b1 = ""
        self.basis = []
        self.qubits = []

        self.info_show_method_compact = False
        self.receive_qubits_rate = 'fast'


    def handle_response(self, response):
        
        if response.find(BobActions.RECEIVE_QUBITS) == 0:
            self.send_message(TXT_WAIT)
            self.__receive_qubits(response[len(BobActions.RECEIVE_QUBITS):])
            self.send_message(TXT_CONTINUE)  # allow other clients to continue their scripts

        elif response.find(BobActions.SEND_B1) == 0:
            self.send_message(BobActions.SEND_B1)
            if self.b1 == '':
                self.send_message('.')
            else:
                self.send_message(self.b1)

        elif response.find(BobActions.RECEIVE_B) == 0:
            self.__receive_b(response[len(BobActions.RECEIVE_B):])

        elif response.find(BobActions.SEND_SOME_A1) == 0:
            self.__send_some_a1(response[len(BobActions.SEND_SOME_A1):])
            
        # else: another message from server -> not important if not considered


    def __set_receiving_qubits_rate(self):
        print("Select the rate at which to show received qubits from Alice",
              f"[current rate: '{self.receive_qubits_rate}']")
        print("1) slow", "2) fast", "3) instant", sep='\n')
        print("----", end="\n > ")
        val = input_int(1, 3, "Error: enter a valid choice (an integer number from 1 to 3)\n----\n > ")
        
        if val == 1:  # slow
            self.receive_qubits_rate = 'slow'
        elif val == 2:  # fast
            self.receive_qubits_rate = 'fast'
        else:  # <-> val == 3 <-> instant
            self.receive_qubits_rate = 'instant'


    def __print_info_during_simulation(self, wait_for):
        if wait_for <= 0:
            return
        clear()
        print(" Receiving qubits . . .")
        self.show_information()
        WaitSeconds(wait_for)


    def __receive_qubits(self, qubits_str):   
        self.a1 = ""
        self.b1 = ""
        self.basis = []
        self.qubits = []
        
        if self.receive_qubits_rate == 'slow':
            wait_long = 1.2
        elif self.receive_qubits_rate == 'fast':
            wait_long = 0.4
        else:  # self.receive_qubits_rate == 'instant'
            wait_long = 0
        wait_short = 0.5 * wait_long
        
        for qubit_str in qubits_str:
            self.__print_info_during_simulation(wait_long)
            # qubit
            self.qubits.append(Qubit(qubit_str))
            self.__print_info_during_simulation(wait_short)
            # string b'
            self.b1 += str(randint(0, 1))
            self.__print_info_during_simulation(wait_short)
            # basis
            basis = Basis()
            basis.set_from_b(self.b1[-1])
            self.basis.append(basis)
            self.__print_info_during_simulation(wait_short)
            # string a'
            measurement = self.qubits[-1].measure(basis)
            self.a1 += '0' if (measurement == +1) else '1'
        clear()


    def __receive_b(self, b):
        new_a1 = ''  # will be the new string a' after the removals, but with spaces
        new_b1 = ''  # will be the new string b' after the removals
        new_basis = []
        new_qubits = []
        
        for i in range(len(b)):
            if b[i] == self.b1[i]:
                new_a1 += self.a1[i]
                new_b1 += self.b1[i]
                new_basis.append(self.basis[i])
                new_qubits.append(self.qubits[i])
            else:
                new_a1 += ' '
        
        print("[Process] discard qubits where Bob measured in different basis than Alice prepared")
        print_in_table([
            ["string a'", self.a1],
            ["string b'", self.b1],
            ["Alice's string b", b],
            ["new string a'", new_a1]
            ])
        print()

        self.a1 = new_a1.replace(' ', '')
        self.b1 = new_b1
        # update also basis and qubits
        self.basis = new_basis
        self.qubits = new_qubits
        
        self.show_information(_end='\n > ')


    def __send_some_a1(self, req_a1):
        if len(req_a1) != len(self.a1):  # request not up to date
            self.send_message(BobActions.SEND_SOME_A)
            self.send_message('.')
            return
        
        # create obfuscated string a': only requested bits are shown
        info_a1 = ''
        i = 0
        for ch in req_a1:
            if ch == '?':
                info_a1 += self.a1[i]
            else:  # ch == 'x'
                info_a1 += 'x'
            i += 1

        # send obfuscated string a' to server for comparison with bits in string a from Alice
        self.send_message(BobActions.SEND_SOME_A1)
        self.send_message(info_a1)
        

    def menu_choice(self, choice):
        
        if choice == self.menu_structure.index(BobActions.SET_RECEIVING_QUBITS_RATE):
            # set receiving qubits rate
            self.__set_receiving_qubits_rate()
            return None
                
        elif choice == self.menu_structure.index(BobActions.CLEAR):
            # clear CLI screen and show menu again
            clear()
            self.show_menu()
            return None
                
        elif choice == self.menu_structure.index(BobActions.CHANGE_INFO_SHOW_METHOD):
            # change how informations are shown
            self.info_show_method_compact = not self.info_show_method_compact
            clear()
            self.show_menu()
            return None
        
        # else: not a valid choice
            return None


    def show_information(self, _end="\n"):
        method = 'compact' if self.info_show_method_compact else 'normal'
        print(f"[Bob's current information ({method} method)]")

        if self.info_show_method_compact:  # compact method
            print_in_table([
                ["encoded qubits", quantum_list_to_compact_string(self.qubits)],
                ["string b'", self.b1],
                ["basis", quantum_list_to_compact_string(self.basis)],
                ["string a'", self.a1]
                ], min_cols = 2)
        else:  # normal method
            print_in_table([
                ["encoded qubits", self.qubits],
                ["string b'", list(self.b1)],
                ["basis", self.basis],
                ["string a'", list(self.a1)]
                ], min_cols = 2)
        
        print(end=_end)


    def show_menu(self, prefix = ''):
        print(prefix, end='')
        self.show_information()
        print("[Bob's direct actions]")
        print_menu_options(self.menu_structure)
        print("------\nEnter the number of the action to be performed", end="\n > ")
    

if __name__ == "__main__":
    
    set_title("Bob")
    bob = Bob()
    bob.connect()
