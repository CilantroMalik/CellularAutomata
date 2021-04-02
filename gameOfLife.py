import random
import time
import os
import argparse
import sys
from pynput.keyboard import Key, Listener, Events, KeyCode

# feature wishlist:
# - clipboard interaction with saving seeds?
# - generate a starting seed that produces a given end state

BOARD_SIZE = 25
DENSITY_FACTOR = 0.25
SPEED = 0.3

parser = argparse.ArgumentParser()
parser.add_argument("--size", action='store', type=int, required=False)
parser.add_argument("--density", action='store', type=float, required=False)
parser.add_argument("--speed", action='store', type=float, required=False)
args = parser.parse_args()
if args.size:
    BOARD_SIZE = args.size
if args.density:
    DENSITY_FACTOR = args.density
if args.speed:
    SPEED = args.speed


def keyPressed(key):
    global wantsToQuit
    if key == 's':
        print("--- Starting Seed ---")
        printBoard(startingSeed)
    if key == 'q':
        wantsToQuit = True


def keyReleased(key):
    global wantsToQuit
    if key == 'r':
        wantsToQuit = False

def generateSeed():
    global board, startingSeed, savedSeed
    if savedSeed:
        startingSeed = [[item for item in board[x]] for x in range(len(board))]
        return
    board = []
    for _ in range(BOARD_SIZE):
        tempRow = []
        for _ in range(BOARD_SIZE):
            tempRow.append("▉▉" if random.random() <= DENSITY_FACTOR else "  ")
        board.append(tempRow)
    startingSeed = [[item for item in board[x]] for x in range(len(board))]


def adj(r, c):
    adjacents = []
    possibleIndices = [(r-1, c-1), (r-1, c+1), (r+1, c-1), (r+1, c+1), (r-1, c), (r+1, c), (r, c-1), (r, c+1)]
    for coords in possibleIndices:
        if 0 <= coords[0] < BOARD_SIZE and 0 <= coords[1] < BOARD_SIZE:
            adjacents.append(coords)
    return adjacents


def printBoard(someBoard):
    for r in range(BOARD_SIZE):
        print("|".join(someBoard[r]))


def encodeBoard(someBoard):
    encodedString = ""
    for r in range(BOARD_SIZE):
        encodedString += "".join([("0" if cell == "  " else "1") for cell in someBoard[r]])
        encodedString += "/"
    return encodedString[:-1]


def parseBoard(encoded):
    parsedBoard = []
    for row in encoded.split("/"):
        currentRow = []
        for cell in row:
            currentRow.append("  " if cell == "0" else "▉▉")
        parsedBoard.append(currentRow)
    return parsedBoard


def runSimulation():
    global board, terminateIn, stateSnapshot, prevStateSnapshot, tertiarySnapshot, stateMessage, wantsToRestart
    os.system('clear')
    printBoard(board)
    time.sleep(SPEED)
    while True:
        if terminateIn > 0:
            terminateIn -= 1
        os.system('clear')
        willBeBorn = []
        willDie = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                countAlive = 0
                for cell in adj(row, col):
                    if board[cell[0]][cell[1]] == "▉▉":
                        countAlive += 1
                if countAlive > 3 and board[row][col] == "▉▉":
                    willDie.append((row, col))
                if countAlive < 2 and board[row][col] == "▉▉":
                    willDie.append((row, col))
                if countAlive == 3 and board[row][col] == "  ":
                    willBeBorn.append((row, col))
        for cell in willBeBorn:
            board[cell[0]][cell[1]] = "▉▉"
        for cell in willDie:
            board[cell[0]][cell[1]] = "  "
        if board == prevStateSnapshot != [] and stateMessage == "":
            stateMessage = "The ecosystem will permanently oscillate between two states, terminating"
            terminateIn = 6
        if board == tertiarySnapshot != [] and stateMessage == "":
            stateMessage = "The ecosystem will permanently oscillate between three states, terminating"
            terminateIn = 9
        tertiarySnapshot = [[item for item in prevStateSnapshot[x]] for x in range(len(prevStateSnapshot))]
        prevStateSnapshot = [[item for item in stateSnapshot[x]] for x in range(len(stateSnapshot))]
        stateSnapshot = [[item for item in board[x]] for x in range(len(board))]
        printBoard(board)
        if stateSnapshot == prevStateSnapshot != [] and stateMessage == "":
            stateMessage = "The ecosystem has reached permanent stasis, terminating"
            terminateIn = 4
        if terminateIn == 0 or wantsToQuit:
            break
        if stateMessage != "":
            print(stateMessage)
        time.sleep(SPEED)


