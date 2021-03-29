import random
import time
import os
import argparse
import sys
from pynput.keyboard import Key, Listener

# feature wishlist:
# - configuration editor with hotkeys (spacebar, arrow keys to navigate)
# - able to tweak parameters on subsequent restarts of the simulation
# - encode starting seeds into simple text string, also clipboard interaction?

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
    global board, startingSeed
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
    global board, startingSeed, stateSnapshot, prevStateSnapshot, tertiarySnapshot, terminateIn, stateMessage
    board, startingSeed, stateSnapshot, prevStateSnapshot, tertiarySnapshot = [], [], [], [], []
    terminateIn, stateMessage = -1, ""


board = []
startingSeed = []
stateSnapshot = []
prevStateSnapshot = []
tertiarySnapshot = []
terminateIn = -1
stateMessage = ""
wantsToQuit = False

# with Listener(on_press=keyPressed, on_release=keyReleased) as listener:
#     listener.join()

generateSeed()
runSimulation()

while True:
    print("--- Options ---")
    print("Enter: restart the simulation")
    print("s: save this starting seed")
    print("q: quit the playground")
    action = input("Choose one of the above options or press Enter: ")
    if action == "":
        print("simulation restarting...")
        time.sleep(1)
        os.system('clear')
        resetSimulation()
        generateSeed()
        runSimulation()
    elif action == "s":
        print("*** Starting Seed ***")
        printBoard(startingSeed)
        restart = input("Press q to quit or anything else to restart: ")
        if restart == 'q':
            sys.exit()
        else:
            resetSimulation()
            generateSeed()
            runSimulation()
    elif action == "q":
        sys.exit()
