import pygame
from CheckerGame import CheckerBoard, Piece
from CheckerAI import CheckerAI
from Transition import BoardTransition
from constants import HEIGHT, WIDTH, _P1PIECE, _P2PIECE, _FORCED_CAPTURE, Q_TABLE_FILE, DEBUG_HEIGHT


if __name__ == "__main__":
    window = pygame.display.set_mode((WIDTH, HEIGHT + DEBUG_HEIGHT))
    clock = pygame.time.Clock()

    ai = CheckerAI("")
    bt = BoardTransition()
    CB = CheckerBoard()

    player = _P2PIECE

    replayable = True
    gameActive = True

    while(replayable):
        CB.initializeBoard()
        # print(CB)

        nextBoardStates = bt.getAllBoards(CB)

        # Treat as pointer to a piece
        selectedPiece:Piece = None
        currentBoardEval = 0
        repeatedMoves = dict()

        while gameActive:
            CB.drawBoard(window)
            clock.tick(60)
            time = pygame.time.get_ticks()

            # if its players turn
            if (CB.turn == player):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameActive = False
                        replayable = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if (selectedPiece is None):
                            selectedPiece = CB.selectPiece()
                        else:
                            if (CB.placePiece(selectedPiece)):
                                nextBoardStates = bt.getAllBoards(CB)
                                wonPlayer = CB.gameEnd(len(nextBoardStates))
                                if (wonPlayer == _P1PIECE):
                                    print("AI Won!")
                                    gameActive = False
                                elif (wonPlayer == _P2PIECE):
                                    print("You Won!")
                                    gameActive = False
                            selectedPiece = None

                if (selectedPiece is not None):
                    selectedPiece.drawOutline(window)

                currentBoardEval = ai.evaluateBoard(CB)
                
            # if its AI's turn
            else:
                depth = 4
                # depth = int(180/(CB.player1NumPieces + CB.player2NumPieces + 36))
                nextBestMove = ai.nextBestMove(CB, depth)
                CB < nextBestMove
                currentBoardEval = ai.evaluateBoard(CB)

                # Game Draw logic
                if (repeatedMoves.get(nextBestMove) is not None):
                    if (repeatedMoves[nextBestMove] >= 3):
                        print("Boards repeated resulted in a draw!")
                        gameActive = False
                    else:
                        repeatedMoves[nextBestMove] += 1
                else:
                    repeatedMoves[nextBestMove] = 1
                
                nextBoardStates = bt.getAllBoards(CB)
                wonPlayer = CB.gameEnd(len(nextBoardStates))
                if (wonPlayer == _P1PIECE):
                    print("AI Won!")
                    ai.applyQReward(wonPlayer)
                    gameActive = False
                elif (wonPlayer == _P2PIECE):
                    print("You Won!")
                    ai.applyQReward(wonPlayer)
                    gameActive = False
            # Monitoring Performance
            # clock.tick()
            # print(clock.get_fps())
            CB.drawPieces(window)
            CB.debug(window, currentBoardEval, "Current Board Evaluation")

            pygame.display.update()

        # Continuation Logic
        CB.drawBoard(window)
        CB.debug(window, currentBoardEval, "Click Here to Play again!")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                replayable = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                if (mouseY > HEIGHT and mouseY < HEIGHT + DEBUG_HEIGHT):
                    gameActive = True

        pygame.display.update()
        

    pygame.quit()

