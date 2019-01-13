import random
import sys


class Player2:
    def __init__(self, level, HP=3):
        self.grid = level.grid
        self.name = "player"
        self.x_pos = level.nbCol - 1
        self.y_pos = level.nbLine - 1
        self.has_key = False
        self.has_treasure = False
        self.win = False
        self.has_sword = False
        self.life = HP
        self.max_col = level.nbCol
        self.max_line = level.nbLine
        self.prev_pos = [self.x_pos, self.y_pos]

    def move_up(self):
        self.prev_pos = [self.x_pos, self.y_pos]
        if self.y_pos - 1 >= 0:
            if self.grid[self.y_pos-1][self.x_pos] != '_':
                self.y_pos -= 1
                return True
        return False

    def move_down(self):
        self.prev_pos = [self.x_pos, self.y_pos]
        if self.y_pos + 1 < self.max_line:
            if self.grid[self.y_pos+1][self.x_pos] != '_':
                self.y_pos += 1
                return True
        return False

    def move_left(self):
        self.prev_pos = [self.x_pos, self.y_pos]
        if self.x_pos - 1 >= 0:
            if self.grid[self.y_pos][self.x_pos-1] != '_':
                self.x_pos -= 1
                return True
        return False

    def move_right(self):
        self.prev_pos = [self.x_pos, self.y_pos]
        if self.x_pos + 1 < self.max_col:
            if self.grid[self.y_pos][self.x_pos+1] != '_':
                self.x_pos += 1
                return True
        return False

    def is_dead(self):
        return self.life <= 0

    def get_state(self):
        return (
            self.has_key,
            self.has_sword,
            self.has_treasure,
            self.life <= 1
        )

    def grid_reaction(self):
        if self.grid[self.y_pos][self.x_pos] == "K":  # key pickup
            self.has_key = True
            self.grid[self.y_pos][self.x_pos] = 'B'
        elif self.grid[self.y_pos][self.x_pos] == "T":  # treasure pickup
            if self.has_key:
                self.has_treasure = True
                self.grid[self.y_pos][self.x_pos] = 'B'
        elif self.grid[self.y_pos][self.x_pos] == "S":  # game ending
            if self.has_treasure:
                self.win = True
        elif self.grid[self.y_pos][self.x_pos] == "E":  # fighting an enemy
            if not self.has_sword:
                if random.uniform(0, 1) < 0.3:
                    self.life -= 1
            # self.grid[self.y_pos][self.x_pos] = 'B'
        elif self.grid[self.y_pos][self.x_pos] == "C":  # falling into crack
            self.life -= 1
            return True, False
        elif self.grid[self.y_pos][self.x_pos] == "W":  # sword pickup
            self.has_sword = True
            self.grid[self.y_pos][self.x_pos] = 'B'
        elif self.grid[self.y_pos][self.x_pos] == "R":  # trap
            tmp = random.uniform(0, 1)
            if tmp <= 0.1:
                self.life -= 1
                return True, False
            elif tmp <= 0.3:
                self.x_pos = self.max_col - 1
                self.y_pos = self.max_line - 1
                return True, True
        elif self.grid[self.y_pos][self.x_pos] == "P":  # teleport
            self.x_pos = random.randint(0, self.max_col - 1)
            self.y_pos = random.randint(0, self.max_line - 1)
            while self.grid[self.y_pos][self.x_pos] == "_" or  \
                    self.x_pos == self.prev_pos[0] and self.y_pos == self.prev_pos[1]:
                self.x_pos = random.randint(0, self.max_col - 1)
                self.y_pos = random.randint(0, self.max_line - 1)
            return True, True
        elif self.grid[self.y_pos][self.x_pos] == "M":  # moving platform
            moved = False
            while not moved:
                tmp = random.randint(0, 3)
                if tmp == 0:
                    if self.x_pos + 1 != self.max_col and self.x_pos + 1 != self.prev_pos[0] and \
                            self.grid[self.y_pos][self.x_pos + 1] != "_":
                        self.x_pos += 1
                        moved = True
                elif tmp == 1:
                    if self.x_pos - 1 != -1 and self.x_pos - 1 != self.prev_pos[0]and \
                            self.grid[self.y_pos][self.x_pos - 1] != "_":
                        self.x_pos -= 1
                        moved = True
                elif tmp == 2:
                    if self.y_pos + 1 != self.max_line and self.y_pos + 1 != self.prev_pos[1]and \
                            self.grid[self.y_pos + 1][self.x_pos] != "_":
                        self.y_pos += 1
                        moved = True
                else:
                    if self.y_pos - 1 != -1 and self.y_pos - 1 != self.prev_pos[1]and \
                            self.grid[self.y_pos - 1][self.x_pos] != "_":
                        self.y_pos -= 1
                        moved = True
            return True, True

        return False, False
