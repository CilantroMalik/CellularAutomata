import random
import time
import os
import argparse
import sys
from pynput.keyboard import Key, Listener, Events, KeyCode

# feature wishlist:
# - clipboard interaction with saving seeds?
# - generate a starting seed that produces a given end state

# -- game constants --
BOARD_SIZE = 25  # number of cells in one side of the square board
DENSITY_FACTOR = 0.25  # chance that any given cell gets filled in a randomly generated initial configuration
SPEED = 0.3  # time between each step of the simulation

# -- parse command line interface --
parser = argparse.ArgumentParser()
parser.add_argument("--size", action='store', type=int, required=False)  # corresponds to BOARD_SIZE
parser.add_argument("--density", action='store', type=float, required=False)  # corresponds to DENSITY_FACTOR
parser.add_argument("--speed", action='store', type=float, required=False)  # corresponds to SPEED
args = parser.parse_args()
if args.size:  # all arguments are optional, so have to check for each one before setting the appropriate constant
    BOARD_SIZE = args.size
if args.density:
    DENSITY_FACTOR = args.density
if args.speed:
    SPEED = args.speed


# -- helper functions --

# keyPressed: handle a key press from a listener
def keyPressed(key):
    global wantsToQuit
    if key == 's':  # displays the starting seed for the current run of the simulation
        print("--- Starting Seed ---")
        printBoard(startingSeed)
    if key == 'q':  # sets a flag that will end the simulation on the next run loop
        wantsToQuit = True

# keyReleased: handle a key release from a listener
def keyReleased(key):
    global wantsToQuit
    if key == 'r':  # restart the game (i.e. set the quit flag back to False)
        wantsToQuit = False

# generateSeed: create a starting seed for the game and store it, or load a provided seed if applicable
def generateSeed():
    global board, startingSeed, savedSeed  # we will be reading from and/or writing to these game state variables
    if savedSeed:  # if the user inputted a seed somehow (either a saved one through a code, or created through config editor)
        startingSeed = [[item for item in board[x]] for x in range(len(board))]  # make sure to shallow copy to the starting seed
        return  # no need to go through the normal process
    board = []  # empty out the board in case this is running on a restart
    for _ in range(BOARD_SIZE):  # iterate for each row and column --> visits each cell on the board
        tempRow = []
        for _ in range(BOARD_SIZE):
            tempRow.append("▉▉" if random.random() <= DENSITY_FACTOR else "  ")  # fill the cell randomly, using the density factor
    startingSeed = [[item for item in board[x]] for x in range(len(board))]  # again, shallow copy the board's initial state into startingSeed


# adj: returns a list of the coordinates of cells adjacent to the cell with the given coordinates
def adj(r, c):
    adjacents = []
    possibleIndices = [(r-1, c-1), (r-1, c+1), (r+1, c-1), (r+1, c+1), (r-1, c), (r+1, c), (r, c-1), (r, c+1)]  # possible adjacent coords
    for coords in possibleIndices:  # have to check whether each set of coordinates is actually valid and actually on the board
        if 0 <= coords[0] < BOARD_SIZE and 0 <= coords[1] < BOARD_SIZE:  # coordinates are not out of bounds
            adjacents.append(coords)
    return adjacents


# printBoard: print out the cells of the given board with vertical separators
def printBoard(someBoard):
    for r in range(BOARD_SIZE):
        print("|".join(someBoard[r]))


# encodeBoard: convert the given board into a string of 0s and 1s with rows separated by a slash
def encodeBoard(someBoard):
    encodedString = ""
    for r in range(BOARD_SIZE):
        encodedString += "".join([("0" if cell == "  " else "1") for cell in someBoard[r]])  # iterate over each row w/ list comprehension
        encodedString += "/"  # row separator
    return encodedString[:-1]  # remove the trailing slash


# parseBoard: companion to encodeBoard that decodes a board string into its corresponding 2D array object
def parseBoard(encoded):
    parsedBoard = []
    for row in encoded.split("/"):  # access each row individually
        currentRow = []
        for cell in row:
            currentRow.append("  " if cell == "0" else "▉▉")  # convert 0s and 1s into standard cell notation
        parsedBoard.append(currentRow)  # build up the board row by row
    return parsedBoard


