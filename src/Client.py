from GameLogic.Util import WIDTH, HEIGHT
import pygame
from Network import Network
from GameLogic.Game import Game
pygame.font.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")

'''Client's Game Implementation:
        - Onces client ready, waits for Server to signal that game is starting
        - Every 30fps, client will send Server its current coords
        - Server will process that coords and send client back the 'updated' tiles if 
            it passed the tile checking
        - If client passed the tile checking, client will update its own board (by setting the tile colour)
        '''


def main(network):
    run = True
    clock = pygame.time.Clock()
    n = network
    player = int(n.get_p())
    print("You are Player", player)

    while run:
        clock.tick(60)  # Runs the game in 60fps
        try:
            # Get data from the server in 60fps (to update own board) 
            board = n.send("get")
            g = Game(board.get_board())
            g.game_screen()
            while True:
                g.input_dir(n)
                g.update()
                g.draw()
            
        
        except:
            run = False
            print("Couldn't get game")
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            # if other types of event (movements...)

        # run = False


def menu_screen():
    run = True
    clock = pygame.time.Clock()
    n = Network()

    win.fill((128, 128, 128))
    font = pygame.font.SysFont("comicsans", 60)
    text = font.render("Click to Play!", True, (255, 0, 0))
    win.blit(text, (100, 200))
    pygame.display.update()

    while run:
        clock.tick(60)  # Makes the client game run in 60fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("quitting game...")
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("button pressed - ready")
                run = False
                p1 = n.connect()
                print("p1: ", p1)
                new_game = n.send("playerOn")
                # new_game = n.recv()
                print("new game received: ", new_game)
                if new_game == "GameFull":
                    print("Game is full... Closing client connection...")
                    n.disconnect()
                    pygame.quit()
                    run = False

                win.fill((200, 200, 128))
                font = pygame.font.SysFont("comicsans", 60)
                text = font.render("Player READY", True, (255, 0, 0))
                win.blit(text, (100, 200))
                pygame.display.update()
    main(n)


while True:
    menu_screen()
