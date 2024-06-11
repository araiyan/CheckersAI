import pygame
from CheckerGame import CheckerBoard, Piece
from CheckerAI import CheckerAI
from Transition import BoardTransition
from constants import HEIGHT, WIDTH, _P1PIECE, _P2PIECE, Q_TABLE_FILE, DEBUG_HEIGHT

TRAIN_EPOCH = 1000
# In milliseconds
TURN_TIME = 100

if __name__ == "__main__":
	pygame.init()
	clock = pygame.time.Clock()
	window = pygame.display.set_mode((WIDTH, HEIGHT + DEBUG_HEIGHT))

	ai = CheckerAI(Q_TABLE_FILE)
	bt = BoardTransition()

	TurnEvent = pygame.USEREVENT + 1

	trainActive = True
	currentEpoch = 0
	totalRewardApplied = 0

	while (currentEpoch < TRAIN_EPOCH and trainActive):
		print("Epoch: ", currentEpoch)
		pygame.time.set_timer(TurnEvent, TURN_TIME)
		CB = CheckerBoard()
		CB.initializeBoard()

		gameActive = True
		repeatedMoves = dict()
		currentBoardEval = 0

		while gameActive:
			CB.drawBoard(window)
			time = pygame.time.get_ticks()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					trainActive = False
					gameActive = False
				elif (event.type == TurnEvent):
					# depth = int(180/(CB.player1NumPieces + CB.player2NumPieces + 36))
					nextBestMove = ai.nextBestMove(CB, 2)
					ai.linkVisitedBoard(nextBestMove)

					# Game Draw logic
					if (repeatedMoves.get(nextBestMove) is not None):
						if (repeatedMoves[nextBestMove] >= 3):
							print("Boards repeated resulted in a draw!")
							totalRewardApplied += ai.applyQReward(0)
							gameActive = False
						else:
							repeatedMoves[nextBestMove] += 1
					else:
						repeatedMoves[nextBestMove] = 1

					CB < nextBestMove
					currentBoardEval = ai.evaluateBoard(CB)

					nextBoardStates = bt.getAllBoards(CB)
					wonPlayer = CB.gameEnd(len(nextBoardStates))
					if (wonPlayer == _P1PIECE):
						print("player 1 won!")
						totalRewardApplied += ai.applyQReward(wonPlayer)
						gameActive = False
					elif (wonPlayer == _P2PIECE):
						print("player 2 won!")
						totalRewardApplied += ai.applyQReward(wonPlayer)
						gameActive = False

					pygame.time.set_timer(TurnEvent, TURN_TIME)
			
					
			# Monitoring Performance
			# clock.tick()
			# print(clock.get_fps())

			CB.drawPieces(window)
			CB.debug(window, currentBoardEval, "Current Board Evaluation")

			pygame.display.update()

		currentEpoch += 1

	print("Average Reward per Episode over", currentEpoch, " episodes is: ", totalRewardApplied / currentEpoch)
	pygame.quit()

