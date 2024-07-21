import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('CHESS')
        self.game = Game()

    def mainloop(self):

        game =  self.game
        screen = self.screen
        dragger = self.game.dragger
        board = self.game.board
        
        while True:
            game.show_background(screen)
            game.show_lastmove(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if dragger.dragging:
                dragger.update_blit(screen)
            
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    
                    clicked_row = dragger.mouseY // SQ_SIZE
                    clicked_col = dragger.mouseX // SQ_SIZE

                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        if piece.color == game.next_player:
                            board.calc_moves(piece, clicked_row, clicked_col)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)

                            game.show_background(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQ_SIZE
                    motion_col = event.pos[0] // SQ_SIZE
                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        game.show_background(screen)
                        game.show_lastmove(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)

                elif event.type == pygame.MOUSEBUTTONUP:
                    
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQ_SIZE
                        released_col = dragger.mouseX // SQ_SIZE

                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        if board.valid_move(dragger.piece, move):
                            captured = board.squares[released_row][released_col].has_piece()
                            board.move(dragger.piece, move)
                            board.true_en_passant(dragger.piece)
                            game.play_sound(captured)
                            game.show_background(screen)
                            game.show_lastmove(screen)
                            game.show_pieces(screen)
                            game.next_turn()

                    
                    dragger.undrag_piece()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset()
                        game =  self.game
                        dragger = self.game.dragger
                        board = self.game.board


                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            
            pygame.display.update()


main = Main()
main.mainloop()