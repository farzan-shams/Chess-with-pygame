import pygame
from board import Board
from dragger import Dragger
from config import Config
from square import Square

from const import *

class Game:
    def __init__(self):
        self.next_player = 'white'
        self.hover_square = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()


    def show_background(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    color = (227,193,160)
                else:
                    color = (184,140,80)
                
                rect = (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)

                pygame.draw.rect(surface, color, rect)

                if col == 0:
                    color = (184, 140, 80) if row % 2 == 0 else (227, 193, 160)
                    label = self.config.font.render(str(ROWS-row), 1, color)
                    label_pos = (5, 5 + row * SQ_SIZE)
                    surface.blit(label, label_pos)

                if row == 7:
                    color = (184, 140, 80) if (row + col) % 2 ==0 else (227, 193, 160)
                    label = self.config.font.render(Square.get_alphacol(col), 1, color)
                    label_pos = (col * SQ_SIZE + SQ_SIZE - 20, HEIGHT - 20)
                    surface.blit(label, label_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    if piece is not self.dragger.piece:  
                        piece.set_texture(size = 80)  
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQ_SIZE + SQ_SIZE //2, row * SQ_SIZE + SQ_SIZE // 2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        if self.dragger.dragging:
            piece = self.dragger.piece

            for move in piece.moves:
                color = ('#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C84646')
                rect = (move.final.col * SQ_SIZE, move.final.row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(surface, color, rect)

    def show_lastmove(self, surface):
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = (244, 247, 116) if (pos.row + pos.col) % 2 == 0 else (172, 195, 51)
                rect = (pos.col * SQ_SIZE, pos.row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hover_square:
            color = (180, 180, 180)
            rect = (self.hover_square.col * SQ_SIZE, self.hover_square.row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(surface, color, rect, width=3)



    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hover_square = self.board.squares[row][col]

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()