# Quantum Key Distribution simulation: BB84 protocol
# by Manuel Maiuolo (manuelmaiuolo@gmail.com)
# CUlib.py - version 1.0

# Common Useful Library
from os import system as os_system, name as os_name

# parameters to create local TCP for BB84_client.py
SERVER_PORT = 12084
BUFFER = 1024
###

# constants used from BB84_server.py and from BB84_client.py
TXT_CLIENT_CONNECTED = "client connected"
TXT_CAN_RECEIVE = "can receive"
TXT_READY = "ready"
TXT_NOT_READY = "not ready"
TXT_WAIT = "wait"
TXT_CONTINUE = "continue"
###

"""loop input to get valid integer value in [minVal..maxVal]"""
def input_int(minVal, maxVal, errorSentence=''):
    valid = False
    while not valid:
        try:
            result = int(input())
            if (result < minVal) or (result > maxVal):
                print(errorSentence, end='')
            else:
                valid = True
        except ValueError:
            print(errorSentence, end='')
    return result

"""wait for message from connection_socket"""
def receive(connection_socket):
    return connection_socket.recv(BUFFER).decode('utf-8')

"""send message to connection_socket"""
def send(connection_socket, message):
    connection_socket.send(message.encode('utf-8'))

"""clear console screen"""
def clear():
    if os_name == 'nt':  # for windows
        os_system('cls')
    else:  # for mac and linux(here, os.name is 'posix')
        os_system('clear')

"""set console title"""
def set_title(title):
    if os_name == 'nt':  # for windows
        os_system(f"title {title}")
    else:  # for mac and linux(here, os.name is 'posix')
        print(f'\33]0;{title}\a', end='', flush=True)

"""print list elements as lines in a box"""
def print_in_box(lines):
    maxLen = 0
    for line in lines:
        maxLen = max(maxLen, len(line))

    # +2 counts initial and final space
    boxHorizontal = '+' + '-' * (maxLen + 2) + '+'
    print(boxHorizontal)
    for line in lines:
        print('|', line + (' ' * (maxLen - len(line))), '|')
    print(boxHorizontal)

"""print each tuple in list as row in a table"""
def print_in_table(rows, min_cols=0):
    # if element is iterable and not string: expand row to have each element in a new column
    newRows = []
    for row in rows:
        newRow = []
        for cell in row:
            if type(cell) is str:
                newRow.append(cell)
            else:
                try:
                    newRow.extend(cell)
                except TypeError:
                    newRow.append(cell)
        # consider appending columns to respect min_cols request
        colsToAdd = max(0, min_cols-len(newRow))
        if colsToAdd > 0:
            for _ in range(colsToAdd):
                newRow.append('')
        newRows.append(newRow)
    rows = newRows

    # calculate lengths
    maxLens = []
    for row in rows:
        for i in range(len(row)):
            cellLength = len(str(row[i]))
            try:
                maxLens[i] = max(maxLens[i], cellLength)
            except IndexError:
                maxLens.append(cellLength)

    strHor = "+"
    for maxLen in maxLens:
        # example of cell in table: " abc |" -> count 2 spaces and | paired with +
        strHor += '-' * (maxLen + 2) + '+'

    print(strHor)
    for row in rows:
        print(end='|')  # start row
        for i in range(len(maxLens)):
            try:
                cellText = str(row[i])
                cellLength = len(cellText)
            except IndexError:
                # in case this row doesn't have all the cells -> suppose last cells blank
                cellLength = 0
                cellText = ''
            # calculate spaces before and after to allign text to center
            spacesBefore = (maxLens[i] - cellLength) // 2
            spacesAfter = maxLens[i] - cellLength - spacesBefore
            # print cell
            print(' ', (' ' * spacesBefore), cellText, (' ' * spacesAfter), sep='', end=' |')
        # end row
        print()
    print(strHor)

"""print list elements as numbered options in a menu"""
def print_menu_options(structure):
    i = 1
    for option in structure:
        print(f"{i}) {option}")
        i += 1









