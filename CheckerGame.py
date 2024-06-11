import pygame
from copy import deepcopy
from constants import _P1PIECE, _P2PIECE, _P1KING, _P2KING, _BOARD_COLOR, _PIECE_COLOR, _SQUARE_SIZE, WIDTH, HEIGHT
from constants import _PIECE_RADIUS, _ROWS, _COLS,_PIECE_PADDING, _FORCED_CAPTURE, DEBUG_HEIGHT

pygame.font.init()
font = pygame.font.SysFont('Arial', 24)


# Each piece in the checkers board
class Piece:    
    def __init__(self, row, col, pieceNum):
        self.x = 0
        self.y = 0

        self.king = False
        if (pieceNum == _P1KING or pieceNum == _P2KING):
            self.king = True

        # determines which row and column the piece is located at
        self.row = row
        self.col = col
        self.pieceNum = pieceNum
        if self.pieceNum > 0:
            self.player = 2
        elif self.pieceNum < 0:
            self.player = 1
        else:
            self.player = 0

        # calculates x and y position from row and column
        self.calculatePosition()

    def calculatePosition(self):
        self.x = (self.col * _SQUARE_SIZE) + (_SQUARE_SIZE // 2)
        self.y = (self.row * _SQUARE_SIZE) + (_SQUARE_SIZE // 2)
        
    def draw(self, window):
        pygame.draw.circle(window, _PIECE_COLOR[self.pieceNum], (self.x, self.y), _PIECE_RADIUS - _PIECE_PADDING)

    def drawOutline(self, window):
        pygame.draw.circle(window, ((50, 50, 220)), (self.x, self.y), _PIECE_RADIUS - _PIECE_PADDING + 5)


    def __str__(self) -> str:
        return str(self.pieceNum)

    def __eq__(self, other) -> bool:
        if type(other) is not Piece:
            return False
        return self.pieceNum == other.pieceNum and self.row == other.row and self.col == other.col


# Game board class
class CheckerBoard:
    def __init__(self):
        
        # 2D Board Matrix
        # 0 = empty square
        # -1 = Player 1's piece
        # 1  = Player 2's piece
        # -2 = Player 1's king
        # 2  = Player 2's king
        self.board = []
        # indicated player's turn
        self.turn = _P2PIECE

        self.player1NumPieces = self.player2NumPieces = 12
        self.player1NumKings = self.player2NumKings = 0

        # self.parent = None


    # Sets up pieces for a new game
    def initializeBoard(self, player = _P2PIECE):
        self.player1NumPieces = self.player2NumPieces = 12
        self.player1NumKings = self.player2NumKings = 0

        self.board.clear()
        self.turn = player

        for i in range(_ROWS):
            self.board.append([])
            for j in range(_COLS):
                if (((i+j) % 2) != 0):
                    if (i < 3):
                        self.board[i].append(Piece(i, j, _P1PIECE))
                    elif (i > 4):
                        self.board[i].append(Piece(i, j, _P2PIECE))
                    else:
                        self.board[i].append(0)
                else:
                    self.board[i].append(0)

    # Makes a custom board from a board layout
    def makeCustomBoard(self, boardLayout:list[list]):
        for i in range(_ROWS):
            self.board.append([])
            for j in range(_COLS):
                if (boardLayout[i][j] != 0):
                    self.board[i].append(Piece(i, j, boardLayout[i][j]))
                else:
                    self.board[i].append(0)


    # draws the board with pieces onto the window using pygame
    def drawBoard(self, window) -> None:
        # GUI team works on this

        #background color
        window.fill((255,255,255))

        #draw each square
        for row_index, row in enumerate (self.board):
            for col_index, col in enumerate(row):
                #divide window into 8 equal spaces 
                x = col_index * _SQUARE_SIZE
                y = row_index * _SQUARE_SIZE
                if (row_index + col_index) % 2 == 0:
                    color = _BOARD_COLOR[0]
                else:
                    color = _BOARD_COLOR[1]
        
                #draw each square in the checkersboard
                pygame.draw.rect(window, color, (x, y, _SQUARE_SIZE, _SQUARE_SIZE))
    

    def drawPieces(self, window) -> None:
        for row in self.board:
            for piece in row:
                if (type(piece) is Piece):
                    piece.draw(window)

    def selectPiece(self) -> Piece:
        # get mouse position
        mousePosX, mousePosY = pygame.mouse.get_pos()
        #print(f"Mouse position x: ${mousePosX}, y: ${mousePosY}")
        # calculate board square location clicked on
        pieceRow = mousePosY // _SQUARE_SIZE
        pieceCol = mousePosX // _SQUARE_SIZE
        # print(f"Row: ${pieceRow} Col: ${pieceCol}")

        if (pieceRow < 0 or pieceRow >= _ROWS or pieceCol < 0 or pieceCol >= _COLS):
            return None
        
        selectedSquare = self.board[pieceRow][pieceCol]
        if (type(selectedSquare) is Piece and (selectedSquare.pieceNum * self.turn) > 0):
            #print("selected player piece")
            return selectedSquare
        return None

    
    def placePiece(self, piece) -> bool:
        # get mouse position
        mousePosX, mousePosY = pygame.mouse.get_pos()
        # calculate board square location clicked on
        pieceRow = mousePosY // _SQUARE_SIZE
        pieceCol = mousePosX // _SQUARE_SIZE
        if (pieceRow < 0 or pieceRow > _ROWS or pieceCol < 0 or pieceCol > _COLS):
            return False

        # ensure the checker piece moves to an empty square
        if type(self.board[pieceRow][pieceCol]) is not Piece:

            # Normal move
            if (piece.row - pieceRow == self.turn and abs(pieceCol - piece.col) == 1) or (piece.king and abs(piece.row - pieceRow) == 1 and abs(pieceCol - piece.col) == 1):
                if (_FORCED_CAPTURE):
                    if (len(self.captureMoveExists()) == 0):
                        self.movePieceToEmptySquare(piece.row, piece.col, pieceRow, pieceCol)
                        # switch players turn
                        self.changeTurn()
                        return True
                    else:
                        return False
                else:
                    self.movePieceToEmptySquare(piece.row, piece.col, pieceRow, pieceCol)
                    # switch players turn
                    self.changeTurn()
                    return True
            # Capture move
            elif (piece.row - pieceRow == self.turn * 2 and abs(pieceCol - piece.col) == 2) or (piece.king and abs(piece.row - pieceRow) == 2 and abs(pieceCol - piece.col) == 2):
                captureRow = int((piece.row + pieceRow) / 2)
                captureCol = int((piece.col + pieceCol) / 2)

                capturePiece = self.board[captureRow][captureCol]

                if type(capturePiece) is Piece and (capturePiece.pieceNum * self.turn) < 0:
                    # if the captured piece is opponents piece remove piece and move
                    self.movePieceToEmptySquare(piece.row, piece.col, pieceRow, pieceCol)
                    self.removePieceFromBoard(capturePiece)
                    self.recalculatePieces() # need to remove in future

                    selectedPiece = self.board[pieceRow][pieceCol]
                    possibleCaptures = self.getBoardAfterCaptureMoves(selectedPiece)
                    # if no possible captures exist end turn
                    if (len(possibleCaptures) == 0):
                        self.changeTurn()
                    return True
        return False
            
    
    # moves a piece to an empty square
    def movePieceToEmptySquare(self, positionX, positionY, otherX, otherY) -> Piece:
        self.board[positionX][positionY], self.board[otherX][otherY] = self.board[otherX][otherY], self.board[positionX][positionY]
        piece:Piece = self.board[otherX][otherY]
        piece.row, piece.col = otherX, otherY
        piece.calculatePosition()
        if (not piece.king):
            if piece.row == 0 or piece.row == (_ROWS - 1):
                piece.king = True
                piece.pieceNum = piece.pieceNum * 2
                if (piece.pieceNum < 0):
                    self.player1NumKings += 1
                    self.player1NumPieces -= 1
                else:
                    self.player2NumKings += 1
                    self.player2NumPieces -= 1
                
        return piece
    
    def getBoardAfterCaptureMoves(self, piece:Piece) -> list:
        
        movesToCheck = []
        if (piece.king):
            # if king check all 4 diagnol positions
            movesToCheck.append((piece.row + 1, piece.col + 1))
            movesToCheck.append((piece.row + 1, piece.col - 1))
            movesToCheck.append((piece.row - 1, piece.col + 1))
            movesToCheck.append((piece.row - 1, piece.col - 1))
        else:
            # if piece check the position your moving towards
            movesToCheck.append((piece.row - self.turn, piece.col + 1))
            movesToCheck.append((piece.row - self.turn, piece.col - 1))

        possibleBoards = []
        for move in movesToCheck:
            row = move[0]
            col = move[1]
            if 0 <= row < _ROWS and 0 <= col < _COLS:
                # if valid position
                if (type(self.board[row][col]) is Piece and (self.board[row][col].pieceNum * self.turn) < 0):
                    # if there is an opponents piece in that position
                    newRow = 2*row - piece.row
                    newCol = 2*col - piece.col
                    if 0 <= newRow < _ROWS and 0 <= newCol < _COLS:
                        # checks if the new and col is within bounds
                        if (type(self.board[newRow][newCol]) is not Piece):
                            # if the position across is empty square
                            newBoard = deepcopy(self)
                            # newBoard.board[piece.row][piece.col], newBoard.board[newRow][newCol] = newBoard.board[newRow][newCol], newBoard.board[piece.row][piece.col]
                            newPiece = newBoard.movePieceToEmptySquare(piece.row, piece.col, newRow, newCol)
                            # removes the captured piece from board
                            pieceToRemove:Piece = newBoard.board[row][col]
                            newBoard.removePieceFromBoard(pieceToRemove)

                            # recursive calls for multi captures
                            multiCapture = newBoard.getBoardAfterCaptureMoves(newPiece)
                            if (len(multiCapture) == 0):
                                possibleBoards.append(newBoard)
                            else:
                                possibleBoards.extend(multiCapture)
        
        return possibleBoards
    
    # returns if capture move exists on current board and for which piece its available
    def captureMoveExists(self) -> list[Piece]:
        capturingPieces = []
        for _, row in enumerate(self.board):
            for _, piece in enumerate(row):
                if (type(piece) is Piece and (piece.pieceNum * self.turn) > 0):
                    newCaptureMoves = self.getBoardAfterCaptureMoves(piece)
                    if (len(newCaptureMoves) != 0):
                        capturingPieces.append(piece)
                    
        return capturingPieces
    
    def removePieceFromBoard(self, piece:Piece):
        if (self.turn == _P1PIECE):
            if piece.king:
                self.player1NumKings -= 1
            else:
                self.player1NumPieces -= 1
        else:
            if piece.king:
                self.player2NumKings -= 1
            else:
                self.player2NumPieces -= 1

        self.board[piece.row][piece.col] = 0
        

    def changeTurn(self):
        self.turn = self.turn * -1

    # calculates the correct pieces for the board
    def recalculatePieces(self):
        self.player1NumKings = self.player1NumPieces = self.player2NumKings = self.player2NumPieces = 0
        for _, row in enumerate(self.board):
            for _, piece in enumerate(row):
                if (type(piece) is Piece):
                    if (piece.pieceNum == _P1PIECE):
                        self.player1NumPieces += 1
                    elif (piece.pieceNum == _P2PIECE):
                        self.player2NumPieces += 1
                    elif (piece.pieceNum == _P1KING):
                        self.player1NumKings += 1
                    elif (piece.pieceNum == _P2KING):
                        self.player2NumKings += 1

    # 0 - game not over
    # -1 - player 1 won
    # 1 - player 2 won
    def gameEnd(self, numBoardStates) -> int:
        if (numBoardStates == 0):
            self.recalculatePieces()
            if (self.player1NumPieces + self.player1NumKings) > (self.player2NumPieces + self.player2NumKings):
                return _P1PIECE
            else:
                return _P2PIECE
        
        return 0
    
    def debug(self, window, value, debug_message):

        debug_line = f"{debug_message}: {value}"
        pygame.draw.rect(window, (255, 255, 255), (0, _ROWS * _SQUARE_SIZE, _COLS * _SQUARE_SIZE, DEBUG_HEIGHT))
        text_surface = font.render(debug_line, True, (0, 0, 0))
        window.blit(text_surface, (10, HEIGHT + (DEBUG_HEIGHT / 2)))

    # for printing out the board on the console
    def __str__(self):
        return "\n".join(" ".join(map(str, row)) for row in self.board) + "\n"
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other) -> bool:
        return self.board == other.board
    
    def __lt__(self, other):
        # other.parent = self
        # self.board, other.board = other.board, self.board
        # self.player1NumPieces, other.player1NumPieces = other.player1NumPieces, self.player1NumPieces
        # self.player2NumPieces, other.player2NumPieces = other.player2NumPieces, self.player2NumPieces
        # self.player1NumKings, other.player1NumKings = other.player1NumKings, self.player1NumKings
        # self.player2NumKings, other.player2NumKings = other.player2NumKings, self.player2NumKings
        if (type(other) is CheckerBoard):
            self.board = other.board
            self.player1NumPieces = other.player1NumPieces
            self.player2NumPieces = other.player2NumPieces
            self.player1NumKings = other.player1NumKings
            self.player2NumKings = other.player2NumKings
            self.turn = other.turn
        
