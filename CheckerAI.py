from Transition import BoardTransition
from CheckerGame import CheckerBoard, Piece
import numpy as np
import math
import random
from copy import deepcopy
from constants import Q_TABLE_FILE, _P1PIECE, _P2PIECE, _P1KING, _P2KING, _ROWS, _COLS
#import tensorflow as tf

class CheckerAI:

    #Weights of Heuristic Factors
    _KING_VALUE = 3
    _PIECE_VALUE = 2
    _ADJ_VALUE = 0.2
    _EDGE_VALUE = 0.5
    _PROMO_VALUE = 0.8
    _OPPONENT_MULT = -1.2
    _DISTANCE_MULT = 2

    _LEARNING_RATE = 1
    _GAMMA = 0.95
    _EPSILON = 0.9

    _TERMINAL_NODE_EVAL = 1000

    def __init__(self, qTableName) -> None:
        self.boardTransition = BoardTransition()
        self.saveToDisk = True
        self.qTableName = qTableName

        if (qTableName == ""):
            self.qTableName = Q_TABLE_FILE
            self.saveToDisk = False

        self.visited = [CheckerBoard]
        try:
            print("Loading Trainning Data...")
            self.qTable = np.load(self.qTableName, allow_pickle="TRUE").item()
            print("Successfully Loaded Trainning Data")
        except:
            print("No Q Table exists")
            self.qTable = dict()
            np.save(self.qTableName, self.qTable)

    # Utility function
    # Takes a board state evaluates it
    # Higher evaluation for kings
    def evaluateBoard(self, board:CheckerBoard) -> int:
        # AI Teams works on this
        if (self.qTable.get(board) is not None):
            # print("Using QTable val: ", self.qTable[board])
            return self.qTable.get(board)

        if (board.player1NumPieces + board.player1NumKings) == 0:
            self.qTable[board] = -1 * self._TERMINAL_NODE_EVAL
            return -1 * self._TERMINAL_NODE_EVAL
        elif (board.player2NumPieces + board.player2NumKings) == 0:
            self.qTable[board] = self._TERMINAL_NODE_EVAL
            return self._TERMINAL_NODE_EVAL
        
        boardValue = 0.0
        P1DistanceFromPromo = 0
        P2DistanceFromPromo = 0
        for row in board.board:
            for piece in row:
                if type(piece) is Piece:
                    pieceValue = self._PIECE_VALUE
                    adjSpaces = [(piece.row + 1, piece.col + 1), (piece.row + 1, piece.col - 1), (piece.row - 1, piece.col + 1), (piece.row - 1, piece.col - 1)]
                    # Is the piece defending or being defended by another piece
                    for row, col in adjSpaces:
                        if 0 <= row < _ROWS and 0 <= col < _COLS:
                            if (type(board.board[row][col]) is Piece and (board.board[row][col].player == piece.player)):
                                pieceValue += self._ADJ_VALUE
                    # Is the piece on the edge
                    if piece.col == 0 or piece.col == _COLS:
                        pieceValue += self._EDGE_VALUE
                    # Is the piece defending the promotion line
                    if (piece.row == 0 and piece.pieceNum == _P1PIECE) or (piece.row == _ROWS and piece.pieceNum == _P2PIECE):
                        pieceValue += self._PROMO_VALUE
                    # Is the piece a King
                    if piece.king:
                        pieceValue += self._KING_VALUE
                    # Does the piece not belong to the AI
                    if piece.player == 2:
                        pieceValue *= self._OPPONENT_MULT
                        if not piece.king:
                            P2DistanceFromPromo += (float(_ROWS - piece.row) / _ROWS)
                    else:
                        if not piece.king:
                            P1DistanceFromPromo += (float(piece.row) / _ROWS)
                    boardValue += pieceValue
        # Add the average distance of the pieces from their promotion line
        if board.player1NumPieces > 0 and board.player2NumPieces > 0:
            boardValue += self._DISTANCE_MULT * ((P1DistanceFromPromo / board.player1NumPieces) - (P2DistanceFromPromo / board.player2NumPieces))

        self.qTable[board] = boardValue
        return boardValue
        # return board.player1NumPieces - board.player2NumPieces + ((board.player1NumKings - board.player2NumKings) * self._KING_VALUE)
        
    
    # current_state (board) - current state of the game board
    # depth (int) - how deep in the minimax tree to go
    # is_max (boolean) - True for max level, False for min level
    # alpha (float) - current alpha value of tree
    # beta (float) - current beta value of tree
    # uses a get_children() function that should be made in transition
    def minimax(self, current_state, depth, is_max, alpha : float, beta : float): 
        # no move will be made
        if depth == 0:
            return self.evaluateBoard(current_state)
        
        possible_moves = self.boardTransition.getAllBoards(current_state)
        
        if len(possible_moves) == 0:
            # Terminal Node
            return self._TERMINAL_NODE_EVAL * current_state.turn
        
        # next_move = None
        if is_max: 
            max_val = float('-inf')
            for move in possible_moves: 
                # print("BOARD DEPTH " + str(depth))
                # print(move)
                value = self.minimax(move, depth - 1, False, alpha, beta)
                alpha = max(alpha, value)
                if value > max_val: 
                    max_val = value
                    # next_move = move
                if value >= beta:
                    break
            return max_val
        else: 
            min_val = float('inf')
            for move in possible_moves: 
                # print("BOARD DEPTH " + str(depth))
                # print(move)
                value = self.minimax(move, depth - 1, True, alpha, beta)
                beta = min(beta, value)
                if value < min_val: 
                    min_val = value
                    # next_move = move
                if value <= alpha:
                    break
            return min_val
        
    # Decides if it should take the best move or explore
    def exploration(self, bestMove:CheckerBoard, secondBestMove:CheckerBoard) -> CheckerBoard:
        prob = random.random()
        if (secondBestMove is not None and prob > self._EPSILON):
            print("Exploring a new move")
            return secondBestMove
        return bestMove
        
    # gets the next best move from current board configuration
    # the higher the accuracy level the better the move but it costs more performance
    def nextBestMove(self, currentBoard:CheckerBoard, accuracyLevel:int = 4) -> CheckerBoard:
        self.evaluated_boards = [(currentBoard, self.evaluateBoard(currentBoard))]
        nextMoves = self.boardTransition.getAllBoards(currentBoard)
        if (len(nextMoves) == 0):
            print("No move exists")
            return None
        bestNextMove = None
        secondBestMove = None
        bestMoveVal = currentBoard.turn * math.inf

        alpha = float('-inf')
        beta = float('inf')
        # print("CURRENT:")
        # print(currentBoard)
        # print("MOVES:")
        # for move in nextMoves:
        #     print(move)
        # print("POSSIBLE:")
        for move in nextMoves:
            moveEvaluation = self.minimax(move, accuracyLevel, currentBoard.turn == _P2PIECE, alpha, beta)
            alpha = max(alpha, moveEvaluation)
            if (moveEvaluation * currentBoard.turn < currentBoard.turn * bestMoveVal):
                secondBestMove = bestNextMove
                bestNextMove = move
                bestMoveVal = moveEvaluation

        if bestMoveVal <= (currentBoard.turn * self._TERMINAL_NODE_EVAL):
            # if future move all lead to terminal loss
            bestMoveVal = currentBoard.turn * math.inf
            for move in nextMoves:
                moveEvaluation = self.minimax(move, 2, currentBoard.turn == _P2PIECE, alpha, beta)
                alpha = max(alpha, moveEvaluation)
                if (moveEvaluation * currentBoard.turn < currentBoard.turn * bestMoveVal):
                    secondBestMove = bestNextMove
                    bestNextMove = move
                    bestMoveVal = moveEvaluation
            
            # Then only play best relative move

        # print("Move Confidence:", bestMoveVal)
        
        return self.exploration(bestNextMove, secondBestMove)


    # def deepEval(self, currentState:CheckerBoard, depth:int) -> int:
    #     possibleNextStates = self.boardTransition.getAllBoards(currentState)

    #     if (depth == 0 or len(possibleNextStates) == 0):
    #         return self.evaluateBoard(currentState)
        
    #     maxVal = -math.inf
    #     for state in possibleNextStates:
    #         val = -self.deepEval(state, depth - 1)
    #         if (val > maxVal):
    #             maxVal = val
        
    #     return maxVal
    
    # def get_path(self) -> list["CheckerBoard"]:
    #     path = []
    #     current_node = self
    #     while current_node:
    #         path.append(current_node)
    #         current_node = current_node.parent
    #     return path[::-1]
    
    def linkVisitedBoard(self, board:CheckerBoard):
        newVisited = deepcopy(board)
        self.visited.append(newVisited)

    def playerNumber(self, player) ->str:
        if (player == _P1PIECE):
            return "1"
        elif (player == _P2PIECE):
            return "2"
        return "0"
    
    # Applies Reward to the model and returns the amount of reward applied
    def applyQReward(self, wonPlayer:int) -> int:
        totalReward = 0
        maxTurns = len(self.visited)
        # Our model should try to avoid draws and repeating moves
        if (wonPlayer == 0):
            # So if the game results in a draw don't take moves that end up in a draw
            for i, board in enumerate(self.visited):
                if (self.qTable.get(board) is not None):
                    print("Player ", self.playerNumber(wonPlayer), " won | Previous board val: ", self.qTable[board])
                    appliedReward = board.turn * self._LEARNING_RATE * pow(self._GAMMA, maxTurns - i)
                    self.qTable[board] += appliedReward
                    totalReward -= abs(appliedReward)
                    print("On turn ", i, " | New board val: ", self.qTable[board], "For Player: ", self.playerNumber(board.turn), "\n")
        else:
            # Otherwise apply q reward normally
            for i, board in enumerate(self.visited):
                if (self.qTable.get(board) is not None):
                    print("Player ", self.playerNumber(wonPlayer), " won | Previous board val: ", self.qTable[board])
                    appliedReward = -wonPlayer * self._LEARNING_RATE * pow(self._GAMMA, maxTurns - i)
                    self.qTable[board] += appliedReward
                    totalReward += abs(appliedReward)
                    print("On turn ", i, " | New board val: ", self.qTable[board], "For Player: ", self.playerNumber(board.turn), "\n")

        self.visited.clear()

        return totalReward

    
    # Saves q table inside binary file
    def __del__(self):
        if (self.saveToDisk):
            np.save(self.qTableName, self.qTable)