def resetSimulation():
    global board, startingSeed, stateSnapshot, prevStateSnapshot, tertiarySnapshot, terminateIn, stateMessage, savedSeed
    board, startingSeed, stateSnapshot, prevStateSnapshot, tertiarySnapshot = [], [], [], [], []
    terminateIn, stateMessage, savedSeed = -1, "", False


board = []
startingSeed = []
stateSnapshot = []
prevStateSnapshot = []
tertiarySnapshot = []
terminateIn = -1
stateMessage = ""
wantsToQuit = False
savedSeed = False

# with Listener(on_press=keyPressed, on_release=keyReleased) as listener:
#     listener.join()

print("--- Options ---")
print("Enter: start the simulation with a random seed")
print("c: create a starting configuration in real time")
print("l: load the simulation from a saved seed")
print("o: override default simulation parameters")
action = input("Choose your options (as many as you want, but not both l and c): ")
if "l" in action:
    board = parseBoard(input("Paste in your board code here: "))
    savedSeed = True
if "o" in action:
    if "l" in action:
        print("Parameters to override are speed (s).")
    elif "c" in action:
        print("Parameters to override are board size (b) or speed (s).")
    else:
        print("Parameters to override are board size (b), density factor (d), or speed (s).")
    while True:
        override = input("Type in the corresponding letter, then a space, then the new value: ").split(" ")
        try:
            if override[0] == 'b':
                BOARD_SIZE = int(override[1])
            elif override[0] == 'd':
                DENSITY_FACTOR = float(override[1])
            elif override[0] == 's':
                SPEED = float(override[1])
            again = input("Type o to override another parameter, or enter to start the simulation: ")
            if again == "":
                break
        except ValueError:
            print("Invalid parameter value entered.")
            continue
if "c" in action:
    quit = False
    boardBuilder = [["  "]*BOARD_SIZE for _ in range(BOARD_SIZE)]
    focus = [0, 0]
    while True:
        os.system('clear')
        temp = boardBuilder[focus[0]][focus[1]]
        boardBuilder[focus[0]][focus[1]] = "··"
        printBoard(boardBuilder)
        boardBuilder[focus[0]][focus[1]] = temp
        with Events() as events:
            print("> ")
            event = events.get(0.001 if quit else 100000)
            if quit:
                break
            if event.key == Key.up:
                if focus[0] != 0:
                    focus[0] -= 1
            elif event.key == Key.down:
                if focus[0] != BOARD_SIZE-1:
                    focus[0] += 1
            elif event.key == Key.left:
                if focus[1] != 0:
                    focus[1] -= 1
            elif event.key == Key.right:
                if focus[1] != BOARD_SIZE-1:
                    focus[1] += 1
            elif event.key == KeyCode.from_char("1"):
                boardBuilder[focus[0]][focus[1]] = "▉▉"
            elif event.key == KeyCode.from_char("2"):
                boardBuilder[focus[0]][focus[1]] = "  "
            elif event.key == KeyCode.from_char("q"):
                quit = True
        time.sleep(0.1)
    board = [[item for item in boardBuilder[x]] for x in range(len(boardBuilder))]
    savedSeed = True

generateSeed()
runSimulation()

while True:
    purge = input("Simulation finished. Press enter to continue.")
    print("--- Options ---")
    print("Enter: restart the simulation")
    print("s: save this starting seed")
    print("q: quit the playground")
    action = input("Choose one of the above options or press Enter: ")
    if action == "":
        print("simulation restarting...")
        time.sleep(2)
        os.system('clear')
        resetSimulation()
        generateSeed()
        runSimulation()
    elif action == "s":
        print("*** Starting Seed ***")
        print(encodeBoard(startingSeed))
        restart = input("Press q to quit or anything else to restart: ")
        if restart == 'q':
            sys.exit()
        else:
            resetSimulation()
            generateSeed()
            runSimulation()
    elif action == "q":
        sys.exit()
    print("action was", action, "- end loop")
