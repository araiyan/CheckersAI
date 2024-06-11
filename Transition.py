from CheckerGame import CheckerBoard, Piece
from copy import deepcopy
from typing import List, Tuple
from constants import _P1PIECE, _P2PIECE, _P1KING, _P2KING, _ROWS, _COLS, _FORCED_CAPTURE

# Helps figure out valid moves
class BoardTransition:
    def __init__(self) -> None:
        pass

    """This function returns every board possible in the game's current state (depending on the player)."""
    def getAllBoards(self, board: CheckerBoard) -> List[CheckerBoard]:
        allBoards = []
        captureBoards = []


        for rowIndex, row in enumerate(board.board):

            for colIndex, piece in enumerate(row):

                if (type(piece) is Piece and (piece.pieceNum * board.turn) > 0): #if the current spot is the player's normal/king piece

                    allMoves = self.getAllMovesForPiece(board, piece) #gets all moves for current piece

                    for move in allMoves: # for every move possible, create a board from that move and add to allBoards
                        # newBoard = self.makeMove(deepcopy(board), (rowIndex, colIndex), move)

                        # newBoards = self.captureLogic(newBoard, board.turn)
                        # allBoards.append(newBoards)

                        newBoard = deepcopy(board)
                        newBoard.movePieceToEmptySquare(rowIndex, colIndex, move[0], move[1])
                        newBoard.changeTurn()
                        allBoards.append(newBoard)

                    newCaptureMoves = board.getBoardAfterCaptureMoves(piece)
                    if (len(newCaptureMoves) != 0):
                        captureBoards.extend(newCaptureMoves)

        for captureMoves in captureBoards:
            captureMoves.recalculatePieces() # temporary fix ~~~~
            captureMoves.changeTurn()
        
        if (_FORCED_CAPTURE):
            # if forced capture is on then only return capture moves
            if (len(captureBoards) == 0):
                return allBoards
            else:
                return captureBoards
        else:
            allBoards.extend(captureBoards)
            return allBoards

                

    """This function should get every move possible for the chosen piece. Includes normal moves, capture moves, and king moves."""
    def getAllMovesForPiece(self, board: CheckerBoard, piece:Piece) -> List[Tuple[int, int]]:
        allMoves = []

        if piece.pieceNum == _P1PIECE or piece.king:  # Player 1's piece or king
            
            downDiagonals = [(piece.row + 1, piece.col + 1), (piece.row + 1, piece.col - 1)] # Top -> down diagonals
            
            allMoves.extend(self.getValidMoves(board, downDiagonals)) # Add normal moves 

        if piece.pieceNum == _P2PIECE or piece.king:  # Player 2's piece or king
            
            upDiagonals = [(piece.row - 1, piece.col + 1), (piece.row - 1, piece.col - 1)] # Bottom -> up diagonals
           
            allMoves.extend(self.getValidMoves(board, upDiagonals))  # Add normal moves
            
        # capturing_moves = self.getCapturingMoves(board, piece) # Add capture moves
        # allMoves.extend(capturing_moves)

        return allMoves
    

    """This function checks to see if the move given can be made on the board, i.e. not out of bounds of the board"""
    def getValidMoves(self, board: CheckerBoard, diagonals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        validMoves = []
        for newRow, newColumn in diagonals:
            
            if 0 <= newRow < _ROWS and 0 <= newColumn < _COLS: # Check if the new position is within the bounds of the board
                if not isinstance(board.board[newRow][newColumn], Piece): # if the new position is empty it is a valid move
                    validMoves.append((newRow, newColumn)) # Add the move to validMoves

        return validMoves


        
    """This function moves the piece from it's original position to it's desired position and checks if the ending position is worthy of promotion"""
    def makeMove(self, board: CheckerBoard, startPosition: Tuple[int, int], endPosition: Tuple[int, int]) -> CheckerBoard:
        startRow, startColumn = startPosition
        endRow, endColumn = endPosition

        #Puts piece to new location and remove at old location
        board.board[endRow][endColumn] = board.board[startRow][startColumn] 
        board.board[startRow][startColumn] = 0

        # Check for promotion to king
        if endRow == 0 and board.board[endRow][endColumn] == 1:
            board.board[endRow][endColumn] = 3
            self.player1NumKings += 1

        elif endRow == len(board.board) - 1 and board.board[endRow][endColumn] == 2:
            board.board[endRow][endColumn] = 4
            self.player2NumKings += 1

        return board


    """This function gets all the capture moves for this piece and follows the rule where if there is another capture available after the initial
    capture, then it will continue to capture. Returns a list of all capture moves available made by the piece.
    """
    def getCaptureMoves(self, board: CheckerBoard, piece:Piece) -> List[Tuple[int, int]]:
        capturing_moves = []
        row, column = piece.row, piece.col
        player = piece
        opponent = 1 if player == 2 else 2
        
        # Define the diagonals to check for capturing moves
        downDiagonals = [(row + 1, column + 1), (row + 1, column - 1)] if player == 1 else [(row - 1, column + 1), (row - 1, column - 1)]
        
        # Check for capturing moves in forward diagonals
        for newRow, newColumn in downDiagonals:
            capture_row = newRow + (newRow - row)
            capture_col = newColumn + (newColumn - column)
            # Check if the new position and capture position are within the bounds of the board
            if 0 <= newRow < len(board.board) and 0 <= newColumn < len(board.board[0]) \
                    and 0 <= capture_row < len(board.board) and 0 <= capture_col < len(board.board[0]):
                # Check if the new position contains an opponent's piece and the capture position is empty
                if isinstance(board.board[newRow][newColumn], Piece) and board.board[newRow][newColumn].pieceNum == opponent and not isinstance(board.board[capture_row][capture_col], Piece):
                    capturing_moves.append((capture_row, capture_col))
        
        return capturing_moves
    



    """This function recursively uses getCaptureMoves to get all the sequences of boards after the first capture, to see if there
    are any captures available after the first one.
    """
    def captureLogic(self, board: CheckerBoard, player: int) -> CheckerBoard:
        allBoards = []
        # Iterate through each piece on the board
        for row in range(len(board.board)):

            for column in range(len(board.board[row])):

                if board.board[row][column] == player or board.board[row][column] == player + 2:  # If it's the player's piece or king
                    capturing_moves = self.getCaptureMoves(board, (row, column))

                    if capturing_moves:

                        for capture_move in capturing_moves:
                            newBoard = self.makeMove(deepcopy(board), (row, column), capture_move)
                            # Recursively check for multiple captures
                            newBoards = self.captureLogic(newBoard, player)
                            allBoards.extend(newBoards)

        if not allBoards:
            allBoards.append(board)
        return allBoards

