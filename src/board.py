from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound

import os

import copy

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]

        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, test=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if piece.name == 'pawn':
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:

                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not test:
                    sound = Sound(os.path.join('sounds/capture.mp3'))
                    sound.play()
                
            else:
                self.check_promotion(piece, final)


        if piece.name == 'king':
            if self.castling(initial, final) and not test:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        piece.moved = True

        piece.clear_moves()

        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves
    
    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2
    
    def true_en_passant(self, piece):
        if piece.name != 'pawn':
            return
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True
    
    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, test=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemypiece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True

        return False   


    def calc_moves(self, piece, row, col, bool=True):

        def pawn_moves():
            steps = 1 if piece.moved else 2

            start = row + piece.dir
            end = row + piece.dir * (1 + steps)
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        initial = Square(row, col)
                        final = Square(move_row, col)

                        move = Move(initial, final)

                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                    else:
                        break
                else:
                    break

            move_row = row + piece.dir
            move_cols = [col-1, col+1]
            for move_col in move_cols:
                if Square.in_range(move_row, move_col):
                    if self.squares[move_row][move_col].has_enemypiece(piece.color):
                        initial = Square(row, col)
                        final_piece = self.squares[move_row][move_col].piece
                        final = Square(move_row, move_col, final_piece)
                        
                        move = Move(initial, final)

                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        
                        else:
                            piece.add_move(move)


            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_enemypiece(piece.color):
                    p = self.squares[row][col-1].piece
                    if p.name == 'pawn':
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)

                            move = Move(initial, final)

                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)

                            else:
                                piece.add_move(move)

            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_enemypiece(piece.color):
                    p = self.squares[row][col+1].piece
                    if p.name == 'pawn':
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col+1, p)

                            move = Move(initial, final)

                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            

        def straightline_moves(increments):
            for incr in increments:
                row_incr, col_incr = incr
                move_row = row + row_incr
                move_col = col + col_incr

                while True:
                    if Square.in_range(move_row, move_col):
                        initial = Square(row, col)
                        final_piece  = self.squares[move_row][move_col].piece
                        final = Square(move_row, move_col, final_piece)
                        move = Move(initial, final)

                        if self.squares[move_row][move_col].isempty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                        
                        elif self.squares[move_row][move_col].has_enemypiece(piece.color):
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break

                        elif self.squares[move_row][move_col].has_playerpiece(piece.color):
                            break

                    else: break

                    move_row += row_incr
                    move_col += col_incr

        def knight_moves():
            poss_moves = [(row-2, col+1), (row-2, col-1), (row+1, col+2), (row+1, col-2), (row+2, col+1), (row+2, col-1), (row-1, col+2), (row-1, col-2)]

            for move in poss_moves:
                move_row, move_col = move

                if Square.in_range(move_row, move_col):
                    if self.squares[move_row][move_col].isempty_or_enemy(piece.color):
                        
                        initial = Square(row, col)
                        final_piece  = self.squares[move_row][move_col].piece
                        final = Square(move_row, move_col, final_piece)

                        move = Move(initial, final)
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else:
                                break
                        else:
                            piece.add_move(move)

        def king_moves():
            poss_moves =[(row-1, col+0), (row-1, col+1), (row+0, col+1), (row+1, col+1), (row+1, col+0), (row+1, col-1), (row+0, col-1), (row-1, col-1)]

            for move in poss_moves:
                move_row, move_col = move

                if Square.in_range(move_row, move_col):
                    if self.squares[move_row][move_col].isempty_or_enemy(piece.color):
                        initial = Square(row, col)
                        final = Square(move_row, move_col)
                        move = Move(initial, final)

                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            if not piece.moved:
                left_rook = self.squares[row][0].piece
                if left_rook.name == 'rook':
                    if not left_rook.moved:
                        for i in range(1, 4):
                            if self.squares[row][i].has_piece():
                                break

                            if i == 3:
                                piece.left_rook = left_rook
                                
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)
                                left_rook.add_move(moveR)

                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        left_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    left_rook.add_move(moveR)
                                    piece.add_move(moveK)

                right_rook = self.squares[row][7].piece
                if right_rook.name == 'rook':
                    if not right_rook.moved:
                        for i in range(5, 7):
                            if self.squares[row][i].has_piece():
                                break

                            if i == 6:
                                piece.right_rook = right_rook
                                
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)
                                
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        right_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    right_rook.add_move(moveR)
                                    piece.add_move(moveK)


        if piece.name == 'pawn':
            pawn_moves()
        elif piece.name == 'knight':
            knight_moves()
        elif piece.name == 'bishop':
            straightline_moves([(-1, 1), (-1, -1), (1, 1), (1, -1)])
        elif piece.name == 'rook':
            straightline_moves([(-1, 0), (1, 0), (0, 1), (0, -1)])
        elif piece.name == 'queen':
            straightline_moves([(-1, 1), (-1, -1), (1, 1), (1, -1), (-1, 0), (1, 0), (0, 1), (0, -1)])
        elif piece.name == 'king':
            king_moves()
    
    def _create(self):
        
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = ((6, 7) if color == 'white' else (1, 0))

        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))
    
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        self.squares[row_other][4] = Square(row_other, 4, King(color))

        self.squares[row_other][3] = Square(row_other, 3, Queen(color))