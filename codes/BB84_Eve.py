# Quantum Key Distribution simulation: BB84 protocol
# by Manuel Maiuolo (manuelmaiuolo@gmail.com)
# BB84_Eve.py - version 1.0

from BB84_client import BB84Client
from BB84lib import *
from CUlib import *
from time import sleep as WaitSeconds

class EveActions():
    ## Direct actions
    # Local
    SET_RECEIVING_QUBITS_RATE = "set the rate at which to show eavesdropped qubits from Alice"
    CLEAR = "clear the CLI screen"
    CHANGE_INFO_SHOW_METHOD = "change how Eve's current information are shown"
    
    # Server: None
    
    ## Indirect actions
    RECEIVE_QUBITS = "RECEIVE_QUBITS"
    SEND_QUBITS = "SEND_QUBITS"
    

class Eve(BB84Client):
    def __init__(self):
        
        self.menu_structure = [
            EveActions.SET_RECEIVING_QUBITS_RATE,
            EveActions.CLEAR,
            EveActions.CHANGE_INFO_SHOW_METHOD
            ]

        menu_functions = (len(self.menu_structure), self.menu_choice, self.show_menu)
        super().__init__("Eve", self.handle_response, menu_functions)
        
        self.a_eve = ""
        self.b_eve = ""
        self.basis = []
        self.qubits = []

        self.info_show_method_compact = False
        self.receive_qubits_rate = 'fast'


    def handle_response(self, response):
        
        if response.find(EveActions.RECEIVE_QUBITS) == 0:
            self.send_message(TXT_WAIT)
            self.__receive_qubits(response[len(EveActions.RECEIVE_QUBITS):])
            self.send_message(TXT_CONTINUE)  # allow other clients to continue their scripts

            # wait for server to be ready to receive again
            WaitSeconds(0.5)
            # now automatically send qubits to Bob
            info = ""  # will be qubits
            for qubit in self.qubits:
                info += str(qubit.value)
            self.send_message(EveActions.SEND_QUBITS)
            self.send_message(info)
            print("Quantum state sent to Bob.", end="\n\n")
            
        # else: another message from server -> not important if not considered


    def __set_receiving_qubits_rate(self):
        print("Select the rate at which to show eavesdropped qubits from Alice",
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
        self.a_eve = ""
        self.b_eve = ""
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
            self.b_eve += str(randint(0, 1))
            self.__print_info_during_simulation(wait_short)
            # basis
            basis = Basis()
            basis.set_from_b(self.b_eve[-1])
            self.basis.append(basis)
            self.__print_info_during_simulation(wait_short)
            # string a'
            measurement = self.qubits[-1].measure(basis)
            self.a_eve += '0' if (measurement == +1) else '1'

        clear()
        self.__print_info_during_simulation(0.5)


    def menu_choice(self, choice):
        
        if choice == self.menu_structure.index(EveActions.SET_RECEIVING_QUBITS_RATE):
            # set receiving qubits rate
            self.__set_receiving_qubits_rate()
            return None
                
        elif choice == self.menu_structure.index(EveActions.CLEAR):
            # clear CLI screen and show menu again
            clear()
            self.show_menu()
            return None
                
        elif choice == self.menu_structure.index(EveActions.CHANGE_INFO_SHOW_METHOD):
            # change how informations are shown
            self.info_show_method_compact = not self.info_show_method_compact
            clear()
            self.show_menu()
            return None
        
        # else: not a valid choice
            return None


    def show_information(self, _end="\n"):
        method = 'compact' if self.info_show_method_compact else 'normal'
        print(f"[Eve's current information ({method} method)]")

        if self.info_show_method_compact:  # compact method
            print_in_table([
                ["encoded qubits eavesdropped", quantum_list_to_compact_string(self.qubits)],
                ["string b chosen by Eve", self.b_eve],
                ["basis according to string b", quantum_list_to_compact_string(self.basis)],
                ["string a according to Eve", self.a_eve]
                ], min_cols = 2)
        else:  # normal method
            print_in_table([
                ["encoded qubits eavesdropped", self.qubits],
                ["string b chosen by Eve", list(self.b_eve)],
                ["basis according to string b", self.basis],
                ["string a according to Eve", list(self.a_eve)]
                ], min_cols = 2)
        
        print(end=_end)


    def show_menu(self, prefix = ''):
        print(prefix, end='')
        self.show_information(_end='')
        print("Eve's presence automatically ensures that the qubits sent by Alice are eavesdropped by Eve,\nand the new qubits for Bob are sent by Eve.\n")
        print("[Eve's direct actions]")
        print_menu_options(self.menu_structure)
        print("------\nEnter the number of the action to be performed", end="\n > ")


if __name__ == "__main__":
    
    set_title("Eve")
    eve = Eve()
    eve.connect()
