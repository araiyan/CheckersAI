from Transition import BoardTransition
from CheckerGame import CheckerBoard
import numpy as np
import math
from constants import Q_TABLE_FILE
#import tensorflow as tf

class CheckerAI:
    _KING_VALUE = 3
    _TERMINAL_NODE_EVAL = 100
    def __init__(self) -> None:
        self.boardTransition = BoardTransition()
        try:
            self.qTable = np.load(Q_TABLE_FILE, allow_pickle="TRUE").item()
        except:
            print("No Q Table exists")
            self.qTable = dict()
            np.save(Q_TABLE_FILE, self.qTable)

    # Utility function
    # Takes a board state evaluates it
    # Higher evaluation for kings
    def evaluateBoard(self, board:CheckerBoard) -> int:
        # AI Teams works on this
        # pass
        # if board.turn == 1: 
        return board.player1NumPieces - board.player2NumPieces + ((board.player1NumKings - board.player2NumKings) * self._KING_VALUE)
        # else: 
        #     return board.player2NumPieces - board.player1NumPieces + ((board.player2NumKings - board.player1NumKings) * self._KING_VALUE)
   
    
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
            return self._TERMINAL_NODE_EVAL * -current_state.turn
        
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
        
        
    # gets the next best move from current board configuration
    # the higher the accuracy level the better the move but it costs more performance
    def nextBestMove(self, currentBoard:CheckerBoard, accuracyLevel:int = 3):
        self.evaluated_boards = [(currentBoard, self.evaluateBoard(currentBoard))]
        nextMoves = self.boardTransition.getAllBoards(currentBoard)
        if (len(nextMoves) == 0):
            print("No move exists")
            return None
        bestNextMove = None
        bestMoveVal = -math.inf

        alpha = float('-inf')
        beta = float('inf')
        # print("CURRENT:")
        # print(currentBoard)
        # print("MOVES:")
        # for move in nextMoves:
        #     print(move)
        # print("POSSIBLE:")
        for move in nextMoves:
            moveEvaluation = self.minimax(move, accuracyLevel, False, alpha, beta)
            alpha = max(alpha, moveEvaluation)
            if (moveEvaluation > bestMoveVal):
                bestNextMove = move
                bestMoveVal = moveEvaluation

        if bestMoveVal >= self._TERMINAL_NODE_EVAL:
            # if future move all lead to terminal loss
            bestMoveVal = -math.inf
            for move in nextMoves:
                moveEvaluation = self.minimax(move, 1, False, alpha, beta)
                alpha = max(alpha, moveEvaluation)
                if (moveEvaluation > bestMoveVal):
                    bestNextMove = move
                    bestMoveVal = moveEvaluation
            
            # Then only play best relative move

        print("Move Confidence:", bestMoveVal)
        
        return bestNextMove


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
    
    def get_path(self) -> list["CheckerBoard"]:
        path = []
        current_node = self
        while current_node:
            path.append(current_node)
            current_node = current_node.parent
        return path[::-1]
    
    # Saves q table inside binary file
    def __del__(self):
        np.save(Q_TABLE_FILE, self.qTable)