# runSimulation: main function that actually runs the simulation
def runSimulation():
    global board, terminateIn, stateSnapshot, prevStateSnapshot, tertiarySnapshot, stateMessage  # all game state variables
    os.system('clear')
    printBoard(board)  # print the current state of the board
    time.sleep(SPEED)
    while True:  # keep running until the simulation terminates
        if terminateIn > 0:  # count down the termination timer if it is active
            terminateIn -= 1
        os.system('clear')  # clear the window on every step so transitions are seamless
        willBeBorn = []  # list of cells that go from dead to alive on this time step
        willDie = []  # list of cells that go from alive to dead on this time step
        for row in range(BOARD_SIZE):  # iterate through each cell
            for col in range(BOARD_SIZE):
                countAlive = 0  # count its alive neighbors by looping through adjacents
                for cell in adj(row, col):
                    if board[cell[0]][cell[1]] == "▉▉":  # check whether each neighbor is alive
                        countAlive += 1
                if countAlive > 3 and board[row][col] == "▉▉":  # rule 1: live cell w/ more than three live neighbors -> death by overpopulation
                    willDie.append((row, col))
                if countAlive < 2 and board[row][col] == "▉▉":  # rule 2: live cell w/ less than two live neighbors -> death by isolation
                    willDie.append((row, col))
                if countAlive == 3 and board[row][col] == "  ":  # rule 3: dead cell with exactly three live neighbors -> birth
                    willBeBorn.append((row, col))
        for cell in willBeBorn:  # handle births and deaths after logic is complete — only now modify the actual board state
            board[cell[0]][cell[1]] = "▉▉"
        for cell in willDie:
            board[cell[0]][cell[1]] = "  "
        if board == prevStateSnapshot != [] and stateMessage == "":  # if this board is the same as two steps ago, we have periodicity of 2
            stateMessage = "The ecosystem will permanently oscillate between two states, terminating"
            terminateIn = 6  # let it go on for a few more steps to make the periodic nature clear to the user
        if board == tertiarySnapshot != [] and stateMessage == "":  # if this board is the same as three steps ago, we have periodicity of 3
            stateMessage = "The ecosystem will permanently oscillate between three states, terminating"
            terminateIn = 9  # let it go on for three more periods so the user can see that it will repeat infinitely
        # update the snapshots: shuffle each one back one position and set the current board to the most recent snapshot
        tertiarySnapshot = [[item for item in prevStateSnapshot[x]] for x in range(len(prevStateSnapshot))]
        prevStateSnapshot = [[item for item in stateSnapshot[x]] for x in range(len(stateSnapshot))]
        stateSnapshot = [[item for item in board[x]] for x in range(len(board))]
        printBoard(board)  # print out the board with changes from this time step
        if stateSnapshot == prevStateSnapshot != [] and stateMessage == "":  # if the past two states are equal, we have a stationary system
            stateMessage = "The ecosystem has reached permanent stasis, terminating"
            terminateIn = 4  # wait a little and then terminate
        if terminateIn == 0 or wantsToQuit:  # if the terminate counter is zero, end the game
            break
        if stateMessage != "":  # if there is a message about stasis or oscillation, display that below the board
            print(stateMessage)
        time.sleep(SPEED)  # wait the specified amount between time steps


# resetSimulation: resets all global game state variables to their initial state
def resetSimulation():
    global board, startingSeed, stateSnapshot, prevStateSnapshot, tertiarySnapshot, terminateIn, stateMessage, savedSeed
    board, startingSeed, stateSnapshot, prevStateSnapshot, tertiarySnapshot = [], [], [], [], []  # clear all arrays
    terminateIn, stateMessage, savedSeed = -1, "", False  # reset terminate counter, state message, and saved seed


board = []  # keep track of the current board state
startingSeed = []  # keep track of the initial board state
stateSnapshot = []  # holds the previous board state
prevStateSnapshot = []  # holds the board state from two time steps ago
tertiarySnapshot = []  # holds the board state from three time steps ago
terminateIn = -1  # game end counter, starts at -1 and set to an actual value if the simulation will end imminently
stateMessage = ""  # message stating why the simulation would end, if and when it does
wantsToQuit = False  # flag that signals that the user has inputted a quit command mid-simulation
savedSeed = False  # signals whether the user has inputted a seed (saved or created) so a random one shouldn't be generated

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
